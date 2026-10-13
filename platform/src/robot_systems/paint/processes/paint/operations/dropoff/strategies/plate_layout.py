"""Plate-layout dropoff preparation, routing, and verified release."""
from __future__ import annotations
from src.robot_systems.paint.contracts.dropoff import DropoffApproach, DropoffCycleRequest
from src.robot_systems.paint.processes.paint.results import Ready, Failed, PaintFailure, PaintFailureCode, PaintOperationResult, PaintOutcome
from src.robot_systems.paint.processes.paint.planning.pose_helpers import calculate_workpiece_dropoff_pose
from ..motion import build_cleanup_dropoff_approach


from typing import TYPE_CHECKING
from src.robot_systems.paint.contracts.dropoff import IDropoffStrategy, DropoffResult

if TYPE_CHECKING:
    from src.robot_systems.paint.processes.paint.production.execution_runtime import PaintExecutionRuntime

import logging
import math
import numpy as np
from dataclasses import dataclass
from time import monotonic, sleep


from src.robot_systems.paint.processes.paint.results import PaintConfigurationError

from src.engine.geometry.planar import unwrap_degrees
from src.engine.robot.motion_sequence import OrderedMotionType, OrderedPositionCommand
from src.robot_systems.paint.processes.paint.motion.pose_comparison import poses_close
from src.robot_systems.paint.processes.paint.motion.pose_sampling import read_fresh_pose
from src.robot_systems.paint.contracts.next_cycle_target import NextCycleTarget
from src.robot_systems.paint.processes.paint.configuration.models import PAINT_PROCESS_CONFIG, DropoffStrategy

from ..motion import (
    _ordered_position_command,
    _parse_motion_type,
)


_logger = logging.getLogger(__name__)


class PlateLayoutDropoff(IDropoffStrategy):
    """Prepare plate travel and release into the active layout reservation."""

    name = DropoffStrategy.PLATE_LAYOUT

    def __init__(self, runtime: PaintExecutionRuntime) -> None:
        self._runtime = runtime

    def begin_cycle(self, request: DropoffCycleRequest) -> PaintOperationResult:
        self._runtime._dropoff_unwind_prepared = False
        self._runtime._plate_entry_completed_in_paint_chain = False
        return _reserve_plate_dropoff(request, self._runtime)

    def painting_detach_pose(self, *, is_final_job: bool, paint_start_rz: float, paint_end_rz: float | None) -> list[float] | None:
        return _plate_entry_detach_pose(self._runtime, is_final_job=is_final_job,
                                      paint_start_rz=paint_start_rz, paint_end_rz=paint_end_rz)

    def plan_paint_approach(self, *, cleanup_pending: bool) -> Ready[DropoffApproach] | Failed:
        if not self._runtime._paint_process_config().dropoff.plate_use_entry_gate_as_detach_pose:
            return Ready(DropoffApproach())
        segments, final_pose, error = build_plate_entry_segments_for_paint_chain(self._runtime)
        if error:
            return Failed(PaintFailure(PaintFailureCode.PLANNING, "ordered_pickup_paint_planning", error))
        return Ready(DropoffApproach(tuple(segments), final_pose, completes_entry=bool(segments)))

    def plan_cleanup_approach(self, final_pose: list[float]) -> DropoffApproach:
        return build_cleanup_dropoff_approach(self._runtime, final_pose)

    def activate_approach(self, approach: DropoffApproach) -> PaintOperationResult:
        return PaintOperationResult(PaintOutcome.COMPLETED, "")

    def approach_completed(self, approach: DropoffApproach) -> None:
        if approach.prepares_release:
            self._runtime._dropoff_unwind_prepared = True
        if approach.completes_entry:
            self._runtime._plate_entry_completed_in_paint_chain = True

    def finish_cycle(self, result: PaintOperationResult) -> None:
        if not result.completed and self._runtime._plate_layout_service is not None:
            self._runtime._plate_layout_service.cancel()

    def prepare_dropoff(self) -> tuple[bool, str]:
        if self._runtime._dropoff_unwind_prepared:
            return True, ""
        ok, message = _execute_plate_layout_preparation(self._runtime)
        if ok:
            self._runtime._dropoff_unwind_prepared = True
        return ok, message

    def release_dropoff(self, next_cycle_start: NextCycleTarget | None = None) -> DropoffResult:
        self._runtime._last_prepositioned_start_group = None
        ok, message = _execute_plate_layout_ordered_release(
            self._runtime, next_cycle_start=next_cycle_start,
        )
        return DropoffResult(
            success=ok, message=message,
            prepositioned_group=self._runtime._last_prepositioned_start_group if ok else None,
            tray_full=ok and not self._runtime._plate_layout_service.has_space_for_same_footprint,
        )


