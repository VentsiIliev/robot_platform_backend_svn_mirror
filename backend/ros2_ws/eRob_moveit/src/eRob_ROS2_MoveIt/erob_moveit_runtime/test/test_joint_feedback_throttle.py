"""Safety feedback must remain fresh while expensive runtime work is throttled."""
import ast
from pathlib import Path
import sys
from threading import Lock
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from status.robot_state_store import RobotStateStore
from configuration.runtime import LocalConfigurationRuntime


class TestJointFeedbackThrottle(unittest.TestCase):
    def setUp(self):
        path = ROOT / 'scripts/robot_controller.py'
        tree = ast.parse(path.read_text())
        controller = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == 'RobotController')
        callback = next(n for n in controller.body if isinstance(n, ast.FunctionDef) and n.name == 'joint_state_callback')
        self.clock = SimpleNamespace(monotonic=lambda: self.now)
        namespace = {'time': self.clock}
        exec(compile(ast.Module(body=[callback], type_ignores=[]), str(path), 'exec'), namespace)
        class Controller:
            current_joint_state = property(
                lambda self: self.state_store.get_current_joint_state(),
                lambda self, value: self.state_store.set_current_joint_state(value))
        Controller.joint_state_callback = namespace['joint_state_callback']
        self.node = Controller()
        self.node.state_store = RobotStateStore()
        self.node._runtime_joint_input_period = 0.1
        self.node._last_runtime_joint_input_ts = 0.0
        self.node.runtime_adapter = Mock()
        self.node.monitor = None
        self.node.lock = Lock()
        self.node.execution_lock = Lock()
        self.node.is_executing = False
        self.node.is_motion_active = lambda: False
        self.node.has_pending_motion = lambda: False
        self.names = tuple(f'Joint_{i+1}' for i in range(6))
        self.now = 0.0

    def sample(self, tick, velocity=None):
        self.now = 100.0 + tick * 0.01
        message = SimpleNamespace(
            name=self.names, position=[0.0]*6,
            velocity=[0.0]*6 if velocity is None else velocity,
            header=SimpleNamespace(stamp=SimpleNamespace(sec=1, nanosec=tick*10000000)))
        with patch('motion.execution.braking_state.time.monotonic', return_value=self.now):
            self.node.joint_state_callback(message)
        return message

    def test_full_rate_feedback_survives_ten_hz_runtime_throttle(self):
        for tick in range(26):
            message = self.sample(tick)
            self.assertIs(self.node.current_joint_state, message)
            if tick:
                state = self.node.state_store.get_braking_state()
                self.assertIsNotNone(state)
                self.assertEqual(state.received_at, self.now)
        self.assertLess(self.node.runtime_adapter.on_joint_state.call_count, 5)
        runtime = LocalConfigurationRuntime(
            SimpleNamespace(JOINT_NAMES=self.names), lambda: self.node,
            lambda: SimpleNamespace(cartesian_servo=None))
        runtime._apply_calibration = Mock()
        # Runtime uses the same monotonic time domain as the sampled feedback.
        with patch('configuration.runtime.time.monotonic', return_value=self.now):
            self.assertIsNone(runtime.apply('calibration', {}))
            runtime._apply_calibration.assert_called_once()

    def test_throttled_samples_still_expose_motion_and_invalidate_missing_velocity(self):
        self.sample(0)
        self.sample(1)
        self.sample(2, [0.2]*6)
        self.assertEqual(self.node.state_store.get_braking_state().velocity, (0.2,)*6)
        self.sample(3, [])
        self.assertIsNone(self.node.state_store.get_braking_state())
        self.assertEqual(self.node.runtime_adapter.on_joint_state.call_count, 1)


if __name__ == '__main__':
    unittest.main()
