"""Bounded checks report observations while policies independently choose actions."""

import unittest
from collections import deque

from src.robot_systems.paint.contracts.paint_head_check.errors import (
    HeadInspectionFailure,
    HeadInspectionFailureCode,
    PaintHeadConfigurationError,
    PaintHeadProcessingError,
)
from src.robot_systems.paint.contracts.paint_head_check.interfaces import (
    IHeadInspectionControl,
    IPaintHeadCheckObserver,
    IPaintHeadInspector,
)
from src.robot_systems.paint.contracts.paint_head_check.models import (
    HeadCheckContext,
    HeadCheckProgress,
    HeadInspectionWindow,
    PaintHeadAction,
    PaintHeadObservation,
    PaintHeadObservationReason,
    PaintHeadState,
    PaintHeadStateReactions,
)
from src.robot_systems.paint.contracts.paint_head_check.results import (
    HeadCheckCancelled,
    HeadCheckPassed,
    HeadCheckPaused,
    HeadCheckRejected,
    HeadCheckStopped,
    HeadObservationResult,
    ObservationFailed,
    ObservationReceived,
)
from src.robot_systems.paint.paint_head_check.coordinator import PaintHeadCheckCoordinator
from src.robot_systems.paint.paint_head_check.reactions import ConfiguredPaintHeadReactionPolicy


class FakeControl(IHeadInspectionControl):
    def __init__(self) -> None:
        self.stopped = False
        self.paused = False

    def should_stop(self) -> bool:
        return self.stopped

    def pause_requested(self) -> bool:
        return self.paused


class RecordingObserver(IPaintHeadCheckObserver):
    def inspection_started(self, context: HeadCheckContext) -> None:
        pass

    def __init__(self) -> None:
        self.observations: list[PaintHeadObservation] = []
        self.failures: list[HeadInspectionFailure] = []
        self.contexts: list[HeadCheckContext] = []

    def observation_received(
        self,
        observation: PaintHeadObservation,
        context: HeadCheckContext,
    ) -> None:
        self.observations.append(observation)
        self.contexts.append(context)

    def inspection_failed(
        self,
        failure: HeadInspectionFailure,
        context: HeadCheckContext,
    ) -> None:
        self.failures.append(failure)
        self.contexts.append(context)


class FakeInspector(IPaintHeadInspector):
    def __init__(self, results: list[HeadObservationResult]) -> None:
        self.results = deque(results)
        self.begin_count = 0
        self.end_count = 0
        self.error: Exception | None = None
        self.cancel_on_read = False
        self.control: FakeControl | None = None

    def begin_inspection(self) -> None:
        self.begin_count += 1
        if self.error is not None:
            raise self.error

    def next_observation(
        self,
        window: HeadInspectionWindow,
        control: IHeadInspectionControl,
    ) -> HeadObservationResult:
        if self.cancel_on_read and self.control is not None:
            self.control.stopped = True
        return self.results.popleft()

    def end_inspection(self) -> None:
        self.end_count += 1


def observed(state: PaintHeadState, sequence: int) -> ObservationReceived:
    return ObservationReceived(
        PaintHeadObservation(
            state,
            state,
            PaintHeadObservationReason.INSUFFICIENT_EVIDENCE,
            sequence,
            1.0,
            1.0,
            1.1,
            1,
            None,
            False,
        )
    )


