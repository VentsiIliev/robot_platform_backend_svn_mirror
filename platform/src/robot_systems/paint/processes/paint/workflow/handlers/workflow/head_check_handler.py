"""Before-cycle checkpoint with explicit positioning and continuation."""

from typing import assert_never

from src.robot_systems.paint.contracts.paint_head_check.errors import (
    HeadInspectionFailure,
    HeadInspectionFailureCode,
    PaintHeadCheckError,
)
from src.robot_systems.paint.contracts.paint_head_check.results import (
    HeadCheckCancelled,
    HeadCheckPassed,
    HeadCheckPaused,
    HeadCheckRejected,
    HeadCheckResult,
    HeadCheckSkipped,
    HeadCheckStopped,
    HeadInspectionMoveCancelled,
    HeadInspectionMoveFailed,
    HeadInspectionMovePaused,
    HeadInspectionPositionReached,
)
from src.robot_systems.paint.processes.paint.head_check_support import (
    PaintHeadWorkflowControl,
    head_check_failed,
    head_check_stopped,
)
from src.robot_systems.paint.processes.paint.results import PaintOperationResult, PaintOutcome
from src.robot_systems.paint.processes.paint.workflow.context import PaintExecutionContext
from src.robot_systems.paint.processes.paint.workflow.state import PaintExecutionState


def handle_before_cycle_head_check(ctx: PaintExecutionContext) -> PaintExecutionState:
    next_state = ctx.head_check_next_state
    if next_state is None:
        ctx.set_outcome(
            head_check_failed(
                HeadInspectionFailure(
                    HeadInspectionFailureCode.CONFIGURATION_INVALID,
                    "Before-cycle head check has no configured workflow continuation",
                )
            )
        )
        return PaintExecutionState.ERROR
    return _handle(ctx, PaintExecutionState.BEFORE_CYCLE_HEAD_CHECK, next_state)


def _handle(
    ctx: PaintExecutionContext,
    state: PaintExecutionState,
    next_state: PaintExecutionState,
) -> PaintExecutionState:
    control = PaintHeadWorkflowControl(ctx)
    if control.should_stop():
        return _cancelled(ctx)
    if control.pause_requested():
        return _paused(ctx, state)
    run = ctx.head_check_run
    if run is None:
        return next_state
    if not ctx.head_check_return_pending:
        try:
            result = run.check_before_cycle(control)
        except PaintHeadCheckError as error:
            result = HeadCheckRejected(error.failure)
        transition = _apply_result(ctx, result, state)
        if transition is not None:
            return transition

    if ctx.head_check_return_pending:
        if ctx.head_check_return is None:
            ctx.set_outcome(
                head_check_failed(
                    HeadInspectionFailure(
                        HeadInspectionFailureCode.RETURN_TARGET_INVALID,
                        "Paint-head inspection has no configured return route",
                    )
                )
            )
            return PaintExecutionState.ERROR
        moved = ctx.head_check_return(control)
        match moved:
            case HeadInspectionMoveCancelled():
                return _cancelled(ctx)
            case HeadInspectionMovePaused():
                return _paused(ctx, state)
            case HeadInspectionMoveFailed(failure):
                ctx.set_outcome(head_check_failed(failure))
                return PaintExecutionState.ERROR
            case HeadInspectionPositionReached():
                ctx.head_check_return_pending = False
            case _ as unreachable:
                assert_never(unreachable)
    return next_state


def _apply_result(
    ctx: PaintExecutionContext,
    result: HeadCheckResult,
    state: PaintExecutionState,
) -> PaintExecutionState | None:
    match result:
        case HeadCheckPassed():
            ctx.head_check_return_pending = True
            return None
        case HeadCheckSkipped():
            return None
        case HeadCheckCancelled():
            return _cancelled(ctx)
        case HeadCheckRejected(evidence):
            ctx.set_outcome(head_check_failed(evidence))
            return PaintExecutionState.ERROR
        case HeadCheckStopped(evidence):
            if ctx.cycle_start_unwind_completed and ctx.head_check_run is not None:
                ctx.head_check_run.retain_retry_position()
            ctx.set_outcome(head_check_stopped(evidence))
            return PaintExecutionState.FINISHED
        case HeadCheckPaused(evidence):
            if evidence is not None:
                if ctx.head_check_pause_request is not None:
                    ctx.head_check_pause_request()
                else:
                    ctx.control.request_pause()
            return _paused(ctx, state)
        case _ as unreachable:
            assert_never(unreachable)


def _paused(ctx: PaintExecutionContext, state: PaintExecutionState) -> PaintExecutionState:
    ctx.pause_from(state)
    return PaintExecutionState.PAUSED


def _cancelled(ctx: PaintExecutionContext) -> PaintExecutionState:
    ctx.set_outcome(PaintOperationResult(PaintOutcome.CANCELLED, "Paint-head inspection cancelled"))
    return PaintExecutionState.STOPPED
