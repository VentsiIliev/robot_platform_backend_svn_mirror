"""Run an already prepared paint cycle without owning caller-specific resources."""
from __future__ import annotations

from dataclasses import dataclass, asdict
import logging
from time import monotonic

from src.engine.diagnostics.events import current_context, diagnostic_context, observe
from src.engine.diagnostics.actions import ActionRecorder
from src.robot_systems.paint.diagnostics.cycle_evidence import publish_cycle_settings, publish_execution_plan

_logger = logging.getLogger(__name__)

from src.robot_systems.paint.processes.paint.workflow.context import PaintExecutionContext
from src.robot_systems.paint.processes.paint.workflow.machine_factory import PaintExecutionMachineFactory
from src.robot_systems.paint.processes.paint.workflow.state import PaintExecutionState
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
    operation = "magazine_transfer" if context.magazine_stage_only else (
        "adjustment_cycle" if context.adjustment_session is not None else
        "pickup_only" if context.process_config is not None
        and context.process_config.stop_after_calibration_pickup else "cycle")
    started = monotonic()
    token = {**current_context(), **context.diagnostic_context}
    if not token.get('operation_id'):
        token = {**ActionRecorder().operation_context(), **token}
    with diagnostic_context(**token), diagnostic_context(cycle_id=context.diagnostic_cycle_id,
                            cycle_index=context.cycle_index, operation=operation):
        try:
            context.diagnostic_evidence.update(publish_cycle_settings(context))
            if context.execution_plan is not None:
                publish_execution_plan(context)
        except Exception:
            pass
        configuration_revision = context.diagnostic_evidence.get('effective_process_settings', {}).get('sha256')
        context.diagnostic_context = {**current_context(), 'configuration_revision': configuration_revision}
        with diagnostic_context(configuration_revision=configuration_revision):
            observe(_logger, "paint.cycle.started", metrics={f"paint.{operation}.attempts": 1},
                    initial_state=initial_state.name, magazine_group=context.magazine_group,
                    adjustment=context.adjustment_session is not None,
                    configuration_revision=configuration_revision,
                    evidence=context.diagnostic_evidence)
            try:
                machine = PaintExecutionMachineFactory().build(context, initial_state=initial_state)
                machine.start_execution()
                machine_error = machine.get_snapshot().last_error
                result = context.result
                if machine_error is not None and result.failure is None:
                    result = PaintOperationResult.failed(PaintFailureCode.INTERNAL, "paint_cycle", machine_error)
            except Exception:
                observe(_logger, "paint.cycle.exception", level=logging.ERROR,
                        metrics={f"paint.{operation}.exceptions": 1},
                        duration_s=monotonic() - started)
                _logger.exception("Paint cycle raised before returning an outcome")
                raise
            metrics = {f"paint.{operation}.outcome.{result.outcome.value}": 1,
                       f"paint.{operation}.duration_seconds": monotonic() - started}
            if result.failure is not None:
                metrics[f"paint.failure.{result.failure.code.value}"] = 1
            observe(_logger, "paint.cycle.ended",
                    level=logging.ERROR if result.failure else logging.INFO,
                    metrics=metrics, outcome=result.outcome.value, message=result.message,
                    stop_reason=None if result.stop_reason is None else result.stop_reason.value,
                    planned_waypoints=result.planned_waypoints,
                    failure=None if result.failure is None else asdict(result.failure),
                    evidence=context.diagnostic_evidence,
                    workpiece_evidence=context.diagnostic_evidence.get('workpiece', {}).get('availability', 'not_captured'),
                    machine_error=machine_error)
            return PaintCycleExecution(result, machine_error)
