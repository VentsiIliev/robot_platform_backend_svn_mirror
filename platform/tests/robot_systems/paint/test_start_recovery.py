"""Start/restart must route tray positions before unwind and navigation."""
import unittest
from dataclasses import replace
from types import SimpleNamespace
from unittest.mock import Mock, patch

from src.engine.robot.motion_sequence import OrderedMotionType
from src.robot_systems.paint.contracts.next_cycle_target import NextCycleTarget
from src.robot_systems.paint.processes.paint.configuration.models import PaintDropoffConfig, PaintProcessConfig
from src.robot_systems.paint.processes.paint.start_recovery import (
    StartRecoveryService, StartRecoveryResult, StartRecoveryOutcome, StartRecoveryFailureCode,
)
from src.robot_systems.paint.processes.paint.start_recovery.errors import RecoveryMotionFailedError
from src.robot_systems.paint.processes.paint.start_recovery.contracts import StartRecoveryRequest
from src.robot_systems.paint.processes.paint.start_recovery.strategies import TrayReturnRecoveryStrategy
from src.robot_systems.paint.processes.paint.production.execution_control import PaintExecutionControl
from src.robot_systems.paint.processes.paint.workflow.context import PaintExecutionContext
from src.robot_systems.paint.processes.paint.workflow.state import PaintExecutionState
from src.robot_systems.paint.processes.paint.workflow.handlers.lifecycle.startup_handler import handle_starting


def config():
    return PaintDropoffConfig(
        strategy="plate_layout",
        plate_corners=[[0, 0, 0, 180, 0, 0], [100, 0, 0, 180, 0, 0],
                       [100, 200, 0, 180, 0, 0], [0, 200, 0, 180, 0, 0]],
        plate_robot_tool=1, plate_robot_user=1,
        plate_exit_gate_pose=[120, 200, 100, 180, 0, 0],
        plate_next_cycle_midpoint_enabled=True,
        plate_next_cycle_waypoints=[
            dict(position=[200, 200, 100, 180, 0, 0], vel_percent=40, acc_percent=30, motion_type="ptp", blendR=0),
            dict(position=[200, 0, 100, 180, 0, 0], vel_percent=40, acc_percent=30, motion_type="linear", blendR=0),
        ],
    )


def target():
    return NextCycleTarget("Magazine", (300, 0, 100, 180, 0, 0), 40, 30, OrderedMotionType.PTP)


