"""Behavior at the editor, hardware, and interrupted-motion boundaries."""
import unittest
from unittest.mock import MagicMock

from src.engine.robot.motion_sequence import OrderedMotionProfile, OrderedMotionType, OrderedPositionCommand
from src.robot_systems.paint.processes.paint.adapters.workpiece_editor import PaintWorkpiecePathExecutor
from src.robot_systems.paint.processes.paint.production.execution_control import PaintExecutionControl
from src.robot_systems.paint.hardware.vacuum_control import PaintVacuumControl
from src.robot_systems.paint.processes.paint.motion.executor import PaintMotionExecutor
from src.robot_systems.paint.processes.paint.motion.recovery import PaintMotionRecovery


class TestEditorExecutionAdapter(unittest.TestCase):
    def setUp(self):
        self.runtime = MagicMock()
        self.preview = MagicMock()
        self.adapter = PaintWorkpiecePathExecutor(self.runtime, preview=self.preview)

    def test_approved_action_runs_prepared_cycle_and_preserves_result(self):
        plan = object()
        self.runtime.execute_paint_process.return_value = (False, "Tray is full")
        self.assertEqual(
            (False, "Tray is full"),
            self.adapter.execute_process_action(plan, " PAINT_PROCESS "),
        )
        self.runtime.execute_paint_process.assert_called_once_with(plan)
        self.assertTrue(self.adapter.get_process_actions()[0].requires_projected_path_plot)

    def test_unsupported_action_and_direct_execution_do_not_start_cycle(self):
        plan = object()
        self.assertFalse(self.adapter.execute_process_action(plan, "unknown")[0])
        self.assertFalse(self.adapter.execute_process_paths(plan)[0])
        self.runtime.execute_paint_process.assert_not_called()

    def test_preview_aliases_reach_runtime_without_executing(self):
        workpiece, plan = {"id": "preview"}, object()
        self.runtime.prepare_workpiece_execution_plan.return_value = plan
        self.assertIs(plan, self.adapter.prepare_workpiece_preview(workpiece, skip_debug_plot=True))
        self.runtime.prepare_workpiece_execution_plan.assert_called_once_with(workpiece, skip_debug_plot=True)
        self.assertIs(self.preview.get_projected_pivot_paths.return_value, self.adapter.get_pivot_preview_paths(plan))
        self.assertIs(self.preview.get_pivot_motion_snapshots.return_value, self.adapter.get_pivot_motion_preview(plan))
        self.runtime.execute_paint_process.assert_not_called()


class TestMotionRecoveryComposition(unittest.TestCase):
    def setUp(self):
        self.robot = MagicMock()
        self.control = PaintExecutionControl()
        self.recovery = PaintMotionRecovery(self.robot, lambda: self.control)
        self.tool = 1
        self.motion = PaintMotionExecutor(
            self.robot, tool_provider=lambda: self.tool,
            user_provider=lambda: 2, recovery=self.recovery,
        )

    @staticmethod
    def command(x):
        return OrderedPositionCommand(
            label=str(x), motion_type=OrderedMotionType.LINEAR,
            position=(x, 0, 0, 0, 0, 0), profile=OrderedMotionProfile(10, 10),
        )

    def test_backend_segment_is_preserved_across_pause_and_resume(self):
        commands = [self.command(0), self.command(10), self.command(20)]
        self.robot.get_execution_status.return_value = {
            "ordered_motion_chain": {
                "active": True, "phase": "executing",
                "current_segment_index": 1, "current_segment_protected": False,
            },
        }

        def execute(**kwargs):
            if self.robot.execute_ordered_motion_chain.call_count == 1:
                self.control.request_pause()
                self.recovery.pause_current_execution()
                self.control.resume()
                return -1
            return 0

        self.robot.execute_ordered_motion_chain.side_effect = execute
        self.assertTrue(self.motion.move_ordered_pickup_sequence("transfer", commands))
        self.robot.stop_motion.assert_called_once_with()
        self.assertEqual(commands[1:], self.robot.execute_ordered_motion_chain.call_args.kwargs["segments"])
        self.robot.get_current_position_fresh.assert_not_called()
        self.assertIsNone(self.motion.last_motion_error)

    def test_protected_backend_segment_defers_robot_stop(self):
        self.robot.get_execution_status.return_value = {
            "ordered_motion_chain": {
                "active": True, "phase": "executing", "current_segment_protected": True,
            },
        }
        self.recovery.pause_current_execution()
        self.robot.stop_motion.assert_not_called()
        self.assertIsNone(self.recovery.consume_ordered_chain_resume_start_index())

    def test_motion_reads_latest_tool_and_user(self):
        self.tool = 7
        self.robot.move_linear.return_value = True
        self.assertTrue(self.motion.move_pickup_phase(
            "transfer", [0] * 6, velocity=10, acceleration=20,
            motion_type=OrderedMotionType.LINEAR,
        ))
        self.assertEqual(7, self.robot.move_linear.call_args.kwargs["tool"])
        self.assertEqual(2, self.robot.move_linear.call_args.kwargs["user"])


class TestVacuumControl(unittest.TestCase):
    def test_dry_run_bypasses_required_on_and_off_without_hardware_commands(self):
        pump = MagicMock()
        vacuum = PaintVacuumControl(
            pump,
            enabled_provider=lambda: True,
            dry_run_provider=lambda: True,
        )

        self.assertEqual((True, ""), vacuum.turn_vacuum_on(required=True))
        self.assertEqual((True, ""), vacuum.turn_vacuum_off(wait_for_blow_off=False))
        pump.turn_on.assert_not_called()
        pump.turn_off.assert_not_called()
        pump.turn_off_nonblocking.assert_not_called()

    def test_required_disabled_pump_fails_without_hardware_command(self):
        pump = MagicMock()
        vacuum = PaintVacuumControl(pump, enabled_provider=lambda: False)
        self.assertFalse(vacuum.turn_vacuum_on(required=True)[0])
        pump.turn_on.assert_not_called()

    def test_pump_exception_returns_failure(self):
        pump = MagicMock()
        pump.turn_on.side_effect = OSError("disconnected")
        vacuum = PaintVacuumControl(pump, enabled_provider=lambda: True)
        self.assertFalse(vacuum.turn_vacuum_on(required=True)[0])

    def test_nonblocking_release_uses_nonblocking_blowoff(self):
        pump = MagicMock()
        pump.turn_off_nonblocking.return_value = True
        vacuum = PaintVacuumControl(pump, enabled_provider=lambda: True)
        self.assertEqual((True, ""), vacuum.turn_vacuum_off(wait_for_blow_off=False))
        pump.turn_off_nonblocking.assert_called_once_with()
        pump.turn_off.assert_not_called()
