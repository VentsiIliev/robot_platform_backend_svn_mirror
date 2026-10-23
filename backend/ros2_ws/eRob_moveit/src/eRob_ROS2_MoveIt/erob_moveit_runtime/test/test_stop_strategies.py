"""Strategy selection and trajectory/dispatch contract checks; no robot commands."""
from pathlib import Path
import sys
from types import SimpleNamespace
import unittest
from unittest.mock import MagicMock, patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'scripts'))
from builtin_interfaces.msg import Duration
from motion.execution.braking_state import BrakingState
from motion.execution import stop_strategies as strategies
from motion.execution.stop_strategies.measured_ruckig import MeasuredRuckigStop


class TestStrategySelection(unittest.TestCase):
    def test_named_planned_path_and_default_preserve_previous_behavior(self):
        for config in (SimpleNamespace(), SimpleNamespace(EXECUTOR_COLLISION_STOP_STRATEGY='planned_path')):
            strategy = strategies.create_collision_stop_strategy(config)
            self.assertIsInstance(strategy, strategies.PlannedPathStop)
            self.assertEqual(strategy.stop_kind, 'collision')

    def test_named_measured_strategy_preloads_generator(self):
        config = SimpleNamespace(EXECUTOR_COLLISION_STOP_STRATEGY='measured_ruckig')
        with patch('motion.execution.stop_strategies.measured_ruckig.CollisionBrake.from_config') as load:
            strategy = strategies.create_collision_stop_strategy(config)
        self.assertIsInstance(strategy, MeasuredRuckigStop)
        load.assert_called_once_with(config)
        self.assertIs(strategy.generator, load.return_value)

    def test_legacy_boolean_only_applies_when_named_setting_absent(self):
        for enabled, expected in ((True, 'measured_ruckig'), (False, 'planned_path')):
            config = SimpleNamespace(EXECUTOR_COLLISION_STOP_USE_MEASURED_STATE=enabled)
            self.assertEqual(strategies.collision_strategy_name(config), expected)
            config.EXECUTOR_COLLISION_STOP_STRATEGY = 'planned_path'
            self.assertEqual(strategies.collision_strategy_name(config), 'planned_path')

    def test_unknown_and_empty_names_refused_without_selecting_another_algorithm(self):
        for name in ('typo', ''):
            with self.assertRaisesRegex(ValueError, 'Unknown collision stop strategy'):
                strategies.create_collision_stop_strategy(SimpleNamespace(EXECUTOR_COLLISION_STOP_STRATEGY=name))

    def test_missing_measured_library_never_selects_planned_path(self):
        config = SimpleNamespace(EXECUTOR_COLLISION_STOP_STRATEGY='measured_ruckig')
        with patch('motion.execution.stop_strategies.measured_ruckig.CollisionBrake.from_config',
                   side_effect=RuntimeError('missing library')):
            with self.assertRaisesRegex(RuntimeError, 'missing library'):
                strategies.create_collision_stop_strategy(config)

    def test_registry_accepts_an_additional_implementation(self):
        implementation = MagicMock()
        config = SimpleNamespace(EXECUTOR_COLLISION_STOP_STRATEGY='additional')
        with patch.dict(strategies.STRATEGIES, additional=implementation):
            result = strategies.create_collision_stop_strategy(config)
        implementation.assert_called_once_with(config)
        self.assertIs(result, implementation.return_value)


class TestMeasuredStrategyContract(unittest.TestCase):
    def setUp(self):
        self.names = tuple(f'Joint_{i+1}' for i in range(6))
        self.state = BrakingState(self.names, (0.,)*6, (.1,)*6, (0.,)*6, 100., 10.)
        self.rows = [(0.,)+self.state.position+self.state.velocity+self.state.acceleration,
                     (.1,)+(.005,)*6+(0.,)*12]
        self.generator = SimpleNamespace(names=self.names, generate=MagicMock(return_value=self.rows))
        self.config = SimpleNamespace()
        with patch('motion.execution.stop_strategies.measured_ruckig.CollisionBrake.from_config',
                   return_value=self.generator):
            self.strategy = MeasuredRuckigStop(self.config)
        self.executor = SimpleNamespace(
            _node=SimpleNamespace(
                state_store=SimpleNamespace(get_braking_state=lambda: self.state),
                get_clock=lambda: SimpleNamespace(now=lambda: SimpleNamespace(nanoseconds=10010000000))),
            _sec_to_duration=lambda seconds: Duration(sec=int(seconds), nanosec=round((seconds-int(seconds))*1e9)))
        self.clock = patch('motion.execution.stop_strategies.measured_ruckig.time.monotonic', return_value=100.01)
        self.clock.start()
        self.addCleanup(self.clock.stop)

    def test_returns_measured_points_and_fresh_dispatch_requirements(self):
        plan, detail = self.strategy.build(self.executor)
        self.assertEqual(plan.trajectory.joint_names, list(self.names))
        self.assertEqual(list(plan.trajectory.points[0].velocities), list(self.state.velocity))
        self.assertEqual(list(plan.trajectory.points[-1].velocities), [0.]*6)
        self.assertEqual(plan.trajectory.header.stamp.sec, 0)
        self.assertEqual(plan.trajectory.header.frame_id, "zeroerr_command_brake_v1")
        self.assertIn("takeover=controller_command", detail)
        self.assertEqual(plan.held_joint_names, frozenset())
        self.assertEqual(plan.server_timeout_s, 0.)
        self.assertEqual(plan.goal_velocity_tolerance, .02)
        self.assertAlmostEqual(plan.dispatch_deadline, 100.05)
        self.assertIn('generator=measured_ruckig', detail)

    def test_stale_source_stamp_refuses_before_generation(self):
        self.executor._node.get_clock = lambda: SimpleNamespace(now=lambda: SimpleNamespace(nanoseconds=11000000000))
        plan, detail = self.strategy.build(self.executor)
        self.assertIsNone(plan)
        self.assertIn('timestamp', detail)
        self.generator.generate.assert_not_called()

    def test_feedback_expiring_during_generation_is_refused(self):
        with patch('motion.execution.stop_strategies.measured_ruckig.time.monotonic', return_value=100.1):
            plan, detail = self.strategy.build(self.executor)
        self.assertIsNone(plan)
        self.assertIn('aged out', detail)

    def test_generator_refusal_and_invalid_tolerance_are_propagated(self):
        self.generator.generate.side_effect = ValueError('travel budget exceeded')
        plan, detail = self.strategy.build(self.executor)
        self.assertIsNone(plan)
        self.assertIn('travel budget exceeded', detail)
        self.generator.generate.side_effect = None
        self.config.EXECUTOR_COLLISION_STOP_GOAL_VELOCITY_TOL_RAD_S = float('nan')
        plan, detail = self.strategy.build(self.executor)
        self.assertIsNone(plan)
        self.assertIn('standstill velocity tolerance', detail)

    def test_disabled_collision_brake_does_not_generate(self):
        self.config.EXECUTOR_COLLISION_STOP_ENABLED = False
        plan, detail = self.strategy.build(self.executor)
        self.assertIsNone(plan)
        self.generator.generate.assert_not_called()


if __name__ == '__main__':
    unittest.main()
