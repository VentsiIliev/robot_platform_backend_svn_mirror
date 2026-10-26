"""Pilz optimizer forwarding, timing preservation and asynchronous failure guards."""
from concurrent.futures import Future
from pathlib import Path
from types import SimpleNamespace
from threading import RLock
import sys
import unittest
from unittest.mock import Mock, patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from builtin_interfaces.msg import Duration
from moveit_msgs.msg import RobotTrajectory
from trajectory_msgs.msg import JointTrajectory, JointTrajectoryPoint
from motion.planning import sequence
from motion.strategies import PilzMoveLinStrategy
from motion.execution.trajectory_optimizer import RuckigTrajectoryOptimizer
from motion.execution import trajectory_optimization


class PilzOptimizerTests(unittest.TestCase):
    def setUp(self):
        self.rc = SimpleNamespace(
            plan_generation=4, lock=RLock(), is_executing=True,
            get_logger=lambda: Mock(), trajectory_executor=Mock())
        self.trajectory = RobotTrajectory()
        self.trajectory.joint_trajectory.joint_names = ['Joint_1']
        for q, t in [(0., 0), (.1, 1), (.2, 2)]:
            self.trajectory.joint_trajectory.points.append(JointTrajectoryPoint(
                positions=[q], velocities=[0.], accelerations=[0.], time_from_start=Duration(sec=t)))
        self.future = Future()
        self.future.set_result(SimpleNamespace(response=SimpleNamespace(
            error_code=SimpleNamespace(val=1), planned_trajectories=[self.trajectory])))

    def test_strategy_forwards_explicit_optimizer_and_group(self):
        strategy = PilzMoveLinStrategy(1, 2, 3, 0, 0, 0, .2, .6,
                                      planning_group='manipulator_fast', trajectory_optimizer='RUCKIG')
        with patch.object(sequence, 'send_motion_sequence', return_value=0) as send:
            self.assertEqual(strategy.execute(self.rc), 0)
        self.assertEqual(send.call_args.kwargs['trajectory_optimizer'], 'RUCKIG')
        self.assertEqual(send.call_args.kwargs['planning_group'], 'manipulator_fast')

    def test_unspecified_optimizer_keeps_pilz_timing(self):
        with patch.object(sequence, '_send_trajectory_to_controller') as send:
            sequence._sequence_response(self.rc, self.future, 4, 0)
        points = send.call_args.args[1].points
        self.assertEqual([p.time_from_start.sec for p in points], [0, 1, 2])

    def test_explicit_optimizer_finishes_before_dispatch_and_preserves_input(self):
        optimizer = Mock()
        with patch.object(sequence, '_send_trajectory_to_controller') as send:
            sequence._sequence_response(self.rc, self.future, 4, 0, optimizer, (.2, .6))
            send.assert_not_called()
            args = optimizer.optimize.call_args.args
            self.assertEqual(args[2:4], (.2, .6))
            self.assertEqual([p.positions[0] for p in args[1].joint_trajectory.points], [0., .1, .2])
            args[-1](args[1])
            send.assert_called_once()

    def test_stop_during_optimization_discards_late_result(self):
        optimizer = Mock()
        with patch.object(sequence, '_send_trajectory_to_controller') as send:
            sequence._sequence_response(self.rc, self.future, 4, 0, optimizer)
            args = optimizer.optimize.call_args.args
            self.rc.plan_generation = 5
            args[-1](args[1])
            send.assert_not_called()

    def test_optimizer_failure_never_dispatches_original_pilz_trajectory(self):
        optimizer = Mock()
        with patch.object(sequence, '_send_trajectory_to_controller') as send:
            sequence._sequence_response(self.rc, self.future, 4, 0, optimizer)
            optimizer.optimize.call_args.args[-1](None)
            send.assert_not_called()
        self.assertEqual(self.rc.last_move_result, -7)
        self.assertFalse(self.rc.is_executing)
        self.assertIn('not dispatched', self.rc.last_motion_error)

    def test_invalid_optimizer_rejected_before_planning(self):
        self.rc.wait_for_motion_sequence_service = Mock()
        result = sequence.send_motion_sequence(self.rc, [{'vel': 20, 'acc': 60}], trajectory_optimizer='typo')
        self.assertEqual(result, -1)
        self.rc.wait_for_motion_sequence_service.assert_not_called()

    def test_ruckig_preserves_timing_and_requires_real_ruckig_result(self):
        apply = Mock()
        optimizer = RuckigTrajectoryOptimizer(apply_fn=apply, preserve_timing=True, strict=True)
        optimizer.optimize(self.rc, self.trajectory, .2, .6, Mock())
        self.assertEqual(apply.call_args.kwargs, {'preserve_timing': True, 'strict': True})

    def test_preserve_mode_uses_separate_service_client(self):
        self.rc.ruckig_client = Mock()  # ordinary client must not receive Pilz smoothing
        client = Mock()
        client.wait_for_service.return_value = True
        self.rc.create_client = Mock(return_value=client)
        trajectory_optimization.apply_ruckig_service(
            self.rc, self.trajectory, .2, .6, Mock(), preserve_timing=True)
        self.assertEqual(self.rc.create_client.call_args.args[1], '/smooth_ruckig')
        self.rc.ruckig_client.call_async.assert_not_called()
        request = client.call_async.call_args.args[0]
        self.assertEqual(list(request.trajectory.points), list(self.trajectory.joint_trajectory.points))

    def test_missing_smoothing_service_fails_without_totg(self):
        client = Mock()
        client.wait_for_service.return_value = False
        self.rc.ruckig_smoothing_client = client
        done = Mock()
        with patch.object(trajectory_optimization, 'apply_ipp_totg') as fallback:
            trajectory_optimization.apply_ruckig_service(
                self.rc, self.trajectory, .2, .6, done, preserve_timing=True)
        fallback.assert_not_called()
        done.assert_called_once_with(None)

    def test_totg_fallback_response_is_rejected_in_preserve_mode(self):
        client = Mock()
        client.wait_for_service.return_value = True
        response = Future()
        response.set_result(SimpleNamespace(optimizer_applied='TOTG', fallback_used=True,
                                            trajectory=self.trajectory))
        client.call_async.return_value = response
        self.rc.ruckig_smoothing_client = client
        done = Mock()
        with patch.object(trajectory_optimization, 'apply_ipp_totg') as fallback:
            trajectory_optimization.apply_ruckig_service(
                self.rc, self.trajectory, .2, .6, done, preserve_timing=True)
        fallback.assert_not_called()
        done.assert_called_once_with(None)


if __name__ == '__main__':
    unittest.main()
