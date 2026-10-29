"""Disabled/mode gates precede hardware access, while target faults remain fatal."""

import unittest
from dataclasses import replace

from src.robot_systems.paint.component_ids import MovementGroupID
from src.robot_systems.paint.contracts.paint_head_check.errors import (
    HeadInspectionFailure,
    HeadInspectionFailureCode,
    PaintHeadInspectionTargetError,
)
from src.robot_systems.paint.contracts.paint_head_check.interfaces import (
    IHeadInspectionControl,
    IHeadInspectionMotion,
    IHeadInspectionTargetProvider,
    IPaintHeadCheckObserver,
    IPaintHeadInspector,
)
from src.robot_systems.paint.contracts.paint_head_check.models import (
    HeadCheckContext,
    HeadCheckOperatingMode,
    HeadInspectionMotionType,
    HeadInspectionTarget,
    HeadInspectionWindow,
    PaintHeadAction,
    PaintHeadCheckConfiguration,
    PaintHeadObservation,
    PaintHeadObservationReason,
    PaintHeadState,
    PaintHeadStateReactions,
)
from src.robot_systems.paint.contracts.paint_head_check.results import (
    HeadCheckPassed,
    HeadCheckRejected,
    HeadCheckSkipped,
    HeadInspectionMoveFailed,
    HeadInspectionMoveResult,
    HeadInspectionPositionReached,
    HeadObservationResult,
    ObservationReceived,
)
from src.robot_systems.paint.paint_head_check.policy_registry import (
    EVERY_CYCLE_POLICY,
    FIRST_THEN_INTERVAL_POLICY,
)
from src.robot_systems.paint.paint_head_check.run import PaintHeadCheckRunFactory


class FakeControl(IHeadInspectionControl):
    def should_stop(self) -> bool:
        return False

    def pause_requested(self) -> bool:
        return False


class FakeInspector(IPaintHeadInspector):
    def __init__(self) -> None:
        self.begin_count = 0
        self.end_count = 0

    def begin_inspection(self) -> None:
        self.begin_count += 1

    def end_inspection(self) -> None:
        self.end_count += 1

    def next_observation(
        self,
        window: HeadInspectionWindow,
        control: IHeadInspectionControl,
    ) -> HeadObservationResult:
        return ObservationReceived(
            PaintHeadObservation(
                PaintHeadState.PRESENT,
                PaintHeadState.PRESENT,
                PaintHeadObservationReason.ALIGNED,
                1,
                window.started_at,
                window.started_at,
                window.started_at,
                1,
                None,
                False,
            )
        )


class FakeTargetProvider(IHeadInspectionTargetProvider):
    def __init__(self) -> None:
        self.calls = 0
        self.invalid = False

    def resolve(self) -> HeadInspectionTarget:
        self.calls += 1
        if self.invalid:
            raise PaintHeadInspectionTargetError(
                HeadInspectionFailure(
                    HeadInspectionFailureCode.INSPECTION_GROUP_MISSING,
                    "Vertical Shaft Alignment is not configured",
                )
            )
        return HeadInspectionTarget(
            MovementGroupID.VERTICAL_SHAFT_ALIGNMENT,
            (1, 2, 3, 180, 0, 0),
            20,
            30,
            HeadInspectionMotionType.POINT_TO_POINT,
        )


class FakeMotion(IHeadInspectionMotion):
    def __init__(self) -> None:
        self.calls = 0
        self.failed = False

    def move_to_inspection(
        self,
        target: HeadInspectionTarget,
        control: IHeadInspectionControl,
    ) -> HeadInspectionMoveResult:
        self.calls += 1
        if self.failed:
            return HeadInspectionMoveFailed(
                HeadInspectionFailure(
                    HeadInspectionFailureCode.INSPECTION_MOTION_FAILED,
                    "Motion failed",
                )
            )
        return HeadInspectionPositionReached()


class RecordingObserver(IPaintHeadCheckObserver):
    def inspection_started(self, context: HeadCheckContext) -> None:
        pass

    def __init__(self) -> None:
        self.failures: list[HeadInspectionFailure] = []

    def observation_received(
        self,
        observation: PaintHeadObservation,
        context: HeadCheckContext,
    ) -> None:
        pass

    def inspection_failed(
        self,
        failure: HeadInspectionFailure,
        context: HeadCheckContext,
    ) -> None:
        self.failures.append(failure)


