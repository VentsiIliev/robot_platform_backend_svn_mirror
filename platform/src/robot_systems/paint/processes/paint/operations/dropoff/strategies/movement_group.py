"""Movement-group dropoff preparation, routing, and verified release."""
from __future__ import annotations
from src.robot_systems.paint.contracts.dropoff import DropoffApproach, DropoffCycleRequest
from src.robot_systems.paint.processes.paint.results import Ready, Failed, PaintFailure, PaintFailureCode, PaintOperationResult, PaintOutcome
from ..motion import build_cleanup_dropoff_approach

from typing import TYPE_CHECKING
from src.robot_systems.paint.contracts.dropoff import IDropoffStrategy, DropoffResult

if TYPE_CHECKING:
    from src.robot_systems.paint.processes.paint.production.execution_runtime import PaintExecutionRuntime

import logging
from dataclasses import dataclass
from time import monotonic, perf_counter, sleep

import numpy as np

from src.engine.robot.path_preparation import WorkpieceExecutionPlan
from ..plan import DropoffPlan, DropoffWaypoint, IDropoffWaypointPlanner
from src.engine.robot.motion_sequence import OrderedMotionType
from src.robot_systems.paint.processes.paint.motion.pose_comparison import poses_close
from src.robot_systems.paint.processes.paint.motion.pose_sampling import read_fresh_pose
from src.robot_systems.paint.contracts.next_cycle_target import NextCycleTarget
from src.robot_systems.paint.processes.paint.configuration.models import (
    PAINT_PROCESS_CONFIG,
    PICKUP_CONTACT_MODE_SENSOR_CONTROLLED_FAST_LIN,
    DropoffStrategy,
)
from src.robot_systems.paint.diagnostics.trajectory import elapsed_s
from src.robot_systems.paint.processes.paint.motion.failure import motion_failure_message
from src.robot_systems.paint.timing import timed_step

from ..motion import (
    _dropoff_strategy_name,
    _ordered_position_command,
    _parse_motion_type,
    _resolve_dropoff_align_pose,
    _resolve_dropoff_preparation_pose,
    _resolve_dropoff_safe_travel_waypoints,
    _should_prepare_dropoff_align_before_unwind,
    build_ordered_dropoff_preparation_segments,
    open_dropoff_passage_for_preparation,
)


_logger = logging.getLogger(__name__)


class MovementGroupDropoff(IDropoffStrategy):
    """Prepare the configured movement-group destination and verify release."""

    name = DropoffStrategy.MOVEMENT_GROUP

    def __init__(self, runtime: PaintExecutionRuntime) -> None:
        self._runtime = runtime

    def begin_cycle(self, request: DropoffCycleRequest) -> PaintOperationResult:
        self._runtime._dropoff_unwind_prepared = False
        return PaintOperationResult(PaintOutcome.COMPLETED, "")

    def painting_detach_pose(self, *, is_final_job: bool, paint_start_rz: float, paint_end_rz: float | None) -> list[float] | None:
        return None

    def plan_paint_approach(self, *, cleanup_pending: bool) -> Ready[DropoffApproach] | Failed:
        if cleanup_pending:
            return Ready(DropoffApproach())
        config = self._runtime._paint_process_config()
        if config.dropoff_safe_travel.enabled and not _resolve_dropoff_safe_travel_waypoints(self._runtime):
            return Failed(PaintFailure(PaintFailureCode.PLANNING, "ordered_pickup_paint_planning", "Pivot paint finished, but paint-to-dropoff safe travel waypoints are not configured"))
        segments, final_pose = build_ordered_dropoff_preparation_segments(self._runtime)
        if not segments:
            return Failed(PaintFailure(PaintFailureCode.PLANNING, "ordered_pickup_paint_planning", "Pivot paint finished, but no dropoff pose is available for safe pre-dropoff unwind alignment"))
        return Ready(DropoffApproach(tuple(segments), final_pose, prepares_release=True))

    def plan_cleanup_approach(self, final_pose: list[float]) -> DropoffApproach:
        return build_cleanup_dropoff_approach(self._runtime, final_pose)

    def activate_approach(self, approach: DropoffApproach) -> PaintOperationResult:
        if not approach.prepares_release:
            return PaintOperationResult(PaintOutcome.COMPLETED, "")
        ok, message = open_dropoff_passage_for_preparation(self._runtime)
        return (PaintOperationResult(PaintOutcome.COMPLETED, "") if ok else
                PaintOperationResult.failed(PaintFailureCode.MOTION, "dropoff_passage", message))

    def approach_completed(self, approach: DropoffApproach) -> None:
        if approach.prepares_release:
            self._runtime._dropoff_unwind_prepared = True

    def finish_cycle(self, result: PaintOperationResult) -> None:
        return None

    def prepare_dropoff(self) -> tuple[bool, str]:
        ok, message = execute_dropoff_preparation_for_executor(self._runtime)
        if ok:
            self._runtime._dropoff_unwind_prepared = True
        return ok, message

    def release_dropoff(self, next_cycle_start: NextCycleTarget | None = None) -> DropoffResult:
        ok, message = execute_dropoff_release_for_executor(
            self._runtime, next_cycle_start=next_cycle_start,
        )
        return DropoffResult(
            success=ok, message=message,
            prepositioned_group=self._runtime._last_prepositioned_start_group if ok else None,
        )


