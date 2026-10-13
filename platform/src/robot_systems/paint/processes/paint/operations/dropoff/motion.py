"""Shared dropoff motion helpers and legacy configured dispatch entry points."""
from __future__ import annotations
from src.robot_systems.paint.contracts.dropoff import DropoffApproach

import logging
from dataclasses import dataclass

import numpy as np


from src.engine.geometry.planar import unwrap_degrees
from src.engine.robot.motion_sequence import (
    OrderedMotionMetadata,
    OrderedMotionProfile,
    OrderedMotionType,
    OrderedPositionCommand,
    OrderedUnwindJoint6Command,
)
from src.robot_systems.paint.contracts.next_cycle_target import NextCycleTarget
from src.robot_systems.paint.processes.paint.configuration.models import DropoffStrategy

_logger = logging.getLogger(__name__)


def _ordered_position_command(
    label: str,
    pose: object,
    velocity_percent: object,
    acceleration_percent: object,
    motion_type: OrderedMotionType,
    blend_radius: object = 0.0,
    *,
    protected: bool = False,
) -> OrderedPositionCommand:
    return OrderedPositionCommand(
        label=label,
        motion_type=motion_type,
        position=tuple(float(value) for value in pose),
        profile=OrderedMotionProfile(
            float(velocity_percent),
            float(acceleration_percent),
            float(blend_radius),
        ),
        metadata=OrderedMotionMetadata(protected=protected),
    )


def _parse_motion_type(value: object, *, field_name: str) -> OrderedMotionType:
    """Validate an external/configured motion type at its input boundary."""
    return OrderedMotionType.parse(value, field_name=field_name)


@dataclass(frozen=True)
class _DropoffRouteItem:
    label: str
    position: list[float]
    velocity_percent: float
    acceleration_percent: float
    motion_type: OrderedMotionType
    blend_radius: float


def open_dropoff_passage_for_preparation(executor: object) -> tuple[bool, str]:
    """Open the configured passage before planning any route that crosses its lid."""
    if _dropoff_strategy_name(executor) is DropoffStrategy.PLATE_LAYOUT:
        return True, ""
    # Validate the configured release target before changing the planning scene.
    # A disabled sub-zero dropoff must not open the paint passage or allow an
    # ordered cleanup chain containing that target to execute.
    if _dropoff_strategy_name(executor) is DropoffStrategy.MOVEMENT_GROUP:
        dropoff = executor._paint_process_config().dropoff
        pose = _resolve_dropoff_align_pose(executor)
        if pose is not None and float(pose[2]) < 0.0 and not dropoff.allow_sub_zero_dropoff:
            _logger.error(
                "[DROPOFF] Refusing preparation before opening passage: "
                "negative target with Allow Sub-Zero Dropoff disabled"
            )
            return False, "Dropoff cancelled: Allow Sub-Zero Dropoff is disabled"
    passage_id = str(executor._dropoff_motion_corridor_id or "")
    if not passage_id:
        return True, ""
    if not executor._robot_service.set_motion_passage_closed(passage_id, False):
        return False, f"Dropoff preparation cancelled: failed to open passage '{passage_id}'"
    _logger.info("[DROPOFF] Opened motion passage '%s' before dropoff-route planning", passage_id)
    return True, ""


def _on_workpiece_release_verified(executor: object) -> tuple[bool, str]:
    """Dispatch older release callers to the strategy's destination bookkeeping."""
    if _dropoff_strategy_name(executor) is DropoffStrategy.PLATE_LAYOUT:
        from .strategies.plate_layout import _on_workpiece_release_verified as notify
    else:
        from .strategies.movement_group import _on_workpiece_release_verified as notify
    return notify(executor)


