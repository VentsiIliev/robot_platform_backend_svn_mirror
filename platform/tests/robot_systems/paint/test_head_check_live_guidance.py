"""Live guidance stays read-only, survives alignment and revokes late results on Start."""

import logging
import unittest
from collections import deque
from dataclasses import replace
from threading import Condition, Event
from time import monotonic
from unittest.mock import MagicMock

from src.robot_systems.paint.contracts.paint_head_check.errors import (
    HeadInspectionFailure,
    HeadInspectionFailureCode,
)
from src.robot_systems.paint.contracts.paint_head_check.interfaces import (
    IHeadInspectionControl,
    IPaintHeadInspector,
    IPaintHeadAlignmentGuidance,
)
from src.robot_systems.paint.contracts.paint_head_check.models import (
    HeadInspectionWindow,
    HeadCheckOperatingMode,
    HeadInspectionPositionTolerance,
    PaintHeadState,
    PaintHeadAction,
)
from src.robot_systems.paint.contracts.paint_head_check.results import (
    ObservationReceived,
    ObservationFailed,
    ObservationCancelled,
    HeadCheckStopped,
)
from src.robot_systems.paint.paint_head_check.live_guidance import PaintHeadLiveGuidance
from src.robot_systems.paint.paint_head_check.adapters.guidance_position import (
    PaintHeadGuidancePositionGuard,
)
from src.robot_systems.paint.paint_head_check.configuration import default_head_check_configuration
from src.robot_systems.paint.paint_head_check.run import PaintHeadCheckRunFactory
from tests.robot_systems.paint.test_head_check_run import (
    FakeControl,
    FakeInspector,
    FakeMotion,
    FakeTargetProvider,
    RecordingObserver as CheckObserver,
)


def observation(state: PaintHeadState):
    result = FakeInspector().next_observation(HeadInspectionWindow(1, 2, 1), FakeControl())
    return replace(result.observation, state=state, observed_state=state)


class LiveInspector(IPaintHeadInspector):
    def __init__(self):
        self.started = Event()
        self.acquiring = Event()
        self.evaluating = Event()
        self.ended = Event()
        self.release = Event()
        self.release.set()
        self.condition = Condition()
        self.results = deque()
        self.begin_count = 0

    def begin_inspection(self):
        self.begin_count += 1
        self.started.set()

    def end_inspection(self):
        self.ended.set()

    def push(self, result):
        with self.condition:
            self.results.append(result)
            self.condition.notify_all()

    def next_observation(self, window: HeadInspectionWindow, control: IHeadInspectionControl):
        self.acquiring.set()
        with self.condition:
            while not self.results and not control.should_stop():
                self.condition.wait(0.01)
            if control.should_stop():
                return ObservationCancelled()
            result = self.results.popleft()
        self.evaluating.set()
        if not self.release.wait(2):
            raise RuntimeError("Test evaluator was not released")
        return result


class LiveObserver:
    def __init__(self):
        self.condition = Condition()
        self.observations = []
        self.failures = []
        self.ends = []

    def guidance_started(self):
        pass

    def guidance_observation(self, observation):
        with self.condition:
            self.observations.append(observation)
            self.condition.notify_all()

    def guidance_failed(self, failure):
        with self.condition:
            self.failures.append(failure)
            self.condition.notify_all()

    def guidance_ended(self, failure=None):
        with self.condition:
            self.ends.append(failure)
            self.condition.notify_all()

    def wait_for(self, predicate):
        with self.condition:
            return self.condition.wait_for(predicate, timeout=2)