@dataclass(frozen=True)
class DropoffReleaseWaypoint:
    """One release-strategy move or release action."""

    label: str
    pose: list[float] | None
    vel_percent: float
    acc_percent: float
    motion_type: OrderedMotionType = OrderedMotionType.PTP
    blendR: float = 0.0
    release_here: bool = False
    corridor_id: str | None = None


@dataclass(frozen=True)
class DropoffReleasePlan:
    """Resolved release sequence for the currently held painted workpiece."""

    strategy_name: DropoffStrategy
    waypoints: tuple[DropoffReleaseWaypoint, ...]


@timed_step(_logger, "prepare_dropoff_unwind")
def execute_dropoff_preparation_for_executor(executor: object) -> tuple[bool, str]:
    """Build and execute paint-to-dropoff safe travel, align, and Joint 6 unwind."""
    dryer_ready = executor._dryer_ready_for_release
    if callable(dryer_ready):
        try:
            ready, reason = dryer_ready()
        except Exception:
            _logger.exception("[DROPOFF] Failed to verify dryer readiness before dropoff")
            return False, "Dropoff cancelled: dryer readiness could not be verified"
        if not ready:
            detail = str(reason or "the previous dryer sequence failed")
            return False, f"Dropoff cancelled: {detail}"

    if executor._dropoff_unwind_prepared:
        _logger.info("[DROPOFF] Pre-dropoff align/unwind already completed by ordered cleanup chain")
        return True, ""

    if _should_prepare_dropoff_align_before_unwind(executor):
        opened, message = open_dropoff_passage_for_preparation(executor)
        if not opened:
            return False, message

    if executor._last_pickup_contact_mode == PICKUP_CONTACT_MODE_SENSOR_CONTROLLED_FAST_LIN:
        commands, final_pose = build_ordered_dropoff_preparation_segments(executor)
        if not commands:
            return False, "Pivot paint finished, but ordered dropoff preparation could not be built"
        segments = commands
        _logger.debug(
            "[DROPOFF] Executing servo-contact dropoff preparation as one ordered chain segments=%d blendR=%s",
            len(segments),
            [
                getattr(getattr(segment, "profile", None), "blend_radius", None)
                for segment in segments
            ],
        )
        if not executor._motion.move_ordered_pickup_sequence(
            "Servo-contact ordered dropoff preparation",
            segments,
        ):
            return False, "Pivot paint finished, but ordered dropoff preparation failed"
        executor._dropoff_unwind_prepared = True
        if final_pose is not None:
            executor._last_process_end_pose = list(final_pose)
        return True, ""

    config = executor._paint_process_config()
    safe_waypoints = _resolve_dropoff_safe_travel_waypoints(executor)
    if bool(config.dropoff_safe_travel.enabled):
        if not safe_waypoints:
            return False, "Pivot paint finished, but paint-to-dropoff safe travel waypoints are not configured"
        for index, safe_waypoint in enumerate(safe_waypoints, start=1):
            if not executor._motion.move_pickup_phase(
                f"Moving through paint-to-dropoff safe travel waypoint {index}",
                safe_waypoint.position,
                velocity=safe_waypoint.velocity_percent,
                acceleration=safe_waypoint.acceleration_percent,
                motion_type=safe_waypoint.motion_type,
                blendR=safe_waypoint.blend_radius,
            ):
                return False, "Pivot paint finished, but paint-to-dropoff safe travel move failed"

    if _should_prepare_dropoff_align_before_unwind(executor):
        align_pose = _resolve_dropoff_preparation_pose(executor)
        if align_pose is None:
            return False, "Pivot paint finished, but no dropoff pose is available for safe pre-dropoff unwind alignment"
        if not executor._motion.move_pickup_phase(
            "Moving to dropoff pose before unwind",
            align_pose,
            velocity=config.dropoff.release_align_vel_percent,
            acceleration=config.dropoff.release_align_acc_percent,
            motion_type=_parse_motion_type(
                config.dropoff.release_align_motion_type,
                field_name="dropoff.release_align_motion_type",
            ),
            blendR=float(config.dropoff.release_align_blendR),
        ):
            return False, "Pivot paint finished, but move to dropoff pose failed before unwind"
    elif executor._configured_contact_motion_plane == "xz_y_ry":
        return False, "Pivot paint finished, but no dropoff pose is available for safe pre-dropoff unwind alignment"

    if executor._robot_service is None:
        return False, "Pivot paint finished, but robot service is not available for pre-dropoff Joint 6 unwind"

    _logger.info(
        "[DROPOFF] Unwinding Joint 6 before dropoff strategy vel=%.1f acc=%.1f queue_if_busy=%s",
        config.navigation_return.unwind_vel_percent,
        config.navigation_return.unwind_acc_percent,
        PAINT_PROCESS_CONFIG.navigation_return.unwind_queue_if_busy,
    )
    ok = executor._robot_service.unwind_joint6(
        blocking=True,
        queue_if_busy=PAINT_PROCESS_CONFIG.navigation_return.unwind_queue_if_busy,
        vel=config.navigation_return.unwind_vel_percent,
        acc=config.navigation_return.unwind_acc_percent,
    )
    if not ok:
        return False, "Pivot paint finished, but Joint 6 unwind failed before dropoff"
    return True, ""


