"""Checks guard prepared entry and post-release returns without duplicating release."""

import unittest
from collections import deque
from dataclasses import dataclass
from unittest.mock import patch

from src.robot_systems.paint.component_ids import MovementGroupID
from src.robot_systems.paint.contracts.dropoff import DropoffResult
from src.robot_systems.paint.contracts.next_cycle_target import NextCycleTarget
from src.robot_systems.paint.contracts.paint_head_check.errors import (
    HeadInspectionFailure,
    HeadInspectionFailureCode,
)
from src.robot_systems.paint.contracts.paint_head_check.interfaces import (
    IHeadInspectionControl,
    IPaintHeadCheckRun,
)
from src.robot_systems.paint.contracts.paint_head_check.models import (
    HeadInspectionMotionType,
    HeadInspectionTarget,
    PaintHeadObservation,
    PaintHeadObservationReason,
    PaintHeadState,
)
from src.robot_systems.paint.contracts.paint_head_check.results import (
    HeadCheckPassed,
    HeadCheckRejected,
    HeadCheckResult,
    HeadCheckSkipped,
    HeadCheckStopped,
    HeadInspectionMovePaused,
    HeadInspectionMoveResult,
    HeadInspectionPositionReached,
)
from src.robot_systems.paint.processes.paint.configuration.models import PaintProcessConfig
from src.robot_systems.paint.processes.paint.production.cycle_runner import run_paint_cycle
from src.robot_systems.paint.processes.paint.production.execution_control import (
    PaintExecutionControl,
)
from src.robot_systems.paint.processes.paint.production.service import PaintProductionService
from src.robot_systems.paint.processes.paint.results import PaintFailureCode, PaintOperationResult
from src.robot_systems.paint.processes.paint.workflow.context import PaintExecutionContext
from src.robot_systems.paint.processes.paint.workflow.handlers.dropoff.dropoff_handler import (
    handle_dropoff,
)
from src.robot_systems.paint.processes.paint.workflow.handlers.workflow.head_check_handler import (
    handle_before_cycle_head_check,
)
from src.robot_systems.paint.processes.paint.workflow.state import PaintExecutionState


def evidence() -> PaintHeadObservation:
    return PaintHeadObservation(
        PaintHeadState.MISSING,
        PaintHeadState.MISSING,
        PaintHeadObservationReason.EMPTY_MOUNT,
        1,
        1.0,
        1.0,
        1.0,
        1,
        None,
        False,
    )


class StubRun(IPaintHeadCheckRun):
    def prepare_retry_in_place(self) -> bool:
        return False

    def retain_retry_position(self) -> None:
        pass

    def __init__(self) -> None:
        self.initial_due = True
        self.initial_results: deque[HeadCheckResult] = deque([HeadCheckPassed(evidence())])
        self.return_results: deque[HeadCheckResult] = deque([HeadCheckPassed(evidence())])
        self.initial_calls = 0
        self.return_calls = 0
        self.completed_cycles = 0

    def inspection_target(self) -> HeadInspectionTarget:
        return HeadInspectionTarget(
            MovementGroupID.VERTICAL_SHAFT_ALIGNMENT,
            (1, 2, 3, 180, 0, 0),
            20,
            30,
            HeadInspectionMotionType.POINT_TO_POINT,
        )

    def check_before_cycle_due(self) -> bool:
        return self.initial_due

    def record_completed_cycle(self) -> None:
        self.completed_cycles += 1

    def check_before_cycle(self, control: IHeadInspectionControl) -> HeadCheckResult:
        self.initial_calls += 1
        result = self.initial_results.popleft() if self.initial_due else HeadCheckSkipped()
        if isinstance(result, HeadCheckPassed):
            self.initial_due = False
        return result


class StubDestination:
    def finish_cycle(self, result: PaintOperationResult) -> None:
        pass


class StubExecutor:
    def __init__(self) -> None:
        self._dropoff_strategy = StubDestination()
        self._post_execute_callback = None
        self.targets: list[NextCycleTarget | None] = []

    def _wait_for_paint_resume(self, control: PaintExecutionControl) -> bool:
        return control.wait_if_paused()

    def prepare_dropoff(self) -> tuple[bool, str]:
        return True, ""

    def release_dropoff(self, next_cycle_start: NextCycleTarget | None = None) -> DropoffResult:
        self.targets.append(next_cycle_start)
        return DropoffResult(True)


class StubProduction:
    def __init__(self) -> None:
        self._path_executor = StubExecutor()
        self.release_count = 0

    def release_dropoff(self, context: PaintExecutionContext) -> DropoffResult:
        self.release_count += 1
        return DropoffResult(True)

    def _restore_brightness(self) -> None:
        pass

    def _set_dashboard_live_view_paused(
        self,
        paused: bool,
        *,
        reason: str = "",
        image: object | None = None,
    ) -> None:
        pass


@dataclass(frozen=True)
class StubPlan:
    execution_jobs: tuple[object, ...] = ()