class LiveGuidanceTests(unittest.TestCase):
    def setUp(self):
        self.inspector = LiveInspector()
        self.observer = LiveObserver()
        self.guard = MagicMock()
        self.guard.check.return_value = None
        self.ready = Event()
        self.ready.set()
        self.service = PaintHeadLiveGuidance(
            lambda: self.inspector,
            self.guard,
            self.observer,
            self.ready.is_set,
            logger=logging.getLogger(__name__),
        )
        self.addCleanup(self.service.close)
        self.target = FakeTargetProvider().resolve()

    def start_live(self):
        self.service.offer(self.target, 1)
        self.service.start_pending()
        self.assertTrue(self.inspector.started.wait(1))

    def test_offer_waits_for_stopped_transition_and_hardware_cleanup(self):
        self.ready.clear()
        self.service.offer(self.target, 1)
        self.assertFalse(self.inspector.started.is_set())
        self.service.start_pending()
        self.assertFalse(self.inspector.started.wait(0.05))
        self.ready.set()
        self.assertTrue(self.inspector.started.wait(1))
        self.service.start_pending()
        self.assertEqual(1, self.inspector.begin_count)

    def test_live_feedback_continues_after_present_and_recovers_from_camera_loss(self):
        self.start_live()
        self.inspector.push(ObservationReceived(observation(PaintHeadState.MISALIGNED)))
        self.inspector.push(
            ObservationFailed(
                HeadInspectionFailure(HeadInspectionFailureCode.TIMEOUT, "Camera stopped")
            )
        )
        self.inspector.push(ObservationReceived(observation(PaintHeadState.PRESENT)))
        self.inspector.push(ObservationReceived(observation(PaintHeadState.MISSING)))
        self.assertTrue(self.observer.wait_for(lambda: len(self.observer.observations) == 3))
        self.assertEqual(
            [PaintHeadState.MISALIGNED, PaintHeadState.PRESENT, PaintHeadState.MISSING],
            [item.state for item in self.observer.observations],
        )
        self.assertEqual(1, len(self.observer.failures))
        self.assertEqual([], self.observer.ends)
        self.assertEqual(1, self.inspector.begin_count)  # confirmation is not reset each frame

    def test_cancel_revokes_a_detection_already_in_flight(self):
        self.inspector.release.clear()
        self.start_live()
        self.inspector.push(ObservationReceived(observation(PaintHeadState.PRESENT)))
        self.assertTrue(self.inspector.evaluating.wait(1))
        self.service.cancel()
        self.inspector.release.set()
        self.assertTrue(self.inspector.ended.wait(1))
        self.assertEqual([], self.observer.observations)
        self.assertEqual([None], self.observer.ends)

    def test_motion_detected_during_detection_discards_its_result(self):
        self.inspector.release.clear()
        self.start_live()
        self.inspector.push(ObservationReceived(observation(PaintHeadState.PRESENT)))
        self.assertTrue(self.inspector.evaluating.wait(1))
        self.guard.check.return_value = HeadInspectionFailure(
            HeadInspectionFailureCode.INSPECTION_POSITION_CHANGED, "Moved"
        )
        self.inspector.release.set()
        self.assertTrue(self.observer.wait_for(lambda: bool(self.observer.ends)))
        self.assertEqual([], self.observer.observations)
        self.assertIs(
            HeadInspectionFailureCode.INSPECTION_POSITION_CHANGED, self.observer.ends[0].code
        )

    def test_cancelled_pending_offer_never_starts(self):
        self.service.offer(self.target, 1)
        self.service.cancel()
        self.service.start_pending()
        self.assertFalse(self.inspector.started.is_set())

    def test_invalid_position_does_not_acquire_frames(self):
        self.guard.check.return_value = HeadInspectionFailure(
            HeadInspectionFailureCode.INSPECTION_POSITION_CHANGED, "Moved"
        )
        self.service.offer(self.target, 1)
        self.service.start_pending()
        self.assertTrue(self.observer.wait_for(lambda: bool(self.observer.ends)))
        self.assertFalse(self.inspector.started.is_set())


class GuidancePositionTests(unittest.TestCase):
    def setUp(self):
        self.navigation = MagicMock(spec=["get_current_observer_position"])
        self.robot = MagicMock(spec=["get_execution_status"])
        self.provider = FakeTargetProvider()
        self.target = self.provider.resolve()
        self.navigation.get_current_observer_position.return_value = list(self.target.position)
        self.robot.get_execution_status.return_value = {"is_executing": False}
        self.permitted = True
        self.guard = PaintHeadGuidancePositionGuard(
            self.navigation,
            self.robot,
            self.provider,
            lambda: self.permitted,
            HeadInspectionPositionTolerance(0.5, 0.2),
        )

    def test_stationary_taught_pose_is_read_fresh_without_motion_or_frame_activation(self):
        self.assertIsNone(self.guard.check(self.target))
        self.navigation.get_current_observer_position.assert_called_once_with(
            self.target.group_id.value, fresh=True
        )

    def test_motion_invalid_pose_or_disabled_setting_ends_guidance(self):
        self.robot.get_execution_status.return_value = {"is_executing": True}
        self.assertIsNotNone(self.guard.check(self.target))
        self.robot.get_execution_status.return_value = {"is_executing": False}
        self.navigation.get_current_observer_position.return_value[0] += 0.6
        self.assertIsNotNone(self.guard.check(self.target))
        self.permitted = False
        self.assertIs(
            HeadInspectionFailureCode.SERVICE_UNAVAILABLE, self.guard.check(self.target).code
        )

    def test_position_and_reference_target_are_reverified(self):
        self.robot.get_execution_status.side_effect = [
            {"is_executing": False},
            {"is_executing": True},
        ]
        self.assertIsNotNone(self.guard.check(self.target))
        self.provider.invalid = True
        self.assertIs(
            HeadInspectionFailureCode.INSPECTION_GROUP_MISSING, self.guard.check(self.target).code
        )