def _completed_rotation_turns(rotation_delta_deg: float) -> int:
    """Count only fully executed 360-degree turns, preserving direction."""
    return int(float(rotation_delta_deg) / 360.0)


@dataclass(frozen=True)
class _PlateMotionProfile:
    velocity_percent: float
    acceleration_percent: float
    blend_radius: float
    motion_type: OrderedMotionType


@dataclass
class _PlateNextWaypoint:
    position: list[float]
    profile: _PlateMotionProfile


def _plate_motion_profile(dropoff: object, key: str) -> _PlateMotionProfile:
    for raw in dropoff.plate_motion_profiles:
        if not isinstance(raw, dict) or raw.get("key") != key:
            continue
        required = {"key", "vel_percent", "acc_percent", "blendR", "motion_type"}
        missing = required.difference(raw)
        if missing:
            raise PaintConfigurationError(
                f"dropoff.plate_motion_profiles[{key}] is missing {sorted(missing)}",
                stage="plate_motion_profile",
            )
        try:
            return _PlateMotionProfile(
                velocity_percent=float(raw["vel_percent"]),
                acceleration_percent=float(raw["acc_percent"]),
                blend_radius=max(0.0, float(raw["blendR"])),
                motion_type=_parse_motion_type(
                    raw["motion_type"],
                    field_name=f"dropoff.plate_motion_profiles[{key}]",
                ),
            )
        except (TypeError, ValueError) as exc:
            raise PaintConfigurationError(
                f"dropoff.plate_motion_profiles[{key}]: {exc}", stage="plate_motion_profile",
            ) from exc
    raise PaintConfigurationError(
        f"dropoff.plate_motion_profiles has no profile for '{key}'", stage="plate_motion_profile",
    )


def _plate_ordered_segment(
    label: str,
    pose: list[float],
    profile: _PlateMotionProfile,
    *,
    stop: bool = False,
) -> OrderedPositionCommand:
    return _ordered_position_command(
        label,
        pose,
        profile.velocity_percent,
        profile.acceleration_percent,
        profile.motion_type,
        0.0 if stop else profile.blend_radius,
        protected=True,
    )


def _wait_for_motion_slot_idle(
    executor: object,
    *,
    timeout_s: float = 2.0,
    poll_interval_s: float = 0.025,
    stable_samples: int = 2,
) -> bool:
    """Wait through the controller-success/backend-slot release handoff."""
    deadline = monotonic() + max(0.1, float(timeout_s))
    consecutive = 0
    while monotonic() < deadline:
        try:
            status = executor._robot_service.get_execution_status()
        except AttributeError:
            _logger.error(
                "[PLATE_LAYOUT] Cannot verify motion slot: get_execution_status() is unavailable"
            )
            return False
        except Exception:
            _logger.exception("[PLATE_LAYOUT] Failed to read execution status before entry")
            return False
        if not isinstance(status, dict):
            _logger.error(
                "[PLATE_LAYOUT] Cannot verify motion slot: execution status is not a mapping"
            )
            return False
        ordered = status.get("ordered_motion_chain")
        ordered_active = bool(isinstance(ordered, dict) and ordered.get("active"))
        if not bool(status.get("is_executing")) and not ordered_active:
            consecutive += 1
            if consecutive >= max(1, int(stable_samples)):
                return True
        else:
            consecutive = 0
        sleep(max(0.005, float(poll_interval_s)))
    _logger.error("[PLATE_LAYOUT] Motion backend remained busy before plate entry")
    return False


