"""A blocked inspection retries fresh frames without repeating prepared startup motion."""

import logging
import unittest
from dataclasses import replace
from unittest.mock import MagicMock, patch

from src.robot_systems.paint.contracts.paint_head_check.errors import HeadInspectionFailureCode
from src.robot_systems.paint.contracts.paint_head_check.interfaces import IHeadInspectionControl
from src.robot_systems.paint.contracts.paint_head_check.models import (
    HeadCheckOperatingMode,
    HeadInspectionPositionTolerance,
    HeadInspectionTarget,
    PaintHeadState,
)
from src.robot_systems.paint.contracts.paint_head_check.results import HeadInspectionMoveResult
from src.robot_systems.paint.paint_head_check.adapters.retry_position import (
    VerifiedInspectionRetryPosition,
)
from src.robot_systems.paint.paint_head_check.configuration import default_head_check_configuration
from src.robot_systems.paint.paint_head_check.run import PaintHeadCheckRunFactory
from src.robot_systems.paint.processes.paint.configuration.models import PaintProcessConfig
from src.robot_systems.paint.processes.paint.production.execution_control import (
    PaintExecutionControl,
)
from src.robot_systems.paint.processes.paint.production.service import PaintProductionService
from src.robot_systems.paint.processes.paint.start_recovery.results import (
    StartRecoveryOutcome,
    StartRecoveryResult,
)
from src.robot_systems.paint.processes.paint.workflow.context import PaintExecutionContext
from src.robot_systems.paint.processes.paint.workflow.handlers.lifecycle.startup_handler import (
    handle_starting,
)
from src.robot_systems.paint.processes.paint.workflow.handlers.workflow.head_check_handler import (
    handle_before_cycle_head_check,
)
from src.robot_systems.paint.processes.paint.workflow.state import PaintExecutionState
from tests.robot_systems.paint.test_head_check_retry_position import FakeNavigation, FakeRobot
from tests.robot_systems.paint.test_head_check_run import (
    FakeMotion,
    FakeTargetProvider,
    RecordingObserver,
)
from tests.robot_systems.paint.test_head_check_stop import StateInspector


class TrackingMotion(FakeMotion):
    def __init__(self, navigation: FakeNavigation) -> None:
        super().__init__()
        self.navigation = navigation

    def move_to_inspection(
        self, target: HeadInspectionTarget, control: IHeadInspectionControl
    ) -> HeadInspectionMoveResult:
        result = super().move_to_inspection(target, control)
        self.navigation.pose = list(target.position)
        return result