class HeadCheckWorkflowTests(unittest.TestCase):
    def setUp(self) -> None:
        self.run = StubRun()
        self.production = StubProduction()
        self.return_count = 0
        self.context = PaintExecutionContext(
            production_service=self.production,
            stop_requested=self.should_stop,
            control=PaintExecutionControl(),
            process_config=PaintProcessConfig(),
            head_check_run=self.run,
            head_check_return=self.return_to_start,
            head_check_next_state=PaintExecutionState.PICKUP,
        )
        self.context.head_check_pause_request = self.context.control.request_pause
        self.context.execution_plan = StubPlan()

    @staticmethod
    def should_stop() -> bool:
        return False

    def return_to_start(self, control: IHeadInspectionControl) -> HeadInspectionMoveResult:
        self.return_count += 1
        return HeadInspectionPositionReached()

    def test_initial_check_reports_then_returns_before_entering_pickup(self) -> None:
        self.assertIs(PaintExecutionState.PICKUP, handle_before_cycle_head_check(self.context))
        self.assertEqual(1, self.run.initial_calls)
        self.assertEqual(1, self.return_count)
        self.assertFalse(self.context.head_check_return_pending)

    def test_invalid_position_is_a_head_check_failure_and_never_enters_pickup(self) -> None:
        failure = HeadInspectionFailure(
            HeadInspectionFailureCode.INSPECTION_GROUP_MISSING,
            "Vertical Shaft Alignment is missing",
        )
        self.run.initial_results = deque([HeadCheckRejected(failure)])
        self.assertIs(PaintExecutionState.ERROR, handle_before_cycle_head_check(self.context))
        self.assertIs(PaintFailureCode.HEAD_CHECK, self.context.result.failure.code)
        self.assertIn("Vertical Shaft Alignment", self.context.result.message)
        self.assertEqual(0, self.return_count)

    def test_rejected_missing_or_misaligned_stays_at_inspection_without_pickup(self) -> None:
        from dataclasses import replace

        for state in (PaintHeadState.MISSING, PaintHeadState.MISALIGNED):
            with self.subTest(state=state):
                self.run.initial_results = deque(
                    [
                        HeadCheckRejected(replace(evidence(), state=state, observed_state=state)),
                    ]
                )
                self.assertIs(
                    PaintExecutionState.ERROR, handle_before_cycle_head_check(self.context)
                )
                self.assertEqual(0, self.return_count)
                self.assertFalse(self.context.head_check_return_pending)
                self.assertIs(PaintFailureCode.HEAD_CHECK, self.context.result.failure.code)

    def test_pause_during_return_resumes_return_without_repeating_inspection(self) -> None:
        moves = deque([HeadInspectionMovePaused(), HeadInspectionPositionReached()])

        def return_route(control: IHeadInspectionControl) -> HeadInspectionMoveResult:
            return moves.popleft()

        self.context.head_check_return = return_route
        self.assertIs(PaintExecutionState.PAUSED, handle_before_cycle_head_check(self.context))
        self.assertTrue(self.context.head_check_return_pending)
        self.assertIs(PaintExecutionState.PICKUP, handle_before_cycle_head_check(self.context))
        self.assertEqual(1, self.run.initial_calls)
        self.assertFalse(self.context.head_check_return_pending)

    def test_dropoff_does_not_inspect_or_update_head_check_progress(self) -> None:
        self.assertIs(PaintExecutionState.POST_RETURN, handle_dropoff(self.context))
        self.assertEqual(1, self.production.release_count)
        self.assertEqual(0, self.run.initial_calls)
        self.assertEqual(0, self.run.completed_cycles)
        self.assertEqual(0, self.return_count)

    def test_configured_stop_is_an_expected_stop_and_keeps_the_head_in_view(self) -> None:
        self.run.initial_results = deque([HeadCheckStopped(evidence())])
        self.assertIs(PaintExecutionState.FINISHED, handle_before_cycle_head_check(self.context))
        self.assertTrue(self.context.result.expected_stop)
        self.assertFalse(self.context.result.completed)
        self.assertIsNone(self.context.result.failure)
        self.assertEqual(0, self.return_count)
        self.assertEqual(0, self.production.release_count)

    def test_prepared_pickup_entry_cannot_bypass_a_rejected_initial_check(self) -> None:
        self.run.initial_results = deque(
            [
                HeadCheckRejected(
                    HeadInspectionFailure(
                        HeadInspectionFailureCode.INSPECTION_POSITION_INVALID,
                        "Inspection pose is invalid",
                    )
                )
            ]
        )
        with patch(
            "src.robot_systems.paint.processes.paint.workflow.machine_factory.handle_pickup",
        ) as pickup:
            result = run_paint_cycle(self.context, initial_state=PaintExecutionState.PICKUP)
        self.assertIs(PaintFailureCode.HEAD_CHECK, result.result.failure.code)
        pickup.assert_not_called()
        self.assertEqual(0, self.production.release_count)

    def test_release_route_never_receives_an_inspection_endpoint(self) -> None:
        executor = StubExecutor()
        service = PaintProductionService(
            workpiece_preparation_service=None,
            capture_snapshot_service=None,
            path_preparation_service=None,
            path_executor=executor,
        )
        self.context.repeats_after_success = False
        result = service.release_dropoff(self.context)
        self.assertTrue(result.success)
        self.assertEqual([None], executor.targets)
        self.assertEqual(0, self.run.initial_calls)


if __name__ == "__main__":
    unittest.main()