class TestStartRecovery(unittest.TestCase):
    def setUp(self):
        self.read = Mock(return_value=[25, 50, 0, 180, 0, 360])
        self.execute = Mock(return_value=True)
        self.destination = Mock(return_value=target())
        self.service = StartRecoveryService(read_pose=self.read, execute_route=self.execute)

    def prepare(self, dropoff=None, **kwargs):
        return self.service.prepare(dropoff=dropoff or config(), target_provider=self.destination,
                                    should_stop=kwargs.get("should_stop", lambda: False),
                                    tool=kwargs.get("tool", 1), user=1)

    def test_tray_route_uses_clearance_gate_all_return_waypoints_and_magazine(self):
        self.assertEqual(StartRecoveryOutcome.RECOVERED, self.prepare().outcome)
        segments = self.execute.call_args.args[1]
        self.assertEqual([(25, 50, 50), (50, 100, 50), (120, 200, 100),
                          (200, 200, 100), (200, 0, 100), (300, 0, 100)],
                         [s.position[:3] for s in segments])
        self.assertEqual(OrderedMotionType.LINEAR, segments[0].motion_type)
        self.assertEqual(0, segments[0].profile.blend_radius)
        self.assertEqual(0, segments[-1].profile.blend_radius)
        self.assertTrue(all(s.position[5] == 360 for s in segments))

    def test_outside_tray_preserves_start_and_does_not_resolve_target(self):
        self.read.return_value = [101, 50, 0, 180, 0, 0]
        self.assertTrue(self.prepare().succeeded)
        self.execute.assert_not_called()
        self.destination.assert_not_called()

    def test_edges_and_high_poses_still_require_return(self):
        for pose in ([0, 0, 1000, 180, 0, 0], [100, 200, 1000, 180, 0, 0]):
            with self.subTest(pose=pose):
                self.read.return_value = pose
                self.assertTrue(self.prepare().succeeded)
                self.assertEqual(1000, self.execute.call_args.args[1][0].position[2])

    def test_rotated_polygon_does_not_use_bounding_box(self):
        corners = ((0, 50), (50, 0), (100, 50), (50, 100))
        request = StartRecoveryRequest((1, 1, 50, 180, 0, 0), corners, config(), self.destination)
        self.assertFalse(TrayReturnRecoveryStrategy().matches(request))
        self.assertTrue(TrayReturnRecoveryStrategy().matches(replace(request, pose=(50, 50, 50, 180, 0, 0))))

    def test_missing_route_invalid_region_and_wrong_frame_reject_without_motion(self):
        for cfg in (replace(config(), plate_next_cycle_midpoint_enabled=False),
                    replace(config(), plate_next_cycle_waypoints=[]),
                    replace(config(), plate_exit_gate_pose=[]),
                    replace(config(), plate_corners=[]),
                    replace(config(), plate_robot_user=2)):
            with self.subTest(config=cfg):
                self.assertFalse(self.prepare(cfg).succeeded)
        self.execute.assert_not_called()

    def test_fresh_pose_failure_rejects_instead_of_assuming_outside(self):
        self.read.side_effect = RuntimeError("offline")
        self.assertFalse(self.prepare().succeeded)
        self.execute.assert_not_called()

    def test_no_motion_after_cancellation_or_unknown_destination(self):
        self.assertFalse(self.prepare(should_stop=lambda: True).succeeded)
        self.read.assert_not_called()
        self.destination.return_value = None
        self.assertFalse(self.prepare().succeeded)
        self.execute.assert_not_called()

    def test_failed_return_does_not_fall_back_and_new_start_reads_pose_again(self):
        self.execute.return_value = False
        self.assertFalse(self.prepare().succeeded)
        self.assertEqual(1, self.execute.call_count)
        self.read.return_value = [75, 150, 20, 180, 0, 0]
        self.execute.return_value = True
        self.assertTrue(self.prepare().succeeded)
        self.assertEqual(2, self.read.call_count)
        self.assertEqual((75, 150, 50), self.execute.call_args.args[1][0].position[:3])

    def test_non_tray_system_needs_no_pose_read(self):
        self.assertTrue(self.prepare(PaintDropoffConfig()).succeeded)
        self.read.assert_not_called()

    def test_below_tray_rejected(self):
        self.read.return_value = [25, 50, -20, 180, 0, 0]
        self.assertFalse(self.prepare().succeeded)
        self.execute.assert_not_called()


class TestStartRecoveryWorkflow(unittest.TestCase):
    def context(self, prepare):
        return PaintExecutionContext(
            production_service=SimpleNamespace(prepare_start_recovery=prepare, _restore_capture_view=Mock()),
            process_config=PaintProcessConfig(), stop_requested=lambda: False, control=PaintExecutionControl(),
        )

    def test_recovery_precedes_unwind_and_repeats_for_new_attempt(self):
        events = []
        def prepare(ctx):
            events.append("return")
            return StartRecoveryResult(StartRecoveryOutcome.RECOVERED)
        with patch("src.robot_systems.paint.processes.paint.workflow.handlers.lifecycle.startup_handler.unwind_joint6_at_cycle_start",
                   side_effect=lambda ctx: events.append("unwind") or True):
            for _ in range(2):
                self.assertEqual(PaintExecutionState.CAPTURE_WORKPIECE, handle_starting(self.context(prepare)))
        self.assertEqual(["return", "unwind", "return", "unwind"], events)

    def test_failed_recovery_blocks_unwind_and_production(self):
        ctx = self.context(Mock(return_value=StartRecoveryResult(StartRecoveryOutcome.FAILED, RecoveryMotionFailedError().failure)))
        with patch("src.robot_systems.paint.processes.paint.workflow.handlers.lifecycle.startup_handler.unwind_joint6_at_cycle_start") as unwind:
            self.assertEqual(PaintExecutionState.ERROR, handle_starting(ctx))
            unwind.assert_not_called()
        ctx.production_service._restore_capture_view.assert_not_called()

    def test_pause_resume_does_not_replay_start_recovery(self):
        prepare = Mock()
        ctx = self.context(prepare)
        ctx.is_resuming = True
        ctx.resume_state = PaintExecutionState.PREPARE_WORKPIECE
        self.assertEqual(ctx.resume_state, handle_starting(ctx))
        prepare.assert_not_called()


