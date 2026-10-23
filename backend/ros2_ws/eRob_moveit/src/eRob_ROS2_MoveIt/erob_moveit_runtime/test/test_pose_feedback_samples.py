"""Timestamp/pose coherence and HTTP propagation without a ROS installation."""
import ast
import __future__
from pathlib import Path
import sys
from threading import RLock
from types import MethodType, SimpleNamespace
from unittest.mock import Mock
import numpy as np
import pytest

SCRIPTS = Path(__file__).resolve().parents[1] / 'scripts'
sys.path.insert(0, str(SCRIPTS))
from runtime_api.state.api import StateApi
from runtime_gateway.base import RuntimeGateway
from rest.routes.state import state_blueprint
from rest.routes.common import install_http_contract
from flask import Flask


def bind_methods(relative, class_name, names, instance, **namespace):
    path = SCRIPTS / relative
    cls = next(n for n in ast.parse(path.read_text()).body if isinstance(n, ast.ClassDef) and n.name == class_name)
    selected = [n for n in cls.body if isinstance(n, ast.FunctionDef) and n.name in names]
    code = compile(ast.fix_missing_locations(ast.Module(body=selected, type_ignores=[])), str(path), 'exec',
                   flags=__future__.annotations.compiler_flag)
    exec(code, namespace)
    for name in names:
        setattr(instance, name, MethodType(namespace[name], instance))


def monitor():
    node = SimpleNamespace(get_clock=lambda: SimpleNamespace(now=lambda: SimpleNamespace(nanoseconds=1_100_000_000)))
    result = SimpleNamespace(node=node, _cartesian_lock=RLock(), _cartesian_source_stamp_ns=None,
                             _last_source_transform=None, T_tcp=np.eye(4), latest_data={})
    transforms = SimpleNamespace(quaternion_to_matrix=lambda _: np.eye(3), matrix_to_euler=lambda _: np.zeros(3))
    bind_methods('status/robot_monitor.py', 'RobotMonitor',
                 {'_cartesian_position_callback', '_update_cartesian_from_source', 'set_tcp_transform', 'get_cartesian_sample'},
                 result, np=np, TransformationUtils=transforms)
    return result


def message(ns=1_000_000_000, x=0.12):
    return SimpleNamespace(header=SimpleNamespace(stamp=SimpleNamespace(sec=ns // 1_000_000_000, nanosec=ns % 1_000_000_000)),
                           pose=SimpleNamespace(position=SimpleNamespace(x=x, y=0.43, z=0.03),
                                                orientation=SimpleNamespace(x=0, y=0, z=0, w=1)))


def test_sample_has_actual_source_stamp_and_coherent_pose_copy():
    m = monitor()
    assert m.get_cartesian_sample() is None
    m._cartesian_position_callback(message())
    sample = m.get_cartesian_sample()
    assert sample['sample_timestamp_ns'] == 1_000_000_000
    assert sample['observation_timestamp_ns'] == 1_100_000_000
    np.testing.assert_allclose(sample['position'], [120, 430, 30, 0, 0, 0])
    sample['position'][0] = 999
    assert m.get_cartesian_sample()['position'][0] == 120
    # Repeated HTTP reads never create a new source timestamp.
    assert m.get_cartesian_sample()['sample_timestamp_ns'] == 1_000_000_000


@pytest.mark.parametrize('source_ns', [999_000_000, 1_000_000_000])
def test_duplicate_and_out_of_order_feedback_cannot_replace_pose(source_ns):
    m = monitor()
    m._cartesian_position_callback(message())
    m._cartesian_position_callback(message(source_ns, x=9))
    assert m.get_cartesian_sample()['position'][0] == 120
    transform = np.eye(4)
    transform[0, 3] = .01
    m.set_tcp_transform(transform)
    assert m.get_cartesian_sample()['sample_timestamp_ns'] == 1_000_000_000
    assert m.get_cartesian_sample()['position'][0] == pytest.approx(130)


def test_backend_transforms_sample_to_active_user_without_changing_timestamps():
    m = monitor()
    m._cartesian_position_callback(message())
    workobject = SimpleNamespace(apply=Mock(side_effect=lambda pose, inverse: [pose[0] - 10, *pose[1:]]))
    backend = SimpleNamespace(node=SimpleNamespace(monitor=m), active_workobject_user_id=1,
                              get_workobject=Mock(return_value=workobject))
    bind_methods('backend/moveit_robot_backend.py', 'MoveItRobotBackend', {'get_current_position_sample'}, backend)
    sample = backend.get_current_position_sample()
    assert sample['position'][0] == 110
    assert sample['sample_timestamp_ns'] == 1_000_000_000
    backend.get_workobject.assert_called_once_with(1)
    workobject.apply.assert_called_once()


def test_http_preserves_source_timestamps_and_unavailable_feedback_fails_closed():
    gateway = Mock(spec=RuntimeGateway)
    sample = {'position': [120, 430, 30, 180, 0, 0],
              'sample_timestamp_ns': 1_000_000_000, 'observation_timestamp_ns': 1_010_000_000}
    gateway.get_current_position_sample.return_value = sample
    api = StateApi(gateway)
    app = Flask(__name__)
    install_http_contract(app)
    app.register_blueprint(state_blueprint(api))
    client = app.test_client()
    response = client.get('/position/current/sample')
    assert response.status_code == 200
    assert all(response.json[key] == value for key, value in sample.items())
    gateway.get_current_position_sample.return_value = None
    assert client.get('/position/current/sample').status_code == 503
