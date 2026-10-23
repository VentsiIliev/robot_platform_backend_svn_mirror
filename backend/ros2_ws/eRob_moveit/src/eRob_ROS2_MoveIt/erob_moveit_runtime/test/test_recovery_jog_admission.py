"""Exercise HTTP-to-controller recovery admission without ROS or robot motion."""
import ast
from pathlib import Path
from threading import Lock
from time import perf_counter
from types import MethodType, SimpleNamespace
from unittest.mock import Mock
import sys

import pytest

SCRIPTS = Path(__file__).resolve().parents[1] / 'scripts'
sys.path.insert(0, str(SCRIPTS))
from runtime_api.common import ApiSettings
from runtime_api.handlers import RuntimeApi
from runtime_gateway.base import RuntimeGateway


def methods(relative, cls_name, names):
    path = SCRIPTS / relative
    tree = ast.parse(path.read_text())
    cls = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == cls_name)
    selected = [n for n in cls.body if isinstance(n, ast.FunctionDef) and n.name in names]
    namespace = {
        'perf_counter': perf_counter, 'time': __import__('time'),
        'config': SimpleNamespace(MOTION_ERROR_DRIVE_NOT_ENABLED=-15, MOTION_ERROR_HARDWARE_NOT_READY=-12),
        'MOTION_ERROR_DRIVE_NOT_ENABLED': -15, 'MOTION_ERROR_HARDWARE_NOT_READY': -12,
    }
    exec(compile(ast.fix_missing_locations(ast.Module(body=selected, type_ignores=[])), str(path), 'exec'), namespace)
    return {name: namespace[name] for name in names}


@pytest.fixture
def stack(monkeypatch):
    # Existing tests extract controller methods to avoid creating a ROS node.
    node = SimpleNamespace(
        _fake_hardware=False, _motion_interlock_lock=Lock(), _ethercat_fault_lock=Lock(),
        _collision_detection_suppressed=True, _ethercat_motion_fault=False,
        _motion_interlock_active=False, _collision_recovery_hold=False,
        _collision_monitor_ready=True, _collision_monitor_state_ts=__import__('time').monotonic(),
        cell_scene_manager=SimpleNamespace(is_ready=Mock(return_value=True)),
        is_drive_operation_enabled_for_motion=Mock(return_value=True),
        get_drive_enable_fault_reason=Mock(return_value='drive disabled'),
        get_hardware_fault_reason=Mock(return_value='hardware held'),
        is_motion_stack_ready=Mock(return_value=True), get_motion_stack_fault_reason=Mock(return_value='not ready'),
        get_logger=Mock(), get_tool_transform=Mock(return_value=None),
        _motion=SimpleNamespace(execute=Mock(return_value=0)),
    )
    for name, method in methods('robot_controller.py', 'RobotController', {
        'execute', 'is_hardware_ready_for_motion', 'is_hardware_ready_for_collision_recovery',
    }).items():
        setattr(node, name, MethodType(method, node))
    robot = SimpleNamespace(node=node, apply_workobject=lambda pose, user_id: pose)
    for name, method in methods('backend/moveit_robot_backend.py', 'MoveItRobotBackend', {
        'move_liner', '_reject_if_drive_not_enabled',
    }).items():
        setattr(robot, name, MethodType(method, robot))
    local = SimpleNamespace(node=node, robot=robot)
    local.move_linear = MethodType(methods('runtime_gateway/local.py', 'LocalRuntimeGateway', {'move_linear'})['move_linear'], local)
    gateway = Mock(spec=RuntimeGateway)
    gateway.is_motion_stack_ready.return_value = True
    gateway.is_runtime_initialized.return_value = True
    gateway.last_motion_error.return_value = None
    gateway.last_submitted_task_id.return_value = 42
    gateway.move_linear.side_effect = local.move_linear
    strategy = Mock()
    monkeypatch.setitem(sys.modules, 'motion.strategies', SimpleNamespace(
        SingleTargetStrategy=strategy, PilzMoveLinStrategy=strategy))
    api = RuntimeApi(gateway=gateway, settings=ApiSettings())
    return api, node, gateway, strategy


def submit(api, **flags):
    return api.motion.move_linear({'position': [0, 0, 30, 180, 0, 0], 'blocking': False, **flags})


def test_explicit_recovery_reaches_execution_through_both_checks(stack):
    api, node, gateway, strategy = stack
    response = submit(api, recovery_jog=True, allow_collision_recovery=True)
    assert response.status == 202
    node._motion.execute.assert_called_once_with(strategy.return_value, queue_if_busy=False)
    assert strategy.call_args.kwargs['avoid_collisions'] is False


@pytest.mark.parametrize('flags', [{}, {'allow_collision_recovery': True}, {'recovery_jog': False, 'allow_collision_recovery': True}])
def test_unflagged_moves_stay_blocked_during_suppression(stack, flags):
    api, node, gateway, strategy = stack
    assert submit(api, **flags).status == 503
    node._motion.execute.assert_not_called()


@pytest.mark.parametrize('blocker', ['drive', 'ethercat', 'cell_scene', 'motion_stack', 'suppression_off'])
def test_recovery_retains_hardware_and_scene_requirements(stack, blocker):
    api, node, gateway, strategy = stack
    if blocker == 'drive':
        node.is_drive_operation_enabled_for_motion.return_value = False
    elif blocker == 'ethercat':
        node._ethercat_motion_fault = True
    elif blocker == 'cell_scene':
        node.cell_scene_manager.is_ready.return_value = False
    elif blocker == 'motion_stack':
        node.is_motion_stack_ready.return_value = False
    else:
        node._collision_detection_suppressed = False
    assert submit(api, recovery_jog=True, allow_collision_recovery=True).status != 200
    node._motion.execute.assert_not_called()


def test_controller_rechecks_recovery_state_at_submission(stack):
    api, node, gateway, strategy = stack
    node.is_hardware_ready_for_collision_recovery = Mock(side_effect=[True, False])
    assert submit(api, recovery_jog=True, allow_collision_recovery=True).status == 503
    node._motion.execute.assert_not_called()


@pytest.mark.parametrize('value', ['true', 1, None])
def test_recovery_marker_must_be_boolean(stack, value):
    api, node, gateway, strategy = stack
    assert submit(api, recovery_jog=value).status == 400
    gateway.move_linear.assert_not_called()


def test_normal_motion_remains_available_without_suppression(stack):
    api, node, gateway, strategy = stack
    node._collision_detection_suppressed = False
    assert submit(api).status == 202
    node._motion.execute.assert_called_once_with(strategy.return_value, queue_if_busy=True)
    assert strategy.call_args.kwargs['avoid_collisions'] is True
