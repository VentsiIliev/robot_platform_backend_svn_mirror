"""All four APIs run against a fake remote-shaped gateway, without ROS or robot configuration."""
import ast
import importlib
import json
from pathlib import Path
import subprocess
import sys
from unittest.mock import Mock

import pytest
from flask import Flask

SCRIPTS = Path(__file__).resolve().parents[1] / 'scripts'
sys.path.insert(0, str(SCRIPTS))
from runtime_api.common import ApiSettings
from runtime_api.contracts import ApiResponse, request_context
from runtime_api.handlers import RuntimeApi
from runtime_api.motion.requests import parse_move_linear_request
from runtime_gateway.base import RuntimeGateway
from runtime_gateway.errors import GatewayError
from rest.routes.configuration import configuration_blueprint
from rest.routes.motion import motion_blueprint
from rest.routes.state import state_blueprint
from rest.routes.control import control_blueprint
from rest.routes.common import install_http_contract


@pytest.fixture
def setup():
    gateway = Mock(spec=RuntimeGateway)
    gateway.is_runtime_initialized.return_value = True
    gateway.is_motion_stack_ready.return_value = True
    gateway.last_submitted_task_id.return_value = 42
    gateway.last_motion_error.return_value = None
    facade = RuntimeApi(gateway=gateway, settings=ApiSettings(drive_verify_timeout_s=0.01))
    app = Flask(__name__)
    install_http_contract(app)
    app.register_blueprint(configuration_blueprint(facade.configuration))
    app.register_blueprint(motion_blueprint(facade.motion))
    app.register_blueprint(state_blueprint(facade.state))
    app.register_blueprint(control_blueprint(facade.control))
    return gateway, facade, app.test_client()


def test_all_groups_work_through_gateway(setup):
    gateway, api, client = setup
    gateway.get_configuration.return_value = {'success': True, 'profile': 'test', 'revision': 'r'}
    gateway.move_linear.return_value = 0
    gateway.get_current_position.return_value = [0]*6
    gateway.set_digital_output.return_value = 0
    assert client.get('/configuration/calibration').json['profile'] == 'test'
    assert client.post('/move/linear', json={'position': [0]*6}).json['task_id'] == 42
    assert client.get('/position/current').json['position'] == [0]*6
    assert client.post('/io/digital_output', json={'port': 1, 'value': 1}).json['success']
    gateway.get_configuration.assert_called_once_with('calibration')
    gateway.move_linear.assert_called_once()
    gateway.get_current_position.assert_called_once()
    gateway.set_digital_output.assert_called_once_with(1, 1)


@pytest.mark.parametrize('operation,call', [
    ('configuration.get', lambda api: api.configuration.get('calibration')),
    ('motion.move_linear', lambda api: api.motion.move_linear({'position': [0]*6})),
    ('state.current_position', lambda api: api.state.current_position()),
    ('control.set_collision_suppression', lambda api: api.control.set_collision_suppression({'suppressed': False})),
])
def test_gateway_timeout_has_consistent_typed_error_and_unknown_outcome(setup, operation, call):
    gateway, api, client = setup
    error = GatewayError('confirmation_timeout', 'Controller did not acknowledge command abc',
                         kind='timeout', outcome_unknown=True, details={'command_id': 'abc'})
    for method in ('get_configuration', 'move_linear', 'get_current_position', 'set_collision_suppressed'):
        getattr(gateway, method).side_effect = error
    with request_context('client-request-123'):
        response = call(api)
    assert response.status == 504
    assert response.body['request_id'] == 'client-request-123'
    assert response.error == {'code': 'confirmation_timeout', 'message': str(error), 'source': 'gateway',
                             'operation': operation, 'retryable': False, 'outcome_unknown': True,
                             'details': {'command_id': 'abc'}}
    assert response.body['error'] == str(error)


