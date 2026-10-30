"""Accepted starts own one inspection run; modes and settings stay explicit."""

import unittest
from dataclasses import replace
from unittest.mock import MagicMock, patch

from src.robot_systems.paint.contracts.paint_head_check.interfaces import (
    IPaintHeadCheckRun,
    IPaintHeadCheckRunFactory,
)
from src.robot_systems.paint.contracts.paint_head_check.models import HeadCheckOperatingMode
from src.robot_systems.paint.processes.paint.configuration.models import PaintProcessConfig
from src.robot_systems.paint.processes.paint.production.cycle_runner import PaintCycleExecution
from src.robot_systems.paint.processes.paint.production.service import PaintProductionService
from src.robot_systems.paint.processes.paint.results import (
    PaintFailureCode,
    PaintOperationResult,
    PaintOutcome,
)


class HeadCheckStartTests(unittest.TestCase):
    def setUp(self) -> None:
        self.config = PaintProcessConfig()
        self.config = replace(
            self.config,
            run_while_workpiece_found=False,
            magazine_load=replace(self.config.magazine_load, enabled=False),
            head_check=replace(self.config.head_check, enabled=True),
        )
        self.factory = MagicMock(spec=IPaintHeadCheckRunFactory)
        self.settings = MagicMock()
        self.settings.get_snapshot.side_effect = self.snapshot
        self.service = PaintProductionService(
            workpiece_preparation_service=None,
            capture_snapshot_service=None,
            path_preparation_service=None,
            path_executor=MagicMock(),
            paint_process_config_service=self.settings,
            head_check_run_factory=self.factory,
            dry_run_snapshot_source=MagicMock(),
        )
        self.context_runs = []
        self.service.run_cycle_result = MagicMock(side_effect=self.cycle)
        self.service._move_to_calibration_before_manual_cycle = MagicMock(
            return_value=PaintOperationResult(PaintOutcome.COMPLETED, "At calibration"),
        )

    def snapshot(self) -> PaintProcessConfig:
        return self.config

    def cycle(self, *args: object, **kwargs: object) -> PaintOperationResult:
        self.context_runs.append(self.service._head_check_run)
        return PaintOperationResult(PaintOutcome.COMPLETED, "Completed")

    def test_each_start_creates_one_run_from_its_settings_snapshot(self) -> None:
        first_run, second_run = MagicMock(spec=IPaintHeadCheckRun), MagicMock(spec=IPaintHeadCheckRun)
        self.factory.create_run.side_effect = [first_run, second_run]
        self.service.run_once_result()
        original = self.config.head_check
        self.config = replace(self.config, head_check=replace(original, timeout_seconds=2.5))
        self.service.run_once_result()
        self.assertEqual([first_run, second_run], self.context_runs)
        self.assertEqual(2, self.factory.create_run.call_count)
        first, second = self.factory.create_run.call_args_list
        self.assertIs(first.args[0], original)
        self.assertEqual(1.0, first.args[0].timeout_seconds)
        self.assertEqual(2.5, second.args[0].timeout_seconds)
        first_run.close.assert_called_once_with()
        second_run.close.assert_called_once_with()
        self.assertIsNone(self.service._head_check_run)

    def test_workflow_exception_releases_the_run_snapshot(self) -> None:
        run = MagicMock(spec=IPaintHeadCheckRun)
        self.factory.create_run.return_value = run
        self.service.run_cycle_result.side_effect = RuntimeError("Workflow failed")
        with self.assertRaisesRegex(RuntimeError, "Workflow failed"):
            self.service.run_once_result()
        run.close.assert_called_once_with()
        self.assertIsNone(self.service._head_check_run)

    def test_early_dry_run_configuration_failure_releases_the_run_snapshot(self) -> None:
        run = MagicMock(spec=IPaintHeadCheckRun)
        self.factory.create_run.return_value = run
        self.config = replace(self.config, enable_dry_run_mode=True)
        self.service._dry_run_snapshot_source = None
        self.assertFalse(self.service.run_once_result().completed)
        run.close.assert_called_once_with()
        self.service.run_cycle_result.assert_not_called()

    def test_disabled_start_does_not_require_or_create_inspection_service(self) -> None:
        self.config = replace(
            self.config, head_check=replace(self.config.head_check, enabled=False)
        )
        self.assertTrue(self.service.run_once_result().completed)
        self.factory.create_run.assert_not_called()
        self.assertEqual([None], self.context_runs)

    def test_pickup_only_bypasses_checks_including_adjustment_and_dry_run(self) -> None:
        self.config = replace(
            self.config, stop_after_calibration_pickup=True, enable_dry_run_mode=True
        )
        self.assertTrue(self.service.run_once_result(adjustment_session=object()).completed)
        self.factory.create_run.assert_not_called()
        self.assertEqual([None], self.context_runs)

    def test_dry_run_and_adjustment_select_inspection_modes(self) -> None:
        self.config = replace(self.config, enable_dry_run_mode=True)
        self.service.run_once_result()
        self.assertIs(HeadCheckOperatingMode.DRY_RUN, self.factory.create_run.call_args.args[1])
        self.service.run_once_result(adjustment_session=object())
        self.assertIs(HeadCheckOperatingMode.ADJUSTMENT, self.factory.create_run.call_args.args[1])

    def test_enabled_without_service_fails_before_workpiece_execution(self) -> None:
        service = PaintProductionService(
            workpiece_preparation_service=None,
            capture_snapshot_service=None,
            path_preparation_service=None,
            path_executor=None,
            paint_process_config_service=self.settings,
        )
        result = service.run_once_result()
        self.assertIs(PaintFailureCode.HEAD_CHECK, result.failure.code)
        self.assertIn("inspection service is not configured", result.message)

    def test_cycle_completion_advances_schedule_but_magazine_staging_does_not(self) -> None:
        run = MagicMock(spec=IPaintHeadCheckRun)
        self.service._head_check_run = run
        with patch(
            "src.robot_systems.paint.processes.paint.production.service.run_paint_cycle",
            return_value=PaintCycleExecution(
                PaintOperationResult(PaintOutcome.COMPLETED, "Completed")
            ),
        ):
            for staging in (False, True):
                result = PaintProductionService.run_cycle_result(
                    self.service,
                    lambda: False,
                    process_config=self.config,
                    magazine_config=None,
                    cycle_index=1,
                    magazine_stage_only=staging,
                )
                self.assertTrue(result.completed)
        run.record_completed_cycle.assert_called_once_with()


if __name__ == "__main__":
    unittest.main()
