"""Offline checks for profile-scoped source timestamps and feedback cadence."""
import ast
import importlib.util
from pathlib import Path
import sys
from types import ModuleType, SimpleNamespace
from typing import Optional
from unittest.mock import Mock

import pytest

PACKAGE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PACKAGE))


def stamp(sec, nanosec=0):
    return SimpleNamespace(sec=sec, nanosec=nanosec)


def pose_message():
    return SimpleNamespace(header=SimpleNamespace(stamp=None, frame_id=None), pose=SimpleNamespace(
        position=SimpleNamespace(x=0, y=0, z=0), orientation=SimpleNamespace(x=0, y=0, z=0, w=1)))


def publisher(source_stamps=False):
    # Execute the actual publisher class with ROS transport replaced by test doubles.
    class Base:
        def __init__(self, name):
            self.parameters = {'use_tf_source_timestamps': source_stamps}
            self.logger = Mock()
            self.clock_stamp = stamp(200)

        def declare_parameter(self, key, default):
            self.parameters.setdefault(key, default)

        def get_parameter(self, key):
            return SimpleNamespace(value=self.parameters[key])

        def get_clock(self):
            return SimpleNamespace(now=lambda: SimpleNamespace(to_msg=lambda: self.clock_stamp))

        def get_logger(self):
            return self.logger

    transform = SimpleNamespace(header=SimpleNamespace(stamp=stamp(100)), transform=SimpleNamespace(
        translation=SimpleNamespace(x=.12, y=.43, z=.03), rotation=SimpleNamespace(x=0, y=0, z=0, w=1)))
    buffer = SimpleNamespace(lookup_transform=Mock(return_value=transform))
    path = PACKAGE / 'scripts/zeroerr_state_publisher.py'
    cls = next(n for n in ast.parse(path.read_text()).body if isinstance(n, ast.ClassDef) and n.name == 'ZeroErrStatePublisher')
    namespace = {'__name__': 'offline_feedback_test', 'CartesianPublisherBase': Base, 'Optional': Optional,
                 'PoseStamped': pose_message, '_DEFAULT_SOURCE_FRAME': 'ee_link', '_BASE_FRAME': 'base_link',
                 'rclpy': SimpleNamespace(time=SimpleNamespace(Time=lambda: None)),
                 'tf2_ros': SimpleNamespace(Buffer=lambda: buffer, TransformListener=Mock()),
                 'LookupException': LookupError, 'ConnectivityException': ConnectionError,
                 'ExtrapolationException': ValueError}
    exec(compile(ast.fix_missing_locations(ast.Module(body=[cls], type_ignores=[])), str(path), 'exec'), namespace)
    return namespace['ZeroErrStatePublisher'](), transform


def test_source_mode_preserves_tf_stamp_and_does_not_freshen_repeated_pose():
    node, transform = publisher(True)
    first = node._get_cartesian_pose()
    node.clock_stamp = stamp(201)
    second = node._get_cartesian_pose()
    assert first.header.stamp == second.header.stamp == transform.header.stamp
    assert first.header.frame_id == 'base_link'
    assert (first.pose.position.x, first.pose.position.y, first.pose.position.z) == (.12, .43, .03)
    assert second.pose.orientation.w == 1
    transform.header.stamp = stamp(101)
    assert node._get_cartesian_pose().header.stamp == stamp(101)


def test_legacy_default_retains_publication_stamps_and_identical_pose_values():
    node, transform = publisher()
    first = node._get_cartesian_pose()
    node.clock_stamp = stamp(201)
    second = node._get_cartesian_pose()
    assert first.header.stamp == stamp(200)
    assert second.header.stamp == stamp(201)
    assert first.pose == second.pose
    assert first.pose.position.x == transform.transform.translation.x


def test_zero_source_stamp_is_not_replaced_with_a_fresh_clock_reading():
    node, transform = publisher(True)
    transform.header.stamp = stamp(0)
    assert node._get_cartesian_pose().header.stamp == stamp(0)


@pytest.mark.parametrize('source_mode', [False, True])
def test_missing_tf_still_returns_no_pose_and_warns_once(source_mode):
    node, _ = publisher(source_mode)
    node._tf_buffer.lookup_transform.side_effect = LookupError('missing')
    assert node._get_cartesian_pose() is None
    assert node._get_cartesian_pose() is None
    node.logger.warning.assert_called_once()


