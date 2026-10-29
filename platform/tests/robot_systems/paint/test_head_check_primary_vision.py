"""On-demand inspection must not capture twice, reuse old frames or leak callbacks."""

import unittest
from collections.abc import Callable

import numpy as np
from numpy.typing import NDArray

from src.robot_systems.paint.component_ids import CameraRoleID
from src.robot_systems.paint.contracts.paint_head_check.errors import (
    HeadInspectionFailureCode,
    PaintHeadContractError,
)
from src.robot_systems.paint.contracts.paint_head_check.interfaces import IHeadInspectionControl
from src.robot_systems.paint.contracts.paint_head_check.models import (
    HeadInspectionWindow,
    PaintHeadObservation,
    PaintHeadObservationReason,
    PaintHeadState,
)
from src.robot_systems.paint.contracts.paint_head_check.results import (
    HeadObservationResult,
    ObservationCancelled,
    ObservationFailed,
    ObservationPaused,
    ObservationReceived,
)
from src.robot_systems.paint.paint_head_check.adapters.frames import IHeadFrameEvaluator
from src.robot_systems.paint.paint_head_check.adapters.primary_vision import (
    PrimaryVisionPaintHeadInspector,
)
from src.shared_contracts.events.vision_events import CameraFrameMetadata


class FakeClock:
    def __init__(self) -> None:
        self.now = 10.0

    def __call__(self) -> float:
        return self.now


class FakeControl(IHeadInspectionControl):
    def __init__(self) -> None:
        self.stopped = False
        self.paused = False

    def should_stop(self) -> bool:
        return self.stopped

    def pause_requested(self) -> bool:
        return self.paused


class FakeSubscriptions:
    def __init__(self, clock: FakeClock) -> None:
        self.clock = clock
        self.sequence = 0
        self.callbacks: list[Callable[[object], None]] = []
        self.topics: list[str] = []

    def subscribe(self, topic: str, callback: Callable[[object], None]) -> None:
        self.topics.append(topic)
        self.callbacks.append(callback)

    def unsubscribe(self, topic: str, callback: Callable[[object], None]) -> None:
        self.topics.remove(topic)
        self.callbacks.remove(callback)

    def publish(
        self,
        image: object,
        *,
        camera: str = CameraRoleID.PRIMARY_VISION.value,
        metadata: CameraFrameMetadata | None = None,
    ) -> None:
        self.sequence += 1
        metadata = metadata or CameraFrameMetadata(self.sequence, self.clock.now)
        for callback in tuple(self.callbacks):
            callback({"camera": camera, "image": image, "metadata": metadata})


class FakeEvaluator:
    def __init__(self, clock: FakeClock) -> None:
        self.clock = clock
        self.reset_count = 0
        self.images: list[NDArray[np.uint8]] = []
        self.evaluation_duration = 0.0

    def reset(self) -> None:
        self.reset_count += 1

    def evaluate(
        self,
        image: NDArray[np.uint8],
        *,
        frame_sequence: int,
        frame_captured_at: float,
        frame_received_at: float,
    ) -> HeadObservationResult:
        self.images.append(image)
        self.clock.now += self.evaluation_duration
        return ObservationReceived(
            PaintHeadObservation(
                state=PaintHeadState.UNKNOWN,
                observed_state=PaintHeadState.PRESENT,
                reason=PaintHeadObservationReason.CONFIRMING_STATUS,
                frame_sequence=frame_sequence,
                frame_captured_at=frame_captured_at,
                frame_received_at=frame_received_at,
                evaluated_at=self.clock.now,
                calibration_revision=1,
                alignment=None,
                held_warning=False,
            )
        )