@pytest.mark.parametrize('body', [[], 'abc', False, 5, {'position': [float('nan')]*6},
                                      {'position': [True]*6}, {'position': [0]*6, 'blocking': 'false'},
                                      {'position': [0]*6, 'tool': True}, {'position': [0]*6, 'vel': -1}])
def test_invalid_motion_requests_do_not_reach_gateway(setup, body):
    gateway, api, client = setup
    response = api.motion.move_linear(body)
    assert response.status == 400
    assert response.error['source'] == 'validation'
    gateway.move_linear.assert_not_called()


def test_actual_controller_failure_is_preserved(setup):
    gateway, api, client = setup
    gateway.move_linear.return_value = -14
    gateway.last_motion_error.return_value = 'Joint_6: PATH_TOLERANCE_VIOLATED, position error 0.21 rad'
    response = api.move_linear({'position': [0]*6})
    assert response.status == 409
    assert response.body['result'] == -14
    assert response.error['code'] == 'motion_error_14'
    assert response.error['message'] == gateway.last_motion_error.return_value
    assert response.error['details']['result'] == -14


def test_configuration_save_pending_is_successful_save_not_successful_application(setup):
    gateway, api, client = setup
    gateway.update_configuration.return_value = {
        'success': True, 'saved': {'x': 2}, 'applied': {'x': 1}, 'revision': 'new',
        'pending_application': True, 'application_error': 'Robot is executing', 'restart_required': False}
    response = client.patch('/configuration/calibration', json={'expected_revision': 'old', 'changes': {'REFERENCE_TOOL_ID': 1}})
    assert response.status_code == 200
    assert response.json['success'] and response.json['pending_application']
    gateway.update_configuration.assert_called_once_with('calibration', {'REFERENCE_TOOL_ID': 1}, 'old', tool_id=None, user_id=None)


def test_read_failures_are_not_reported_as_success(setup):
    gateway, api, client = setup
    gateway.get_current_position.return_value = None
    assert api.state.current_position().status == 503
    gateway.get_current_position.return_value = [float('inf')]*6
    response = api.state.current_position()
    assert response.status == 500
    assert response.error['code'] == 'invalid_runtime_response'
    json.dumps(response.body, allow_nan=False)


def test_prepared_plan_get_and_delete_use_their_respective_gateway_operations(setup):
    gateway, api, client = setup
    gateway.prepared_ordered_motion_chain_status.return_value = {'plan_id': 'p', 'state': 'prepared'}
    gateway.discard_prepared_ordered_motion_chain.return_value = {'plan_id': 'p', 'state': 'discarded'}
    assert client.get('/execute/ordered_motion_chain/prepared/p').json['state'] == 'prepared'
    assert client.delete('/execute/ordered_motion_chain/prepared/p').json['state'] == 'discarded'
    gateway.prepared_ordered_motion_chain_status.assert_called_once_with('p')
    gateway.discard_prepared_ordered_motion_chain.assert_called_once_with('p')


def test_apis_do_not_import_transports_or_local_backend():
    for group in ('configuration', 'motion', 'state', 'control'):
        folder = SCRIPTS / 'runtime_api' / group
        assert {p.name for p in folder.glob('*.py')} == {'__init__.py', 'api.py', 'requests.py', 'responses.py'}
        for source in folder.glob('*.py'):
            tree = ast.parse(source.read_text())
            for node in ast.walk(tree):
                if isinstance(node, ast.ImportFrom):
                    assert not node.module.startswith(('rest', 'flask', 'rclpy', 'runtime_gateway.local', 'robot_controller', 'config'))
                if isinstance(node, ast.Attribute):
                    assert node.attr not in {'_node_getter', '_robot_getter', '_configuration_service'}
    program = "from runtime_api.handlers import RuntimeApi; import sys; assert 'config' not in sys.modules; assert 'rclpy' not in sys.modules; assert 'flask' not in sys.modules"
    result = subprocess.run([sys.executable, '-c', program], env={'PATH': '/usr/bin:/bin', 'PYTHONPATH': str(SCRIPTS)}, capture_output=True, text=True)
    assert result.returncode == 0, result.stderr


