"""Offline API/storage checks; never connects to hardware or starts ROS."""
from copy import deepcopy
from pathlib import Path
import sys
import tempfile
from unittest.mock import patch

import pytest
import yaml
from flask import Flask

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from configuration.domain import ConfigurationError, Conflict, canonical_calibration, edit_tool, tool_snapshot
from rest.routes.configuration import configuration_blueprint
from runtime_api.configuration.api import ConfigurationApi
from runtime_gateway.base import RuntimeGateway
from unittest.mock import Mock
from configuration.repository import YamlProfileRepository
from configuration.service import ConfigurationService

CALIBRATION = {
    'TOOL_REGISTRY': {'TOOL_0': [0]*6, 'TOOL_1': [1, 2, 3, 0, 0, 90], 'TOOL_2': [4, 5, 6, 0, 0, 90]},
    'TOOL_ID_MAP': {0: 'TOOL_0', 1: 'TOOL_1', 2: 'TOOL_2'},
    'WORKOBJECT_REGISTRY': {'WOBJ_0': [0]*6}, 'WORKOBJECT_ID_MAP': {0: 'WOBJ_0'},
}


class Runtime:
    def __init__(self):
        self.value = canonical_calibration(CALIBRATION)
        self.calls = 0
        self.pending = False

    def snapshot(self, section):
        return deepcopy(self.value)

    def apply(self, section, value):
        self.calls += 1
        if self.pending:
            return 'Saved; robot is busy'
        self.value = deepcopy(value)
        return None


@pytest.fixture
def context(tmp_path):
    profile = tmp_path / 'config' / 'profile_a'
    profile.mkdir(parents=True)
    path = profile / 'calibration.yaml'
    path.write_text(yaml.safe_dump(CALIBRATION))
    repository = YamlProfileRepository('profile_a', {'calibration': path}, root=profile)
    runtime = Runtime()
    service = ConfigurationService(repository, runtime)
    app = Flask(__name__)
    gateway = Mock(spec=RuntimeGateway)
    gateway.get_configuration.side_effect = service.get
    gateway.update_configuration.side_effect = service.update
    gateway.apply_configuration.side_effect = service.retry_application
    app.register_blueprint(configuration_blueprint(ConfigurationApi(gateway)))
    return service, runtime, path, app.test_client()


def test_revision_save_resolves_relative_geometry_and_keeps_standalone_data(context):
    service, runtime, path, client = context
    before = client.get('/configuration/calibration').get_json()
    assert not before['pending_application']
    result = client.patch('/configuration/calibration/tools/2', json={
        'expected_revision': before['revision'],
        'changes': {'reference_tool_id': 1, 'relative_transform': [10, 0, 0, 0, 0, 0]},
    })
    assert result.status_code == 200
    data = result.get_json()
    assert data['tools']['tool_registry']['TOOL_2'] == pytest.approx([1, 12, 3, 0, 0, 90])
    saved = yaml.safe_load(path.read_text())
    assert 'TOOL_REGISTRY' not in saved
    assert tool_snapshot(saved)['tool_registry'] == data['tools']['tool_registry']
    assert runtime.calls == 1
    assert data['pending_application'] is False


def test_stale_edit_cannot_overwrite_newer_values(context):
    service, runtime, path, client = context
    view = service.get('calibration')
    service.update('calibration', {'transform': [1]*6}, view['revision'], tool_id=2)
    before = path.read_bytes()
    response = client.patch('/configuration/calibration/tools/2', json={
        'expected_revision': view['revision'], 'changes': {'transform': [9]*6}})
    assert response.status_code == 409
    assert path.read_bytes() == before
    assert runtime.calls == 1


@pytest.mark.parametrize('changes', [
    {'transform': [True]*6}, {'transform': [float('inf')]*6}, {'transform': [0]*5},
    {'reference_tool_id': 2, 'relative_transform': [0]*6},
    {'reference_tool_id': 99, 'relative_transform': [0]*6},
    {'collision_profile': 'unknown'}, {'typo': True},
])
def test_invalid_tool_changes_leave_disk_and_runtime_untouched(context, changes):
    service, runtime, path, client = context
    before = path.read_bytes()
    with pytest.raises(ConfigurationError):
        service.update('calibration', changes, service.get('calibration')['revision'], tool_id=2)
    assert path.read_bytes() == before
    assert runtime.calls == 0


