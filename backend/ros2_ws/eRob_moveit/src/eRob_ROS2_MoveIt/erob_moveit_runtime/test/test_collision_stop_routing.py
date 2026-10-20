"""Separate operator and collision stopping without requiring a ROS process."""
import ast
import math
from pathlib import Path
import threading
from types import SimpleNamespace
import unittest
from unittest.mock import MagicMock

import yaml
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'scripts'))
from motion.execution.stop_strategies.base import StopPlan

ROOT = Path(__file__).resolve().parents[2]


def extract(path, class_name, names, namespace):
    tree = ast.parse(path.read_text())
    cls = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == class_name)
    methods = [n for n in cls.body if isinstance(n, ast.FunctionDef) and n.name in names]
    exec(compile(ast.fix_missing_locations(ast.Module(body=methods, type_ignores=[])), str(path), 'exec'), namespace)
    return namespace


class TestCollisionStopRouting(unittest.TestCase):
    def setUp(self):
        path = ROOT / 'erob_moveit_runtime/scripts/motion/execution/motion_coordinator.py'
        self.methods = extract(path, 'MotionCoordinator', {'stop_motion', 'collision_stop', '_stop_motion'}, {})
        self.executor = SimpleNamespace(
            send_path_stop_trajectory=MagicMock(return_value=True),
            send_collision_stop_trajectory=MagicMock(return_value=True))
        self.queue = SimpleNamespace(clear=MagicMock(return_value=2))
        self.coordinator = SimpleNamespace(
            _node=SimpleNamespace(trajectory_executor=self.executor, get_logger=lambda: MagicMock()),
            _motion_queue=self.queue, active_execute_send_future=None,
            active_controller_goal=MagicMock(), lock=threading.Lock(), plan_generation=0,
            last_move_result=0)
        self.coordinator._stop_motion = lambda **kwargs: self.methods['_stop_motion'](self.coordinator, **kwargs)

    def test_operator_stop_uses_original_sender(self):
        result = self.methods['stop_motion'](self.coordinator)
        self.assertEqual(result['state'], 'STOPPING')
        self.executor.send_path_stop_trajectory.assert_called_once_with()
        self.executor.send_collision_stop_trajectory.assert_not_called()

    def test_collision_stop_uses_dedicated_sender_and_clears_queue(self):
        result = self.methods['collision_stop'](self.coordinator)
        self.assertEqual(result['queue_cleared'], 2)
        self.executor.send_collision_stop_trajectory.assert_called_once_with()
        self.executor.send_path_stop_trajectory.assert_not_called()

    def test_later_process_stop_does_not_overwrite_active_collision_stop(self):
        self.executor._active_goal_is_stop = True
        self.executor._active_stop_kind = 'collision'
        pending = MagicMock()
        self.coordinator.active_execute_send_future = pending
        result = self.methods['stop_motion'](self.coordinator)
        self.assertEqual(result['stop_kind'], 'collision')
        pending.cancel.assert_not_called()
        self.coordinator.active_controller_goal.cancel_goal_async.assert_not_called()
        self.executor.send_path_stop_trajectory.assert_not_called()

    def test_collision_can_brake_when_execution_handle_is_missing(self):
        self.coordinator.active_controller_goal = None
        self.coordinator.is_executing = True
        result = self.methods['collision_stop'](self.coordinator)
        self.assertEqual(result['state'], 'STOPPING')
        self.executor.send_collision_stop_trajectory.assert_called_once()
        self.executor.send_path_stop_trajectory.assert_not_called()

    def test_collision_fallback_never_uses_operator_profile(self):
        self.executor.send_collision_stop_trajectory.return_value = False
        self.coordinator.is_executing = True
        self.coordinator.execution_lock = threading.Lock()
        self.queue.mark_current_complete = MagicMock()
        result = self.methods['collision_stop'](self.coordinator)
        self.assertTrue(result['success'])
        self.assertIsNone(self.coordinator.active_controller_goal)
        self.executor.send_path_stop_trajectory.assert_not_called()


class TestStopProfiles(unittest.TestCase):
    def test_joint6_hold_and_duration_are_independent(self):
        config = SimpleNamespace(**yaml.safe_load((ROOT / 'zeroerr/config/runtime_defaults.yaml').read_text()))
        self.assertEqual(config.EXECUTOR_PATH_STOP_HOLD_JOINT_NAMES, ['Joint_6', 'j6'])
        self.assertEqual(config.EXECUTOR_COLLISION_STOP_HOLD_JOINT_NAMES, [])
        config.EXECUTOR_PATH_STOP_DURATION_S = 0.6

        class Trajectory:
            def __init__(self):
                self.header = SimpleNamespace()

        ns = extract(ROOT / 'erob_moveit_runtime/scripts/motion/execution/stop_strategies/planned_path.py',
                     'PlannedPathStop', {'build'},
                     {'StopPlan': StopPlan, 'math': math, 'time': SimpleNamespace(monotonic=lambda: 0.0),
                      'JointTrajectory': Trajectory, 'JointTrajectoryPoint': SimpleNamespace})
        executor = SimpleNamespace(
            _last_sent_trajectory=SimpleNamespace(joint_names=[f'Joint_{i+1}' for i in range(6)],
                points=[SimpleNamespace(time_from_start=0.0), SimpleNamespace(time_from_start=1.0)]),
            _active_goal_started_monotonic=0.0,
            _get_latest_joint_state_in_trajectory_order=lambda _: [0.0]*6,
            _sample_joint_trajectory=lambda _, t: ([t]*6, [1.0]*6),
            _duration_to_sec=float, _sec_to_duration=float,
            _node=SimpleNamespace(get_clock=lambda: SimpleNamespace(now=lambda: SimpleNamespace(to_msg=lambda: None))))
        operator_plan, op_detail = ns['build'](SimpleNamespace(config=config, stop_kind='operator'), executor)
        collision_plan, col_detail = ns['build'](SimpleNamespace(config=config, stop_kind='collision'), executor)
        operator, collision = operator_plan.trajectory, collision_plan.trajectory
        self.assertIn("held_joints=['Joint_6']", op_detail)
        self.assertIn('held_joints=[]', col_detail)
        self.assertTrue(all(p.velocities[5] == 0.0 and p.positions[5] == 0.0 for p in operator.points))
        self.assertEqual(operator.points[-1].time_from_start, 0.6)
        self.assertEqual(collision.points[-1].time_from_start, 0.3)
        self.assertEqual(collision.points[0].velocities[5], 1.0)
        self.assertEqual(collision.points[-1].velocities[5], 0.0)
        self.assertGreater(collision.points[-1].positions[5], 0.0)


if __name__ == '__main__':
    unittest.main()