class PrimaryVisionInspectorTests(unittest.TestCase):
    def setUp(self) -> None:
        self.clock = FakeClock()
        self.control = FakeControl()
        self.subscriptions = FakeSubscriptions(self.clock)
        self.evaluator = FakeEvaluator(self.clock)
        self.factory_calls = 0
        self.inspector = PrimaryVisionPaintHeadInspector(
            self.subscriptions,
            self.build_evaluator,
            clock=self.clock,
        )
        self.window = HeadInspectionWindow(10.0, 15.0, 1.0)
        self.addCleanup(self.inspector.end_inspection)

    def build_evaluator(self) -> IHeadFrameEvaluator:
        self.factory_calls += 1
        return self.evaluator

    def test_construction_is_inert_until_a_check_is_requested(self) -> None:
        self.assertEqual(0, self.factory_calls)
        self.assertEqual([], self.subscriptions.callbacks)
        self.inspector.begin_inspection()
        self.assertEqual(1, self.factory_calls)
        self.assertEqual(["camera/primary_vision/frame"], self.subscriptions.topics)
        self.assertEqual(1, self.evaluator.reset_count)

    def test_callback_only_snapshots_a_frame_and_worker_runs_evaluation(self) -> None:
        self.inspector.begin_inspection()
        image = np.zeros((2, 3, 3), dtype=np.uint8)
        self.subscriptions.publish(image)
        image.fill(255)
        self.assertEqual([], self.evaluator.images)
        result = self.inspector.next_observation(self.window, self.control)
        self.assertIsInstance(result, ObservationReceived)
        self.assertEqual(1, len(self.evaluator.images))
        np.testing.assert_array_equal(self.evaluator.images[0], np.zeros_like(image))

    def test_only_latest_frame_is_processed_when_worker_falls_behind(self) -> None:
        self.inspector.begin_inspection()
        self.subscriptions.publish(np.zeros((2, 3, 3), dtype=np.uint8))
        self.subscriptions.publish(np.ones((2, 3, 3), dtype=np.uint8))
        result = self.inspector.next_observation(self.window, self.control)
        self.assertIsInstance(result, ObservationReceived)
        if isinstance(result, ObservationReceived):
            self.assertEqual(2, result.observation.frame_sequence)
        np.testing.assert_array_equal(self.evaluator.images[0], np.ones((2, 3, 3), dtype=np.uint8))

    def test_old_or_preinspection_frames_do_not_reach_detector(self) -> None:
        self.inspector.begin_inspection()
        self.subscriptions.publish(np.zeros((2, 3, 3), dtype=np.uint8))
        self.clock.now = 12.0
        result = self.inspector.next_observation(self.window, self.control)
        self.assertIsInstance(result, ObservationFailed)
        if isinstance(result, ObservationFailed):
            self.assertIs(HeadInspectionFailureCode.FRAME_STALE, result.failure.code)
        self.assertEqual([], self.evaluator.images)

    def test_delayed_delivery_cannot_make_a_prearrival_capture_fresh(self) -> None:
        self.inspector.begin_inspection()
        self.subscriptions.publish(
            np.zeros((2, 3, 3), dtype=np.uint8),
            metadata=CameraFrameMetadata(sequence=1, captured_at_monotonic=9.0),
        )
        result = self.inspector.next_observation(self.window, self.control)
        self.assertIsInstance(result, ObservationFailed)
        if isinstance(result, ObservationFailed):
            self.assertIs(HeadInspectionFailureCode.FRAME_STALE, result.failure.code)
        self.assertEqual([], self.evaluator.images)

    def test_repeated_or_out_of_order_captures_cannot_replace_a_newer_frame(self) -> None:
        for repeated_sequence in (1, 2):
            with self.subTest(repeated_sequence=repeated_sequence):
                self.inspector.begin_inspection()
                self.subscriptions.publish(
                    np.ones((2, 3, 3), dtype=np.uint8),
                    metadata=CameraFrameMetadata(sequence=2, captured_at_monotonic=10.0),
                )
                self.subscriptions.publish(
                    np.zeros((2, 3, 3), dtype=np.uint8),
                    metadata=CameraFrameMetadata(
                        sequence=repeated_sequence,
                        captured_at_monotonic=10.0,
                    ),
                )
                result = self.inspector.next_observation(self.window, self.control)
                self.assertIsInstance(result, ObservationReceived)
                if isinstance(result, ObservationReceived):
                    self.assertEqual(2, result.observation.frame_sequence)
                np.testing.assert_array_equal(
                    self.evaluator.images[-1],
                    np.ones((2, 3, 3), dtype=np.uint8),
                )
                self.inspector.end_inspection()

    def test_slow_processing_cannot_return_an_observation_older_than_the_freshness_limit(
        self,
    ) -> None:
        self.inspector.begin_inspection()
        self.subscriptions.publish(np.zeros((2, 3, 3), dtype=np.uint8))
        self.evaluator.evaluation_duration = 2.0
        result = self.inspector.next_observation(self.window, self.control)
        self.assertIsInstance(result, ObservationFailed)
        if isinstance(result, ObservationFailed):
            self.assertIs(HeadInspectionFailureCode.FRAME_STALE, result.failure.code)

    def test_camera_and_image_contract_failures_are_typed(self) -> None:
        self.inspector.begin_inspection()
        self.subscriptions.publish(None, camera="auxiliary")
        invalid_camera = self.inspector.next_observation(self.window, self.control)
        self.assertIsInstance(invalid_camera, ObservationFailed)
        if isinstance(invalid_camera, ObservationFailed):
            self.assertIs(HeadInspectionFailureCode.CAMERA_READ_FAILED, invalid_camera.failure.code)
        self.subscriptions.publish(None)
        invalid_image = self.inspector.next_observation(self.window, self.control)
        self.assertIsInstance(invalid_image, ObservationFailed)
        if isinstance(invalid_image, ObservationFailed):
            self.assertIs(HeadInspectionFailureCode.IMAGE_INVALID, invalid_image.failure.code)

    def test_stop_and_pause_return_distinct_outcomes_without_a_frame(self) -> None:
        self.inspector.begin_inspection()
        self.control.paused = True
        self.assertIsInstance(
            self.inspector.next_observation(self.window, self.control),
            ObservationPaused,
        )
        self.control.stopped = True
        self.assertIsInstance(
            self.inspector.next_observation(self.window, self.control),
            ObservationCancelled,
        )

    def test_deadline_is_enforced_after_processing_not_only_before_it(self) -> None:
        self.inspector.begin_inspection()
        self.subscriptions.publish(np.zeros((2, 3, 3), dtype=np.uint8))
        self.evaluator.evaluation_duration = 6.0
        result = self.inspector.next_observation(self.window, self.control)
        self.assertIsInstance(result, ObservationFailed)
        if isinstance(result, ObservationFailed):
            self.assertIs(HeadInspectionFailureCode.TIMEOUT, result.failure.code)

    def test_end_unsubscribes_and_new_check_resets_confirmation(self) -> None:
        self.inspector.begin_inspection()
        self.subscriptions.publish(np.zeros((2, 3, 3), dtype=np.uint8))
        self.inspector.end_inspection()
        self.assertEqual([], self.subscriptions.callbacks)
        self.inspector.begin_inspection()
        self.assertEqual(1, self.factory_calls)
        self.assertEqual(2, self.evaluator.reset_count)
        self.control.stopped = True
        self.assertIsInstance(
            self.inspector.next_observation(self.window, self.control),
            ObservationCancelled,
        )
        self.assertEqual([], self.evaluator.images)

    def test_misordered_lifecycle_calls_raise_a_custom_contract_error(self) -> None:
        with self.assertRaises(PaintHeadContractError):
            self.inspector.next_observation(self.window, self.control)
        self.inspector.begin_inspection()
        with self.assertRaises(PaintHeadContractError):
            self.inspector.begin_inspection()


if __name__ == "__main__":
    unittest.main()