def test_cycle_through_another_tool_is_rejected(context):
    service, runtime, path, client = context
    first = service.get('calibration')
    service.update('calibration', {'reference_tool_id': 1, 'relative_transform': [0]*6}, first['revision'], tool_id=2)
    with pytest.raises(ConfigurationError, match='cycle'):
        service.update('calibration', {'reference_tool_id': 2, 'relative_transform': [0]*6},
                       service.get('calibration')['revision'], tool_id=1)


def test_failed_atomic_replace_does_not_change_runtime_or_original(context):
    service, runtime, path, client = context
    before = path.read_bytes()
    with patch('configuration.repository.os.replace', side_effect=OSError('disk full')):
        response = client.patch('/configuration/calibration/tools/2', json={
            'expected_revision': service.get('calibration')['revision'], 'changes': {'transform': [8]*6}})
    assert response.status_code == 503
    assert path.read_bytes() == before
    assert runtime.calls == 0
    assert list(path.parent.glob('.calibration.yaml.*')) == []


def test_save_pending_is_distinct_from_applied_and_can_retry(context):
    service, runtime, path, client = context
    runtime.pending = True
    result = service.update('calibration', {'transform': [8]*6}, service.get('calibration')['revision'], tool_id=2)
    assert result['success'] and result['pending_application']
    assert result['applied']['TOOL_DEFINITIONS']['TOOL_2']['transform'] != [8]*6
    runtime.pending = False
    result = service.retry_application('calibration', result['revision'])
    assert not result['pending_application']


def test_missing_revision_and_nonobject_json_are_rejected(context):
    service, runtime, path, client = context
    for body in [[], {}, {'changes': {'transform': [0]*6}}]:
        assert client.patch('/configuration/calibration/tools/2', json=body).status_code == 400


def test_profile_include_revision_and_writes_are_isolated(tmp_path):
    root = tmp_path / 'config'
    profile = root / 'one'
    profile.mkdir(parents=True)
    shared = root / 'shared.yaml'
    shared.write_text('schema_version: 1\nmonitor:\n  detection_enabled: true\n  limit: 3.5\n')
    path = profile / 'sensorless_collision.yaml'
    path.write_text('RUNTIME_INCLUDES: [../shared.yaml]\n')
    other = root / 'two.yaml'
    other.write_text('untouched: true\n')
    repo = YamlProfileRepository('one', {'sensorless_collision': path}, root=profile)
    from configuration.repository import revision
    before = repo.read('sensorless_collision')
    shared_before = shared.read_bytes()
    with repo.transaction('sensorless_collision'):
        changed = deepcopy(before)
        changed['monitor']['limit'] = 4.0
        repo.write('sensorless_collision', changed, revision(before))
    assert yaml.safe_load(path.read_text()) == {'RUNTIME_INCLUDES': ['../shared.yaml'], 'monitor': {'limit': 4.0}}
    assert shared.read_bytes() == shared_before
    assert other.read_text() == 'untouched: true\n'
    shared.write_text(shared.read_text().replace('3.5', '3.6'))
    # Inherited field changed even though the effective overridden field did not: only effective revisions matter.
    shared.write_text(shared.read_text().replace('true', 'false'))
    with pytest.raises(Conflict):
        repo.write('sensorless_collision', changed, revision(changed))


def test_paths_and_includes_cannot_escape_profile_tree(tmp_path):
    with pytest.raises(ConfigurationError):
        YamlProfileRepository('one', {'calibration': '/etc/passwd'}, root=tmp_path)
    profile = tmp_path / 'config' / 'one'
    profile.mkdir(parents=True)
    path = profile / 'calibration.yaml'
    path.write_text('RUNTIME_INCLUDES: [../../../outside.yaml]\n')
    repo = YamlProfileRepository('one', {'calibration': path}, root=profile)
    with pytest.raises(ConfigurationError, match='escapes'):
        repo.read('calibration')


def test_revision_is_bound_to_profile_and_section(context):
    service, runtime, path, client = context
    same_values = YamlProfileRepository('different_profile', {'calibration': path}, root=path.parent)
    other = ConfigurationService(same_values, runtime)
    with pytest.raises(Conflict):
        other.update('calibration', {'transform': [0]*6}, service.get('calibration')['revision'], tool_id=2)
    assert runtime.calls == 0


