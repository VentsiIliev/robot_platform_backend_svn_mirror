"""Expected production conditions must never masquerade as hardware faults."""
import unittest
from types import SimpleNamespace
from unittest.mock import MagicMock

from src.robot_systems.paint.processes.paint.results import PaintOperationResult, PaintOutcome, PaintFailureCode
from src.robot_systems.paint.processes.paint.production.execution_control import PaintExecutionControl
from src.robot_systems.paint.processes.paint.workflow import (
    PaintExecutionContext, PaintExecutionMachineFactory, PaintExecutionState,
)
from src.robot_systems.paint.processes.paint.workflow.handlers.workflow.preparation_handler import handle_prepare_workpiece
from src.robot_systems.paint.processes.paint.paint_process import PaintProcess
from src.shared_contracts.events.process_events import ProcessState


class TestExpectedTermination(unittest.TestCase):
    def context(self, outcome):
        service = MagicMock()
        service._path_executor._plate_layout_service = None
        return PaintExecutionContext(
            production_service=service, stop_requested=lambda: False,
            control=PaintExecutionControl(),
            result=PaintOperationResult(outcome, 'Expected stop'),
        )

    def test_expected_outcomes_restore_resources_without_failure(self):
        for outcome in (PaintOutcome.NO_WORKPIECE, PaintOutcome.UNMATCHED,
                        PaintOutcome.TRAY_FULL, PaintOutcome.WORK_AREA_FULL):
            with self.subTest(outcome=outcome):
                ctx = self.context(outcome)
                machine = PaintExecutionMachineFactory().build(ctx, initial_state=PaintExecutionState.FINISHED)
                machine.step()
                self.assertEqual(ctx.current_state, PaintExecutionState.FINISHED)
                self.assertEqual(ctx.result.outcome, outcome)
                self.assertIsNone(ctx.result.failure)
                self.assertIsNone(machine.get_snapshot().last_error)
                ctx.production_service._restore_brightness.assert_called_once()
                ctx.production_service._set_dashboard_live_view_paused.assert_called_once()

    def test_no_contour_finishes_without_attempting_preparation(self):
        ctx = self.context(PaintOutcome.NO_WORKPIECE)
        ctx.snapshot = SimpleNamespace(contours=[])
        self.assertEqual(handle_prepare_workpiece(ctx), PaintExecutionState.FINISHED)
        ctx.production_service._workpiece_preparation.prepare_result.assert_not_called()

    def test_cleanup_failure_promotes_expected_stop_to_real_failure(self):
        ctx = self.context(PaintOutcome.UNMATCHED)
        ctx.production_service._restore_brightness.side_effect = RuntimeError('restore failed')
        machine = PaintExecutionMachineFactory().build(ctx, initial_state=PaintExecutionState.FINISHED)
        machine.step()
        self.assertEqual(ctx.result.outcome, PaintOutcome.FAILED)
        self.assertEqual(ctx.result.failure.stage, 'cycle_cleanup')
        self.assertIsNotNone(machine.get_snapshot().last_error)
        ctx.production_service._set_dashboard_live_view_paused.assert_called_once()

    def test_process_expected_outcomes_stop_and_retain_typed_result(self):
        for outcome in (PaintOutcome.NO_WORKPIECE, PaintOutcome.UNMATCHED,
                        PaintOutcome.TRAY_FULL, PaintOutcome.WORK_AREA_FULL,
                        PaintOutcome.CANCELLED, PaintOutcome.COMPLETED):
            with self.subTest(outcome=outcome):
                service = MagicMock()
                result = PaintOperationResult(outcome, 'Expected stop')
                service.run_once_result.return_value = result
                process = PaintProcess(service, MagicMock())
                process._state = ProcessState.RUNNING
                process._run_in_background()
                if process._stop_thread is not None:
                    process._stop_thread.join(1)
                self.assertEqual(process.state, ProcessState.STOPPED)
                self.assertIs(process.last_result, result)
                self.assertIsNone(process.last_failure)
                if outcome in (PaintOutcome.UNMATCHED, PaintOutcome.TRAY_FULL, PaintOutcome.WORK_AREA_FULL):
                    service.publish_dashboard_message.assert_called_once()
                    self.assertEqual(service.publish_dashboard_message.call_args.args[0], 'warning')
                else:
                    service.publish_dashboard_message.assert_not_called()

    def test_real_failure_still_enters_error(self):
        service = MagicMock()
        service.run_once_result.return_value = PaintOperationResult.failed(PaintFailureCode.VACUUM, 'pickup', 'No workpiece: vacuum failed')
        process = PaintProcess(service, MagicMock())
        process._state = ProcessState.RUNNING
        process._run_in_background()
        self.assertEqual(process.state, ProcessState.ERROR)
        self.assertEqual(process.last_failure.code, PaintFailureCode.VACUUM)
        service.publish_dashboard_message.assert_not_called()

    def test_unmatched_retry_rejects_error_even_with_stale_unmatched_result(self):
        process = PaintProcess(MagicMock(), MagicMock())
        process._state = ProcessState.ERROR
        process._last_result = PaintOperationResult(PaintOutcome.UNMATCHED, 'Unknown workpiece')
        self.assertFalse(process.retry_unmatched_workpiece())