class HeadCheckRetryWorkflowTests(unittest.TestCase):
    def setUp(self) -> None:
        self.navigation = FakeNavigation()
        self.robot = FakeRobot()
        self.motion = TrackingMotion(self.navigation)
        self.inspector = StateInspector(PaintHeadState.MISSING)
        self.factory = PaintHeadCheckRunFactory(
            self.inspector,
            FakeTargetProvider(),
            self.motion,
            RecordingObserver(),
            retry_position=VerifiedInspectionRetryPosition(
                self.navigation,
                self.robot,
                self.reference_frame,
                HeadInspectionPositionTolerance(0.5, 0.2),
                logging.getLogger(__name__),
            ),
        )
        self.configuration = replace(default_head_check_configuration(), enabled=True)
        self.production = MagicMock()
        self.production.prepare_start_recovery.return_value = StartRecoveryResult(
            StartRecoveryOutcome.NOT_REQUIRED
        )
        self.production_return = MagicMock()
        from src.robot_systems.paint.contracts.paint_head_check.results import (
            HeadInspectionPositionReached,
        )

        self.production_return.return_value = HeadInspectionPositionReached()
        self.unwind_patch = patch(
            "src.robot_systems.paint.processes.paint.workflow.handlers.lifecycle.startup_handler.unwind_joint6_at_cycle_start",
            side_effect=self.unwind,
        )
        self.unwind_call = self.unwind_patch.start()
        self.addCleanup(self.unwind_patch.stop)

    @staticmethod
    def reference_frame() -> tuple[int, int]:
        return 1, 1

    @staticmethod
    def unwind(context: PaintExecutionContext) -> bool:
        context.cycle_start_unwind_completed = True
        return True

    @staticmethod
    def should_stop() -> bool:
        return False

    def context(self) -> PaintExecutionContext:
        return PaintExecutionContext(
            production_service=self.production,
            stop_requested=self.should_stop,
            control=PaintExecutionControl(),
            process_config=PaintProcessConfig(),
            head_check_run=self.factory.create_run(
                self.configuration, HeadCheckOperatingMode.PRODUCTION
            ),
            head_check_return=self.production_return,
        )

    def stop_first_check(self) -> PaintExecutionContext:
        context = self.context()
        self.assertIs(PaintExecutionState.BEFORE_CYCLE_HEAD_CHECK, handle_starting(context))
        self.assertIs(PaintExecutionState.FINISHED, handle_before_cycle_head_check(context))
        self.assertTrue(context.result.expected_stop)
        return context

    def test_repeated_stops_skip_unwind_and_position_move_but_reset_acquisition(self) -> None:
        self.stop_first_check()
        self.stop_first_check()
        self.assertEqual(1, self.unwind_call.call_count)
        self.production.prepare_start_recovery.assert_called_once()
        self.assertEqual(1, self.motion.calls)
        self.assertEqual(2, self.inspector.begin_count)
        self.assertEqual(2, self.inspector.end_count)
        self.production_return.assert_not_called()
        self.inspector.state = PaintHeadState.PRESENT
        context = self.context()
        self.assertIs(PaintExecutionState.BEFORE_CYCLE_HEAD_CHECK, handle_starting(context))
        self.assertIs(
            PaintExecutionState.CAPTURE_WORKPIECE, handle_before_cycle_head_check(context)
        )
        self.production_return.assert_called_once()
        self.assertEqual(1, self.motion.calls)
        self.assertEqual(1, self.unwind_call.call_count)
        self.assertTrue(context.cycle_start_unwind_completed)
        # A passed check clears the shortcut before later production cycles.
        self.assertFalse(
            self.factory.create_run(
                self.configuration, HeadCheckOperatingMode.PRODUCTION
            ).prepare_retry_in_place()
        )

    def test_jogged_robot_falls_back_to_the_normal_startup_path(self) -> None:
        self.stop_first_check()
        self.navigation.pose = [5, 2, 3, 180, 0, 0]
        self.stop_first_check()
        self.assertEqual(2, self.unwind_call.call_count)
        self.assertEqual(2, self.production.prepare_start_recovery.call_count)
        self.assertEqual(2, self.motion.calls)

    def test_pose_changing_after_startup_verification_cannot_trigger_blind_motion(self) -> None:
        self.stop_first_check()
        context = self.context()
        self.assertIs(PaintExecutionState.BEFORE_CYCLE_HEAD_CHECK, handle_starting(context))
        self.navigation.pose = [5, 2, 3, 180, 0, 0]
        self.assertIs(PaintExecutionState.ERROR, handle_before_cycle_head_check(context))
        self.assertIs(
            HeadInspectionFailureCode.INSPECTION_POSITION_CHANGED,
            context.result.failure.head_check_failure.code,
        )
        self.assertEqual(1, self.motion.calls)
        self.assertEqual(1, self.inspector.begin_count)
        self.production_return.assert_not_called()

    def test_unprepared_editor_stop_does_not_authorize_skipping_startup(self) -> None:
        context = self.context()
        context.head_check_next_state = PaintExecutionState.PICKUP
        self.assertIs(PaintExecutionState.FINISHED, handle_before_cycle_head_check(context))
        self.stop_first_check()
        self.assertEqual(1, self.unwind_call.call_count)
        self.assertEqual(2, self.motion.calls)

    def test_manual_start_does_not_leave_the_verified_inspection_pose_before_retry(self) -> None:
        self.stop_first_check()
        retry = self.factory.create_run(self.configuration, HeadCheckOperatingMode.PRODUCTION)
        service = PaintProductionService(
            workpiece_preparation_service=None,
            capture_snapshot_service=None,
            path_preparation_service=None,
            path_executor=None,
            navigation_service=MagicMock(),
        )
        service._head_check_run = retry
        service.prepare_start_recovery = MagicMock()
        result = service._move_to_calibration_before_manual_cycle(
            PaintProcessConfig().magazine_load, self.should_stop
        )
        self.assertTrue(result.completed)
        service.prepare_start_recovery.assert_not_called()
        service._navigation_service.move_to_calibration_position.assert_not_called()


if __name__ == "__main__":
    unittest.main()
