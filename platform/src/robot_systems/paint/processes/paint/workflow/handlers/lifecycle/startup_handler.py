from __future__ import annotations

from src.robot_systems.paint.processes.paint.results import PaintOperationResult, PaintOutcome

from src.robot_systems.paint.processes.paint.workflow.context import PaintExecutionContext
from src.robot_systems.paint.processes.paint.workflow.handlers.common.motion_handlers import (
    unwind_joint6_at_cycle_start,
)
from src.robot_systems.paint.processes.paint.workflow.state import PaintExecutionState
from src.robot_systems.paint.contracts.paint_head_check.errors import PaintHeadCheckError
from src.robot_systems.paint.processes.paint.head_check_support import head_check_failed


def handle_starting(ctx: PaintExecutionContext) -> PaintExecutionState:
    """Choose the first production phase for this cycle."""
    if ctx.should_stop():
        ctx.set_outcome(PaintOperationResult(PaintOutcome.CANCELLED, "Paint process stopped"))
        return PaintExecutionState.STOPPED
    if ctx.is_resuming and ctx.resume_state is not None:
        resume_state = ctx.resume_state
        ctx.is_resuming = False
        return resume_state
    retry_in_place = False
    if ctx.head_check_run is not None and ctx.head_check_run.check_before_cycle_due():
        try:
            ctx.head_check_run.inspection_target()
            retry_in_place = ctx.head_check_run.prepare_retry_in_place()
        except PaintHeadCheckError as error:
            ctx.set_outcome(head_check_failed(error.failure))
            return PaintExecutionState.ERROR
    if retry_in_place:
        # Reuse the already completed startup unwind from the retained inspection stop.
        ctx.cycle_start_unwind_completed = True
    else:
        recovery = ctx.production_service.prepare_start_recovery(ctx)
        if not recovery.succeeded:
            ctx.set_outcome(recovery.to_operation_result())
            return (PaintExecutionState.STOPPED if ctx.result.outcome is PaintOutcome.CANCELLED
                    else PaintExecutionState.ERROR)
        if not unwind_joint6_at_cycle_start(ctx):
            ctx.set_result(False, "Cycle-start Joint 6 unwind failed before production navigation")
            return PaintExecutionState.ERROR
    next_state = _next_phase(ctx)
    if (
        ctx.head_check_run is not None
        and ctx.head_check_run.check_before_cycle_due()
        and next_state is not PaintExecutionState.ERROR
    ):
        ctx.head_check_next_state = next_state
        return PaintExecutionState.BEFORE_CYCLE_HEAD_CHECK
    return next_state


def _next_phase(ctx: PaintExecutionContext) -> PaintExecutionState:
    service = ctx.production_service
    if ctx.cached_workpiece_contour is not None and ctx.snapshot is not None:
        service._restore_capture_view("processing cached staged workpiece")
        return PaintExecutionState.PREPARE_WORKPIECE
    if ctx.magazine_config is not None and ctx.magazine_config.enabled:
        if service._magazine_load_service is None:
            ctx.set_result(False, "Magazine loading is enabled but its service is not configured")
            return PaintExecutionState.ERROR
        service._set_dashboard_live_view_paused(
            True,
            reason="magazine workflow robot motion starting",
        )
        return PaintExecutionState.MAGAZINE_MOVE_TO_MAGAZINE
    service._restore_capture_view("at paint capture location")
    return PaintExecutionState.CAPTURE_WORKPIECE
