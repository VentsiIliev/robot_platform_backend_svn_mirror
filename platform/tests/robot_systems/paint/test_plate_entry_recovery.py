"""One pre-release unwind retry must never replay paint or release twice."""
import unittest
from dataclasses import replace
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from src.robot_systems.paint.processes.paint.configuration.models import PaintProcessConfig, PaintDropoffConfig
from src.robot_systems.paint.processes.paint.operations.dropoff.strategies.plate_entry_recovery import (
    is_recoverable_entry_rejection, recover_plate_entry_unwind,
)
from src.robot_systems.paint.processes.paint.operations.dropoff.strategies.plate_layout import (
    PlateLayoutDropoff, _execute_plate_layout_ordered_release,
)
from src.robot_systems.paint.processes.paint.tray_dry.plate_layout import PlateLayoutService
from src.robot_systems.paint.processes.paint.production.execution_control import PaintExecutionControl
from src.robot_systems.paint.processes.paint.configuration.serializer import PaintProcessConfigSerializer
from src.robot_systems.paint.applications.paint_process_settings.mapper import PaintProcessSettingsMapper

ERROR = "Ordered PTP segment 'Plate entry' rejected: no safe PTP IK candidate: collision contacts=[Link_2<->tool0]"
NO_IK_ERROR = "ordered-chain planning failed: Ordered PTP segment 'Plate entry: passage gate to plate center' rejected: no IK candidates found"
BEFORE = [50, 50, 200, 180, 0, 360]
AFTER = [50, 50, 200, 180, 0, 0]
RECOVERY = "src.robot_systems.paint.processes.paint.operations.dropoff.strategies.plate_entry_recovery"


