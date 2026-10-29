"""A configured inspection stop is retryable and retains its typed evidence."""

import unittest
from dataclasses import replace
from unittest.mock import MagicMock

from src.robot_systems.paint.applications.dashboard.controller.paint_dashboard_controller import (
    PaintDashboardController,
)
from src.robot_systems.paint.applications.dashboard.service.paint_dashboard_service import (
    PaintDashboardService,
)
from src.robot_systems.paint.contracts.paint_head_check.interfaces import IHeadInspectionControl
from src.robot_systems.paint.contracts.paint_head_check.models import (
    HeadCheckOperatingMode,
    HeadInspectionWindow,
    PaintHeadState,
)
from src.robot_systems.paint.contracts.paint_head_check.results import (
    HeadCheckPassed,
    HeadCheckStopped,
    HeadObservationResult,
    ObservationReceived,
)
from src.robot_systems.paint.paint_head_check.configuration import default_head_check_configuration
from src.robot_systems.paint.paint_head_check.run import PaintHeadCheckRunFactory
from src.robot_systems.paint.processes.paint.head_check_support import head_check_stopped
from src.robot_systems.paint.processes.paint.paint_process import PaintProcess
from src.robot_systems.paint.processes.paint.results import PaintOperationResult, PaintOutcome
from src.shared_contracts.events.process_events import ProcessState
from tests.robot_systems.paint.test_head_check_run import (
    FakeControl,
    FakeInspector,
    FakeMotion,
    FakeTargetProvider,
    RecordingObserver,
)


class StateInspector(FakeInspector):
    def __init__(self, state: PaintHeadState) -> None:
        super().__init__()
        self.state = state

    def next_observation(
        self, window: HeadInspectionWindow, control: IHeadInspectionControl
    ) -> HeadObservationResult:
        received = super().next_observation(window, control)
        assert isinstance(received, ObservationReceived)
        return ObservationReceived(
            replace(received.observation, state=self.state, observed_state=self.state)
        )


class HeadCheckStopTests(unittest.TestCase):
    def run_for_state(self, state: PaintHeadState) -> HeadCheckPassed | HeadCheckStopped:
        inspector = StateInspector(state)
        factory = PaintHeadCheckRunFactory(
            inspector, FakeTargetProvider(), FakeMotion(), RecordingObserver()
        )
        run = factory.create_run(
            replace(default_head_check_configuration(), enabled=True),
            HeadCheckOperatingMode.PRODUCTION,
        )
        result = run.check_before_cycle(FakeControl())
        self.assertEqual(1, inspector.begin_count)
        self.assertEqual(1, inspector.end_count)
        self.assertIsInstance(result, (HeadCheckPassed, HeadCheckStopped))
        assert isinstance(result, (HeadCheckPassed, HeadCheckStopped))
        return result

    def test_default_missing_and_misaligned_stop_but_present_continues(self) -> None:
        for state in (PaintHeadState.MISSING, PaintHeadState.MISALIGNED):
            with self.subTest(state=state):
                result = self.run_for_state(state)
                self.assertIsInstance(result, HeadCheckStopped)
                self.assertIs(state, result.evidence.state)
        self.assertIsInstance(self.run_for_state(PaintHeadState.PRESENT), HeadCheckPassed)

    def test_stopped_process_retries_on_start_without_reset_or_obscuring_the_feed(self) -> None:
        result = self.run_for_state(PaintHeadState.MISSING)
        assert isinstance(result, HeadCheckStopped)
        stopped = head_check_stopped(result.evidence)
        production = MagicMock()
        production.last_failure = None
        production.consecutive_completed_cycles = 0
        production.run_once_result.side_effect = [
            stopped,
            PaintOperationResult(PaintOutcome.COMPLETED, "Paint completed"),
        ]
        process = PaintProcess(production, MagicMock())
        self.addCleanup(process.shutdown)
        process.start()
        assert process._thread is not None
        process._thread.join(2)
        self.assertFalse(process._thread.is_alive())
        if process._stop_thread is not None:
            process._stop_thread.join(2)
        self.assertIs(ProcessState.STOPPED, process.state)
        self.assertIs(stopped, process.last_result)
        self.assertIs(result.evidence, stopped.head_check_evidence)
        self.assertIsNone(process.last_failure)
        self.assertTrue(PaintDashboardService(process).load_state().can_start)
        production.prepare_failure_record.assert_not_called()
        controller = PaintDashboardController.__new__(PaintDashboardController)
        self.assertIsNone(
            controller._dashboard_warning_for_event(ProcessState.STOPPED.value, stopped.message)
        )
        process.start()
        assert process._thread is not None
        process._thread.join(2)
        self.assertFalse(process._thread.is_alive())
        if process._stop_thread is not None:
            process._stop_thread.join(2)
        self.assertEqual(2, production.run_once_result.call_count)
        self.assertIs(ProcessState.STOPPED, process.state)
        self.assertTrue(process.last_result.completed)


if __name__ == "__main__":
    unittest.main()