def test_transport_errors_and_correlation_are_consistent(setup):
    gateway, api, client = setup
    response = client.post('/move/linear', data='{invalid', content_type='application/json',
                           headers={'X-Request-ID': 'customer-123'})
    assert response.status_code == 400
    assert response.json['error_info']['code'] == 'invalid_json'
    assert response.json['error_info']['source'] == 'transport'
    assert response.json['request_id'] == response.headers['X-Request-ID'] == 'customer-123'
    assert client.post('/move/linear', data='text').status_code == 415
    missing = client.get('/unknown-route')
    assert missing.status_code == 404
    assert missing.json['error_info']['code'] == 'not_found'
    assert missing.json['request_id'] != response.json['request_id']
    gateway.move_linear.assert_not_called()


def test_async_acknowledgement_is_not_reported_as_completed(setup):
    gateway, api, client = setup
    gateway.move_linear.return_value = 0
    response = api.motion.move_linear({'position': [0]*6, 'blocking': False})
    assert response.status == 202
    assert response.body['accepted'] is True
    assert response.body['final'] is False
    gateway.move_linear.return_value = 3
    response = api.motion.move_linear({'position': [0]*6, 'blocking': True})
    assert response.status == 202 and response.body['queue_position'] == 3
    assert response.body['final'] is False


def test_config_saved_but_gateway_confirmation_failed_preserves_cause(context=None):
    from configuration.ports import ApplicationFailure
    error = GatewayError('controller_confirmation_timeout', 'Controller did not acknowledge revision abc',
                         kind='timeout', outcome_unknown=True, details={'revision': 'abc'})
    failure = ApplicationFailure.from_exception(error)
    assert failure.code == 'controller_confirmation_timeout'
    assert failure.outcome_unknown is True
    assert failure.details['revision'] == 'abc'
    assert str(error) in failure.message


def test_openapi_describes_all_routes_with_generated_error_contracts(setup):
    import re
    from rest.openapi import OPENAPI_SPEC
    gateway, api, client = setup
    schemas = OPENAPI_SPEC['components']['schemas']
    assert set(schemas['ResponseBody']['required']) == {'success', 'request_id'}
    assert set(schemas['ErrorInfo']['required']) == {'code', 'message', 'source', 'operation', 'retryable', 'outcome_unknown', 'details'}
    for rule in client.application.url_map.iter_rules():
        if rule.endpoint == 'static':
            continue
        path = re.sub(r'<(?:[^:>]+:)?([^>]+)>', r'{\1}', rule.rule)
        assert path in OPENAPI_SPEC['paths'], path
        for method in rule.methods - {'HEAD', 'OPTIONS'}:
            operation = OPENAPI_SPEC['paths'][path][method.lower()]
            assert operation['tags'][0] in {'configuration', 'motion', 'state', 'control'}
            assert operation['responses']['504']['content']['application/json']['schema']['$ref'].endswith('ResponseBody')
    json.dumps(OPENAPI_SPEC, allow_nan=False)


def test_explicit_servo_speeds_do_not_require_percentage_defaults(setup):
    gateway, api, client = setup
    gateway.servo_jog_start.return_value = 0
    result = api.motion.servo_jog_start({'axis': 'X', 'direction': 'PLUS', 'linear_mm_s': 5.0})
    assert result.body['success'] is True, result.body
    assert gateway.servo_jog_start.call_args.kwargs['linear_mm_s'] == 5.0
    assert gateway.servo_jog_start.call_args.args[2] is None  # No percentage was supplied.


def test_nested_nonfinite_motion_values_are_rejected_before_dispatch(setup):
    gateway, api, client = setup
    result = api.motion.execute_sequence({'segments': [{'position': [0]*6, 'vel': float('inf'), 'acc': 10}]})
    assert result.status == 400
    gateway.execute_sequence.assert_not_called()


