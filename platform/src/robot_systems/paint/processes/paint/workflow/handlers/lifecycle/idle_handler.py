from __future__ import annotations

from src.robot_systems.paint.processes.paint.workflow.context import PaintExecutionContext
from src.robot_systems.paint.processes.paint.workflow.state import PaintExecutionState


def handle_idle(ctx: PaintExecutionContext) -> PaintExecutionState:
    return PaintExecutionState.IDLE
