from __future__ import annotations

from src.robot_systems.paint.processes.paint.results import PaintOperationResult, PaintOutcome

from src.robot_systems.paint.processes.paint.workflow.context import PaintExecutionContext
from src.robot_systems.paint.processes.paint.workflow.state import PaintExecutionState


def guard_control(ctx: PaintExecutionContext, state: PaintExecutionState) -> PaintExecutionState | None:
    """Return a terminal/paused state when cooperative process control requires it."""
    if ctx.should_stop():
        ctx.set_outcome(PaintOperationResult(PaintOutcome.CANCELLED, "Paint process stopped"))
        return PaintExecutionState.STOPPED
    if not ctx.run_allowed.is_set() or ctx.control.pause_requested():
        ctx.pause_from(state)
        return PaintExecutionState.PAUSED
    return None