def test_application_exception_still_reports_durable_save_as_pending(context):
    service, runtime, path, client = context
    with patch.object(runtime, 'apply', side_effect=RuntimeError('adapter offline')):
        result = service.update('calibration', {'transform': [9]*6}, service.get('calibration')['revision'], tool_id=2)
    assert result['success'] and result['pending_application']
    assert service.get('calibration')['pending_application']
    assert tool_snapshot(yaml.safe_load(path.read_text()))['tool_registry']['TOOL_2'] == [9]*6


def test_sensorless_runtime_reports_actual_controller_and_unapplied_restart_fields(tmp_path):
    from types import SimpleNamespace
    from configuration.runtime import LocalConfigurationRuntime
    root = Path(__file__).resolve().parents[2] / 'zeroerr' / 'config'
    profile = tmp_path / 'config' / 'one'
    profile.mkdir(parents=True)
    shared = profile.parent / 'shared'
    shared.mkdir()
    (shared / 'sensorless_collision.yaml').write_bytes((root / 'shared/sensorless_collision.yaml').read_bytes())
    path = profile / 'sensorless_collision.yaml'
    path.write_text('RUNTIME_INCLUDES: [../shared/sensorless_collision.yaml]\n')
    repo = YamlProfileRepository('one', {'sensorless_collision': path}, root=profile)
    startup = repo.read('sensorless_collision')
    observed = {**deepcopy(startup['monitor']), '_controller': deepcopy(startup['controller'])}
    def apply_monitor(changes):
        observed.update(changes)
    runtime = LocalConfigurationRuntime(SimpleNamespace(), lambda: None, lambda: None,
        sensorless_startup=startup, monitor_getter=lambda: observed, monitor_apply=apply_monitor)
    service = ConfigurationService(repo, runtime)
    assert not service.get('sensorless_collision')['pending_application']
    observed['collision_detection_suppressed'] = True
    assert not service.get('sensorless_collision')['pending_application']
    with pytest.raises(ConfigurationError, match='transient'):
        service.update('sensorless_collision', {'monitor': {'collision_detection_suppressed': True}},
                       service.get('sensorless_collision')['revision'])
    result = service.update('sensorless_collision', {'monitor': {'confirm_duration_ms': 60.0}},
                            service.get('sensorless_collision')['revision'])
    assert not result['pending_application']
    result = service.update('sensorless_collision', {'controller': {'warmup_sec': 4.0}}, result['revision'])
    assert result['pending_application'] and result['restart_required']
    assert result['applied']['controller']['warmup_sec'] == startup['controller']['warmup_sec']
    before = path.read_bytes()
    with pytest.raises(ConfigurationError):
        service.update('sensorless_collision', {'controller': {'filter_alpha': 2.0}}, result['revision'])
    assert path.read_bytes() == before


def test_calibration_application_waits_for_fresh_stationary_state():
    import time
    from threading import Lock
    from types import SimpleNamespace
    from unittest.mock import Mock
    from configuration.runtime import LocalConfigurationRuntime
    config = SimpleNamespace(JOINT_NAMES=['J1', 'J2'])
    node = Mock()
    node.execution_lock = Lock()
    node.is_executing = False
    node.is_motion_active.return_value = False
    node.has_pending_motion.return_value = False
    measured = SimpleNamespace(names=('J1', 'J2'), velocity=(0.0, 0.0), received_at=time.monotonic())
    node.state_store.get_braking_state.return_value = measured
    robot = SimpleNamespace(cartesian_servo=None)
    runtime = LocalConfigurationRuntime(config, lambda: node, lambda: robot)
    with patch.object(runtime, '_apply_calibration') as apply:
        assert runtime.apply('calibration', CALIBRATION) is None
        apply.assert_called_once()
        measured.received_at = time.monotonic() - 1
        assert 'fresh' in runtime.apply('calibration', CALIBRATION).message
        measured.received_at = time.monotonic()
        measured.velocity = (0.1, 0)
        assert 'stationary' in runtime.apply('calibration', CALIBRATION).message
        node.has_pending_motion.return_value = True
        assert 'executing' in runtime.apply('calibration', CALIBRATION).message
    assert not node.execution_lock.locked()