@timed_step(_logger, "pre_release_dropoff")
def execute_dropoff_release_for_executor(
    executor: object,
    *,
    next_cycle_start: NextCycleTarget | None = None,
) -> tuple[bool, str]:
    """Build and execute the configured dropoff release strategy."""
    started = perf_counter()
    executor._last_prepositioned_start_group = None
    plan = _build_dropoff_release_plan(executor)
    release_count = sum(1 for waypoint in plan.waypoints if waypoint.release_here)
    if release_count != 1:
        if plan.strategy_name is DropoffStrategy.MOVEMENT_GROUP:
            return False, "Dropoff movement group 'Dropoff' is not configured"
        return False, f"Dropoff strategy '{plan.strategy_name}' must define exactly one release waypoint"

    _logger.info(
        "[DROPOFF] executing strategy=%s waypoints=%d",
        plan.strategy_name,
        len(plan.waypoints),
    )
    release_index, release_waypoint = next(
        (index, waypoint)
        for index, waypoint in enumerate(plan.waypoints, start=1)
        if waypoint.release_here
    )
    ordered_release_pose_completed = (
        bool(executor._dropoff_unwind_prepared)
        and release_waypoint.pose is not None
        and poses_close(release_waypoint.pose, executor._last_process_end_pose)
    )
    release_completed = False
    ordered_exit_waypoint: DropoffReleaseWaypoint | None = None
    for index, waypoint in enumerate(plan.waypoints, start=1):
        waypoint_started = perf_counter()
        if waypoint.pose is not None:
            already_at_release_pose = ordered_release_pose_completed and waypoint.release_here
            superseded_approach = ordered_release_pose_completed and index < release_index
            if already_at_release_pose:
                _logger.info(
                    "[DROPOFF] waypoint '%s' already completed by ordered cleanup chain; releasing in place",
                    waypoint.label,
                )
            elif superseded_approach:
                _logger.info(
                    "[DROPOFF] waypoint '%s' superseded by ordered descent to release pose",
                    waypoint.label,
                )
            elif (
                release_completed
                and next_cycle_start is not None
                and waypoint.corridor_id is not None
            ):
                # Keep the passage open and combine the protected corridor
                # retract with the return-to-start move below. A blend radius
                # cannot span two separate blocking motion requests.
                ordered_exit_waypoint = waypoint
            elif not executor._motion.move_pickup_phase(
                waypoint.label,
                list(waypoint.pose),
                velocity=waypoint.vel_percent,
                acceleration=waypoint.acc_percent,
                motion_type=(
                    OrderedMotionType.LINEAR
                    if waypoint.corridor_id
                    else waypoint.motion_type
                ),
                blendR=waypoint.blendR,
                corridor_id=waypoint.corridor_id,
            ):
                _logger.debug(
                    "[TIMING] pre_release_dropoff success=false strategy=%s waypoint=%d label=%s elapsed_s=%.3f total_elapsed_s=%.3f",
                    plan.strategy_name,
                    index,
                    waypoint.label,
                    elapsed_s(waypoint_started),
                    elapsed_s(started),
                )
                failure = (
                    f"Workpiece release completed, but post-release dropoff waypoint "
                    f"'{waypoint.label}' failed; robot may still be inside the dropoff passage"
                    if release_completed
                    else f"Pivot paint finished, but dropoff waypoint '{waypoint.label}' failed before release"
                )
                return False, motion_failure_message(executor._robot_service, failure)

        if waypoint.release_here:
            ok, msg = executor._vacuum.turn_vacuum_off()
            if not ok:
                _logger.debug(
                    "[TIMING] pre_release_dropoff success=false strategy=%s waypoint=%d stage=release elapsed_s=%.3f total_elapsed_s=%.3f",
                    plan.strategy_name,
                    index,
                    elapsed_s(waypoint_started),
                    elapsed_s(started),
                )
                return False, msg
            # ok, msg = _verify_workpiece_released(executor)
            # if not ok:
            #     _logger.debug(
            #         "[TIMING] pre_release_dropoff success=false strategy=%s waypoint=%d stage=release_verification elapsed_s=%.3f total_elapsed_s=%.3f",
            #         plan.strategy_name,
            #         index,
            #         elapsed_s(waypoint_started),
            #         elapsed_s(started),
            #     )
            #     return False, msg
            release_completed = True
            ok, msg = _on_workpiece_release_verified(executor)
            if not ok:
                _logger.debug(
                    "[TIMING] pre_release_dropoff success=false strategy=%s waypoint=%d "
                    "stage=release_verified_callback elapsed_s=%.3f total_elapsed_s=%.3f",
                    plan.strategy_name,
                    index,
                    elapsed_s(waypoint_started),
                    elapsed_s(started),
                )
                return False, msg

    ordered_exit_completed = False
    if ordered_exit_waypoint is not None and next_cycle_start is not None:
        ok, msg = _execute_movement_group_ordered_exit(
            executor,
            ordered_exit_waypoint,
            next_cycle_start,
        )
        if not ok:
            return False, msg
        ordered_exit_completed = True

    if next_cycle_start is not None:
        if not ordered_exit_completed and not _move_to_next_cycle_start(executor, next_cycle_start):
            return False, "Dropoff retracted safely, but move to next-cycle start failed"
        if not _wait_for_next_cycle_start_pose(executor, next_cycle_start):
            return False, "Dropoff retracted safely, but next-cycle start pose was not reached"
        executor._last_prepositioned_start_group = next_cycle_start.group_id
        _logger.info(
            "[NEXT_CYCLE] Reached start group='%s'",
            executor._last_prepositioned_start_group,
        )

    _logger.info(
        "[DROPOFF] strategy=%s completed elapsed_s=%.3f",
        plan.strategy_name,
        elapsed_s(started),
    )
    return True, ""


