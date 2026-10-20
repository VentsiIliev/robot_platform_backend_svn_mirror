from __future__ import annotations
from src.robot_systems.paint.contracts.dropoff import DropoffCycleRequest

import logging


from src.engine.robot.motion_sequence import (
    OrderedMotionCommand,
    OrderedUnwindJoint6Command,
)
from src.robot_systems.paint.processes.paint.operations.pickup.executor import (
    build_ordered_paint_contact_segments,
    build_ordered_pickup_segments,
)
from src.robot_systems.paint.processes.paint.configuration.models import (
    PICKUP_CONTACT_MODE_PLANNED,
    PICKUP_CONTACT_MODE_SENSOR_CONTROLLED_FAST_LIN,
)
from src.robot_systems.paint.processes.paint.workflow.context import PaintExecutionContext
from src.robot_systems.paint.processes.paint.workflow.handlers.common.motion_handlers import (
    fail_paint_motion,
    finish_paint_motion,
    motion_failure_message,
    start_paint_motion_if_needed,
    unwind_joint6_at_cycle_start,
    wait_or_guard,
)
from src.robot_systems.paint.processes.paint.workflow.state import PaintExecutionState
from src.robot_systems.paint.processes.paint.planning.projection.command_job import PaintContactCommandJob
from src.robot_systems.paint.timing import timed_block, timed_step

from src.robot_systems.paint.processes.paint.results import (
    Failed, Ready, PaintFailureCode, PaintOperationResult, PaintOutcome,
)

_logger = logging.getLogger(__name__)


def handle_pickup(ctx: PaintExecutionContext) -> PaintExecutionState:
    executor = ctx.production_service._path_executor
    start_paint_motion_if_needed(ctx)

    guarded = wait_or_guard(ctx, PaintExecutionState.PICKUP)
    if guarded is not None:
        finish_paint_motion(ctx, success=False)
        return guarded

    if not unwind_joint6_at_cycle_start(ctx):
        fail_paint_motion(ctx, "Cycle-start Joint 6 unwind failed before pickup")
        return PaintExecutionState.ERROR

    planning = executor._pickup.build_plan_result(ctx.execution_plan)
    if isinstance(planning, Failed):
        ctx.operation_failure = planning.failure
        fail_paint_motion(ctx, planning.failure.message)
        return PaintExecutionState.ERROR
    pickup_plan = planning.value

    if pickup_plan is not None:
        def calibration_source():
            magazine = ctx.magazine_config or ctx.process_config.magazine_load
            group_id = str(magazine.calibration_group_id)
            navigation = ctx.production_service._magazine_load_service._navigation
            return group_id, navigation.get_group_position(group_id)

        reserved = executor._dropoff_strategy.begin_cycle(DropoffCycleRequest(
            ctx.execution_plan, pickup_plan, calibration_source,
        ))
        if not reserved.completed:
            finish_paint_motion(ctx, success=False)
            ctx.set_outcome(reserved)
            return (PaintExecutionState.FINISHED if reserved.outcome is PaintOutcome.TRAY_FULL
                    else PaintExecutionState.ERROR)

    stop_after_pickup = bool(
        ctx.process_config.stop_after_calibration_pickup and ctx.adjustment_session is None
    )
    ctx.paint_ordered_result = (
        execute_ordered_pickup_and_paint_contact_result(
            executor,
            ctx.execution_plan,
            pickup_plan=pickup_plan,
        )
        if pickup_plan is not None and not stop_after_pickup and ctx.adjustment_session is None
        else PaintOperationResult(PaintOutcome.NOT_APPLICABLE, "Separate pickup requested")
    )
    if ctx.paint_ordered_result.outcome is not PaintOutcome.NOT_APPLICABLE:
        result = ctx.paint_ordered_result
        ctx.paint_total_waypoints = result.planned_waypoints
        msg = result.message
        if not result.completed:
            if result.outcome is PaintOutcome.CANCELLED:
                finish_paint_motion(ctx, success=False)
                ctx.set_outcome(result)
                return PaintExecutionState.STOPPED
            if result.outcome is PaintOutcome.NO_WORKPIECE:
                finish_paint_motion(ctx, success=False)
                ctx.set_outcome(result)
                return PaintExecutionState.FINISHED
            ctx.operation_failure = result.failure
            fail_paint_motion(ctx, msg)
            return PaintExecutionState.ERROR
        ctx.paint_contact_executed_in_ordered_chain = True
        return PaintExecutionState.PAINT_CONTACT

    if _unmatched_second_pass_requested(executor, ctx.execution_plan):
        fail_paint_motion(ctx, "Two-pass painting requires ordered motion-chain support")
        return PaintExecutionState.ERROR

    result = executor._pickup.execute_result(
        ctx.execution_plan, pickup_plan=pickup_plan, stop_after_retract=stop_after_pickup,
    )
    if not result.completed:
        if result.outcome in {PaintOutcome.NO_WORKPIECE, PaintOutcome.CANCELLED}:
            finish_paint_motion(ctx, success=False)
            ctx.set_outcome(result)
            return (PaintExecutionState.STOPPED if result.outcome is PaintOutcome.CANCELLED
                    else PaintExecutionState.FINISHED)
        ctx.operation_failure = result.failure
        fail_paint_motion(ctx, result.message)
        return PaintExecutionState.ERROR
    if stop_after_pickup:
        finish_paint_motion(ctx, success=True)
        ctx.set_result(True, "Calibration pickup test completed")
        return PaintExecutionState.COMPLETED
    return PaintExecutionState.PAINT_CONTACT