@pytest.mark.parametrize('planned,executed', [(0, 0), (1, 0), (2, 1)])
def test_ordered_chain_exception_reaches_http_without_resetting_progress(setup, monkeypatch, planned, executed):
    # Extract the backend entry point so this regression runs without a ROS node.
    from time import perf_counter
    from types import MethodType, SimpleNamespace
    import traceback

    path = SCRIPTS / 'backend/moveit_robot_backend.py'
    tree = ast.parse(path.read_text())
    cls = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == 'MoveItRobotBackend')
    method = next(n for n in cls.body if isinstance(n, ast.FunctionDef) and n.name == 'execute_ordered_motion_chain')
    namespace = {'perf_counter': perf_counter, 'traceback': traceback,
                 'config': SimpleNamespace(apply_limit_profiles=Mock(), DEFAULT_VEL_PERCENT=30, DEFAULT_ACC_PERCENT=30)}
    exec(compile(ast.fix_missing_locations(ast.Module(body=[method], type_ignores=[])), str(path), 'exec'), namespace)

    status_path = SCRIPTS / 'motion/scheduling/status_adapter.py'
    status_tree = ast.parse(status_path.read_text())
    functions = [n for n in status_tree.body if isinstance(n, ast.FunctionDef) and n.name in
                 {'ordered_chain_starting_status', 'ordered_chain_terminal_status'}]
    status_namespace = {'Any': object}
    exec(compile(ast.fix_missing_locations(ast.Module(body=functions, type_ignores=[])), str(status_path), 'exec'), status_namespace)
    monkeypatch.setitem(sys.modules, 'motion.scheduling.status_adapter', SimpleNamespace(
        **{n.name: status_namespace[n.name] for n in functions}))
    monkeypatch.setitem(sys.modules, 'motion.move_linear_timing', SimpleNamespace(begin=Mock(), clear=Mock(), mark=Mock()))
    validation = SimpleNamespace(scheduler_group_status=(), scheduler_group_states={}, scheduler_segment_states={},
                                 log_message=lambda: 'validated', timing_fields=lambda: {})
    monkeypatch.setitem(sys.modules, 'motion.scheduling.motion_adapters', SimpleNamespace(
        OrderedMotionBatchValidationFailure=Mock(), validate_ordered_motion_batch_from_mappings=Mock(return_value=validation)))

    error = "ordered-chain planning failed: Ordered PTP segment 'Plate entry: passage gate to plate center' rejected: no IK candidates found"
    node = SimpleNamespace(last_motion_error='stale previous error', get_logger=Mock(),
                           is_hardware_ready_for_motion=lambda: True)
    status = {}

    def fail_planning(*args, **kwargs):
        assert node.last_motion_error is None
        status.update(planned_segments_count=planned, executed_segments_count=executed)
        raise RuntimeError(error)

    backend = SimpleNamespace(node=node, _reject_if_drive_not_enabled=lambda _: None,
                              _set_ordered_motion_chain_status=lambda **updates: status.update(updates),
                              _execute_ordered_motion_chain_pipelined=fail_planning)
    execute = MethodType(namespace['execute_ordered_motion_chain'], backend)
    gateway, api, client = setup
    gateway.execute_ordered_motion_chain.side_effect = execute
    gateway.last_motion_error.side_effect = lambda: node.last_motion_error
    response = client.post('/execute/ordered_motion_chain', json={
        'segments': [{'type': 'ptp', 'position': [0, 0, 200, 180, 0, 0]}], 'blocking': True})

    assert response.status_code == 500
    assert response.json['result'] == -1
    assert response.json['error'] == error
    assert response.json['detail'] == error
    assert response.json['error_info']['message'] == error
    assert status['phase'] == 'error'
    assert status['active'] is False
    assert status['error'] == error
    assert status['planned_segments_count'] == planned
    assert status['executed_segments_count'] == executed