class GuidanceOfferTests(unittest.TestCase):
    def test_only_a_misalignment_stop_arms_guidance_after_inspection_ends(self):
        for state in (PaintHeadState.MISALIGNED, PaintHeadState.MISSING, PaintHeadState.PRESENT):
            with self.subTest(state=state):
                inspector = FakeInspector()
                original = inspector.next_observation
                inspector.next_observation = lambda window, control: ObservationReceived(
                    replace(
                        original(window, control).observation, state=state, observed_state=state
                    )
                )
                guidance = MagicMock(spec=IPaintHeadAlignmentGuidance)
                factory = PaintHeadCheckRunFactory(
                    inspector,
                    FakeTargetProvider(),
                    FakeMotion(),
                    CheckObserver(),
                    guidance=guidance,
                )
                run = factory.create_run(
                    replace(default_head_check_configuration(), enabled=True),
                    HeadCheckOperatingMode.PRODUCTION,
                )
                guidance.cancel.assert_called_once()
                run.check_before_cycle(FakeControl())
                self.assertEqual(
                    1 if state is PaintHeadState.MISALIGNED else 0, guidance.offer.call_count
                )
                self.assertEqual(1, inspector.end_count)

    def test_timeout_stop_retains_prior_misalignment_for_live_guidance(self):
        inspector = FakeInspector()
        replies = deque(
            [
                ObservationReceived(observation(PaintHeadState.MISALIGNED)),
                ObservationFailed(
                    HeadInspectionFailure(HeadInspectionFailureCode.TIMEOUT, "Expired")
                ),
            ]
        )
        inspector.next_observation = lambda window, control: replies.popleft()
        guidance = MagicMock(spec=IPaintHeadAlignmentGuidance)
        config = replace(default_head_check_configuration(), enabled=True)
        config = replace(
            config,
            state_reactions=replace(config.state_reactions, misaligned=PaintHeadAction.RETRY),
            timeout_action=PaintHeadAction.STOP,
        )
        factory = PaintHeadCheckRunFactory(
            inspector, FakeTargetProvider(), FakeMotion(), CheckObserver(), guidance=guidance
        )
        result = factory.create_run(config, HeadCheckOperatingMode.PRODUCTION).check_before_cycle(
            FakeControl()
        )
        self.assertIsInstance(result, HeadCheckStopped)
        self.assertIs(PaintHeadState.MISALIGNED, result.last_observation.state)
        guidance.offer.assert_called_once()


