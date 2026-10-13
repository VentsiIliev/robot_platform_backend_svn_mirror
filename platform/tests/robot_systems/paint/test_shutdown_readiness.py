import unittest
from types import SimpleNamespace
from unittest.mock import Mock

from src.robot_systems.paint.paint_robot_system import PaintRobotSystem
from src.shared_contracts.events.process_events import ProcessState


class TestPaintShutdownReadiness(unittest.TestCase):
    def setUp(self):
        self.system = PaintRobotSystem()
        self.system._main_process = SimpleNamespace(
            state=ProcessState.IDLE,
            is_stopping=False,
        )
        self.system._calibration_process = SimpleNamespace(
            state=ProcessState.IDLE,
            is_stopping=False,
        )
        self.system._robot = Mock()
        self.system._robot.get_execution_status.return_value = {
            "is_executing": False,
            "queue_size": 0,
            "state": "idle",
        }

    def test_active_or_stopping_process_blocks_shutdown(self):
        for state, stopping in (
            (ProcessState.RUNNING, False),
            (ProcessState.PAUSED, False),
            (ProcessState.STOPPED, True),
        ):
            with self.subTest(state=state, stopping=stopping):
                self.system._main_process.state = state
                self.system._main_process.is_stopping = stopping
                self.assertEqual(
                    self.system.get_shutdown_block_reason(),
                    "process_active",
                )

    def test_robot_execution_or_queue_blocks_shutdown(self):
        for status in (
            {"is_executing": True},
            {"is_executing": False, "queue_size": 1},
            {"state": "stopping"},
            {"ordered_motion_chain": {"active": True}},
        ):
            with self.subTest(status=status):
                self.system._robot.get_execution_status.return_value = status
                self.assertEqual(
                    self.system.get_shutdown_block_reason(),
                    "robot_moving",
                )

    def test_idle_system_allows_shutdown(self):
        self.assertIsNone(self.system.get_shutdown_block_reason())

    def test_missing_execution_status_during_backend_startup_allows_shutdown(self):
        self.system._robot.get_execution_status.return_value = None
        self.assertIsNone(self.system.get_shutdown_block_reason())