def _verify_workpiece_released(executor: object) -> tuple[bool, str]:
    """Verify that vacuum cleared after pump-off at the dropoff waypoint."""
    pump_enabled = bool(executor._is_vacuum_pump_enabled())
    if not pump_enabled:
        _logger.info("[DROPOFF] Release verification skipped: vacuum pump disabled")
        return True, ""

    sensor = executor._vacuum_sensor
    if sensor is None:
        _logger.warning("[DROPOFF] Release verification skipped: vacuum sensor not configured")
        return True, ""

    _logger.info("[DROPOFF] Verifying workpiece release with vacuum sensor")
    try:
        vacuum_detected = bool(sensor.is_vacuum_detected())
    except Exception:
        _logger.exception("[DROPOFF] Vacuum sensor read raised during release verification")
        return False, "Vacuum pump turned off, but workpiece release verification failed: sensor read unavailable"
    if not bool(sensor.is_healthy()):
        return False, "Vacuum pump turned off, but workpiece release verification failed: sensor read unavailable"
    if vacuum_detected:
        return False, "Vacuum pump turned off, but the vacuum sensor still detects the workpiece"

    _logger.info("[DROPOFF] Workpiece release verified: vacuum is no longer detected")
    return True, ""


def build_ordered_dropoff_preparation_segments(
    executor: object,
) -> tuple[list[OrderedPositionCommand | OrderedUnwindJoint6Command], list[float] | None]:
    """
    Build the post-paint ordered dropoff preparation chain.

    This is the place to adjust ordered dropoff preparation move shape:

    - safe-travel segment labels
    - safe-travel/dropoff align velocity and acceleration
    - route `blendR`
    - final Joint 6 unwind segment settings
    """
    config = executor._paint_process_config()
    route_items: list[_DropoffRouteItem] = []

    safe_waypoints = _resolve_dropoff_safe_travel_waypoints(executor)
    if bool(config.dropoff_safe_travel.enabled):
        if not safe_waypoints:
            return [], None

        for index, safe_waypoint in enumerate(safe_waypoints, start=1):
            route_items.append(_DropoffRouteItem(
                label=f"prepare_dropoff_safe_travel_{index}",
                position=list(safe_waypoint.position),
                velocity_percent=safe_waypoint.velocity_percent,
                acceleration_percent=safe_waypoint.acceleration_percent,
                motion_type=safe_waypoint.motion_type,
                blend_radius=safe_waypoint.blend_radius,
            ))

    if _should_prepare_dropoff_align_before_unwind(executor):
        reference_pose = route_items[-1].position if route_items else executor._last_process_end_pose
        align_pose = _resolve_dropoff_preparation_pose(executor, reference_pose)
        if align_pose is None:
            return [], None

        route_items.append(_DropoffRouteItem(
            label="prepare_dropoff_align",
            position=list(align_pose),
            velocity_percent=float(config.dropoff.release_align_vel_percent),
            acceleration_percent=float(config.dropoff.release_align_acc_percent),
            motion_type=_parse_motion_type(
                config.dropoff.release_align_motion_type,
                field_name="dropoff.release_align_motion_type",
            ),
            blend_radius=float(config.dropoff.release_align_blendR),
        ))

    segments: list[OrderedPositionCommand | OrderedUnwindJoint6Command] = []
    if route_items:
        start_pose = list(executor._last_process_end_pose) if executor._last_process_end_pose is not None else None
        adjusted_positions = _apply_distributed_dropoff_unwind(
            executor,
            [item.position for item in route_items],
            start_pose,
        )

        for index, (item, adjusted_position) in enumerate(zip(route_items, adjusted_positions)):
            is_last_route_pose = index == len(route_items) - 1
            segments.append(_ordered_position_command(
                item.label,
                adjusted_position,
                item.velocity_percent,
                item.acceleration_percent,
                item.motion_type,
                item.blend_radius,
            ))
        final_pose = list(adjusted_positions[-1])
    else:
        final_pose = list(executor._last_process_end_pose) if executor._last_process_end_pose is not None else None

    segments.append(OrderedUnwindJoint6Command(
        label="prepare_dropoff_unwind",
        velocity_percent=float(config.navigation_return.unwind_vel_percent),
        acceleration_percent=float(config.navigation_return.unwind_acc_percent),
        protected=True,
    ))

    release_pose = _resolve_dropoff_align_pose(executor, final_pose)
    if (
        release_pose is not None
        and len(release_pose) >= 3
        and float(release_pose[2]) < 0.0
        and config.dropoff.allow_sub_zero_dropoff
    ):
        # Unwind above the opening, then make the corridor descent the final
        # protected segment. The ordered chain therefore hard-stops exactly at
        # the configured release pose; DROPOFF releases there and retracts.
        descent_pose = list(final_pose) if final_pose is not None else list(release_pose)
        descent_pose[2] = float(release_pose[2])
        segments.append(_ordered_position_command(
            "prepare_dropoff_descend_to_release",
            descent_pose,
            config.dropoff.release_align_vel_percent,
            config.dropoff.release_align_acc_percent,
            OrderedMotionType.LINEAR,
            0.0,
            protected=True,
        ))
        final_pose = list(descent_pose)

    return segments, final_pose


