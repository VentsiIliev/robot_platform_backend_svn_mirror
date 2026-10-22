import unittest
from types import SimpleNamespace
from unittest.mock import Mock

from src.engine.common_settings_ids import CommonSettingsID
from src.engine.robot.configuration.robot_settings import SafetyLimits
from src.engine.robot.safety.safety_checker import (
    InvalidSettingsServiceError, SafetyChecker, SafetyLimitsNotFoundError,
)


class TestSafetyChecker(unittest.TestCase):
    def setUp(self):
        self.limits = SafetyLimits(z_min=0)
        self.settings = Mock()
        self.settings.get.return_value = SimpleNamespace(safety_limits=self.limits)
        self.checker = SafetyChecker(CommonSettingsID.ROBOT_CONFIG, self.settings)

    def test_missing_settings_rejected_at_construction(self):
        with self.assertRaises(InvalidSettingsServiceError):
            SafetyChecker(CommonSettingsID.ROBOT_CONFIG)

    def test_missing_limits_raises_for_both_queries(self):
        for config in (None, SimpleNamespace(), SimpleNamespace(safety_limits=None)):
            self.settings.get.return_value = config
            for method in (self.checker.get_violations, self.checker.is_within_safety_limits):
                with self.subTest(config=config, method=method.__name__):
                    with self.assertRaises(SafetyLimitsNotFoundError):
                        method([0, 0, 300])

    def test_repository_failure_propagates(self):
        self.settings.get.side_effect = OSError('settings unreadable')
        for method in (self.checker.get_violations, self.checker.is_within_safety_limits):
            with self.assertRaises(OSError):
                method([0, 0, 300])

    def test_empty_and_short_positions_blocked(self):
        for position in (None, [], [10, 20]):
            with self.assertRaises(ValueError):
                self.checker.is_within_safety_limits(position)

    def test_valid_and_boundary_positions_allowed(self):
        for position in ([100, -200, 400, 0, 0, 0], [-500, -500, 0], [500, 500, 800]):
            self.assertTrue(self.checker.is_within_safety_limits(position))
            self.assertEqual(self.checker.get_violations(position), [])

    def test_outside_each_axis_blocked(self):
        for position in ([-501, 0, 300], [501, 0, 300], [0, -501, 300],
                         [0, 501, 300], [0, 0, -1], [0, 0, 801]):
            self.assertFalse(self.checker.is_within_safety_limits(position))
            self.assertTrue(self.checker.get_violations(position))

    def test_invalid_bounds_rejected_on_every_check(self):
        for field in ('x_min', 'x_max', 'y_min', 'y_max', 'z_min', 'z_max'):
            original = getattr(self.limits, field)
            for value in (None, '500', True, float('nan'), float('inf'), -float('inf')):
                with self.subTest(field=field, value=value):
                    setattr(self.limits, field, value)
                    with self.assertRaises(ValueError):
                        self.checker.get_violations([0, 0, 300])
            setattr(self.limits, field, original)
        for axis in ('x', 'y', 'z'):
            original = getattr(self.limits, f'{axis}_min')
            setattr(self.limits, f'{axis}_min', getattr(self.limits, f'{axis}_max') + 1)
            with self.assertRaises(ValueError):
                self.checker.get_violations([0, 0, 300])
            setattr(self.limits, f'{axis}_min', original)

    def test_invalid_coordinates_rejected(self):
        for index in range(6):
            for value in (None, '1', True, float('nan'), float('inf')):
                position = [0, 0, 300, 0, 0, 0]
                position[index] = value
                with self.subTest(index=index, value=value):
                    with self.assertRaises(ValueError):
                        self.checker.get_violations(position)

    def test_generic_escape_never_authorized(self):
        for current, target in (([600, 0, 300], [500, 0, 300]), ([], [])):
            self.assertFalse(self.checker.is_escape_move(current, target))
