"""Offline persistence, conflict and runtime application checks for cell fixtures."""
from copy import deepcopy
from pathlib import Path
from threading import Lock
from types import SimpleNamespace
from unittest.mock import Mock
import sys
import time

import pytest
import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'scripts'))
from configuration.cell_scene import validate_cell_scene
from configuration.domain import ConfigurationError, Conflict
from configuration.repository import YamlProfileRepository
from configuration.service import ConfigurationService
from configuration.runtime import LocalConfigurationRuntime
from runtime_api.configuration.requests import section_name

DOCUMENT = {'CELL_COLLISION_OBJECTS': {'cell_fixture_test': {
    'enabled': True, 'frame':'mounting_surface', 'size_mm':[10.,20.,30.], 'pose':[50.,60.,70.,0.,0.,90.]}}}


class Runtime:
    def __init__(self):
        self.document = deepcopy(DOCUMENT)
        self.failure = None
    def snapshot(self, section):
        return deepcopy(self.document)
    def apply(self, section, value):
        if not self.failure:
            self.document = deepcopy(value)
        return self.failure


def test_cell_scene_save_survives_repository_and_service_restart(tmp_path):
    path = tmp_path/'cell_scene.yaml'
    path.write_text(yaml.safe_dump(DOCUMENT))
    runtime = Runtime()
    service = ConfigurationService(YamlProfileRepository('tray', {'cell_scene':path}, root=tmp_path), runtime)
    view = service.get('cell_scene')
    saved = service.update('cell_scene', {'CELL_COLLISION_OBJECTS':{'cell_fixture_test':{'enabled':False}}},view['revision'])
    assert not saved['pending_application']
    assert saved['saved']['CELL_COLLISION_OBJECTS']['cell_fixture_test']['enabled'] is False
    repository = YamlProfileRepository('tray', {'cell_scene':path}, root=tmp_path)
    assert repository.read('cell_scene') == saved['saved']
    fresh_runtime = Runtime()
    fresh_runtime.document = repository.read('cell_scene')
    restarted = ConfigurationService(repository,fresh_runtime).get('cell_scene')
    assert not restarted['pending_application']
    with pytest.raises(Conflict):
        service.update('cell_scene', {'CELL_COLLISION_OBJECTS':{'cell_fixture_test':{'enabled':True}}},view['revision'])


def test_saved_pending_state_can_be_retried_without_losing_revision(tmp_path):
    path = tmp_path/'cell_scene.yaml'
    path.write_text(yaml.safe_dump(DOCUMENT))
    runtime = Runtime()
    runtime.failure = 'Saved; robot is busy'
    service = ConfigurationService(YamlProfileRepository('tray', {'cell_scene':path}, root=tmp_path), runtime)
    view = service.get('cell_scene')
    result = service.update('cell_scene', {'CELL_COLLISION_OBJECTS':{'cell_fixture_test':{'enabled':False}}},view['revision'])
    assert result['pending_application']
    assert result['applied']['CELL_COLLISION_OBJECTS']['cell_fixture_test']['enabled'] is True
    assert yaml.safe_load(path.read_text())['CELL_COLLISION_OBJECTS']['cell_fixture_test']['enabled'] is False
    runtime.failure = None
    retry = service.retry_application('cell_scene', result['revision'])
    assert not retry['pending_application']
    assert retry['revision'] == result['revision']


@pytest.mark.parametrize('field,value', [('enabled',1),('enabled','false'),('size_mm',[0,1,2]),
    ('size_mm',[True,1,2]),('size_mm',[float('nan'),1,2]),('pose',[0]*5),('frame','bad frame')])
def test_invalid_cell_scene_is_rejected(field,value):
    document = deepcopy(DOCUMENT)
    document['CELL_COLLISION_OBJECTS']['cell_fixture_test'][field] = value
    with pytest.raises(ConfigurationError):
        validate_cell_scene(document)


def test_cell_scene_application_uses_stationarity_gate_and_releases_lock():
    assert section_name('cell_scene') == 'cell_scene'
    manager = Mock()
    manager.snapshot.return_value = DOCUMENT
    node = SimpleNamespace(execution_lock=Lock(),is_executing=False,
        is_motion_active=lambda:False,has_pending_motion=lambda:False,cell_scene_manager=manager,
        state_store=Mock())
    measured = SimpleNamespace(names=('J1','J2'),velocity=(0.,0.),received_at=time.monotonic())
    node.state_store.get_braking_state.return_value=measured
    config = SimpleNamespace(JOINT_NAMES=('J1','J2'),_CONFIG={})
    runtime = LocalConfigurationRuntime(config,lambda:node,lambda:SimpleNamespace(cartesian_servo=None))
    assert runtime.apply('cell_scene',DOCUMENT) is None
    manager.apply.assert_called_once_with(DOCUMENT)
    assert runtime.snapshot('cell_scene') == DOCUMENT
    measured.velocity=(1.,0.)
    assert runtime.apply('cell_scene',DOCUMENT).code == 'configuration_robot_moving'
    assert manager.apply.call_count == 1
    assert not node.execution_lock.locked()


def test_http_cell_scene_route_preserves_profile_and_revision_contract(tmp_path):
    from flask import Flask
    from rest.routes.configuration import configuration_blueprint
    from runtime_api.configuration.api import ConfigurationApi
    path=tmp_path/'cell_scene.yaml'
    path.write_text(yaml.safe_dump(DOCUMENT))
    service=ConfigurationService(YamlProfileRepository('tray',{'cell_scene':path},root=tmp_path),Runtime())
    gateway=Mock()
    gateway.get_configuration.side_effect=service.get
    gateway.update_configuration.side_effect=service.update
    gateway.apply_configuration.side_effect=service.retry_application
    app=Flask(__name__)
    app.register_blueprint(configuration_blueprint(ConfigurationApi(gateway)))
    client=app.test_client()
    view=client.get('/configuration/cell_scene').get_json()
    response=client.patch('/configuration/cell_scene',json={'expected_revision':view['revision'],
        'changes':{'CELL_COLLISION_OBJECTS':{'cell_fixture_test':{'enabled':False}}}})
    assert response.status_code==200
    assert response.get_json()['saved']['CELL_COLLISION_OBJECTS']['cell_fixture_test']['enabled'] is False
    assert client.patch('/configuration/cell_scene',json={'expected_revision':view['revision'],
        'changes':{'CELL_COLLISION_OBJECTS':{'cell_fixture_test':{'enabled':True}}}}).status_code==409