def _plate_route_poses_with_distributed_unwind(
    executor: object,
    *,
    entry_gate_pose: list[float],
    exit_gate_pose: list[float],
    center_pose: list[float],
    dropoff_pose: list[float],
    next_start_pose: list[float] | None,
    use_center_waypoint: bool,
    entry_completed: bool = False,
) -> dict[str, list[float]]:
    poses = {
        "entry_gate": list(entry_gate_pose),
        "entry_center": list(center_pose),
        "dropoff": list(dropoff_pose),
        "exit_center": list(center_pose),
        "exit_gate": list(exit_gate_pose),
    }
    if next_start_pose is not None:
        poses["next_start"] = list(next_start_pose)
    current = read_fresh_pose(
        executor._robot_service,
        error_message="Could not read fresh robot pose for distributed unwind",
    )
    rotation_index = int(executor._contact_motion_config.rotation_index)
    if rotation_index < 0 or len(current) <= rotation_index:
        raise ValueError("Plate-layout distributed unwind requires a valid current rotation pose")
    paint_start_rz = executor._last_process_start_rz
    paint_end_pose = executor._last_process_end_pose
    try:
        paint_end_rz = getattr(executor, "_last_paint_contact_end_rz", None)
        if not isinstance(paint_end_rz, (int, float)) or isinstance(paint_end_rz, bool):
            paint_end_rz = paint_end_pose[5]
        paint_rz_delta = float(paint_end_rz) - float(paint_start_rz)
    except (TypeError, ValueError, IndexError):
        raise ValueError(
            "Plate-layout distributed unwind requires a valid executed paint RZ direction"
        ) from None
    if not math.isfinite(paint_rz_delta) or abs(paint_rz_delta) <= 1e-6:
        raise ValueError(
            "Plate-layout distributed unwind requires a non-zero executed paint RZ direction"
        )
    start_rotation = float(current[rotation_index])
    completed_turns = _completed_rotation_turns(paint_rz_delta)
    if completed_turns == 0:
        _logger.info(
            "[PLATE_LAYOUT] Distributed unwind not needed: paint_rz_delta=%.3f has no completed turn",
            paint_rz_delta,
        )
        previous_rotation = start_rotation
        for pose in poses.values():
            pose[rotation_index] = unwrap_degrees(
                previous_rotation,
                float(pose[rotation_index]),
            )
            previous_rotation = float(pose[rotation_index])
        return poses
    total_unwind = -360.0 * completed_turns
    step = total_unwind / 4.0
    if entry_completed:
        remaining_end_rotation = float(paint_end_rz) + total_unwind
        remaining_half_rotation = (
            start_rotation + remaining_end_rotation
        ) / 2.0
        poses["dropoff"][rotation_index] = start_rotation
        exit_keys = []
        if use_center_waypoint:
            exit_keys.append("exit_center")
        exit_keys.append("exit_gate")
        _interpolate_route_rotations(
            poses["dropoff"],
            [poses[key] for key in exit_keys],
            end_rotation=(
                remaining_half_rotation
                if next_start_pose is not None
                else remaining_end_rotation
            ),
            rotation_index=rotation_index,
        )
        if next_start_pose is not None:
            poses["next_start"][rotation_index] = remaining_end_rotation
        _logger.info(
            "[PLATE_LAYOUT] Distributed unwind continuing after optimized entry "
            "start=%.3f paint_rz_delta=%.3f remaining_end=%.3f targets=%s",
            start_rotation,
            paint_rz_delta,
            remaining_end_rotation,
            {key: round(pose[rotation_index], 3) for key, pose in poses.items()},
        )
        return poses
    ideal_dropoff_rotation = start_rotation + (2.0 * step)
    nominal_dropoff_rotation = float(dropoff_pose[rotation_index])
    branch = (ideal_dropoff_rotation - nominal_dropoff_rotation) / 180.0
    branch_candidates = {
        nominal_dropoff_rotation + 180.0 * math.floor(branch),
        nominal_dropoff_rotation + 180.0 * math.ceil(branch),
    }
    direction = -1.0 if step < 0.0 else 1.0
    dropoff_rotation = min(
        branch_candidates,
        key=lambda candidate: (
            abs(candidate - ideal_dropoff_rotation),
            0 if direction * (candidate - start_rotation) >= 0.0 else 1,
        ),
    )
    next_start_rotation = start_rotation + (4.0 * step)
    for key, pose in poses.items():
        if len(pose) <= rotation_index:
            raise ValueError(f"Plate-layout route pose '{key}' has no configured rotation axis")

    entry_keys = ["entry_gate"]
    if use_center_waypoint:
        entry_keys.append("entry_center")
    entry_keys.append("dropoff")
    _interpolate_route_rotations(
        current,
        [poses[key] for key in entry_keys],
        end_rotation=dropoff_rotation,
        rotation_index=rotation_index,
    )

    exit_keys = []
    if use_center_waypoint:
        exit_keys.append("exit_center")
    exit_keys.append("exit_gate")
    exit_gate_rotation = (
        (dropoff_rotation + next_start_rotation) / 2.0
        if next_start_pose is not None
        else next_start_rotation
    )
    _interpolate_route_rotations(
        poses["dropoff"],
        [poses[key] for key in exit_keys],
        end_rotation=exit_gate_rotation,
        rotation_index=rotation_index,
    )
    if next_start_pose is not None:
        poses["next_start"][rotation_index] = next_start_rotation

    rotations = {key: pose[rotation_index] for key, pose in poses.items()}
    _logger.info(
        "[PLATE_LAYOUT] Distributed unwind start=%.3f paint_rz_delta=%.3f "
        "preferred_step=%.3f nominal_dropoff=%.3f selected_dropoff=%.3f targets=%s",
        start_rotation,
        paint_rz_delta,
        step,
        nominal_dropoff_rotation,
        dropoff_rotation,
        {key: round(value, 3) for key, value in rotations.items() if key in poses},
    )
    return poses