def _resolve_dropoff_safe_travel_waypoints(executor: object) -> list[dict]:
    config = executor._paint_process_config().dropoff_safe_travel
    if not bool(config.enabled):
        return []
    dropoff = executor._paint_process_config().dropoff
    return executor._read_configured_waypoints(
        config.positions,
        float(dropoff.release_align_vel_percent),
        float(dropoff.release_align_acc_percent),
        OrderedMotionType.PTP,
    )


def _apply_distributed_dropoff_unwind(
    executor: object,
    poses: list[list[float]],
    start_pose: list[float] | None,
) -> list[list[float]]:
    """
    Progressively shift the active rotation component by whole-turn equivalents
    so Joint 6 can unwind while travelling toward dropoff.
    """
    if not poses:
        return []

    adjusted = [list(pose) for pose in poses]
    if start_pose is None or len(start_pose) < 6:
        return adjusted

    rotation_index = int(executor._contact_motion_config.rotation_index)
    if rotation_index < 0 or len(start_pose) <= rotation_index:
        return adjusted
    if any(len(pose) <= rotation_index for pose in adjusted):
        return adjusted

    start_rotation_deg = float(start_pose[rotation_index])
    nominal_continuous_rotations: list[float] = []
    previous_nominal_rotation_deg = start_rotation_deg

    for pose in adjusted:
        nominal_rotation_deg = float(pose[rotation_index])
        continuous_rotation_deg = unwrap_degrees(previous_nominal_rotation_deg, nominal_rotation_deg)
        nominal_continuous_rotations.append(continuous_rotation_deg)
        previous_nominal_rotation_deg = continuous_rotation_deg

    if not nominal_continuous_rotations:
        return adjusted

    final_nominal_continuous_deg = nominal_continuous_rotations[-1]
    final_canonical_deg = ((final_nominal_continuous_deg + 180.0) % 360.0) - 180.0
    unwind_shift_deg = final_canonical_deg - final_nominal_continuous_deg
    unwind_turns = int(round(unwind_shift_deg / 360.0))
    unwind_shift_deg = 360.0 * unwind_turns

    if unwind_turns == 0:
        _logger.info(
            "[DROPOFF] Distributed unwind not needed: start_rotation=%.3fdeg final_nominal_continuous=%.3fdeg",
            start_rotation_deg,
            final_nominal_continuous_deg,
        )
        return adjusted

    route = [list(start_pose), *adjusted]
    segment_lengths: list[float] = []
    for index in range(1, len(route)):
        previous_xyz = np.asarray(route[index - 1][:3], dtype=float)
        current_xyz = np.asarray(route[index][:3], dtype=float)
        segment_lengths.append(float(np.linalg.norm(current_xyz - previous_xyz)))

    total_distance = float(sum(segment_lengths))
    if total_distance <= 1e-6:
        _logger.warning("[DROPOFF] Distributed unwind skipped because dropoff route has no XYZ travel")
        return adjusted

    cumulative_distance = 0.0
    applied_rotations: list[float] = []
    for index, pose in enumerate(adjusted):
        cumulative_distance += segment_lengths[index]
        fraction = max(0.0, min(1.0, cumulative_distance / total_distance))
        final_rotation_deg = nominal_continuous_rotations[index] + (unwind_shift_deg * fraction)
        pose[rotation_index] = final_rotation_deg
        applied_rotations.append(final_rotation_deg)

    _logger.info(
        "[DROPOFF] Distributed unwind over travel: start_rotation=%.3fdeg nominal_rotations=%s unwind_turns=%d unwind_shift=%.3fdeg applied_rotations=%s travel_mm=%.3f",
        start_rotation_deg,
        [round(value, 3) for value in nominal_continuous_rotations],
        unwind_turns,
        unwind_shift_deg,
        [round(value, 3) for value in applied_rotations],
        total_distance,
    )
    return adjusted


