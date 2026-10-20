"""Offline native braking and measured feedback tests. Never sends robot commands."""
import importlib.util
import math
from pathlib import Path
import random
import subprocess
import tempfile
from types import SimpleNamespace
import unittest

ROOT = Path(__file__).resolve().parents[1]
import sys
sys.path.insert(0, str(ROOT/'scripts'))
from motion.execution.stop_strategies.base import StopPlan
from motion.execution.stop_strategies.ruckig_generator import CollisionBrake
from motion.execution.braking_state import BrakingState, BrakingStateTracker
NAMES = tuple(f'Joint_{i+1}' for i in range(6))


class TestMeasuredCollisionBrake(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temporary = tempfile.TemporaryDirectory()
        cls.library = Path(cls.temporary.name)/'libbrake.so'
        subprocess.run(['g++', '-std=c++17', '-O2', '-Wall', '-Wextra', '-Werror', '-shared', '-fPIC',
            '-I/opt/ros/jazzy/include', str(ROOT/'src_cpp/stop_strategies/measured_ruckig.cpp'),
            '-L/opt/ros/jazzy/lib/x86_64-linux-gnu', '-Wl,-rpath,/opt/ros/jazzy/lib/x86_64-linux-gnu',
            '-lruckig', '-o', str(cls.library)], check=True, timeout=60)

    @classmethod
    def tearDownClass(cls):
        cls.temporary.cleanup()

    def setUp(self):
        self.brake = CollisionBrake(self.library, NAMES,
            dict(max_velocity=[3.0]*6, max_acceleration=[6.0]*6, max_jerk=[30.0]*6),
            [-6.0]*6, [6.0]*6)

    def state(self, v=(.313,.668,-.354,-1.018,0,.311), a=(0.0,)*6, q=(0.0,)*6):
        return BrakingState(NAMES, tuple(q), tuple(v), tuple(a), 100.0, 0.0)

    def generate(self, state=None, **kwargs):
        policy = dict(max_age_s=.05, max_duration_s=.6, max_travel_rad=.35,
                      sample_period_s=.01, now=100.0)
        policy.update(kwargs)
        return self.brake.generate(state or self.state(), **policy)

    def assert_brake(self, state, rows):
        for offset, expected in [(1,state.position),(7,state.velocity),(13,state.acceleration)]:
            for actual, wanted in zip(rows[0][offset:offset+6], expected):
                self.assertAlmostEqual(actual, wanted, places=8)
        for x in rows[-1][7:19]: self.assertAlmostEqual(x, 0.0, places=8)
        self.assertLessEqual(rows[-1][0],.6)
        for left, right in zip(rows,rows[1:]):
            dt=right[0]-left[0]
            self.assertGreater(dt,0.0)
            for axis in range(6):
                a0,a1=left[13+axis],right[13+axis]
                jerk=(a1-a0)/dt
                self.assertLessEqual(abs(jerk),30.00001)
                self.assertLessEqual(abs(a0),6.00001)
                self.assertLessEqual(abs(left[7+axis]),3.00001)
                self.assertLessEqual(abs(left[1+axis]-state.position[axis]),.350001)
                # With every phase boundary sampled, the ROS quintic spline
                # reduces to the exact cubic constant-jerk segment.
                self.assertAlmostEqual(right[7+axis],left[7+axis]+a0*dt+.5*jerk*dt*dt,places=7)
                self.assertAlmostEqual(right[1+axis],left[1+axis]+left[7+axis]*dt+.5*a0*dt*dt+jerk*dt**3/6,places=7)

    def test_logged_velocity_example_has_continuous_joint6_deceleration(self):
        state=self.state()
        rows=self.generate(state)
        self.assert_brake(state,rows)
        self.assertGreater(rows[-1][6], rows[0][6])

    def test_nonzero_acceleration_and_joint_position_do_not_snap_to_plan(self):
        state=self.state(a=(.5,-1,1,2,0,-.5),q=(-.8,-.05,1.84,-.21,1.57,-.48))
        self.assert_brake(state,self.generate(state))

    def test_both_motion_directions_and_mixed_states(self):
        randomizer=random.Random(42)
        for _ in range(100):
            state=self.state(v=[randomizer.uniform(-1,1) for _ in range(6)],
                             a=[randomizer.uniform(-1,1) for _ in range(6)])
            self.assert_brake(state,self.generate(state))

    def test_short_brake_keeps_exact_end_boundary_before_hold_extension(self):
        state = self.state(v=(.0001,)*6, a=(0.0,)*6)
        rows = self.generate(state)
        self.assert_brake(state, rows)
        self.assertEqual(rows[-1][0], .01)
        self.assertGreater(len(rows), 2)

    def test_zero_velocity_generates_stationary_hold(self):
        rows=self.generate(self.state(v=(0.0,)*6))
        self.assertTrue(all(abs(x)<1e-9 for row in rows for x in row[1:]))

    def test_stale_missing_and_mismatched_feedback_refused(self):
        with self.assertRaisesRegex(ValueError,'stale'): self.generate(now=100.1)
        with self.assertRaisesRegex(ValueError,'unavailable'):
            self.brake.generate(None,max_age_s=.05,max_duration_s=.6,max_travel_rad=.35,sample_period_s=.01)
        wrong=BrakingState(('wrong',)+NAMES[1:],(0.0,)*6,(0.0,)*6,(0.0,)*6,100,0)
        with self.assertRaisesRegex(ValueError,'names'):self.generate(wrong)

    def test_nonfinite_inputs_and_invalid_policy_refused(self):
        with self.assertRaisesRegex(ValueError,'invalid'):self.generate(self.state(v=(math.nan,)*6))
        for kwargs in [dict(max_duration_s=-1),dict(max_travel_rad=0),dict(sample_period_s=.00001)]:
            with self.assertRaises(ValueError):self.generate(**kwargs)

    def test_duration_travel_and_position_budgets_refused(self):
        with self.assertRaisesRegex(ValueError,'duration'):self.generate(max_duration_s=.1)
        with self.assertRaisesRegex(ValueError,'travel'):self.generate(max_travel_rad=.01)
        with self.assertRaisesRegex(ValueError,'position limit'):
            self.generate(self.state(v=(1.0,)*6,q=(5.99,)*6))

    def test_velocity_limits_enforced_even_in_velocity_control_interface(self):
        with self.assertRaisesRegex(ValueError,'velocity limit'):
            self.generate(self.state(v=(4.0,)*6),max_duration_s=2.0,max_travel_rad=3.0)

    def test_feedback_joint_order_is_respected(self):
        state=self.state()
        reverse=BrakingState(tuple(reversed(NAMES)),tuple(reversed(state.position)),
            tuple(reversed(state.velocity)),tuple(reversed(state.acceleration)),100,0)
        self.assertEqual(self.generate(state),self.generate(reverse))


class TestBrakingStateTracker(unittest.TestCase):
    def sample(self, velocity, stamp):
        return SimpleNamespace(name=NAMES,position=[0.0]*6,velocity=list(velocity),
            header=SimpleNamespace(stamp=SimpleNamespace(sec=int(stamp),nanosec=round((stamp-int(stamp))*1e9))))

    def test_complete_samples_estimate_filtered_acceleration(self):
        tracker=BrakingStateTracker()
        tracker.observe(self.sample([0.0]*6,1),now=100)
        self.assertIsNone(tracker.state)
        tracker.observe(self.sample([.01]*6,1.01),now=100.01)
        self.assertEqual(tracker.state.velocity,(.01,)*6)
        self.assertTrue(all(0<a<1 for a in tracker.state.acceleration))

    def test_missing_velocity_or_nonfinite_state_invalidates_cached_feedback(self):
        tracker=BrakingStateTracker()
        tracker.observe(self.sample([0.0]*6,1),now=100)
        tracker.observe(self.sample([0.0]*6,1.01),now=100.01)
        self.assertIsNotNone(tracker.state)
        tracker.observe(self.sample([],1.02),now=100.02)
        self.assertIsNone(tracker.state)
        tracker.observe(self.sample([math.nan]*6,1.03),now=100.03)
        self.assertIsNone(tracker.state)

    def test_duplicate_backward_and_long_sample_gaps_need_new_acceleration_window(self):
        for stamp in (1.0,.99,1.2):
            tracker=BrakingStateTracker()
            tracker.observe(self.sample([0.0]*6,1),now=100)
            tracker.observe(self.sample([1.0]*6,stamp),now=100.01)
            self.assertIsNone(tracker.state)




class TestCollisionBrakeDispatch(unittest.TestCase):
    def setUp(self):
        import ast
        from copy import deepcopy
        from unittest.mock import MagicMock
        self.Mock=MagicMock
        path=ROOT/'scripts/motion/execution/trajectory_executor.py'
        tree=ast.parse(path.read_text())
        cls=next(n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=='TrajectoryExecutor')
        methods=[n for n in cls.body if isinstance(n,ast.FunctionDef) and n.name in
                 {'_send_stop_trajectory','_on_controller_goal_response'}]
        class Goal:
            def __init__(self):self.goal_time_tolerance=SimpleNamespace()
        self.ns=dict(math=math, config=SimpleNamespace(EXECUTOR_COLLISION_STOP_STRATEGY='measured_ruckig',
            EXECUTOR_COLLISION_STOP_HOLD_JOINT_NAMES=[],EXECUTOR_PATH_STOP_HOLD_JOINT_NAMES=['Joint_6'],
            EXECUTOR_GOAL_POS_TOL_RAD=.02),deepcopy=deepcopy,
            time=SimpleNamespace(monotonic=lambda:100.0,monotonic_ns=lambda:100000000000,perf_counter=lambda:100.0),
            FollowJointTrajectory=SimpleNamespace(Goal=Goal),JointTolerance=SimpleNamespace)
        exec(compile(ast.fix_missing_locations(ast.Module(body=methods,type_ignores=[])),str(path),'exec'),self.ns)
        trajectory=SimpleNamespace(joint_names=list(NAMES),points=[SimpleNamespace(time_from_start=.37)])
        self.executor=SimpleNamespace(
            _collision_stop_strategy=SimpleNamespace(name='measured_ruckig', build=MagicMock(
                return_value=(StopPlan(trajectory, server_timeout_s=0.0, dispatch_deadline=100.01,
                                       goal_velocity_tolerance=.02), 'generator=measured_ruckig'))),
            _operator_stop_strategy=SimpleNamespace(name='planned_path', build=MagicMock(
                return_value=(StopPlan(trajectory, held_joint_names=frozenset({'Joint_6'})), 'operator'))),
            _controller_client=SimpleNamespace(wait_for_server=MagicMock(return_value=True),
                                             send_goal_async=MagicMock(return_value=MagicMock())),
            _controller_name='manipulator_controller', _node=SimpleNamespace(get_logger=lambda:MagicMock()),
            _next_goal_sequence=lambda:42,_duration_to_sec=float,
            _cancel_unwind_diagnostic_timers=MagicMock(),_cancel_active_drive_monitor=MagicMock(),
            _on_controller_goal_response=MagicMock(),_motion=SimpleNamespace(active_execute_send_future=None))

    def test_measured_stop_bypasses_planned_path_and_does_not_wait_for_server(self):
        self.assertTrue(self.ns['_send_stop_trajectory'](self.executor,stop_kind='collision'))
        self.executor._operator_stop_strategy.build.assert_not_called()
        self.executor._controller_client.wait_for_server.assert_called_once_with(timeout_sec=0.0)
        self.assertEqual(self.executor._active_stop_kind,'collision')
        goal = self.executor._controller_client.send_goal_async.call_args.args[0]
        self.assertTrue(all(t.velocity == .02 for t in goal.goal_tolerance))

    def test_operator_keeps_original_builder(self):
        self.assertTrue(self.ns['_send_stop_trajectory'](self.executor,stop_kind='operator'))
        self.executor._collision_stop_strategy.build.assert_not_called()
        goal = self.executor._controller_client.send_goal_async.call_args.args[0]
        self.assertTrue(all(t.velocity == 0.0 for t in goal.goal_tolerance))
        self.executor._operator_stop_strategy.build.assert_called_once_with(self.executor, stop_duration_s=None)

    def test_stale_generation_and_failed_submission_do_not_leave_stop_active(self):
        from dataclasses import replace
        plan, detail = self.executor._collision_stop_strategy.build.return_value
        self.executor._collision_stop_strategy.build.return_value = (replace(plan, dispatch_deadline=99.9), detail)
        self.assertFalse(self.ns['_send_stop_trajectory'](self.executor,stop_kind='collision'))
        self.executor._controller_client.send_goal_async.assert_not_called()
        self.executor._collision_stop_strategy.build.return_value = (plan, detail)
        self.executor._controller_client.send_goal_async.side_effect=RuntimeError('unavailable')
        self.assertFalse(self.ns['_send_stop_trajectory'](self.executor,stop_kind='collision'))
        self.assertFalse(self.executor._active_goal_is_stop)

    def test_refused_measurement_does_not_fall_back_to_planned_collision_stop(self):
        self.executor._collision_stop_strategy.build.return_value=(None,'stale measurement')
        self.assertFalse(self.ns['_send_stop_trajectory'](self.executor,stop_kind='collision'))
        self.executor._operator_stop_strategy.build.assert_not_called()
        self.executor._controller_client.send_goal_async.assert_not_called()

    def test_strategy_exception_or_unavailable_strategy_refuses_submission(self):
        self.executor._collision_stop_strategy.build.side_effect = RuntimeError('generation failed')
        self.assertFalse(self.ns['_send_stop_trajectory'](self.executor, stop_kind='collision'))
        self.executor._operator_stop_strategy.build.assert_not_called()
        self.executor._collision_stop_strategy = None
        self.executor._collision_stop_strategy_error = 'unknown strategy'
        self.assertFalse(self.ns['_send_stop_trajectory'](self.executor, stop_kind='collision'))
        self.executor._controller_client.send_goal_async.assert_not_called()

    def test_rejected_collision_goal_cancels_previous_motion(self):
        self.executor._active_goal_sequence = 42
        self.executor._active_goal_is_stop = True
        self.executor._active_stop_kind = 'collision'
        previous = self.Mock()
        self.executor._motion.active_controller_goal = previous
        self.executor._fail_current_before_controller_goal = self.Mock()
        self.ns['config'].MOTION_ERROR_CONTROLLER_EXECUTION_FAILED = -2
        future = self.Mock()
        future.result.return_value = SimpleNamespace(accepted=False)
        self.ns['_on_controller_goal_response'](self.executor, future, goal_sequence=42)
        previous.cancel_goal_async.assert_called_once()
        self.assertFalse(self.executor._active_goal_is_stop)
        self.executor._fail_current_before_controller_goal.assert_called_once()

    def test_stale_goal_response_does_not_clear_pending_collision_stop(self):
        self.executor._active_goal_sequence=42
        pending=object()
        self.executor._motion.active_execute_send_future=pending
        self.ns['_on_controller_goal_response'](self.executor,self.Mock(),goal_sequence=41)
        self.assertIs(self.executor._motion.active_execute_send_future,pending)


if __name__ == '__main__':
    unittest.main()