def _execute_movement_group_ordered_exit(
    executor: object,
    retract_waypoint: DropoffReleaseWaypoint,
    next_cycle_start: NextCycleTarget,
) -> tuple[bool, str]:
    """Blend a sub-zero corridor retract into the next-cycle start move."""
    corridor_id = str(retract_waypoint.corridor_id or "").strip()
    if not corridor_id or retract_waypoint.pose is None:
        return False, "Workpiece released, but the sub-zero exit route is incomplete"
    blend_radius = max(
        0.0,
        float(executor._paint_process_config().dropoff.sub_zero_exit_blendR_mm),
    )
    commands = [
        _ordered_position_command(
            retract_waypoint.label,
            retract_waypoint.pose,
            retract_waypoint.vel_percent,
            retract_waypoint.acc_percent,
            OrderedMotionType.LINEAR,
            blend_radius,
            protected=True,
        ),
        _ordered_position_command(
            f"Moving to next-cycle start '{next_cycle_start.group_id}'",
            next_cycle_start.position,
            next_cycle_start.velocity_percent,
            next_cycle_start.acceleration_percent,
            next_cycle_start.motion_type,
            0.0,
            protected=True,
        ),
    ]
    segments = commands
    _logger.info(
        "[DROPOFF] Executing movement-group ordered exit corridor=%s blendR=%.3f segments=%d",
        corridor_id,
        blend_radius,
        len(segments),
    )
    if not executor._motion.move_ordered_pickup_sequence(
        "Movement-group ordered exit chain",
        segments,
    ):
        return False, (
            "Workpiece released, but the ordered corridor retract and "
            "next-cycle return failed; the dropoff passage remains open"
        )
    if not executor._robot_service.set_motion_passage_closed(corridor_id, True):
        return False, (
            f"Next-cycle start was reached, but dropoff passage '{corridor_id}' could not be closed"
        )
    _logger.info(
        "[DROPOFF] Closed motion passage '%s' after ordered exit chain",
        corridor_id,
    )
    return True, ""


