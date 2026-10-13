"""Dropoff lifecycle substitution and built-in compatibility boundaries."""
import unittest
from dataclasses import replace
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from src.robot_systems.paint.contracts.dropoff import DropoffResult, IDropoffStrategy, DropoffApproach, DropoffCycleRequest
from src.robot_systems.paint.processes.paint.configuration.models import DropoffStrategy, PaintProcessConfig, PaintDropoffConfig
from src.robot_systems.paint.processes.paint.production.execution_dependencies import PaintExecutorDependencies
from src.robot_systems.paint.processes.paint.production.execution_runtime import PaintExecutionRuntime
from src.robot_systems.paint.processes.paint.production.execution_control import PaintExecutionControl
from src.robot_systems.paint.processes.paint.operations.dropoff.strategies.configured import ConfiguredDropoffStrategy
from src.robot_systems.paint.processes.paint.operations.dropoff.strategies.plate_layout import PlateLayoutDropoff
from src.robot_systems.paint.processes.paint.operations.dropoff.strategies.movement_group import MovementGroupDropoff
from src.robot_systems.paint.processes.paint.workflow.context import PaintExecutionContext
from src.robot_systems.paint.processes.paint.workflow.state import PaintExecutionState
from src.robot_systems.paint.processes.paint.workflow.handlers.dropoff.prepare_dropoff_handler import handle_prepare_dropoff
from src.robot_systems.paint.processes.paint.workflow.handlers.dropoff.dropoff_handler import handle_dropoff


from src.robot_systems.paint.processes.paint.results import PaintOperationResult, PaintOutcome, Ready, Failed, PaintFailureCode


class _CustomDropoff(IDropoffStrategy):
    def __init__(self):
        self.calls = []
        self.preparation = (True, "")
        self.result = DropoffResult(True, "Released", prepositioned_group="next")

    def begin_cycle(self, request):
        self.calls.append(("begin", request))
        return PaintOperationResult(PaintOutcome.COMPLETED, "")

    def painting_detach_pose(self, **kwargs):
        return [1.0] * 6

    def plan_paint_approach(self, *, cleanup_pending):
        self.calls.append(("plan", cleanup_pending))
        return Ready(DropoffApproach())

    def plan_cleanup_approach(self, final_pose):
        return DropoffApproach(final_pose=final_pose)

    def activate_approach(self, approach):
        self.calls.append(("activate", approach))
        return PaintOperationResult(PaintOutcome.COMPLETED, "")

    def approach_completed(self, approach):
        self.calls.append(("complete", approach))

    def finish_cycle(self, result):
        self.calls.append(("finish", result))

    def prepare_dropoff(self):
        self.calls.append("prepare")
        return self.preparation

    def release_dropoff(self, next_cycle_start=None):
        self.calls.append(("release", next_cycle_start))
        return self.result


class TestDropoffStrategyInjection(unittest.TestCase):
    def setUp(self):
        self.robot = MagicMock()
        self.strategy = _CustomDropoff()
        self.factory = MagicMock(return_value=self.strategy)
        self.runtime = PaintExecutionRuntime(dependencies=PaintExecutorDependencies(
            robot_service=self.robot, dropoff_strategy_factory=self.factory,
        ))

    def test_custom_strategy_receives_preparation_release_and_return_target(self):
        target = object()
        self.assertEqual((True, ""), self.runtime.prepare_dropoff())
        self.assertIs(self.strategy.result, self.runtime.release_dropoff(target))
        self.assertEqual(["prepare", ("release", target)], self.strategy.calls)
        self.factory.assert_called_once_with(self.runtime)
        self.assertEqual([], self.robot.mock_calls)

    def test_custom_preparation_failure_and_release_metadata_are_preserved(self):
        self.strategy.preparation = (False, "Custom gate is closed")
        self.strategy.result = DropoffResult(False, "Custom release verification failed")
        self.assertEqual(self.strategy.preparation, self.runtime.prepare_dropoff())
        self.assertIs(self.strategy.result, self.runtime.release_dropoff())

    def test_workflow_handlers_use_custom_strategy_without_selecting_builtin(self):
        service = SimpleNamespace(
            _path_executor=self.runtime,
            prepare_dropoff=self.runtime.prepare_dropoff,
            release_dropoff=lambda ctx: self.runtime.release_dropoff(),
        )
        context = PaintExecutionContext(
            production_service=service, stop_requested=lambda: False,
            control=PaintExecutionControl(),
        )
        context.execution_plan = SimpleNamespace(execution_jobs=[{}])
        self.assertIs(PaintExecutionState.DROPOFF, handle_prepare_dropoff(context))
        self.assertIs(PaintExecutionState.POST_RETURN, handle_dropoff(context))
        self.assertTrue(context.result_ok)
        self.assertEqual(["prepare", ("release", None)], self.strategy.calls)
        self.assertEqual([], self.robot.mock_calls)