def _should_prepare_dropoff_align_before_unwind(executor: object) -> bool:
    if _dropoff_strategy_name(executor) in {
        DropoffStrategy.MOVEMENT_GROUP,
        DropoffStrategy.PLATE_LAYOUT,
    }:
        return _resolve_dropoff_release_pose(executor) is not None
    return (
        executor._configured_contact_motion_plane == "xz_y_ry"
        and _resolve_dropoff_release_pose(executor) is not None
    )


def _dropoff_strategy_name(executor: object) -> DropoffStrategy:
    # Runtime configuration is frozen for normal cycles. Prefer the injected
    # built-in identity as well, so direct injection and pinned cycle selection
    # cannot accidentally resolve geometry for a different destination.
    name = getattr(getattr(executor, "_dropoff_strategy", None), "name", None)
    if isinstance(name, DropoffStrategy):
        return name
    return executor._paint_process_config().dropoff.strategy


def _resolve_dropoff_release_pose(executor: object) -> list[float] | None:
    if _dropoff_strategy_name(executor) is DropoffStrategy.PLATE_LAYOUT:
        service = executor._plate_layout_service
        reservation = None if service is None else service.pending
        return None if reservation is None else list(reservation.release_pose)
    if _dropoff_strategy_name(executor) is DropoffStrategy.MOVEMENT_GROUP:
        return executor._read_provider_position(executor._dropoff_position_provider)
    if executor._last_pickup_plan is not None and hasattr(executor._last_pickup_plan, "align_pose"):
        return list(executor._last_pickup_plan.align_pose)
    return None


def _resolve_dropoff_align_pose(executor: object, reference_pose: list[float] | None = None) -> list[float] | None:
    pose = _resolve_dropoff_release_pose(executor)
    if pose is None:
        return None
    return _dropoff_align_pose_near_reference(executor, pose, reference_pose)


def _resolve_dropoff_preparation_pose(
    executor: object,
    reference_pose: list[float] | None = None,
) -> list[float] | None:
    """Resolve the safe above-floor endpoint used before a corridor dropoff."""
    if _dropoff_strategy_name(executor) is DropoffStrategy.PLATE_LAYOUT:
        service = executor._plate_layout_service
        reservation = None if service is None else service.pending
        return None if reservation is None else list(reservation.approach_pose)
    pose = _resolve_dropoff_align_pose(executor, reference_pose)
    if pose is None or len(pose) < 3 or float(pose[2]) >= 0.0:
        return pose
    dropoff = executor._paint_process_config().dropoff
    if not dropoff.allow_sub_zero_dropoff:
        return pose
    approach_pose = list(pose)
    approach_pose[2] = float(dropoff.sub_zero_approach_z_mm)
    return approach_pose


def _dropoff_align_pose_near_reference(
    executor: object,
    align_pose: list[float],
    reference_pose: list[float] | None = None,
) -> list[float]:
    pose = list(align_pose)
    reference = reference_pose or executor._last_process_end_pose
    if (
        executor._configured_contact_motion_plane == "xy_z_rz"
        and reference is not None
        and len(pose) >= 6
        and len(reference) >= 6
    ):
        pose[5] = unwrap_degrees(float(reference[5]), float(pose[5]))
    return pose