class GuidanceLifecycleTests(unittest.TestCase):
    def test_start_motion_and_robot_changes_cancel_and_shutdown_unsubscribes(self):
        from src.engine.core.i_messaging_service import IMessagingService
        from src.engine.robot.services.robot_state_snapshot import RobotStateSnapshot
        from src.robot_systems.paint.component_ids import ProcessID
        from src.robot_systems.paint.paint_head_check.adapters.guidance_lifecycle import (
            PaintHeadGuidanceLifecycle,
        )
        from src.shared_contracts.events.process_events import (
            ProcessState,
            ProcessStateEvent,
            ProcessTopics,
        )
        from src.shared_contracts.events.robot_events import RobotTopics

        messaging = MagicMock(spec=IMessagingService)
        guidance = MagicMock(spec=PaintHeadLiveGuidance)
        lifecycle = PaintHeadGuidanceLifecycle(messaging, guidance)
        lifecycle.start()
        callbacks = {call.args[0]: call.args[1] for call in messaging.subscribe.call_args_list}
        callbacks[ProcessTopics.ACTIVE](
            ProcessStateEvent(ProcessID.MAIN_PROCESS, ProcessState.STOPPED, ProcessState.RUNNING)
        )
        guidance.start_pending.assert_called_once()
        callbacks[ProcessTopics.ACTIVE](
            ProcessStateEvent(
                ProcessID.ROBOT_CALIBRATION, ProcessState.RUNNING, ProcessState.STOPPED
            )
        )
        guidance.cancel.assert_called_once()
        callbacks[RobotTopics.STATE](RobotStateSnapshot("idle", [1, 2, 3, 0, 0, 0], 0.1, 0))
        self.assertEqual(2, guidance.cancel.call_count)
        callbacks[RobotTopics.ROBOT_CONFIG_CHANGED](None)
        self.assertEqual(3, guidance.cancel.call_count)
        lifecycle.stop()
        guidance.close.assert_called_once()
        self.assertEqual(4, messaging.unsubscribe.call_count)

    def test_process_cancels_guidance_before_the_start_worker_runs(self):
        from src.engine.core.i_messaging_service import IMessagingService
        from src.robot_systems.paint.processes.paint.paint_process import PaintProcess
        from src.robot_systems.paint.processes.paint.results import (
            PaintOperationResult,
            PaintOutcome,
        )

        production = MagicMock()
        production.last_failure = None
        guidance = MagicMock(spec=IPaintHeadAlignmentGuidance)
        called = Event()
        cancel_counts = []

        def run(stop_requested):
            cancel_counts.append(guidance.cancel.call_count)
            called.set()
            return PaintOperationResult(PaintOutcome.COMPLETED, "Completed")

        production.run_once_result.side_effect = run
        process = PaintProcess(
            production, MagicMock(spec=IMessagingService), head_guidance=guidance
        )
        try:
            process.start()
            self.assertTrue(called.wait(2))
            self.assertEqual([1], cancel_counts)
        finally:
            process.shutdown()


class GuidanceSystemWiringTests(unittest.TestCase):
    def test_system_composes_separate_live_inspectors_and_closes_guidance_before_dependencies(self):
        from src.engine.core.i_messaging_service import IMessagingService
        from src.robot_systems.paint.paint_robot_system import PaintRobotSystem
        from src.shared_contracts.events.process_events import ProcessState

        system = PaintRobotSystem.__new__(PaintRobotSystem)
        system._messaging_service = MagicMock(spec=IMessagingService)
        system._navigation = MagicMock()
        system._robot = MagicMock()
        system._main_process = MagicMock()
        system._main_process.state = ProcessState.STOPPED
        system._main_process.is_stopping = False
        system._paint_process_config_service = MagicMock()
        config = MagicMock()
        config.head_check.enabled = True
        config.stop_after_calibration_pickup = False
        system._paint_process_config_service.get_snapshot.return_value = config
        system.unregister_managed_resource = MagicMock()
        factory = system._build_head_check_run_factory()
        self.assertIsInstance(factory, PaintHeadCheckRunFactory)
        first = system._create_live_head_inspector()
        second = system._create_live_head_inspector()
        self.assertIsNot(first, second)
        self.assertIsNot(first, system._paint_head_inspector)
        self.assertTrue(system._head_guidance_permitted())
        config.head_check.enabled = False
        self.assertFalse(system._head_guidance_permitted())
        config.head_check.enabled = True
        config.stop_after_calibration_pickup = True
        self.assertFalse(system._head_guidance_permitted())

        shutdown_order = []
        lifecycle = system._paint_head_guidance_lifecycle
        original_stop = lifecycle.stop

        def close_live():
            shutdown_order.append("live_guidance")
            original_stop()

        lifecycle.stop = close_live
        system._main_process.shutdown.side_effect = lambda: shutdown_order.append("process")
        system._robot.disable_robot.side_effect = lambda: shutdown_order.append("robot")
        system.on_stop()
        self.assertEqual(["live_guidance", "process", "robot"], shutdown_order)
        self.assertIsNone(system._paint_head_live_guidance)
        self.assertEqual(5, system._messaging_service.unsubscribe.call_count)


if __name__ == "__main__":
    unittest.main()