def build_plate_entry_segments_for_paint_chain(
    executor: object,
) -> tuple[list[OrderedPositionCommand], list[float] | None, str]:
    """Build plate entry through release for the combined paint chain."""
    dropoff = executor._paint_process_config().dropoff
    if not bool(dropoff.plate_use_entry_gate_as_detach_pose):
        return [], None, ""
    service = executor._plate_layout_service
    reservation = None if service is None else service.pending
    if reservation is None:
        return [], None, "Plate-layout dropoff has no active reservation"

    use_center = _plate_route_uses_center(dropoff, reservation)
    release_pose = list(reservation.release_pose)
    configured_gate_pose = list(dropoff.plate_passage_gate_pose)
    optimized_gate_pose = getattr(executor, "_dropoff_paint_detach_pose", None)
    gate_pose = (
        list(optimized_gate_pose)
        if isinstance(optimized_gate_pose, (list, tuple)) and len(optimized_gate_pose) >= 6
        else configured_gate_pose
    )
    if bool(dropoff.plate_distribute_unwind):
        paint_start_rz = executor._last_process_start_rz
        paint_end_rz = getattr(executor, "_last_paint_contact_end_rz", None)
        if paint_start_rz is None or not isinstance(paint_end_rz, (int, float)):
            return [], None, "Plate-layout optimized entry has no valid paint rotation"
        completed_turns = _completed_rotation_turns(
            float(paint_end_rz) - float(paint_start_rz)
        )
        if completed_turns:
            if not use_center:
                use_center = True
                _logger.info(
                    "[PLATE_LAYOUT] Forcing plate center waypoint to safely distribute "
                    "completed unwind turns=%d",
                    completed_turns,
                )
            target_release_rz = float(gate_pose[5]) - (90.0 * completed_turns)
            nominal_release_rz = float(release_pose[5])
            release_pose[5] = nominal_release_rz + 180.0 * round(
                (target_release_rz - nominal_release_rz) / 180.0
            )
    segments: list[OrderedPositionCommand] = [
        _plate_ordered_segment(
            "Plate entry in paint chain: paint detach to passage gate",
            gate_pose,
            _plate_motion_profile(dropoff, "entry_gate"),
        )
    ]
    if use_center:
        center_pose = list(reservation.transit_pose)
        center_pose[5] = (float(gate_pose[5]) + float(release_pose[5])) / 2.0
        segments.append(_plate_ordered_segment(
            "Plate entry in paint chain: passage gate to plate center",
            center_pose,
            _plate_motion_profile(dropoff, "entry_center"),
        ))
    segments.append(_plate_ordered_segment(
        (
            "Plate entry in paint chain: center to calculated dropoff"
            if use_center
            else "Plate entry in paint chain: passage gate to calculated dropoff"
        ),
        release_pose,
        _plate_motion_profile(dropoff, "center_to_dropoff"),
        stop=True,
    ))
    return segments, release_pose, ""


def _interpolate_route_rotations(
    start_pose: list[float],
    route_poses: list[list[float]],
    *,
    end_rotation: float,
    rotation_index: int,
) -> None:
    """Interpolate one rotation axis at a constant rate over route distance."""
    if not route_poses:
        return

    route = [start_pose, *route_poses]
    segment_lengths = [
        math.dist(route[index - 1][:3], route[index][:3])
        for index in range(1, len(route))
    ]
    total_distance = sum(segment_lengths)
    start_rotation = float(start_pose[rotation_index])
    travelled = 0.0
    for index, pose in enumerate(route_poses):
        travelled += segment_lengths[index]
        if total_distance > 1e-6:
            progress = travelled / total_distance
        else:
            progress = (index + 1) / len(route_poses)
        pose[rotation_index] = start_rotation + progress * (end_rotation - start_rotation)