class TestProductionRecoveryIntegration(unittest.TestCase):
    def service(self):
        from src.robot_systems.paint.processes.paint.production.service import PaintProductionService
        self.pose = Mock(return_value=[25, 50, 0, 180, 0, 0])
        self.motion = Mock(return_value=True)
        self.executor = SimpleNamespace(
            _robot_service=SimpleNamespace(get_current_position_fresh=self.pose),
            _motion=SimpleNamespace(move_ordered_pickup_sequence=self.motion),
            _refresh_runtime_config=Mock(), _active_execution_control=None,
            _motion_tool=lambda: 1, _motion_user=lambda: 1,
        )
        self.navigation = Mock()
        self.navigation.get_group_position.return_value = list(target().position)
        return PaintProductionService(
            workpiece_preparation_service=Mock(), capture_snapshot_service=Mock(),
            path_preparation_service=Mock(), path_executor=self.executor,
            magazine_load_service=SimpleNamespace(_navigation=self.navigation),
            navigation_service=self.navigation,
        )

    def test_single_cycle_restart_resolves_magazine_and_restores_control(self):
        from src.robot_systems.paint.processes.paint.configuration.models import PaintMagazineLoadConfig
        service = self.service()
        magazine = PaintMagazineLoadConfig(enabled=True, magazine_group_id="Magazine")
        ctx = PaintExecutionContext(
            production_service=service, process_config=PaintProcessConfig(dropoff=config(), magazine_load=magazine),
            magazine_config=magazine, repeats_after_success=False,
            stop_requested=lambda: False, control=PaintExecutionControl(),
        )
        self.assertTrue(service.prepare_start_recovery(ctx).succeeded)
        self.navigation.get_group_position.assert_called_once_with("Magazine")
        self.assertEqual(target().position, self.motion.call_args.args[1][-1].position)
        self.assertIsNone(self.executor._active_execution_control)
        self.assertIsNone(service._next_cycle_start_target(ctx))
        self.motion.return_value = False
        self.assertFalse(service.prepare_start_recovery(ctx).succeeded)
        self.assertIsNone(self.executor._active_execution_control)

    def test_manual_calibration_move_cannot_bypass_recovery_failure(self):
        service = self.service()
        cfg = PaintProcessConfig(dropoff=config())
        self.motion.return_value = False
        result = service._move_to_calibration_before_manual_cycle(
            cfg.magazine_load, lambda: False, process_config=cfg,
        )
        self.assertFalse(result.completed)
        self.assertEqual(StartRecoveryFailureCode.MOTION_FAILED, result.failure.recovery_code)
        self.navigation.move_to_calibration_position.assert_not_called()