def execute_dropoff_preparation_for_executor(executor: object) -> tuple[bool, str]:
    """Dispatch existing callers to strategy-owned preparation code."""
    if _dropoff_strategy_name(executor) is DropoffStrategy.PLATE_LAYOUT:
        from .strategies.plate_layout import _execute_plate_layout_preparation
        if executor._dropoff_unwind_prepared:
            return True, ""
        return _execute_plate_layout_preparation(executor)
    from .strategies.movement_group import execute_dropoff_preparation_for_executor as prepare
    return prepare(executor)


def execute_dropoff_release_for_executor(
    executor: object, *, next_cycle_start: NextCycleTarget | None = None,
) -> tuple[bool, str]:
    """Dispatch existing callers to strategy-owned verified release code."""
    if _dropoff_strategy_name(executor) is DropoffStrategy.PLATE_LAYOUT:
        from .strategies.plate_layout import _execute_plate_layout_ordered_release
        executor._last_prepositioned_start_group = None
        return _execute_plate_layout_ordered_release(executor, next_cycle_start=next_cycle_start)
    from .strategies.movement_group import execute_dropoff_release_for_executor as release
    return release(executor, next_cycle_start=next_cycle_start)


def _cleanup_position_command(
    label: str,
    motion_type: object,
    position: object,
    velocity_percent: object,
    acceleration_percent: object,
    blend_radius: object,
) -> OrderedPositionCommand:
    """Build one strictly typed cleanup/drop-off position command."""
    return OrderedPositionCommand(
        label=label,
        motion_type=OrderedMotionType(str(motion_type).strip().lower()),
        position=tuple(float(value) for value in position),
        profile=OrderedMotionProfile(
            velocity_percent=float(velocity_percent),
            acceleration_percent=float(acceleration_percent),
            blend_radius=float(blend_radius),
        ),
    )


def build_cleanup_dropoff_approach(executor, final_pose: list[float]) -> DropoffApproach:
    """Preserve the shared cleanup-to-destination safe-travel/unwind sequence."""
    config = executor._paint_process_config()
    post_cleanup_align_pose = None
    if _should_prepare_dropoff_align_before_unwind(executor):
        post_cleanup_align_pose = _resolve_dropoff_preparation_pose(executor, final_pose)
    segments = []
    if post_cleanup_align_pose is not None:
        safe_travel_waypoints = _resolve_dropoff_safe_travel_waypoints(executor)
        if config.dropoff_safe_travel.enabled and safe_travel_waypoints:
            for index, safe_travel_waypoint in enumerate(safe_travel_waypoints, start=1):
                segments.append(_cleanup_position_command(
                    f"prepare_dropoff_safe_travel_{index}",
                    safe_travel_waypoint.motion_type,
                    safe_travel_waypoint.position,
                    safe_travel_waypoint.velocity_percent,
                    safe_travel_waypoint.acceleration_percent,
                    safe_travel_waypoint.blend_radius,
                ))
        segments.append(_cleanup_position_command(
            "prepare_dropoff_align",
            config.dropoff.release_align_motion_type,
            post_cleanup_align_pose,
            config.dropoff.release_align_vel_percent,
            config.dropoff.release_align_acc_percent,
            config.dropoff.release_align_blendR,
        ))
    elif config.dropoff_safe_travel.enabled:
        safe_travel_waypoints = _resolve_dropoff_safe_travel_waypoints(executor)
        for index, safe_travel_waypoint in enumerate(safe_travel_waypoints, start=1):
            segments.append(_cleanup_position_command(
                f"prepare_dropoff_safe_travel_{index}",
                safe_travel_waypoint.motion_type,
                safe_travel_waypoint.position,
                safe_travel_waypoint.velocity_percent,
                safe_travel_waypoint.acceleration_percent,
                safe_travel_waypoint.blend_radius,
            ))
            post_cleanup_align_pose = list(safe_travel_waypoint.position)
    segments.append(OrderedUnwindJoint6Command(
        label="prepare_dropoff_unwind",
        velocity_percent=float(config.navigation_return.unwind_vel_percent),
        acceleration_percent=float(config.navigation_return.unwind_acc_percent),
    ))
    return DropoffApproach(tuple(segments), list(post_cleanup_align_pose or final_pose), prepares_release=True)