class TestConfiguredDropoffStrategies(unittest.TestCase):
    def test_selector_honors_cycle_strategy_switches(self):
        config = PaintProcessConfig()
        owner = SimpleNamespace(_paint_process_config=lambda: config)
        selector = ConfiguredDropoffStrategy(owner)
        with (
            patch.object(MovementGroupDropoff, 'prepare_dropoff', return_value=(True, 'group')) as group,
            patch.object(PlateLayoutDropoff, 'prepare_dropoff', return_value=(True, 'plate')) as plate,
        ):
            config = replace(config, dropoff=replace(config.dropoff, strategy=DropoffStrategy.MOVEMENT_GROUP))
            self.assertEqual((True, 'group'), selector.prepare_dropoff())
            config = replace(config, dropoff=replace(config.dropoff, strategy=DropoffStrategy.PLATE_LAYOUT))
            self.assertEqual((True, 'plate'), selector.prepare_dropoff())
            group.assert_called_once_with()
            plate.assert_called_once_with()

    def test_plate_preparation_does_not_repeat_completed_ordered_unwind(self):
        owner = SimpleNamespace(_dropoff_unwind_prepared=True)
        with patch('src.robot_systems.paint.processes.paint.operations.dropoff.strategies.plate_layout._execute_plate_layout_preparation') as prepare:
            self.assertEqual((True, ''), PlateLayoutDropoff(owner).prepare_dropoff())
            prepare.assert_not_called()

    def test_plate_release_preserves_capacity_and_prepositioning(self):
        owner = SimpleNamespace(
            _last_prepositioned_start_group='stale',
            _plate_layout_service=SimpleNamespace(has_space_for_same_footprint=False),
        )

        def release(runtime, *, next_cycle_start):
            self.assertIsNone(runtime._last_prepositioned_start_group)
            runtime._last_prepositioned_start_group = 'next'
            return True, ''

        with patch('src.robot_systems.paint.processes.paint.operations.dropoff.strategies.plate_layout._execute_plate_layout_ordered_release', side_effect=release):
            result = PlateLayoutDropoff(owner).release_dropoff()
        self.assertTrue(result.success)
        self.assertTrue(result.tray_full)
        self.assertEqual('next', result.prepositioned_group)

    def test_failed_plate_release_does_not_report_capacity_or_prepositioning(self):
        owner = SimpleNamespace(
            _last_prepositioned_start_group='stale',
            _plate_layout_service=SimpleNamespace(has_space_for_same_footprint=False),
        )
        with patch('src.robot_systems.paint.processes.paint.operations.dropoff.strategies.plate_layout._execute_plate_layout_ordered_release', return_value=(False, 'sensor still detects workpiece')):
            result = PlateLayoutDropoff(owner).release_dropoff()
        self.assertFalse(result.success)
        self.assertFalse(result.tray_full)
        self.assertIsNone(result.prepositioned_group)
        self.assertEqual('sensor still detects workpiece', result.message)