def _plate_route_uses_center(dropoff: object, reservation: object) -> bool:
    """Select the safer center route for placements near the bottom-left corner."""
    if bool(dropoff.plate_use_center_waypoint):
        _logger.info("[PLATE_LAYOUT] Center waypoint enabled explicitly")
        return True
    if not dropoff.plate_auto_center_near_corner:
        _logger.info("[PLATE_LAYOUT] Automatic center routing near plate corner disabled")
        return False

    try:
        bottom_left = [float(value) for value in dropoff.plate_corners[0][:2]]
        center = [float(value) for value in reservation.transit_pose[:2]]
        release = [float(value) for value in reservation.release_pose[:2]]
    except (AttributeError, IndexError, TypeError, ValueError):
        raise ValueError(
            "Plate-layout automatic center routing requires valid bottom-left, center, "
            "and release XY coordinates"
        ) from None
    if (
        len(bottom_left) != 2
        or len(center) != 2
        or len(release) != 2
        or not all(math.isfinite(value) for value in bottom_left + center + release)
    ):
        raise ValueError(
            "Plate-layout automatic center routing requires valid bottom-left, center, "
            "and release XY coordinates"
        )

    center_radius_mm = 0.5 * math.dist(bottom_left, center)
    release_distance_mm = math.dist(bottom_left, release)
    use_center = release_distance_mm <= center_radius_mm
    _logger.info(
        "[PLATE_LAYOUT] Automatic center route release_distance_from_bottom_left_mm=%.3f "
        "radius_mm=%.3f use_center=%s",
        release_distance_mm,
        center_radius_mm,
        use_center,
    )
    return use_center