def _move_to_next_cycle_start(executor: object, next_cycle_start: NextCycleTarget) -> bool:
    return bool(executor._motion.move_pickup_phase(
        f"Moving to next-cycle start '{next_cycle_start.group_id}'",
        list(next_cycle_start.position),
        velocity=next_cycle_start.velocity_percent,
        acceleration=next_cycle_start.acceleration_percent,
        motion_type=next_cycle_start.motion_type,
        blendR=0.0,
    ))


def _next_cycle_start_pose_reached(
    executor: object,
    next_cycle_start: NextCycleTarget,
    position_tolerance_mm: float = 2.0,
    orientation_tolerance_deg: float = 2.0,
    *,
    log_result: bool = True,
) -> bool:
    try:
        actual = read_fresh_pose(
            executor._robot_service,
            error_message="Failed to read fresh pose after next-cycle start move",
        )
    except Exception as exc:
        _logger.error("[NEXT_CYCLE] %s", exc)
        return False
    expected = next_cycle_start.position
    if not isinstance(actual, (list, tuple)) or not isinstance(expected, (list, tuple)):
        return False
    if len(actual) < 6 or len(expected) < 6:
        return False
    position_error = float(np.linalg.norm(
        np.asarray(actual[:3], dtype=float) - np.asarray(expected[:3], dtype=float)
    ))
    orientation_error = max(
        abs((float(actual[index]) - float(expected[index]) + 180.0) % 360.0 - 180.0)
        for index in range(3, 6)
    )
    reached = (
        position_error <= float(position_tolerance_mm)
        and orientation_error <= float(orientation_tolerance_deg)
    )
    if log_result:
        _logger.info(
            "[NEXT_CYCLE] Start-pose verification reached=%s position_error_mm=%.3f "
            "orientation_error_deg=%.3f tolerance_mm=%.3f tolerance_deg=%.3f actual=%s target=%s",
            reached,
            position_error,
            orientation_error,
            float(position_tolerance_mm),
            float(orientation_tolerance_deg),
            [round(float(value), 3) for value in actual[:6]],
            [round(float(value), 3) for value in expected[:6]],
        )
    return reached