def configuration() -> PaintHeadCheckConfiguration:
    report = PaintHeadAction.REPORT_ONLY
    return PaintHeadCheckConfiguration(
        enabled=True,
        policy_id=EVERY_CYCLE_POLICY,
        interval_cycles=5,
        timeout_seconds=2.0,
        state_reactions=PaintHeadStateReactions(report, report, report, report),
        failure_action=report,
        timeout_action=report,
        report_until_confirmed=True,
    )


class HeadCheckRunTests(unittest.TestCase):
    def setUp(self) -> None:
        self.inspector = FakeInspector()
        self.target = FakeTargetProvider()
        self.motion = FakeMotion()
        self.observer = RecordingObserver()
        self.control = FakeControl()
        self.factory = PaintHeadCheckRunFactory(
            self.inspector,
            self.target,
            self.motion,
            self.observer,
        )

    def test_off_bypasses_target_validation_motion_and_detector_lifecycle(self) -> None:
        self.target.invalid = True
        run = self.factory.create_run(
            replace(configuration(), enabled=False),
            HeadCheckOperatingMode.PRODUCTION,
        )
        self.assertFalse(run.check_before_cycle_due())
        self.assertIsInstance(run.check_before_cycle(self.control), HeadCheckSkipped)
        run.record_completed_cycle()
        self.assertIsInstance(
            run.check_before_cycle(self.control),
            HeadCheckSkipped,
        )
        self.assertEqual(
            (0, 0, 0), (self.target.calls, self.motion.calls, self.inspector.begin_count)
        )

    def test_pickup_only_skips_but_dry_run_and_adjustment_inspect(self) -> None:
        pickup = self.factory.create_run(configuration(), HeadCheckOperatingMode.PICKUP_ONLY)
        self.assertIsInstance(pickup.check_before_cycle(self.control), HeadCheckSkipped)
        self.assertEqual(0, self.target.calls)
        for mode in (HeadCheckOperatingMode.DRY_RUN, HeadCheckOperatingMode.ADJUSTMENT):
            with self.subTest(mode=mode):
                run = self.factory.create_run(configuration(), mode)
                self.assertIsInstance(run.check_before_cycle(self.control), HeadCheckPassed)
        self.assertEqual(2, self.target.calls)

    def test_reporting_cannot_override_invalid_position_or_failed_motion(self) -> None:
        self.target.invalid = True
        run = self.factory.create_run(configuration(), HeadCheckOperatingMode.PRODUCTION)
        self.assertIsInstance(run.check_before_cycle(self.control), HeadCheckRejected)
        self.assertEqual(0, self.motion.calls)
        self.assertEqual(0, self.inspector.begin_count)
        self.assertTrue(run.check_before_cycle_due())
        self.target.invalid = False
        self.motion.failed = True
        self.assertIsInstance(run.check_before_cycle(self.control), HeadCheckRejected)
        self.assertIs(
            HeadInspectionFailureCode.INSPECTION_MOTION_FAILED,
            self.observer.failures[-1].code,
        )
        self.assertEqual(0, self.inspector.begin_count)

    def test_interval_checks_are_before_cycles_without_inspecting_on_completion(self) -> None:
        run = self.factory.create_run(
            replace(configuration(), policy_id=FIRST_THEN_INTERVAL_POLICY),
            HeadCheckOperatingMode.PRODUCTION,
        )
        for index in range(1, 12):
            result = run.check_before_cycle(self.control)
            self.assertIsInstance(
                result, HeadCheckPassed if index in (1, 6, 11) else HeadCheckSkipped
            )
            count = self.inspector.begin_count
            run.record_completed_cycle()
            self.assertEqual(count, self.inspector.begin_count)
        self.assertEqual(3, self.inspector.begin_count)

    def test_every_cycle_checks_before_next_cycle_and_not_after_final_completion(self) -> None:
        run = self.factory.create_run(configuration(), HeadCheckOperatingMode.PRODUCTION)
        for count in range(1, 4):
            self.assertIsInstance(run.check_before_cycle(self.control), HeadCheckPassed)
            self.assertEqual(count, self.inspector.begin_count)
            run.record_completed_cycle()
            self.assertEqual(count, self.inspector.begin_count)
            self.assertTrue(run.check_before_cycle_due())

    def test_new_runs_have_isolated_initial_check_state(self) -> None:
        first = self.factory.create_run(configuration(), HeadCheckOperatingMode.PRODUCTION)
        first.check_before_cycle(self.control)
        self.assertFalse(first.check_before_cycle_due())
        second = self.factory.create_run(configuration(), HeadCheckOperatingMode.PRODUCTION)
        self.assertTrue(second.check_before_cycle_due())


if __name__ == "__main__":
    unittest.main()