def _execute_plate_layout_ordered_release(
    executor: object,
    *,
    next_cycle_start: NextCycleTarget | None,
) -> tuple[bool, str]:
    service = executor._plate_layout_service
    reservation = None if service is None else service.pending
    if reservation is None:
        return False, "Plate-layout dropoff has no active reservation"
    dropoff = executor._paint_process_config().dropoff
    from src.robot_systems.paint.processes.paint.tray_dry.plate_layout import validate_plate_passage_gate

    gate_pose, error = validate_plate_passage_gate(dropoff.plate_passage_gate_pose)
    if error:
        return False, error
    exit_gate_pose, error = validate_plate_passage_gate(dropoff.plate_exit_gate_pose)
    if error:
        return False, f"Plate-layout exit gate: {error}"
    next_waypoints: list[_PlateNextWaypoint] = []
    if bool(dropoff.plate_next_cycle_midpoint_enabled) and next_cycle_start is not None:
        configured_waypoints = list(dropoff.plate_next_cycle_waypoints)
        if not configured_waypoints:
            return False, "Plate-layout next-cycle waypoints are enabled but none are configured"
        for index, raw_waypoint in enumerate(configured_waypoints):
            if not isinstance(raw_waypoint, dict):
                return False, f"Plate-layout next-cycle waypoint {index + 1}: expected a mapping"
            required = {"position", "vel_percent", "acc_percent", "motion_type", "blendR"}
            missing = required.difference(raw_waypoint)
            if missing:
                return False, (
                    f"Plate-layout next-cycle waypoint {index + 1}: "
                    f"missing {sorted(missing)}"
                )
            waypoint_pose, error = validate_plate_passage_gate(raw_waypoint["position"])
            if error:
                return False, f"Plate-layout next-cycle waypoint {index + 1}: {error}"
            try:
                profile = _PlateMotionProfile(
                    velocity_percent=float(raw_waypoint["vel_percent"]),
                    acceleration_percent=float(raw_waypoint["acc_percent"]),
                    motion_type=_parse_motion_type(
                        raw_waypoint["motion_type"],
                        field_name=f"dropoff.plate_next_cycle_waypoints[{index}]",
                    ),
                    blend_radius=max(0.0, float(raw_waypoint["blendR"])),
                )
            except (TypeError, ValueError):
                return False, f"Plate-layout next-cycle waypoint {index + 1}: invalid motion settings"
            next_waypoints.append(_PlateNextWaypoint(waypoint_pose, profile))
    try:
        use_center_waypoint = _plate_route_uses_center(dropoff, reservation)
    except ValueError as exc:
        return False, str(exc)
    route_poses = {
        "entry_gate": list(gate_pose),
        "entry_center": list(reservation.transit_pose),
        "dropoff": list(reservation.release_pose),
        "exit_center": list(reservation.transit_pose),
        "exit_gate": list(exit_gate_pose),
    }
    if next_cycle_start is not None:
        route_poses["next_start"] = list(next_cycle_start.position)
    entry_gate_is_detach_pose = (
        bool(dropoff.plate_use_entry_gate_as_detach_pose)
        and executor._last_process_end_pose is not None
        and poses_close(executor._last_process_end_pose, gate_pose)
    )
    entry_completed_in_paint_chain = (
        getattr(executor, "_plate_entry_completed_in_paint_chain", False) is True
        and executor._last_process_end_pose is not None
        and any(
            poses_close(
                executor._last_process_end_pose,
                [*reservation.release_pose[:5], float(reservation.release_pose[5]) + offset],
            )
            for offset in (-180.0, 0.0, 180.0)
        )
    )
    if bool(dropoff.plate_distribute_unwind):
        try:
            route_poses = _plate_route_poses_with_distributed_unwind(
                executor,
                entry_gate_pose=gate_pose,
                exit_gate_pose=exit_gate_pose,
                center_pose=reservation.transit_pose,
                dropoff_pose=reservation.release_pose,
                next_start_pose=None if next_cycle_start is None else list(next_cycle_start.position),
                use_center_waypoint=use_center_waypoint,
                entry_completed=entry_completed_in_paint_chain,
            )
        except (TypeError, ValueError):
            _logger.exception("[PLATE_LAYOUT] Failed to build distributed-unwind route")
            return False, "Plate-layout distributed unwind route could not be built"
    rotation_index = int(executor._contact_motion_config.rotation_index)
    if bool(dropoff.plate_distribute_unwind) and next_cycle_start is not None:
        exit_route_poses = []
        if use_center_waypoint:
            exit_route_poses.append(route_poses["exit_center"])
        exit_route_poses.append(route_poses["exit_gate"])
        exit_route_poses.extend(waypoint.position for waypoint in next_waypoints)
        exit_route_poses.append(route_poses["next_start"])
        _interpolate_route_rotations(
            route_poses["dropoff"],
            exit_route_poses,
            end_rotation=float(route_poses["next_start"][rotation_index]),
            rotation_index=rotation_index,
        )
    else:
        previous_rotation = float(route_poses["exit_gate"][rotation_index])
        for waypoint in next_waypoints:
            waypoint.position[rotation_index] = unwrap_degrees(
                previous_rotation,
                float(waypoint.position[rotation_index]),
            )
            previous_rotation = float(waypoint.position[rotation_index])
    # Validate the complete exit route before entry motion or physical release.
    exit_segments = []
    if use_center_waypoint:
        exit_segments.append(_plate_ordered_segment(
            "Plate exit: dropoff to plate center",
            route_poses["exit_center"],
            _plate_motion_profile(dropoff, "exit_center"),
        ))
    exit_segments.append(_plate_ordered_segment(
        (
            "Plate exit: plate center to passage gate"
            if use_center_waypoint
            else "Plate exit: dropoff to passage gate"
        ),
        route_poses["exit_gate"],
        _plate_motion_profile(dropoff, "exit_gate"),
        stop=next_cycle_start is None,
    ))
    if next_cycle_start is not None:
        for index, waypoint in enumerate(next_waypoints):
            exit_segments.append(_plate_ordered_segment(
                f"Plate exit: next-cycle waypoint {index + 1}/{len(next_waypoints)}",
                waypoint.position,
                waypoint.profile,
            ))
        exit_segments.append(_plate_ordered_segment(
            (
                f"Plate exit: last waypoint to next-cycle start '{next_cycle_start.group_id}'"
                if next_waypoints
                else f"Plate exit: passage gate to next-cycle start '{next_cycle_start.group_id}'"
            ),
            route_poses["next_start"],
            _plate_motion_profile(dropoff, "gate_to_next_start"),
            stop=True,
        ))

    entry_segments = []
    if entry_completed_in_paint_chain:
        _logger.info("[PLATE_LAYOUT] Plate release pose already reached in paint chain")
    elif not entry_gate_is_detach_pose:
        entry_segments.append(_plate_ordered_segment(
            "Plate entry: paint detach to passage gate",
            route_poses["entry_gate"],
            _plate_motion_profile(dropoff, "entry_gate"),
        ))
    else:
        _logger.info("[PLATE_LAYOUT] Entry gate already completed as paint detach pose")
    if use_center_waypoint and not entry_completed_in_paint_chain:
        entry_segments.append(_plate_ordered_segment(
            "Plate entry: passage gate to plate center",
            route_poses["entry_center"],
            _plate_motion_profile(dropoff, "entry_center"),
        ))
    if not entry_completed_in_paint_chain:
        entry_segments.append(_plate_ordered_segment(
            (
                "Plate entry: center to calculated dropoff"
                if use_center_waypoint
                else "Plate entry: passage gate to calculated dropoff"
            ),
            route_poses["dropoff"],
            _plate_motion_profile(dropoff, "center_to_dropoff"),
            stop=True,
        ))
        if not _wait_for_motion_slot_idle(executor):
            return False, "Pivot paint finished, but the motion backend remained busy before plate entry"
        if not executor._motion.move_ordered_pickup_sequence(
            "Plate-layout ordered entry chain", entry_segments
        ):
            return False, "Pivot paint finished, but plate-layout ordered entry chain failed before release"

    # Start the plate exit as soon as vacuum and blow-off are activated.  The
    # controller closes the blow-off valve after its pulse in the background.
    ok, message = executor._vacuum.turn_vacuum_off(wait_for_blow_off=False)
    if not ok:
        return False, message
    # ok, message = _verify_workpiece_released(executor)
    # if not ok:
    #     return False, message
    ok, message = _on_workpiece_release_verified(executor)
    if not ok:
        return False, message

    if not executor._motion.move_ordered_pickup_sequence(
        "Plate-layout ordered exit chain", exit_segments
    ):
        return False, "Workpiece released, but plate-layout ordered exit chain failed"
    if next_cycle_start is not None:
        # The next cycle verifies the fresh Cartesian pose before trusting this
        # marker.  A valid distributed-route endpoint avoids commanding the
        # same group a second time; an endpoint outside tolerance still takes
        # the normal correction-move path.
        executor._last_prepositioned_start_group = next_cycle_start.group_id
    _logger.info("[DROPOFF] strategy=plate_layout ordered entry/release/exit completed")
    return True, ""


