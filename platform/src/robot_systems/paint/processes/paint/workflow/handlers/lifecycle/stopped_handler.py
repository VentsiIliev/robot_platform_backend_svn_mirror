from __future__ import annotations

from src.robot_systems.paint.processes.paint.results import PaintOperationResult, PaintOutcome

from src.robot_systems.paint.processes.paint.workflow.context import PaintExecutionContext
from src.robot_systems.paint.processes.paint.workflow.handlers.lifecycle.terminal_common import (
    restore_cycle_resources,
    stop_machine,
)
from src.robot_systems.paint.processes.paint.workflow.state import PaintExecutionState


def handle_stopped(ctx: PaintExecutionContext) -> PaintExecutionState:
    if not ctx.result_message:
        ctx.set_outcome(PaintOperationResult(PaintOutcome.CANCELLED, "Paint process stopped"))
    restore_cycle_resources(ctx)
    stop_machine(ctx)
    return PaintExecutionState.IDLE
