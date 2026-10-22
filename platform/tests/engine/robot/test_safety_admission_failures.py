"""Fault injection at every MotionService entry point using the platform checker."""
import unittest
from types import SimpleNamespace
from unittest.mock import Mock

from src.engine.common_settings_ids import CommonSettingsID
from src.engine.robot.configuration.robot_settings import SafetyLimits
from src.engine.robot.enums.axis import Direction, RobotAxis
from src.engine.robot.motion_sequence import MotionSequenceSegment
from src.engine.robot.safety.safety_checker import SafetyChecker
from src.engine.robot.services.motion_service import MotionService


class TestSafetyAdmissionFailures(unittest.TestCase):
    def make_service(self, fault):
        robot = Mock()
        robot.get_current_position.return_value = [0, 0, -10, 0, 0, 0]
        robot.get_current_position_fresh.return_value = [0, 0, -10, 0, 0, 0]
        settings = Mock()
        settings.get.return_value = SimpleNamespace(safety_limits=SafetyLimits(z_min=0))
        if fault == 'repository':
            settings.get.side_effect = OSError('read failed')
        elif fault == 'missing':
            settings.get.return_value = None
        elif fault == 'malformed':
            settings.get.return_value.safety_limits.x_min = 'bad'
        elif fault == 'infinite':
            settings.get.return_value.safety_limits.x_max = float('inf')
        elif fault == 'reversed':
            settings.get.return_value.safety_limits.x_min = 501
        checker = SafetyChecker(CommonSettingsID.ROBOT_CONFIG, settings)
        if fault == 'unexpected':
            checker.get_violations = Mock(side_effect=RuntimeError('unexpected checker error'))
        elif fault == 'position_read':
            robot.get_current_position_fresh.side_effect = OSError('position read failed')
            robot.get_current_position.side_effect = OSError('position read failed')
        return robot, settings, MotionService(robot, checker)

    def invoke(self, service, operation):
        position = [0, 0, 300, 0, 0, 0]
        if operation in ('move_sequence', 'move_custom_sequence'):
            return getattr(service, operation)([MotionSequenceSegment(position, 10, 10)], 0, 0)
        if operation == 'start_jog':
            return service.start_jog(RobotAxis.Z, Direction.PLUS, 1)
        if operation in ('move_fast_linear', 'fast_recovery'):
            return service.move_fast_linear(position=position, allow_subzero_retract=operation == 'fast_recovery')
        if operation == 'linear_recovery':
            return service.move_linear(position, 0, 0, 10, 10, allow_subzero_step_recovery=True)
        if operation == 'linear_bypass':
            return service.move_linear(position, 0, 0, 10, 10, bypass_safety_limits=True,
                                       allow_collision_recovery=True)
        return getattr(service, operation)(position, 0, 0, 10, 10)

    def test_every_checked_command_rejects_failures_without_driver_submission(self):
        for fault in ('repository', 'missing', 'malformed', 'infinite', 'reversed',
                      'unexpected', 'position_read'):
            for operation in ('move_ptp', 'move_linear', 'move_sequence', 'move_custom_sequence',
                              'start_jog', 'move_fast_linear', 'fast_recovery',
                              'linear_recovery', 'linear_bypass'):
                with self.subTest(fault=fault, operation=operation):
                    robot, _, service = self.make_service(fault)
                    result = self.invoke(service, operation)
                    if operation in ('move_fast_linear', 'fast_recovery'):
                        self.assertFalse(result['success'])
                        self.assertFalse(result['accepted'])
                        self.assertFalse(service._servo_floor_stop.is_set())
                        if fault != 'position_read':
                            self.assertEqual(result['error'], 'platform_safety_unavailable')
                    elif operation == 'start_jog':
                        self.assertEqual(result, -1)
                    else:
                        self.assertIs(result, False)
                    for method in ('move_linear', 'move_ptp', 'start_jog', 'move_fast_linear',
                                   'execute_motion_sequence', 'execute_custom_motion_sequence',
                                   'set_active_tool'):
                        getattr(robot, method).assert_not_called()

    def test_later_segment_failure_rejects_whole_sequence(self):
        for method in ('move_sequence', 'move_custom_sequence'):
            robot, settings, service = self.make_service(None)
            robot.get_current_position_fresh.return_value = [0, 0, 300, 0, 0, 0]
            config = settings.get.return_value
            settings.get.side_effect = [config, OSError('second check failed')]
            segments = [MotionSequenceSegment([0, 0, z, 0, 0, 0], 10, 10) for z in (300, 400)]
            self.assertFalse(getattr(service, method)(segments, 0, 0))
            robot.set_active_tool.assert_not_called()
            robot.execute_motion_sequence.assert_not_called()
            robot.execute_custom_motion_sequence.assert_not_called()

    def test_jog_without_current_position_rejected(self):
        robot, _, service = self.make_service(None)
        robot.get_current_position.return_value = []
        self.assertEqual(service.start_jog(RobotAxis.Z, Direction.PLUS, 1), -1)
        robot.start_jog.assert_not_called()

    def test_malformed_target_cannot_be_bypassed(self):
        for target in (None, [], [0, 0], [0, 0, float('nan')], [0, 0, '300']):
            with self.subTest(target=target):
                robot, _, service = self.make_service(None)
                self.assertFalse(service.move_linear(target, 0, 0, 10, 10, bypass_safety_limits=True))
                robot.move_linear.assert_not_called()

    def test_malformed_checker_result_cannot_be_bypassed(self):
        for result in (None, {}, '', [None]):
            with self.subTest(result=result):
                robot = Mock()
                checker = Mock()
                checker.get_violations.return_value = result
                service = MotionService(robot, checker)
                self.assertFalse(service.move_linear([0, 0, 300], 0, 0, 10, 10,
                                                     bypass_safety_limits=True))
                robot.move_linear.assert_not_called()