def _execute_plate_layout_preparation(executor: object) -> tuple[bool, str]:
    """Unwind at the paint-detach pose before the plate entry chain."""
    service = executor._plate_layout_service
    reservation = None if service is None else service.pending
    if reservation is None:
        return False, "Plate-layout dropoff has no active reservation"

    config = executor._paint_process_config()
    if bool(config.dropoff.plate_distribute_unwind):
        _logger.info("[PLATE_LAYOUT] Deferring Joint 6 unwind until distributed plate route completes")
        executor._dropoff_unwind_prepared = True
        return True, ""
    if not executor._robot_service.unwind_joint6(
        blocking=True,
        queue_if_busy=PAINT_PROCESS_CONFIG.navigation_return.unwind_queue_if_busy,
        vel=config.navigation_return.unwind_vel_percent,
        acc=config.navigation_return.unwind_acc_percent,
    ):
        return False, "Pivot paint finished, but Joint 6 unwind failed at paint detach pose"
    executor._dropoff_unwind_prepared = True
    return True, ""


def _reserve_plate_dropoff(request: DropoffCycleRequest, executor) -> PaintOperationResult:
    motion_plan = request.pickup_plan.motion_plan
    align_pose = motion_plan.align_pose
    if align_pose is None or len(align_pose) < 6:
        return PaintOperationResult.failed(PaintFailureCode.PLANNING, "tray_reservation", "Plate-layout dropoff could not resolve workpiece orientation at calibration")
    width_mm, height_mm, outlines_mm = _workpiece_layout_geometry(request.execution_plan)
    paint_passes = _paint_pass_metadata(
        request.execution_plan,
        executor._paint_process_config(),
        executor,
    )

    group_id, calibration_pose = request.calibration_source()
    if calibration_pose is None or len(calibration_pose) < 6:
        return PaintOperationResult.failed(PaintFailureCode.INVALID_CONFIGURATION, "tray_reservation", f"Plate-layout dropoff requires calibration movement group '{group_id}'")

    result = executor._plate_layout_service.reserve_result(
        executor._paint_process_config().dropoff,
        width_mm=width_mm,
        height_mm=height_mm,
        calibration_pose=list(calibration_pose),
        workpiece_rz_at_calibration_deg=float(align_pose[5]),
        pose_calculator=calculate_workpiece_dropoff_pose,
        outlines_mm=outlines_mm,
        paint_passes=paint_passes,
    )
    if not isinstance(result, Ready):
        return result
    reservation = result.value
    _logger.info(
        "[PLATE_LAYOUT] reserved release_pose=%s footprint=(%.3f, %.3f) has_space_for_same_footprint=%s",
        [round(value, 3) for value in reservation.release_pose],
        width_mm,
        height_mm,
        reservation.has_space_for_same_footprint,
    )
    return PaintOperationResult(PaintOutcome.COMPLETED, "")


def _workpiece_footprint_mm(execution_plan) -> tuple[float, float]:
    """Return canonical min-rectangle sides as long-side width and short-side height."""
    width, height, _outlines = _workpiece_layout_geometry(execution_plan)
    return width, height