class TestDropoffCycleLifecycle(unittest.TestCase):
    @staticmethod
    def request(calibration=None):
        plan = SimpleNamespace(
            execution_jobs=[{}], workpiece={'workpieceId': 'saved'},
            execution_paths=lambda: [[[0, 0], [20, 0], [20, 10], [0, 10]]],
        )
        pickup = SimpleNamespace(motion_plan=SimpleNamespace(align_pose=[0, 0, 10, 180, 0, 5]))
        return DropoffCycleRequest(plan, pickup, calibration or MagicMock(return_value=('calibration', [0, 0, 0, 180, 0, 0])))

    def test_selector_keeps_reserved_strategy_until_cycle_finalization(self):
        config = PaintProcessConfig()
        owner = SimpleNamespace(_paint_process_config=lambda: config)
        selector = ConfiguredDropoffStrategy(owner)
        request = self.request()
        with (
            patch.object(MovementGroupDropoff, 'prepare_dropoff', return_value=(True, 'group')) as group,
            patch.object(PlateLayoutDropoff, 'prepare_dropoff', return_value=(True, 'plate')) as plate,
        ):
            self.assertTrue(selector.begin_cycle(request).completed)
            config = replace(config, dropoff=replace(config.dropoff, strategy=DropoffStrategy.PLATE_LAYOUT))
            self.assertEqual((True, 'group'), selector.prepare_dropoff())
            plate.assert_not_called()
            selector.finish_cycle(PaintOperationResult(PaintOutcome.COMPLETED, ''))
            self.assertEqual((True, 'plate'), selector.prepare_dropoff())
            group.assert_called_once_with()
        request.calibration_source.assert_not_called()

    def test_plate_reservation_returns_capacity_before_motion(self):
        layout, robot = MagicMock(), MagicMock()
        full = PaintOperationResult(PaintOutcome.TRAY_FULL, 'No remaining capacity')
        layout.reserve_result.return_value = full
        config = PaintProcessConfig(dropoff=PaintDropoffConfig(strategy=DropoffStrategy.PLATE_LAYOUT))
        owner = SimpleNamespace(_plate_layout_service=layout, _robot_service=robot,
                                _paint_process_config=lambda: config,
                                _resolve_pivot_offset_mm=lambda *args: 0.0)
        request = self.request()
        result = PlateLayoutDropoff(owner).begin_cycle(request)
        self.assertIs(full, result)
        request.calibration_source.assert_called_once_with()
        self.assertEqual(5.0, layout.reserve_result.call_args.kwargs['workpiece_rz_at_calibration_deg'])
        self.assertEqual([], robot.mock_calls)

    def test_plate_reservation_rejects_missing_calibration_without_reserving(self):
        layout = MagicMock()
        config = PaintProcessConfig(dropoff=PaintDropoffConfig(strategy=DropoffStrategy.PLATE_LAYOUT))
        owner = SimpleNamespace(_plate_layout_service=layout, _paint_process_config=lambda: config,
                                _resolve_pivot_offset_mm=lambda *args: 0.0)
        request = self.request(MagicMock(return_value=('missing', None)))
        result = PlateLayoutDropoff(owner).begin_cycle(request)
        self.assertIs(PaintFailureCode.INVALID_CONFIGURATION, result.failure.code)
        layout.reserve_result.assert_not_called()

    def test_plate_finalization_cancels_on_failure_and_preserves_success(self):
        layout = MagicMock()
        strategy = PlateLayoutDropoff(SimpleNamespace(_plate_layout_service=layout))
        strategy.finish_cycle(PaintOperationResult(PaintOutcome.COMPLETED, ''))
        layout.cancel.assert_not_called()
        strategy.finish_cycle(PaintOperationResult(PaintOutcome.CANCELLED, 'Stopped'))
        layout.cancel.assert_called_once_with()

    def test_approach_receipt_records_only_the_steps_that_completed(self):
        owner = SimpleNamespace(_dropoff_unwind_prepared=False, _plate_entry_completed_in_paint_chain=False)
        strategy = PlateLayoutDropoff(owner)
        strategy.approach_completed(DropoffApproach(completes_entry=True))
        self.assertTrue(owner._plate_entry_completed_in_paint_chain)
        self.assertFalse(owner._dropoff_unwind_prepared)
        strategy.approach_completed(DropoffApproach(prepares_release=True))
        self.assertTrue(owner._dropoff_unwind_prepared)

    def test_selector_releases_cycle_binding_when_finalization_raises(self):
        config = PaintProcessConfig(dropoff=PaintDropoffConfig(strategy=DropoffStrategy.PLATE_LAYOUT))
        owner = SimpleNamespace(_paint_process_config=lambda: config)
        selector = ConfiguredDropoffStrategy(owner)
        with (
            patch.object(PlateLayoutDropoff, 'begin_cycle', return_value=PaintOperationResult(PaintOutcome.COMPLETED, '')),
            patch.object(PlateLayoutDropoff, 'finish_cycle', side_effect=OSError('reservation storage failed')),
        ):
            selector.begin_cycle(self.request())
            with self.assertRaisesRegex(OSError, 'reservation storage failed'):
                selector.finish_cycle(PaintOperationResult(PaintOutcome.CANCELLED, ''))
        config = replace(config, dropoff=replace(config.dropoff, strategy=DropoffStrategy.MOVEMENT_GROUP))
        with patch.object(MovementGroupDropoff, 'prepare_dropoff', return_value=(True, 'next')):
            self.assertEqual((True, 'next'), selector.prepare_dropoff())