@pytest.fixture
def runtime(monkeypatch, tmp_path):
    packages = ModuleType('ament_index_python.packages')
    packages.get_package_share_directory = lambda _: str(PACKAGE)
    parent = ModuleType('ament_index_python')
    parent.packages = packages
    monkeypatch.setitem(sys.modules, 'ament_index_python', parent)
    monkeypatch.setitem(sys.modules, 'ament_index_python.packages', packages)
    monkeypatch.setenv('XDG_CACHE_HOME', str(tmp_path))
    path = PACKAGE / 'launch/zeroerr_launch/runtime_config.py'
    spec = importlib.util.spec_from_file_location('offline_feedback_runtime', path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def launch_parameters(executable, values):
    tree = ast.parse((PACKAGE / 'launch/full_stack.launch.py').read_text())
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call) or not isinstance(node.func, ast.Name) or node.func.id != 'Node':
            continue
        keywords = {kw.arg: kw.value for kw in node.keywords}
        value = keywords.get('executable')
        if isinstance(value, ast.Constant) and value.value == executable:
            mappings = [item for item in keywords['parameters'].elts if isinstance(item, ast.Dict)]
            result = {}
            for mapping in mappings:
                result.update(eval(compile(ast.Expression(mapping), '<launch-parameters>', 'eval'), {
                    'runtime_value': lambda path, key, default: values.get(key, default), 'package_path': str(PACKAGE)}))
            return result
    raise AssertionError(executable)


@pytest.mark.parametrize('profile', ['paint', 'paint_short_links', 'paint_auto_dry', 'welding',
                                     'development_short_links', 'development_extended_links', 'paint_tray_dry'])
def test_effective_launch_policy_is_scoped_to_tray_profile(runtime, monkeypatch, profile):
    monkeypatch.setenv('ZEROERR_ACTIVE_PROFILE', profile)
    values = runtime.load_runtime_config(str(PACKAGE))
    tf = launch_parameters('robot_state_publisher', values)
    cart = launch_parameters('zeroerr_state_publisher.py', values)
    tray = profile == 'paint_tray_dry'
    assert tf['publish_frequency'] == (100 if tray else 15)
    assert cart['publish_hz'] == (100 if tray else 10)
    assert cart['use_tf_source_timestamps'] is tray
    assert values['MONITOR_UPDATE_RATE_HZ'] == 10
    if tray:
        params = runtime.load_state_publisher_params(str(PACKAGE))
        # Derivative estimation does not receive a new rate/timestamp contract.
        topics = params['state_topics']
        assert topics['cartesian_position'] is True
        assert all(topics[key] is False for key in (
            'cartesian_velocity', 'cartesian_acceleration', 'cartesian_jerk',
            'joint_velocity', 'joint_acceleration', 'joint_jerk'))


def extracted_method(path, class_name, method_name, **namespace):
    cls = next(n for n in ast.parse(path.read_text()).body if isinstance(n, ast.ClassDef) and n.name == class_name)
    method = next(n for n in cls.body if isinstance(n, ast.FunctionDef) and n.name == method_name)
    exec(compile(ast.fix_missing_locations(ast.Module(body=[method], type_ignores=[])), str(path), 'exec'), namespace)
    return namespace[method_name]


def test_diagnostic_profile_accepts_repeated_source_timestamps():
    import numpy as np
    path = PACKAGE.parent / 'erob_moveit_runtime/scripts/simple_monitor_gui.py'
    compute = extracted_method(path, 'SimpleMonitorGUI', '_compute_motion_profile', np=np)
    # A timer can publish the same TF twice; the existing plot removes duplicates.
    samples = [{'t': timestamp, 'cartesian': [timestamp, 0, 0, 0, 0, 0],
                'cart_vel_mag': 1., 'cart_acc_mag': 0.}
               for timestamp in (0., 0., .01, .01, .02, .03)]
    result = compute(SimpleNamespace(collected_data=samples))
    np.testing.assert_allclose(result['t'], [0, .01, .02, .03])
    assert all(np.isfinite(result[key]).all() for key in ('progress', 'speed', 'acceleration', 'jerk'))


def test_calibration_coverage_remains_time_throttled_at_100_hz():
    from threading import Lock
    now = [0.]
    path = PACKAGE / 'collision_detection/calibration/data_collection/zeroerr_collision_calibration_runner.py'
    callback = extracted_method(path, 'CalibrationRunner', '_on_pose',
                                time=SimpleNamespace(monotonic=lambda: now[0], time=lambda: now[0]))
    node = SimpleNamespace(_lock=Lock(), dry_run=False, _run_type='external_motion', _running=True,
                           _csv_writer=Mock(), _csv_file=Mock(), _positions=[0]*6, _stage='test',
                           _last_coverage_write=-1., _coverage_points=[], _joint_coverage_points=[],
                           get_parameter=lambda _: SimpleNamespace(value=.2))
    message = pose_message()
    for index in range(101):
        now[0] = index / 100
        callback(node, message)
    assert node._pose is message.pose
    assert 4 <= node._csv_writer.writerow.call_count <= 6
    assert len(node._coverage_points) == node._csv_writer.writerow.call_count