class TestPlateEntryRecovery(unittest.TestCase):
    def test_separate_retreat_is_linear_and_outside_paint_execution_group(self):
        from src.robot_systems.paint.processes.paint.operations.pickup.executor import build_ordered_paint_contact_segments
        from src.robot_systems.paint.processes.paint.planning.projection.command_job import PaintContactCommandJob
        from src.engine.robot.motion_sequence import OrderedMotionType, OrderedPathCommand

        path = [[10, 20, 282, 180, 0, 0], [11, 20, 282, 180, 0, 1]]
        retreat = (50., 20., 282., 180., 0., 1.)
        job = PaintContactCommandJob(1, "Workpiece", 30., 40., retreat)
        segments = build_ordered_paint_contact_segments([path], [job], PaintProcessConfig().contact_staging)
        self.assertEqual(3, len(segments))
        self.assertIsInstance(segments[1], OrderedPathCommand)
        self.assertEqual(tuple(path[-1]), segments[1].path[-1])
        self.assertEqual(retreat, segments[2].position)
        self.assertIs(OrderedMotionType.LINEAR, segments[2].motion_type)
        self.assertFalse(segments[2].metadata.execution_group)
        self.assertEqual(0, segments[2].profile.blend_radius)
        self.assertEqual(30, segments[2].profile.velocity_percent)

    def owner(self):
        config = PaintProcessConfig(dropoff=PaintDropoffConfig(
            strategy="plate_layout", plate_retry_entry_after_unwind=True,
            plate_use_entry_gate_as_detach_pose=True, plate_distribute_unwind=False,
            plate_corners=[[0, 0, 10, 180, 0, 0], [300, 0, 10, 180, 0, 0],
                           [300, 300, 10, 180, 0, 0], [0, 300, 10, 180, 0, 0]],
            plate_passage_gate_pose=[100, 100, 200, 180, 0, 0],
            plate_exit_gate_pose=[100, 100, 200, 180, 0, 0],
        ))
        robot, motion, vacuum = MagicMock(), MagicMock(), MagicMock()
        robot.get_execution_status.return_value = {"is_executing": False, "ordered_motion_chain": {
            "active": False, "phase": "error", "error": ERROR,
            "executed_segments_count": 0, "planned_segments_count": 0,
        }}
        robot.is_healthy.return_value = True
        robot.unwind_joint6.return_value = True
        motion.last_motion_error = ERROR
        vacuum.turn_vacuum_off.return_value = (True, "")
        layout = PlateLayoutService()
        layout.clear()
        layout.reserve(config.dropoff, width_mm=20, height_mm=30,
                       calibration_pose=[0, 0, 0, 180, 0, 0], workpiece_rz_at_calibration_deg=0,
                       pose_calculator=lambda _cal, pose, _rz: list(pose))
        return SimpleNamespace(
            _paint_process_config=lambda: config, _robot_service=robot, _motion=motion,
            _vacuum=vacuum, _plate_layout_service=layout,
            _execution_control=lambda: None, _last_process_end_pose=list(BEFORE),
            _last_process_start_rz=0, _last_paint_contact_end_rz=360,
            _plate_entry_completed_in_paint_chain=False, _dropoff_paint_detach_pose=None,
            _contact_motion_config=SimpleNamespace(rotation_index=5),
        )

    def test_only_explicit_planning_rejections_are_recoverable(self):
        self.assertTrue(is_recoverable_entry_rejection(ERROR))
        self.assertTrue(is_recoverable_entry_rejection(NO_IK_ERROR))
        self.assertTrue(is_recoverable_entry_rejection("LIN planning failed: NO_IK_SOLUTION"))
        for error in (None, -6, "result=-1", "Pilz LIN planning failed: error_code=99999",
                      "collision sensor protective stop", "controller planning collision",
                      "Planning collision: timed out", "cancelled planning: collision"):
            with self.subTest(error=error):
                self.assertFalse(is_recoverable_entry_rejection(error))

    def test_no_ik_rejection_retries_only_before_any_planned_or_executed_entry(self):
        for counts in ((0, 0), (1, 0), (0, 1), (None, 0), (0, None)):
            with self.subTest(counts=counts):
                owner = self.owner()
                owner._motion.last_motion_error = NO_IK_ERROR
                chain = owner._robot_service.get_execution_status.return_value["ordered_motion_chain"]
                chain.update(error=NO_IK_ERROR, planned_segments_count=counts[0],
                             executed_segments_count=counts[1])
                owner._motion.move_ordered_pickup_sequence.side_effect = [False, True, True]
                with patch(RECOVERY + ".wait_for_stable_pose", side_effect=[BEFORE, AFTER]):
                    ok, message = _execute_plate_layout_ordered_release(owner, next_cycle_start=None)
                if counts == (0, 0):
                    self.assertTrue(ok, message)
                    owner._robot_service.unwind_joint6.assert_called_once()
                    owner._vacuum.turn_vacuum_off.assert_called_once()
                    self.assertEqual(3, owner._motion.move_ordered_pickup_sequence.call_count)
                else:
                    self.assertFalse(ok)
                    owner._robot_service.unwind_joint6.assert_not_called()
                    owner._vacuum.turn_vacuum_off.assert_not_called()
                    owner._motion.move_ordered_pickup_sequence.assert_called_once()

    def test_successful_retry_releases_and_commits_only_once(self):
        owner = self.owner()
        owner._motion.move_ordered_pickup_sequence.side_effect = [False, True, True]
        with patch(RECOVERY + ".wait_for_stable_pose", side_effect=[BEFORE, AFTER]):
            ok, message = _execute_plate_layout_ordered_release(owner, next_cycle_start=None)
        self.assertTrue(ok, message)
        owner._robot_service.unwind_joint6.assert_called_once()
        self.assertFalse(owner._robot_service.unwind_joint6.call_args.kwargs["queue_if_busy"])
        self.assertEqual(3, owner._motion.move_ordered_pickup_sequence.call_count)
        owner._vacuum.turn_vacuum_off.assert_called_once()
        self.assertEqual(1, len(owner._plate_layout_service.snapshot(owner._paint_process_config().dropoff)["placements"]))
        self.assertIsNone(owner._plate_layout_service.pending)

    def test_failed_retry_stops_without_release_or_second_unwind(self):
        owner = self.owner()
        owner._motion.move_ordered_pickup_sequence.side_effect = [False, False]
        with patch(RECOVERY + ".wait_for_stable_pose", side_effect=[BEFORE, AFTER]):
            ok, message = _execute_plate_layout_ordered_release(owner, next_cycle_start=None)
        self.assertFalse(ok)
        self.assertIn("retry after unwind failed", message)
        owner._robot_service.unwind_joint6.assert_called_once()
        owner._vacuum.turn_vacuum_off.assert_not_called()
        self.assertIsNotNone(owner._plate_layout_service.pending)

    def test_unwind_failure_and_xyz_drift_block_transfer_retry(self):
        for unwind_ok, after in ((False, AFTER), (True, [60, 50, 200, 180, 0, 0])):
            owner = self.owner()
            owner._robot_service.unwind_joint6.return_value = unwind_ok
            owner._motion.move_ordered_pickup_sequence.return_value = False
            with patch(RECOVERY + ".wait_for_stable_pose", side_effect=[BEFORE, after]):
                ok, _ = _execute_plate_layout_ordered_release(owner, next_cycle_start=None)
            self.assertFalse(ok)
            owner._motion.move_ordered_pickup_sequence.assert_called_once()
            owner._vacuum.turn_vacuum_off.assert_not_called()

    def test_cancel_busy_and_unhealthy_states_do_not_unwind(self):
        for condition in ("cancel", "busy", "unhealthy", "pause"):
            owner = self.owner()
            control = PaintExecutionControl()
            owner._execution_control = lambda: control
            if condition == "cancel":
                control.request_stop()
            if condition == "pause":
                control.request_pause()
            if condition == "unhealthy":
                owner._robot_service.is_healthy.return_value = False
            result, _ = recover_plate_entry_unwind(owner, ERROR, idle_checker=lambda _: condition != "busy")
            self.assertFalse(result)
            owner._robot_service.unwind_joint6.assert_not_called()

    def test_generic_faults_and_exit_failure_never_unwind(self):
        owner = self.owner()
        owner._motion.last_motion_error = "Timed out waiting for trajectory optimizer"
        owner._motion.move_ordered_pickup_sequence.return_value = False
        ok, _ = _execute_plate_layout_ordered_release(owner, next_cycle_start=None)
        self.assertFalse(ok)
        owner._robot_service.unwind_joint6.assert_not_called()
        owner._vacuum.turn_vacuum_off.assert_not_called()
        owner = self.owner()
        owner._motion.move_ordered_pickup_sequence.side_effect = [True, False]
        ok, _ = _execute_plate_layout_ordered_release(owner, next_cycle_start=None)
        self.assertFalse(ok)
        owner._robot_service.unwind_joint6.assert_not_called()
        owner._vacuum.turn_vacuum_off.assert_called_once()

    def test_partial_or_unknown_entry_execution_does_not_unwind(self):
        for field, value in (("executed_segments_count", 1), ("planned_segments_count", 1),
                             ("phase", "completed"), ("error", "controller fault"),
                             ("executed_segments_count", None)):
            owner = self.owner()
            owner._robot_service.get_execution_status.return_value["ordered_motion_chain"][field] = value
            ok, _ = recover_plate_entry_unwind(owner, ERROR, idle_checker=lambda _: True)
            self.assertFalse(ok)
            owner._robot_service.unwind_joint6.assert_not_called()

    def test_rebuilds_ptp_and_linear_routes_without_distributing_unwind_twice(self):
        for mode in ("ptp", "linear"):
            owner = self.owner()
            config = owner._paint_process_config()
            profiles = [dict(profile) for profile in config.dropoff.plate_motion_profiles]
            profiles[0]["motion_type"] = mode
            config = replace(config, dropoff=replace(config.dropoff,
                             plate_distribute_unwind=True, plate_motion_profiles=profiles))
            owner._paint_process_config = lambda: config
            owner._motion.move_ordered_pickup_sequence.side_effect = [False, True, True]
            routed = {
                "entry_gate": [100, 100, 200, 180, 0, 360],
                "entry_center": [150, 150, 60, 180, 0, 270],
                "dropoff": [20, 25, 10, 180, 0, 180],
                "exit_center": [150, 150, 60, 180, 0, 90],
                "exit_gate": [100, 100, 200, 180, 0, 0],
            }
            with (patch(RECOVERY + ".wait_for_stable_pose", side_effect=[BEFORE, AFTER]),
                  patch("src.robot_systems.paint.processes.paint.operations.dropoff.strategies.plate_layout._plate_route_poses_with_distributed_unwind",
                        return_value=routed) as route):
                ok, message = _execute_plate_layout_ordered_release(owner, next_cycle_start=None)
            self.assertTrue(ok, message)
            route.assert_called_once()
            first = owner._motion.move_ordered_pickup_sequence.call_args_list[0].args[1][0]
            retry = owner._motion.move_ordered_pickup_sequence.call_args_list[1].args[1][0]
            self.assertEqual(first.motion_type, retry.motion_type)
            self.assertEqual(360, first.position[5])
            self.assertEqual(0, retry.position[5])
            owner._vacuum.turn_vacuum_off.assert_called_once()

    def test_stop_during_unwind_does_not_retry_or_release(self):
        owner = self.owner()
        control = PaintExecutionControl()
        owner._execution_control = lambda: control
        owner._motion.move_ordered_pickup_sequence.return_value = False

        def stop_during_unwind(**kwargs):
            control.request_stop()
            return True

        owner._robot_service.unwind_joint6.side_effect = stop_during_unwind
        with patch(RECOVERY + ".wait_for_stable_pose", return_value=BEFORE):
            ok, _ = _execute_plate_layout_ordered_release(owner, next_cycle_start=None)
        self.assertFalse(ok)
        owner._motion.move_ordered_pickup_sequence.assert_called_once()
        owner._vacuum.turn_vacuum_off.assert_not_called()

    def test_retry_mode_separates_paint_and_preserves_config_on_roundtrip(self):
        owner = self.owner()
        strategy = PlateLayoutDropoff(owner)
        self.assertIsNone(strategy.painting_detach_pose(is_final_job=True, paint_start_rz=0, paint_end_rz=360))
        self.assertFalse(strategy.plan_paint_approach(cleanup_pending=False).value.segments)
        config = owner._paint_process_config()
        serializer = PaintProcessConfigSerializer()
        self.assertTrue(serializer.from_dict(serializer.to_dict(config)).dropoff.plate_retry_entry_after_unwind)
        flat = PaintProcessSettingsMapper.to_flat_dict(config)
        restored = PaintProcessSettingsMapper.from_flat_dict(flat, config)
        self.assertTrue(restored.dropoff.plate_retry_entry_after_unwind)


if __name__ == "__main__":
    unittest.main()
