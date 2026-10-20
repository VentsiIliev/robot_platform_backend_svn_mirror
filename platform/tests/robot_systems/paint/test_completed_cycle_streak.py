import unittest
from unittest.mock import MagicMock, patch

from src.robot_systems.paint.applications.dashboard.service.paint_dashboard_service import PaintDashboardService
from src.robot_systems.paint.processes.paint.configuration.models import PaintProcessConfig
from src.robot_systems.paint.processes.paint.paint_process import PaintProcess
from src.robot_systems.paint.processes.paint.production.cycle_runner import PaintCycleExecution
from src.robot_systems.paint.processes.paint.production.service import PaintProductionService
from src.robot_systems.paint.processes.paint.results import PaintFailureCode, PaintOperationResult, PaintOutcome


class TestCompletedCycleStreak(unittest.TestCase):
    def test_real_terminal_handler_counts_success_despite_internal_stop_event(self):
        from src.robot_systems.paint.processes.paint.workflow.state import PaintExecutionState
        from src.robot_systems.paint.processes.paint.workflow.machine_factory import PaintExecutionMachineFactory

        production = PaintProductionService(
            workpiece_preparation_service=MagicMock(),
            capture_snapshot_service=MagicMock(),
            path_preparation_service=MagicMock(),
            path_executor=MagicMock(),
        )
        config = PaintProcessConfig(enable_dry_run_mode=True)
        build = PaintExecutionMachineFactory.build

        def build_completed_machine(factory, context, **kwargs):
            context.set_outcome(PaintOperationResult(PaintOutcome.COMPLETED, "Paint completed"))
            return build(factory, context, **kwargs)

        for index in (1, 2):
            with patch.object(PaintExecutionMachineFactory, "build", build_completed_machine):
                result = production.run_cycle_result(
                    lambda: False, process_config=config, magazine_config=None,
                    cycle_index=index, initial_state=PaintExecutionState.COMPLETED,
                )
            self.assertTrue(result.completed)
            self.assertTrue(production._last_execution_context.stop_event.is_set())
            self.assertEqual(production.consecutive_completed_cycles, index)

        production._paint_control.request_stop()
        with patch.object(PaintExecutionMachineFactory, "build", build_completed_machine):
            production.run_cycle_result(
                lambda: False, process_config=config, magazine_config=None,
                cycle_index=3, initial_state=PaintExecutionState.COMPLETED,
            )
        self.assertEqual(production.consecutive_completed_cycles, 2)

    def test_full_cycles_count_transfers_and_stops_do_not_and_failure_resets(self):
        production = PaintProductionService(
            workpiece_preparation_service=MagicMock(),
            capture_snapshot_service=MagicMock(),
            path_preparation_service=MagicMock(),
            path_executor=MagicMock(),
        )
        config = PaintProcessConfig(enable_dry_run_mode=True)
        completed = PaintOperationResult(PaintOutcome.COMPLETED, "Completed")
        failed = PaintOperationResult.failed(PaintFailureCode.MOTION, "pickup", "Failed")
        runner_path = "src.robot_systems.paint.processes.paint.production.service.run_paint_cycle"

        def run(result, **kwargs):
            with patch(runner_path, return_value=PaintCycleExecution(result)):
                production.run_cycle_result(
                    lambda: False, process_config=config, magazine_config=None,
                    cycle_index=1, **kwargs,
                )

        self.assertEqual(production.consecutive_completed_cycles, 0)
        run(completed)
        run(completed)
        self.assertEqual(production.consecutive_completed_cycles, 2)
        run(completed, magazine_stage_only=True)
        run(PaintOperationResult(PaintOutcome.NO_WORKPIECE, "Empty"))
        run(PaintOperationResult(PaintOutcome.CANCELLED, "Stopped"))
        self.assertEqual(production.consecutive_completed_cycles, 2)
        run(failed)
        self.assertEqual(production.consecutive_completed_cycles, 0)
        run(completed)
        process = PaintProcess(production, MagicMock())
        dashboard = PaintDashboardService(process)
        self.assertEqual(dashboard.load_state().consecutive_completed_cycles, 1)
        with patch.object(process, "_request_hardware_stop"):
            process.set_error("Collision")
        self.assertEqual(dashboard.load_state().consecutive_completed_cycles, 0)

    def test_exception_resets_streak(self):
        production = PaintProductionService(
            workpiece_preparation_service=MagicMock(),
            capture_snapshot_service=MagicMock(),
            path_preparation_service=MagicMock(),
            path_executor=MagicMock(),
        )
        config = PaintProcessConfig(enable_dry_run_mode=True)
        path = "src.robot_systems.paint.processes.paint.production.service.run_paint_cycle"
        with patch(path, return_value=PaintCycleExecution(
            PaintOperationResult(PaintOutcome.COMPLETED, "Completed"),
        )):
            production.run_cycle_result(lambda: False, process_config=config, magazine_config=None, cycle_index=1)
        with patch(path, side_effect=RuntimeError("Motion failed")):
            with self.assertRaises(RuntimeError):
                production.run_cycle_result(lambda: False, process_config=config, magazine_config=None, cycle_index=2)
        self.assertEqual(production.consecutive_completed_cycles, 0)