class HeadCheckCoordinatorTests(unittest.TestCase):
    def setUp(self) -> None:
        self.observer = RecordingObserver()
        self.control = FakeControl()
        self.window = HeadInspectionWindow(0.0, 10.0, 10.0)

    def coordinator(
        self,
        inspector: FakeInspector,
        *,
        action: PaintHeadAction = PaintHeadAction.REPORT_ONLY,
        wait_for_confirmation: bool = True,
    ) -> PaintHeadCheckCoordinator:
        return PaintHeadCheckCoordinator(
            inspector,
            ConfiguredPaintHeadReactionPolicy(
                PaintHeadStateReactions(action, action, action, action),
                failure_action=action,
                timeout_action=action,
                report_until_confirmed=wait_for_confirmation,
            ),
            self.observer,
            clock=self.clock,
        )

    @staticmethod
    def clock() -> float:
        return 1.0

    def test_report_only_can_collect_confirmation_without_blocking_missing_or_misaligned(
        self,
    ) -> None:
        for final in (PaintHeadState.PRESENT, PaintHeadState.MISSING, PaintHeadState.MISALIGNED):
            with self.subTest(final=final):
                inspector = FakeInspector(
                    [
                        observed(PaintHeadState.UNKNOWN, 1),
                        observed(PaintHeadState.UNKNOWN, 2),
                        observed(final, 3),
                    ]
                )
                result = self.coordinator(inspector).inspect(
                    HeadCheckProgress(5),
                    self.window,
                    self.control,
                )
                self.assertIsInstance(result, HeadCheckPassed)
                if isinstance(result, HeadCheckPassed):
                    self.assertEqual(observed(final, 3).observation, result.evidence)
                self.assertEqual(3, self.observer.contexts[-1].attempt_number)
                self.assertEqual(1, inspector.begin_count)
                self.assertEqual(1, inspector.end_count)

    def test_first_observation_reporting_mode_is_explicitly_available(self) -> None:
        inspector = FakeInspector([observed(PaintHeadState.UNKNOWN, 1)])
        result = self.coordinator(inspector, wait_for_confirmation=False).inspect(
            HeadCheckProgress(0),
            self.window,
            self.control,
        )
        self.assertIsInstance(result, HeadCheckPassed)
        self.assertEqual(1, len(self.observer.observations))

    def test_reporting_timeout_is_visible_and_can_continue_production(self) -> None:
        inspector = FakeInspector(
            [
                observed(PaintHeadState.UNKNOWN, 1),
                ObservationFailed(
                    HeadInspectionFailure(HeadInspectionFailureCode.TIMEOUT, "Timed out")
                ),
            ]
        )
        result = self.coordinator(inspector).inspect(
            HeadCheckProgress(0), self.window, self.control
        )
        self.assertIsInstance(result, HeadCheckPassed)
        self.assertEqual(1, len(self.observer.observations))
        self.assertIs(HeadInspectionFailureCode.TIMEOUT, self.observer.failures[0].code)

    def test_reject_and_operator_pause_are_distinct_typed_results(self) -> None:
        for action, result_type in (
            (PaintHeadAction.REJECT, HeadCheckRejected),
            (PaintHeadAction.PAUSE, HeadCheckPaused),
            (PaintHeadAction.STOP, HeadCheckStopped),
        ):
            with self.subTest(action=action):
                inspector = FakeInspector([observed(PaintHeadState.MISSING, 1)])
                result = self.coordinator(inspector, action=action).inspect(
                    HeadCheckProgress(0),
                    self.window,
                    self.control,
                )
                self.assertIsInstance(result, result_type)
                self.assertEqual(1, inspector.end_count)

    def test_cancellation_cannot_return_a_late_pass(self) -> None:
        inspector = FakeInspector([observed(PaintHeadState.PRESENT, 1)])
        inspector.control = self.control
        inspector.cancel_on_read = True
        result = self.coordinator(inspector).inspect(
            HeadCheckProgress(0), self.window, self.control
        )
        self.assertIsInstance(result, HeadCheckCancelled)
        self.assertEqual([], self.observer.observations)
        self.assertEqual(1, inspector.end_count)

    def test_timeout_retry_is_rejected_instead_of_spinning_forever(self) -> None:
        inspector = FakeInspector(
            [
                ObservationFailed(
                    HeadInspectionFailure(HeadInspectionFailureCode.TIMEOUT, "Timed out")
                ),
            ]
        )
        with self.assertRaises(PaintHeadConfigurationError):
            self.coordinator(inspector, action=PaintHeadAction.RETRY).inspect(
                HeadCheckProgress(0),
                self.window,
                self.control,
            )
        self.assertEqual(1, inspector.end_count)

    def test_known_initialization_failure_uses_failure_policy(self) -> None:
        inspector = FakeInspector([])
        inspector.error = PaintHeadProcessingError("Could not initialize vision backend")
        result = self.coordinator(inspector).inspect(
            HeadCheckProgress(0), self.window, self.control
        )
        self.assertIsInstance(result, HeadCheckPassed)
        self.assertIs(HeadInspectionFailureCode.PROCESSING_FAILED, self.observer.failures[0].code)
        self.assertEqual(1, inspector.end_count)

    def test_unexpected_error_preserves_its_type_and_releases_inspection(self) -> None:
        inspector = FakeInspector([])
        inspector.error = RuntimeError("unexpected bug")
        with self.assertRaisesRegex(RuntimeError, "unexpected bug"):
            self.coordinator(inspector).inspect(HeadCheckProgress(0), self.window, self.control)
        self.assertEqual(1, inspector.end_count)


if __name__ == "__main__":
    unittest.main()