class TestRecoveryFailureContracts(unittest.TestCase):
    def test_configuration_cases_have_distinct_codes(self):
        cases = [
            (replace(config(), plate_corners=[]), StartRecoveryFailureCode.INVALID_TRAY_GEOMETRY),
            (replace(config(), plate_robot_tool=2), StartRecoveryFailureCode.FRAME_MISMATCH),
            (replace(config(), plate_exit_gate_pose=[]), StartRecoveryFailureCode.INVALID_EXIT_GATE),
            (replace(config(), plate_next_cycle_midpoint_enabled=False), StartRecoveryFailureCode.MISSING_RETURN_WAYPOINTS),
            (replace(config(), plate_next_cycle_waypoints=[{}]), StartRecoveryFailureCode.INVALID_RETURN_WAYPOINT),
            (replace(config(), plate_motion_profiles=[]), StartRecoveryFailureCode.INVALID_MOTION_PROFILE),
            (replace(config(), plate_approach_clearance_mm=float("nan")), StartRecoveryFailureCode.INVALID_CLEARANCE),
        ]
        for cfg, code in cases:
            with self.subTest(code=code):
                execute = Mock()
                service = StartRecoveryService(read_pose=lambda: [25, 50, 0, 180, 0, 0], execute_route=execute)
                result = service.prepare(dropoff=cfg, target_provider=target, should_stop=lambda: False, tool=1, user=1)
                self.assertEqual(StartRecoveryOutcome.FAILED, result.outcome)
                self.assertEqual(code, result.failure.recovery_code)
                self.assertIs(result.failure, result.to_operation_result().failure)
                execute.assert_not_called()

    def test_operational_failures_and_cancellation_are_distinct(self):
        from dataclasses import asdict
        read = Mock(return_value=[25, 50, 0, 180, 0, 0])
        execute = Mock(return_value=False)
        provider = Mock(return_value=target())
        service = StartRecoveryService(read_pose=read, execute_route=execute)
        def prepare():
            return service.prepare(dropoff=config(), target_provider=provider, should_stop=lambda: False, tool=1, user=1)
        self.assertEqual(StartRecoveryFailureCode.MOTION_FAILED, prepare().failure.recovery_code)
        execute.side_effect = RuntimeError("transport lost")
        self.assertEqual(StartRecoveryFailureCode.MOTION_FAILED, prepare().failure.recovery_code)
        provider.side_effect = RuntimeError("missing group")
        self.assertEqual(StartRecoveryFailureCode.TARGET_UNAVAILABLE, prepare().failure.recovery_code)
        read.return_value = [float("nan")] * 6
        result = prepare()
        self.assertEqual(StartRecoveryFailureCode.POSE_UNAVAILABLE, result.failure.recovery_code)
        self.assertEqual("pose_unavailable", asdict(result.to_operation_result().failure)["recovery_code"])
        cancelled = service.prepare(dropoff=config(), target_provider=provider, should_stop=lambda: True, tool=1, user=1)
        self.assertEqual(StartRecoveryOutcome.CANCELLED, cancelled.outcome)
        self.assertIsNone(cancelled.failure)

    def test_strategy_raises_dedicated_exception_before_execution(self):
        from src.robot_systems.paint.processes.paint.start_recovery.errors import BelowTraySurfaceError
        request = StartRecoveryRequest((25, 50, -20, 180, 0, 0),
                                       tuple(tuple(c) for c in config().plate_corners), config(), target)
        with self.assertRaises(BelowTraySurfaceError) as raised:
            TrayReturnRecoveryStrategy().build_route(request)
        self.assertEqual(StartRecoveryFailureCode.BELOW_TRAY_SURFACE, raised.exception.failure.recovery_code)

    def test_missing_and_broken_strategy_do_not_allow_production(self):
        for strategies, expected in (([], StartRecoveryFailureCode.NO_STRATEGY),
                                     ([Mock(matches=Mock(side_effect=RuntimeError("bug")))], StartRecoveryFailureCode.INTERNAL)):
            with self.subTest(expected=expected):
                execute = Mock()
                service = StartRecoveryService(read_pose=lambda: [25, 50, 0, 180, 0, 0],
                                               execute_route=execute, strategies=strategies)
                result = service.prepare(dropoff=config(), target_provider=target, should_stop=lambda: False, tool=1, user=1)
                self.assertEqual(expected, result.failure.recovery_code)
                execute.assert_not_called()

    def test_workflow_preserves_failure_type_and_code(self):
        failure = RecoveryMotionFailedError().failure
        ctx = PaintExecutionContext(
            production_service=SimpleNamespace(prepare_start_recovery=Mock(
                return_value=StartRecoveryResult(StartRecoveryOutcome.FAILED, failure))),
            stop_requested=lambda: False, control=PaintExecutionControl(),
        )
        self.assertEqual(PaintExecutionState.ERROR, handle_starting(ctx))
        self.assertIs(failure, ctx.result.failure)


class TestDistributedRecoveryRotation(unittest.TestCase):
    def test_distributes_rotation_over_entire_return_without_rotating_vertical_lift(self):
        import math
        cfg = replace(config(), plate_distribute_unwind=True)
        for start_rz in (-178.049, 360.0, -540.0):
            with self.subTest(start_rz=start_rz):
                start = (25, 50, 0, 180, 0, start_rz)
                request = StartRecoveryRequest(start, tuple(tuple(c) for c in cfg.plate_corners), cfg, target)
                segments = TrayReturnRecoveryStrategy().build_route(request)
                self.assertEqual(start_rz, segments[0].position[5])
                poses = [s.position for s in segments]
                lengths = [math.dist(a[:3], b[:3]) for a, b in zip(poses, poses[1:])]
                travelled = 0.0
                for pose, distance in zip(poses[1:], lengths):
                    travelled += distance
                    expected = start_rz + travelled / sum(lengths) * (target().position[5] - start_rz)
                    self.assertAlmostEqual(expected, pose[5])
                self.assertAlmostEqual(target().position[5], poses[-1][5])
                self.assertNotEqual(target().position[5], poses[2][5])
                self.assertEqual([s.position[:3] for s in segments], [s.position[:3] for s in
                    TrayReturnRecoveryStrategy().build_route(replace(request, dropoff=replace(cfg, plate_distribute_unwind=False)))])
