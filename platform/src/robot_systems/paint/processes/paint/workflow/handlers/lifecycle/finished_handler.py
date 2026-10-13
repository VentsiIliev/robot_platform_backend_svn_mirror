from __future__ import annotations

from src.robot_systems.paint.processes.paint.workflow.context import PaintExecutionContext
from src.robot_systems.paint.processes.paint.workflow.handlers.lifecycle.terminal_common import (
    restore_cycle_resources, stop_machine,
)
from src.robot_systems.paint.processes.paint.workflow.state import PaintExecutionState


def handle_finished(ctx: PaintExecutionContext) -> PaintExecutionState:
    """Restore resources after an expected stop without marking work completed."""
    if not ctx.result.expected_stop:
        raise ValueError("FINISHED requires an expected-stop outcome")
    restore_cycle_resources(ctx)
    stop_machine(ctx)
    return PaintExecutionState.IDLE