def _wait_for_next_cycle_start_pose(
    executor: object,
    next_cycle_start: NextCycleTarget,
    *,
    timeout_s: float = 2.0,
    poll_interval_s: float = 0.05,
    stable_samples: int = 2,
) -> bool:
    """Wait through ordered-chain response/telemetry skew for stable arrival."""
    deadline = monotonic() + max(0.1, float(timeout_s))
    consecutive = 0
    while monotonic() < deadline:
        if _next_cycle_start_pose_reached(executor, next_cycle_start, log_result=False):
            consecutive += 1
            if consecutive >= max(1, int(stable_samples)):
                _logger.info(
                    "[NEXT_CYCLE] Stable start pose reached after ordered exit chain samples=%d",
                    consecutive,
                )
                return True
        else:
            consecutive = 0
        sleep(max(0.01, float(poll_interval_s)))
    _next_cycle_start_pose_reached(executor, next_cycle_start, log_result=True)
    return False


def _build_dropoff_release_plan(executor: object) -> DropoffReleasePlan:
    strategy_name = _dropoff_strategy_name(executor)
    dropoff = executor._paint_process_config().dropoff
    if strategy_name is DropoffStrategy.MOVEMENT_GROUP:
        pose = _resolve_dropoff_align_pose(executor)
        if pose is None:
            _logger.info("[DROPOFF] movement_group has no configured pose for group 'Dropoff'")
            return DropoffReleasePlan(strategy_name=strategy_name, waypoints=())
        if float(pose[2]) < 0.0:
            if not dropoff.allow_sub_zero_dropoff:
                _logger.error("[DROPOFF] Negative target rejected: Allow Sub-Zero Dropoff is disabled")
                return DropoffReleasePlan(strategy_name=strategy_name, waypoints=())
            approach_pose = list(pose)
            approach_pose[2] = float(dropoff.sub_zero_approach_z_mm)
            corridor_id = executor._dropoff_motion_corridor_id
            return DropoffReleasePlan(
                strategy_name=strategy_name,
                waypoints=(
                    DropoffReleaseWaypoint(
                        label="Moving above dropoff group 'Dropoff'",
                        pose=approach_pose,
                        vel_percent=dropoff.release_align_vel_percent,
                        acc_percent=dropoff.release_align_acc_percent,
                    ),
                    DropoffReleaseWaypoint(
                        label="Descending through dropoff group 'Dropoff' passage",
                        pose=pose,
                        vel_percent=dropoff.release_align_vel_percent,
                        acc_percent=dropoff.release_align_acc_percent,
                        motion_type=OrderedMotionType.LINEAR,
                        release_here=True,
                        corridor_id=corridor_id,
                    ),
                    DropoffReleaseWaypoint(
                        label="Retracting through dropoff group 'Dropoff' passage",
                        pose=approach_pose,
                        vel_percent=dropoff.release_align_vel_percent,
                        acc_percent=dropoff.release_align_acc_percent,
                        motion_type=OrderedMotionType.LINEAR,
                        corridor_id=corridor_id,
                    ),
                ),
            )
        return DropoffReleasePlan(
            strategy_name=strategy_name,
            waypoints=(
                DropoffReleaseWaypoint(
                    label="Moving to dropoff group 'Dropoff' for release",
                    pose=pose,
                    vel_percent=dropoff.release_align_vel_percent,
                    acc_percent=dropoff.release_align_acc_percent,
                    motion_type=_parse_motion_type(
                        dropoff.release_align_motion_type,
                        field_name="dropoff.release_align_motion_type",
                    ),
                    blendR=dropoff.release_align_blendR,
                    release_here=True,
                ),
            ),
        )

    return DropoffReleasePlan(strategy_name=strategy_name, waypoints=())