class TestCustomApproachContribution(unittest.TestCase):
    def test_custom_commands_are_appended_and_completion_requires_success(self):
        from tests.robot_systems.paint.test_paint_workpiece_path_executor import _make_executor
        from src.robot_systems.paint.processes.paint.workflow.handlers.workflow.pickup_handler import execute_ordered_pickup_and_paint_contact_result
        from src.robot_systems.paint.processes.paint.planning.projection.command_job import PaintContactCommandJob
        from src.engine.robot.motion_sequence import OrderedPositionCommand, OrderedMotionProfile, OrderedMotionType
        for succeeded in (False, True):
            with self.subTest(succeeded=succeeded):
                strategy = _CustomDropoff()
                robot = MagicMock()
                robot.get_last_trajectory_command_info.return_value = {'raw': {'error': 'Interrupted'}}
                runtime = _make_executor(robot_service=robot, dropoff_strategy_factory=lambda runtime: strategy)
                runtime._motion = MagicMock()
                runtime._motion.move_ordered_pickup_sequence.return_value = succeeded
                pickup = SimpleNamespace(contact_mode='planned', change_plane_combined_with_first_contact=False,
                                         motion_plan=object(), vacuum_on_before_moves=False)
                plan = SimpleNamespace(workpiece={'workpieceId': 'saved'}, execution_jobs=[{}])
                command = OrderedPositionCommand('custom_destination', OrderedMotionType.LINEAR,
                                                  (0, 0, 10, 180, 0, 0), OrderedMotionProfile(10, 10))
                approach = DropoffApproach((command,), list(command.position))

                def contact(execution_plan, **kwargs):
                    kwargs['collected_command_paths'].append([[0, 0, 10, 180, 0, 0], [1, 0, 10, 180, 0, 0]])
                    kwargs['collected_command_jobs'].append(PaintContactCommandJob(0, 'Contour', 10, 10))
                    return PaintOperationResult(PaintOutcome.COMPLETED, '', planned_waypoints=2)

                runtime._paint_contact = SimpleNamespace(execute_result=contact)
                runtime._edge_cleanup = SimpleNamespace(should_run_after_xz_ry=lambda: False,
                                                       should_run_after_xy_rz=lambda: False)
                with (
                    patch.object(strategy, 'plan_paint_approach', return_value=Ready(approach)),
                    patch('src.robot_systems.paint.processes.paint.workflow.handlers.workflow.pickup_handler.build_ordered_pickup_segments', return_value=[]),
                ):
                    result = execute_ordered_pickup_and_paint_contact_result(runtime, plan, pickup_plan=pickup)
                commands = runtime._motion.move_ordered_pickup_sequence.call_args.args[1]
                self.assertIs(command, commands[-1])
                self.assertEqual(succeeded, result.completed)
                self.assertEqual(succeeded, ('complete', approach) in strategy.calls)


class TestPinnedDropoffGeometry(unittest.TestCase):
    def test_shared_pose_resolution_uses_the_strategy_reserved_for_the_cycle(self):
        from src.robot_systems.paint.processes.paint.operations.dropoff.motion import _resolve_dropoff_release_pose
        config = PaintProcessConfig()
        group_pose = [1, 2, 3, 180, 0, 0]
        plate_pose = [4, 5, 6, 180, 0, 0]
        owner = SimpleNamespace(
            _paint_process_config=lambda: config,
            _read_provider_position=lambda provider: provider(),
            _dropoff_position_provider=lambda: group_pose,
            _plate_layout_service=SimpleNamespace(pending=SimpleNamespace(release_pose=plate_pose)),
        )
        selector = ConfiguredDropoffStrategy(owner)
        owner._dropoff_strategy = selector
        selector.begin_cycle(TestDropoffCycleLifecycle.request())
        config = replace(config, dropoff=replace(config.dropoff, strategy=DropoffStrategy.PLATE_LAYOUT))
        self.assertEqual(group_pose, _resolve_dropoff_release_pose(owner))
        selector.finish_cycle(PaintOperationResult(PaintOutcome.COMPLETED, ''))
        self.assertEqual(plate_pose, _resolve_dropoff_release_pose(owner))

    def test_direct_plate_injection_resolves_its_reserved_pose(self):
        from src.robot_systems.paint.processes.paint.operations.dropoff.motion import _resolve_dropoff_release_pose
        pose = [4, 5, 6, 180, 0, 0]
        owner = SimpleNamespace(
            _paint_process_config=PaintProcessConfig,
            _plate_layout_service=SimpleNamespace(pending=SimpleNamespace(release_pose=pose)),
        )
        owner._dropoff_strategy = PlateLayoutDropoff(owner)
        self.assertEqual(pose, _resolve_dropoff_release_pose(owner))
