from __future__ import annotations

import logging

from src.robot_systems.paint.processes.paint.results import PaintOutcome

from src.robot_systems.paint.processes.paint.execute.diagnostics import elapsed_s
from src.robot_systems.paint.processes.paint.execution_machine.context import PaintExecutionContext
from src.robot_systems.paint.processes.paint.execution_machine.handlers.common.motion_handlers import (
    fail_paint_motion,
    finish_paint_motion,
    wait_or_guard,
)
from src.robot_systems.paint.processes.paint.execution_machine.state import PaintExecutionState

_logger = logging.getLogger(__name__)


def handle_paint_contact(ctx: PaintExecutionContext) -> PaintExecutionState:
    executor = ctx.production_service._path_executor

    guarded = wait_or_guard(ctx, PaintExecutionState.PAINT_CONTACT)
    if guarded is not None:
        finish_paint_motion(ctx, success=False)
        return guarded

    if ctx.paint_contact_executed_in_ordered_chain:
        return PaintExecutionState.EDGE_CLEANUP

    if ctx.adjustment_session is not None:
        from src.robot_systems.paint.processes.paint.execute.incremental_paint_executor import (
            run_incremental_paint_contact_result,
        )
        result = run_incremental_paint_contact_result(ctx)
        if result.outcome is PaintOutcome.CANCELLED:
            finish_paint_motion(ctx, success=False)
            ctx.set_outcome(result)
            return PaintExecutionState.STOPPED
        if not result.completed:
            ctx.operation_failure = result.failure
            fail_paint_motion(ctx, result.message)
            return PaintExecutionState.ERROR
        return PaintExecutionState.PREPARE_DROPOFF

    contact_result = executor._paint_contact.execute_result(ctx.execution_plan, control=ctx.control)
    (ok, msg, total_waypoints) = (contact_result.completed, contact_result.message, contact_result.planned_waypoints)
    ctx.paint_total_waypoints = int(total_waypoints)

    if contact_result.outcome is PaintOutcome.CANCELLED:
        finish_paint_motion(ctx, success=False)
        ctx.set_outcome(contact_result)
        return PaintExecutionState.STOPPED
    if not ok:
        ctx.operation_failure = contact_result.failure
        _logger.debug(
            "[TIMING] paint_process success=false stage=contact total_elapsed_s=%.3f",
            elapsed_s(ctx.paint_started_at),
        )
        fail_paint_motion(ctx, msg)
        return PaintExecutionState.ERROR

    return PaintExecutionState.EDGE_CLEANUP