def test_runtime_calibration_updates_imported_registries_and_rolls_back_on_adapter_failure():
    from types import SimpleNamespace
    from configuration.runtime import LocalConfigurationRuntime
    config = SimpleNamespace(_CONFIG=deepcopy(CALIBRATION))
    for key, value in config._CONFIG.items():
        setattr(config, key, value)
    imported_tools = config.TOOL_REGISTRY
    imported_ids = config.TOOL_ID_MAP
    node = SimpleNamespace(active_tool_name='TOOL_2')
    def set_tool(name):
        node.active_tool_name = name
    node.set_tool = set_tool
    class Robot:
        def __init__(self):
            self.workobject_registry = {0: [0]*6}
            self.fail_once = False
        def get_active_workobject(self):
            return {'user_id': 0}
        def set_workobject(self, value, user_id):
            if self.fail_once:
                self.fail_once = False
                raise RuntimeError('adapter failure')
            self.workobject_registry[user_id] = value
        def set_active_workobject(self, user_id):
            assert user_id in self.workobject_registry
    robot = Robot()
    runtime = LocalConfigurationRuntime(config, lambda: node, lambda: robot)
    candidate = edit_tool(CALIBRATION, 2, {'name': 'NEW_TOOL', 'transform': [8]*6})
    with patch.dict(sys.modules, {'utils.work_object': SimpleNamespace(WorkObject=lambda *values: list(values))}):
        runtime._apply_calibration(node, robot, candidate)
        assert config.TOOL_REGISTRY is imported_tools
        assert config.TOOL_ID_MAP is imported_ids
        assert node.active_tool_name == 'NEW_TOOL'
        assert imported_tools['NEW_TOOL'] == [8]*6
        assert runtime.snapshot('calibration') == candidate
        robot.fail_once = True
        failed = edit_tool(candidate, 2, {'name': 'FAILED_TOOL', 'transform': [9]*6})
        with pytest.raises(RuntimeError, match='adapter failure'):
            runtime._apply_calibration(node, robot, failed)
        assert node.active_tool_name == 'NEW_TOOL'
        assert runtime.snapshot('calibration') == candidate
        assert 'FAILED_TOOL' not in imported_tools


def test_reading_configuration_does_not_rewrite_legacy_calibration(context):
    service, runtime, path, client = context
    before = path.read_bytes()
    assert client.get('/configuration/calibration').status_code == 200
    assert path.read_bytes() == before
    assert 'TOOL_REGISTRY' in yaml.safe_load(path.read_text())


def test_unavailable_runtime_state_does_not_hide_successful_save(context):
    service, runtime, path, client = context
    revision = service.get('calibration')['revision']
    with patch.object(runtime, 'snapshot', side_effect=RuntimeError('runtime disconnected')):
        result = service.update('calibration', {'transform': [7]*6}, revision, tool_id=2)
    assert result['success'] and result['pending_application']
    assert result['applied'] is None
    assert result['restart_required'] is None
    assert tool_snapshot(yaml.safe_load(path.read_text()))['tool_registry']['TOOL_2'] == [7]*6


def test_durable_save_reports_exact_pending_gateway_cause(context):
    from runtime_gateway.errors import GatewayError
    service, runtime, path, client = context
    revision = service.get('calibration')['revision']
    error = GatewayError('controller_confirmation_timeout', 'Controller did not acknowledge command xyz',
                         kind='timeout', outcome_unknown=True, details={'command_id': 'xyz'})
    with patch.object(runtime, 'apply', side_effect=error):
        response = client.patch('/configuration/calibration/tools/2', json={
            'expected_revision': revision, 'changes': {'transform': [3]*6}})
    assert response.status_code == 200
    body = response.get_json()
    assert body['success'] and body['pending_application']
    info = body['application_error_info']
    assert info['code'] == 'controller_confirmation_timeout'
    assert info['source'] == 'gateway'
    assert info['outcome_unknown'] is True and info['retryable'] is False
    assert info['details']['command_id'] == 'xyz'
    assert str(error) in info['message']
    assert tool_snapshot(yaml.safe_load(path.read_text()))['tool_registry']['TOOL_2'] == [3]*6