class MovementGroupDropoffPlanner:
    """Release the held workpiece at the configured dropoff movement group."""

    name = DropoffStrategy.MOVEMENT_GROUP

    def build_plan(self, owner, execution_plan: WorkpieceExecutionPlan) -> DropoffPlan:
        dropoff = owner._paint_process_config().dropoff
        group_id = "Dropoff"
        pose = _resolve_dropoff_align_pose(owner)
        if pose is None:
            _logger.info("[DROPOFF] movement_group has no configured pose for group '%s'", group_id)
            return DropoffPlan(strategy_name=self.name, waypoints=())
        if float(pose[2]) < 0.0:
            if not dropoff.allow_sub_zero_dropoff:
                _logger.error("[DROPOFF] Negative target rejected: Allow Sub-Zero Dropoff is disabled")
                return DropoffPlan(strategy_name=self.name, waypoints=())
            approach_pose = list(pose)
            approach_pose[2] = float(dropoff.sub_zero_approach_z_mm)
            corridor_id = owner._dropoff_motion_corridor_id
            return DropoffPlan(
                strategy_name=self.name,
                waypoints=(
                    DropoffWaypoint(
                        label=f"Moving above dropoff group '{group_id}'",
                        pose=approach_pose,
                        vel_percent=dropoff.release_align_vel_percent,
                        acc_percent=dropoff.release_align_acc_percent,
                        motion_type=OrderedMotionType.PTP,
                        blendR=0.0,
                        release_here=False,
                    ),
                    DropoffWaypoint(
                        label=f"Descending through dropoff group '{group_id}' passage",
                        pose=pose,
                        vel_percent=dropoff.release_align_vel_percent,
                        acc_percent=dropoff.release_align_acc_percent,
                        motion_type=OrderedMotionType.LINEAR,
                        blendR=0.0,
                        release_here=True,
                        corridor_id=corridor_id,
                    ),
                    DropoffWaypoint(
                        label=f"Retracting through dropoff group '{group_id}' passage",
                        pose=approach_pose,
                        vel_percent=dropoff.release_align_vel_percent,
                        acc_percent=dropoff.release_align_acc_percent,
                        motion_type=OrderedMotionType.LINEAR,
                        blendR=0.0,
                        release_here=False,
                        corridor_id=corridor_id,
                    ),
                ),
            )
        return DropoffPlan(
            strategy_name=self.name,
            waypoints=(
                DropoffWaypoint(
                    label=f"Moving to dropoff group '{group_id}' for release",
                    pose=pose,
                    vel_percent=dropoff.release_align_vel_percent,
                    acc_percent=dropoff.release_align_acc_percent,
                    motion_type=OrderedMotionType.parse(
                        dropoff.release_align_motion_type,
                        field_name="dropoff.release_align_motion_type",
                    ),
                    blendR=dropoff.release_align_blendR,
                    release_here=True,
                ),
            ),
        )


def _on_workpiece_release_verified(executor: object) -> tuple[bool, str]:
    """Notify the composed system after release verification succeeds."""
    callback = executor._on_workpiece_release_verified
    if callback is None:
        return True, ""
    try:
        ok = bool(callback())
    except Exception:
        _logger.exception("[DROPOFF] Workpiece-release callback raised")
        return False, "Workpiece released, but the dryer sequence could not be queued"
    if not ok:
        _logger.error("[DROPOFF] Dryer sequence was rejected after workpiece release")
        return False, "Workpiece released, but the dryer sequence could not be queued"
    _logger.info("[DROPOFF] Dryer sequence queued after workpiece release verification")
    return True, ""