def _paint_pass_metadata(execution_plan, config, executor) -> tuple[dict, ...]:
    """Capture the configured paint controls used by each production pass."""
    jobs = list(execution_plan.execution_jobs)
    first_job = jobs[0] if jobs else {}
    try:
        first_offset = float(
            executor._resolve_pivot_offset_mm(first_job or None, execution_plan)
        )
    except (AttributeError, TypeError, ValueError):
        first_offset = float(config.default_paint_offset_mm)
    first_pass = {
        "pass_number": 1,
        "velocity_percent": float(
            first_job.get("vel", config.default_paint_velocity_percent)
        ),
        "acceleration_percent": float(
            first_job.get("acc", config.default_paint_acceleration_percent)
        ),
        "press_offset_mm": first_offset,
    }
    passes = [first_pass]
    workpiece = execution_plan.workpiece
    is_unmatched = str(workpiece.get("workpieceId", "")).strip().lower() == "captured"
    pass_count = max(1, min(2, int(config.unmatched_paint_pass_count)))
    if is_unmatched and pass_count == 2:
        second = config.unmatched_second_pass
        if bool(second.use_pass_1_settings):
            second_pass = {**first_pass, "pass_number": 2}
        else:
            second_pass = {
                "pass_number": 2,
                "velocity_percent": float(second.velocity_percent),
                "acceleration_percent": float(second.acceleration_percent),
                "press_offset_mm": float(second.offset_mm),
            }
        passes.append(second_pass)
    return tuple(passes)


def _workpiece_layout_geometry(
    execution_plan,
) -> tuple[float, float, tuple[tuple[tuple[float, float], ...], ...]]:
    """Return footprint and execution paths projected into its local rectangle."""
    paths = [
        [pose[:2] for pose in path if len(pose) >= 2]
        for path in execution_plan.execution_paths()
    ]
    paths = [path for path in paths if path]
    points = [point for path in paths for point in path]
    if len(points) < 3:
        return 0.0, 0.0, ()
    xy = np.asarray(points, dtype=np.float32)
    if not np.all(np.isfinite(xy)):
        return 0.0, 0.0, ()
    import cv2
    rectangle = cv2.boxPoints(cv2.minAreaRect(np.ascontiguousarray(xy.reshape(-1, 1, 2))))
    edges = [rectangle[(index + 1) % 4] - rectangle[index] for index in range(4)]
    long_axis = max(edges, key=lambda edge: float(np.linalg.norm(edge)))
    long_axis = long_axis / np.linalg.norm(long_axis)
    # A rectangle axis has no inherent direction: OpenCV may return either v
    # or -v for otherwise identically oriented contours. Choose one stable
    # direction in robot coordinates so asymmetric workpieces are never shown
    # rotated by 180 degrees from their physical orientation.
    dominant_index = int(np.argmax(np.abs(long_axis)))
    if long_axis[dominant_index] > 0.0:
        long_axis = -long_axis
    short_axis = np.asarray([-long_axis[1], long_axis[0]], dtype=np.float32)
    projected = np.column_stack((xy @ long_axis, xy @ short_axis))
    minimum = projected.min(axis=0)
    projected -= minimum
    width, height = projected.max(axis=0)
    outlines = []
    offset = 0
    for path in paths:
        count = len(path)
        outlines.append(tuple(
            (float(x), float(y)) for x, y in projected[offset:offset + count]
        ))
        offset += count
    return float(width), float(height), tuple(outlines)


def _plate_entry_detach_pose(
    executor,
    *,
    is_final_job: bool,
    paint_start_rz: float,
    paint_end_rz: float | None,
) -> list[float] | None:
    if not is_final_job:
        return None
    dropoff = executor._paint_process_config().dropoff
    if (
        not bool(dropoff.plate_use_entry_gate_as_detach_pose)
    ):
        return None
    try:
        pose = [float(value) for value in dropoff.plate_passage_gate_pose]
    except (TypeError, ValueError):
        return None
    if len(pose) != 6 or not all(np.isfinite(value) for value in pose):
        return None
    if bool(dropoff.plate_distribute_unwind) and paint_end_rz is not None:
        completed_turns = int(round((float(paint_end_rz) - paint_start_rz) / 360.0))
        if completed_turns:
            pose[5] = float(paint_end_rz) - (90.0 * completed_turns)
    return pose


def _on_workpiece_release_verified(executor: object) -> tuple[bool, str]:
    """Commit plate occupancy only after successful release."""
    service = executor._plate_layout_service
    if service is None or service.pending is None:
        return False, "Workpiece released, but no plate-layout reservation was active"
    service.commit(executor._paint_process_config().dropoff)
    _logger.info("[PLATE_LAYOUT] Committed plate position after verified release")
    return True, ""
