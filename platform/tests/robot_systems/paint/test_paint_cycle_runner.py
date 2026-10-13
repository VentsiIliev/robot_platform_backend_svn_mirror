import unittest
from unittest.mock import MagicMock, patch

from src.robot_systems.paint.processes.paint.production.execution_control import PaintExecutionControl
from src.robot_systems.paint.processes.paint.workflow.context import PaintExecutionContext
from src.robot_systems.paint.processes.paint.workflow.state import PaintExecutionState
from src.robot_systems.paint.processes.paint.production.cycle_runner import run_paint_cycle
from src.robot_systems.paint.processes.paint.results import (
    PaintFailureCode, PaintOperationResult, PaintOutcome,
)


class PaintCycleRunnerTests(unittest.TestCase):
    def setUp(self):
        self.context = PaintExecutionContext(
            production_service=MagicMock(), stop_requested=lambda: False,
            control=PaintExecutionControl(),
        )

    def run_with_machine(self, outcome, error=None, initial_state=PaintExecutionState.STARTING):
        machine = MagicMock()
        machine.get_snapshot.return_value.last_error = error
        machine.start_execution.side_effect = lambda: self.context.set_outcome(outcome)
        with patch(
            "src.robot_systems.paint.processes.paint.production.cycle_runner.PaintExecutionMachineFactory"
        ) as factory:
            factory.return_value.build.return_value = machine
            execution = run_paint_cycle(self.context, initial_state=initial_state)
            factory.return_value.build.assert_called_once_with(self.context, initial_state=initial_state)
        return execution

    def test_expected_stop_is_not_counted_as_completed_paint(self):
        with patch("src.robot_systems.paint.processes.paint.production.cycle_runner.observe") as observed:
            self.run_with_machine(PaintOperationResult(PaintOutcome.NO_WORKPIECE, "No workpiece"))
        final = observed.call_args.kwargs
        self.assertEqual(final["outcome"], "no_workpiece")
        self.assertEqual(final["metrics"]["paint.cycle.outcome.no_workpiece"], 1)
        self.assertNotIn("paint.cycle.outcome.completed", final["metrics"])
        self.assertIsNone(final["failure"])

    def test_preserves_completed_and_cancelled_outcomes(self):
        for outcome in (PaintOutcome.COMPLETED, PaintOutcome.CANCELLED):
            with self.subTest(outcome=outcome):
                result = PaintOperationResult(outcome, "cycle outcome")
                execution = self.run_with_machine(result)
                self.assertIs(execution.result, result)
                self.assertIsNone(execution.machine_error)

    def test_prepared_workpiece_can_start_at_pickup(self):
        result = PaintOperationResult(PaintOutcome.COMPLETED, "painted")
        execution = self.run_with_machine(result, initial_state=PaintExecutionState.PICKUP)
        self.assertIs(execution.result, result)

    def test_framework_error_preserves_actionable_failure(self):
        result = PaintOperationResult.failed(PaintFailureCode.VACUUM, "pickup", "Vacuum unavailable")
        execution = self.run_with_machine(result, "Unhandled terminal error")
        self.assertIs(execution.result, result)
        self.assertEqual(execution.machine_error, "Unhandled terminal error")

    def test_framework_error_without_domain_failure_becomes_internal(self):
        result = PaintOperationResult(PaintOutcome.COMPLETED, "painted")
        execution = self.run_with_machine(result, "Invalid transition")
        self.assertEqual(execution.result.outcome, PaintOutcome.FAILED)
        self.assertEqual(execution.result.failure.code, PaintFailureCode.INTERNAL)
        self.assertEqual(execution.result.message, "Invalid transition")

    def test_construction_and_execution_exceptions_propagate_to_owner(self):
        for phase in ("build", "execute"):
            with self.subTest(phase=phase), patch(
                "src.robot_systems.paint.processes.paint.production.cycle_runner.PaintExecutionMachineFactory"
            ) as factory:
                error = RuntimeError("runner failure")
                if phase == "build":
                    factory.return_value.build.side_effect = error
                else:
                    factory.return_value.build.return_value.start_execution.side_effect = error
                with self.assertRaises(RuntimeError) as raised:
                    run_paint_cycle(self.context)
                self.assertIs(raised.exception, error)


if __name__ == "__main__":
    unittest.main()
