"""Run an already prepared paint cycle without owning caller-specific resources."""
from __future__ import annotations

from dataclasses import dataclass

from src.robot_systems.paint.processes.paint.execution_machine.context import PaintExecutionContext
from src.robot_systems.paint.processes.paint.execution_machine.machine_factory import PaintExecutionMachineFactory
from src.robot_systems.paint.processes.paint.execution_machine.state import PaintExecutionState
from src.robot_systems.paint.processes.paint.results import PaintFailureCode, PaintOperationResult


@dataclass(frozen=True)
class PaintCycleExecution:
    """Domain outcome and any framework error requiring caller-specific recovery.

    A framework error can accompany an existing domain failure; preserve that
    failure rather than replacing its actionable category with INTERNAL.
    """

    result: PaintOperationResult
    machine_error: str | None = None


def run_paint_cycle(
    context: PaintExecutionContext,
    *,
    initial_state: PaintExecutionState = PaintExecutionState.STARTING,
) -> PaintCycleExecution:
    """Execute synchronously; configuration, active-context ownership and recovery stay with callers.

    Exceptions from construction or execution propagate so caller finally
    blocks still release their resources. Handler errors recorded by the state
    machine are returned alongside the typed domain result.
    """
    machine = PaintExecutionMachineFactory().build(context, initial_state=initial_state)
    machine.start_execution()
    machine_error = machine.get_snapshot().last_error
    result = context.result
    if machine_error is not None and result.failure is None:
        result = PaintOperationResult.failed(PaintFailureCode.INTERNAL, "paint_cycle", machine_error)
    return PaintCycleExecution(result, machine_error)