def try_execute_ordered_pickup_and_paint_contact(
    executor: object, prepared_workpiece, *, pickup_plan=None,
) -> tuple[bool, str, int] | None:
    """Legacy adapter; production uses the typed ordered-attempt result."""
    return execute_ordered_pickup_and_paint_contact_result(
        executor, prepared_workpiece, pickup_plan=pickup_plan,
    ).as_legacy_triple()


@timed_step(_logger, "ordered_pickup_paint_contact_chain")
def execute_ordered_pickup_and_paint_contact_result(
    executor: object,
    prepared_workpiece,
    *,
    pickup_plan=None,
) -> PaintOperationResult:
    """Execute pickup/staging and primary paint contact as one preplanned ordered chain."""
    failure_code = PaintFailureCode.PLANNING
    stage = "ordered_pickup_paint_planning"

    if pickup_plan is None:
        planning = executor._pickup.build_plan_result(prepared_workpiece)
        if isinstance(planning, Failed):
            return PaintOperationResult(PaintOutcome.FAILED, planning.failure.message, planning.failure)
        pickup_plan = planning.value
    if pickup_plan.contact_mode not in {
        PICKUP_CONTACT_MODE_PLANNED,
        PICKUP_CONTACT_MODE_SENSOR_CONTROLLED_FAST_LIN,
    }:
        _logger.info(
            "[ORDERED_CHAIN] pickup plus paint contact chain skipped: pickup contact mode=%s",
            pickup_plan.contact_mode,
        )
        return PaintOperationResult(PaintOutcome.NOT_APPLICABLE, "Pickup mode requires separate execution")
    executor._last_pickup_plan = pickup_plan.motion_plan

    if pickup_plan.change_plane_combined_with_first_contact:
        with timed_block(_logger, "pickup_phase", label="Changing plane combined with first pivot contact pose"):
            _logger.info(
                "[PICKUP] Changing plane skipped as standalone move; orientation will be combined with first pivot contact pose"
            )

    paint_paths: list[list[list[float]]] = []
    paint_jobs: list[PaintContactCommandJob] = []
    contact_result = executor._paint_contact.execute_result(
        prepared_workpiece,
        execute_robot=False,
        collected_command_paths=paint_paths,
        collected_command_jobs=paint_jobs,
    )
    (ok, msg, total_waypoints) = (contact_result.completed, contact_result.message, contact_result.planned_waypoints)
    if not contact_result.completed:
        return contact_result
    if not paint_paths:
        return PaintOperationResult.failed(failure_code, stage, 'Pickup succeeded, but no paint contact path was generated', planned_waypoints=total_waypoints)

    paint_segments = build_ordered_paint_contact_segments(
            paint_paths,
            paint_jobs,
            executor._paint_process_config().contact_staging,
            acceleration_scale=(
                executor._paint_process_config().paint_process_acceleration_scale_percent
                / 100.0
            ),
    )
    post_pickup_segments = list(paint_segments)

    second_pass_paths: list[list[list[float]]] = []
    second_pass_jobs: list[PaintContactCommandJob] = []
    config = executor._paint_process_config()
    workpiece = prepared_workpiece.workpiece
    is_unmatched = str(workpiece.get("workpieceId", "")).strip().lower() == "captured"
    pass_count = max(1, min(2, int(config.unmatched_paint_pass_count)))
    if is_unmatched and pass_count == 2:
        pass_2 = config.unmatched_second_pass
        use_first = bool(pass_2.use_pass_1_settings)
        velocity = None if use_first else float(pass_2.velocity_percent)
        acceleration = (
            None
            if use_first
            else executor._scale_process_acceleration(pass_2.acceleration_percent)
        )
        offset = (
            executor._resolve_pivot_offset_mm(None, prepared_workpiece)
            if use_first
            else float(pass_2.offset_mm)
        )
        contact_result = executor._paint_contact.execute_result(
            prepared_workpiece,
            vel_override=velocity,
            acc_override=acceleration,
            execute_robot=False,
            collected_command_paths=second_pass_paths,
            collected_command_jobs=second_pass_jobs,
            pivot_offset_override_mm=offset,
        )
        (ok, msg, second_waypoints) = (contact_result.completed, contact_result.message, contact_result.planned_waypoints)
        if not contact_result.completed:
            return contact_result
        if not second_pass_paths:
            return PaintOperationResult.failed(failure_code, stage, "Second paint pass could not be planned", planned_waypoints=total_waypoints)
        total_waypoints += int(second_waypoints)
        post_pickup_segments.extend(
            build_ordered_second_pass_segments(
                second_pass_paths, second_pass_jobs, config
            )
        )
    final_pose: list[float] | None = (
        list(second_pass_paths[-1][-1]) if second_pass_paths else list(paint_paths[-1][-1])
    )
    final_jobs = second_pass_jobs or paint_jobs
    if final_jobs and final_jobs[-1].retreat_pose is not None:
        final_pose = list(final_jobs[-1].retreat_pose)
    planned_approach = executor._dropoff_strategy.plan_paint_approach(
        cleanup_pending=(executor._edge_cleanup.should_run_after_xz_ry()
                         or executor._edge_cleanup.should_run_after_xy_rz()),
    )
    if isinstance(planned_approach, Failed):
        return PaintOperationResult(PaintOutcome.FAILED, planned_approach.failure.message,
                                    planned_approach.failure, total_waypoints)
    approach = planned_approach.value
    post_pickup_segments.extend(approach.segments)
    final_pose = approach.final_pose or final_pose
    activated = executor._dropoff_strategy.activate_approach(approach)
    if not activated.completed:
        return PaintOperationResult(activated.outcome, activated.message,
                                    activated.failure, total_waypoints)

    if pickup_plan.contact_mode == PICKUP_CONTACT_MODE_SENSOR_CONTROLLED_FAST_LIN:
        _logger.info(
            "[ORDERED_CHAIN] preparing complete post-retract servo chain: "
            "segments=%d paint_paths=%d dropoff_segments=%d",
            len(post_pickup_segments),
            len(paint_paths),
            len(approach.segments),
        )
        pickup_result = executor._pickup.execute_result(
            prepared_workpiece,
            pickup_plan=pickup_plan,
            prepared_continuation_segments=post_pickup_segments,
        )
        ok = pickup_result.completed
        if ok:
            executor._dropoff_strategy.approach_completed(approach)
        if ok and final_pose is not None:
            executor._last_process_end_pose = list(final_pose)
        return PaintOperationResult(pickup_result.outcome, pickup_result.message,
                                    pickup_result.failure, total_waypoints)

    segments: list[OrderedMotionCommand] = build_ordered_pickup_segments(pickup_plan)
    segments.extend(post_pickup_segments)

    if pickup_plan.vacuum_on_before_moves:
        failure_code = PaintFailureCode.VACUUM
        stage = "pickup_vacuum"
        ok, msg = executor._vacuum.turn_vacuum_on()
        if not ok:
            return PaintOperationResult.failed(failure_code, stage, msg, planned_waypoints=total_waypoints)

    failure_code = PaintFailureCode.MOTION
    stage = "ordered_pickup_paint_motion"
    if not executor._motion.move_ordered_pickup_sequence(
        "Ordered pickup plus paint contact chain",
        segments,
    ):
        return PaintOperationResult.failed(failure_code, stage, motion_failure_message(executor._robot_service, 'Ordered pickup and paint contact chain failed'), planned_waypoints=total_waypoints)

    executor._dropoff_strategy.approach_completed(approach)
    if final_pose is not None:
        executor._last_process_end_pose = list(final_pose)
    return PaintOperationResult(PaintOutcome.COMPLETED, '', planned_waypoints=total_waypoints)


def build_ordered_second_pass_segments(
    paint_paths: list[list[list[float]]],
    paint_jobs: list[PaintContactCommandJob],
    config,
) -> list[OrderedMotionCommand]:
    """Build the guarded unwind, re-attach, and contact sequence for pass two."""
    return [
        OrderedUnwindJoint6Command(
            label="paint_pass_2_unwind",
            velocity_percent=float(config.navigation_return.unwind_vel_percent),
            acceleration_percent=float(config.navigation_return.unwind_acc_percent),
            protected=True,
        ),
        *build_ordered_paint_contact_segments(
                paint_paths,
                paint_jobs,
                config.contact_staging,
                label_prefix="paint_pass_2",
                acceleration_scale=(
                    1.0
                    if not bool(config.unmatched_second_pass.use_pass_1_settings)
                    else config.paint_process_acceleration_scale_percent / 100.0
                ),
        ),
    ]


def _unmatched_second_pass_requested(executor: object, execution_plan: object) -> bool:
    config = executor._paint_process_config()
    workpiece = execution_plan.workpiece
    return (
        str(workpiece.get("workpieceId", "")).strip().lower() == "captured"
        and int(config.unmatched_paint_pass_count) == 2
    )
