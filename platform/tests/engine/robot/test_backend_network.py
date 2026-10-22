import importlib.util
import json
import os
from pathlib import Path
import sys
import subprocess
import tempfile
import unittest
from unittest.mock import patch

from src.engine.robot.configuration.backend_network import (
    CONFIG_ENV, load_backend_network, network_config_path,
)
from src.engine.robot.drivers.client_adapters.http_websocket import HttpWebSocketRobotClient
from src.bootstrap.ros_backend_launcher import RosBackendLauncher, _status_urls_from_env


class TestBackendNetwork(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.path = Path(temporary.name) / 'network.json'
        self.payload = dict(bind_host='127.0.0.1', client_host='127.0.0.1',
                            http_port=6100, state_ws_port=6201,
                            execution_ws_port=6302, sensor_ws_port=6403)
        self.path.write_text(json.dumps(self.payload))
        environment = patch.dict(os.environ, {CONFIG_ENV: str(self.path)}, clear=True)
        environment.start()
        self.addCleanup(environment.stop)

    def test_one_file_drives_client_and_launcher(self):
        self.assertEqual(load_backend_network().http_url, 'http://127.0.0.1:6100')
        with patch.object(HttpWebSocketRobotClient, 'health_check', return_value={'status': 'ok'}), \
             patch.object(HttpWebSocketRobotClient, '_start_state_websocket'), \
             patch.object(HttpWebSocketRobotClient, '_start_execution_websocket'), \
             patch.object(HttpWebSocketRobotClient, '_start_sensor_websocket'):
            client = HttpWebSocketRobotClient()
        self.addCleanup(client._session.close)
        self.assertEqual(client.server_url, 'http://127.0.0.1:6100')
        self.assertEqual(client._state_ws_url, 'ws://127.0.0.1:6201/ws/state')
        self.assertEqual(client._execution_ws_url, 'ws://127.0.0.1:6302/ws/execution')
        self.assertEqual(client._sensor_ws_url, 'ws://127.0.0.1:6403/ws/sensors')
        launcher = RosBackendLauncher(auto_launch=False)
        self.assertEqual(launcher._status_urls, ('http://127.0.0.1:6100/startup/status', 'http://127.0.0.1:6100/health'))
        self.assertEqual(launcher._launch_env()[CONFIG_ENV], str(self.path))

    def test_missing_or_malformed_config_never_falls_back(self):
        self.path.unlink()
        with self.assertRaises(FileNotFoundError):
            load_backend_network()
        self.path.write_text('{')
        with self.assertRaises(ValueError):
            load_backend_network()

    def test_invalid_fields_rejected(self):
        for key, value in (('http_port', True), ('http_port', 0), ('http_port', 65536),
                           ('http_port', '5000'), ('state_ws_port', 6100),
                           ('client_host', '0.0.0.0'), ('client_host', '::'),
                           ('bind_host', ''), ('bind_host', 'http://localhost'),
                           ('bind_host', '224.0.0.1')):
            with self.subTest(key=key, value=value):
                self.path.write_text(json.dumps({**self.payload, key: value}))
                with self.assertRaises(ValueError):
                    load_backend_network()
        for payload in ({}, {**self.payload, 'unknown': 1}, []):
            self.path.write_text(json.dumps(payload))
            with self.assertRaises(ValueError):
                load_backend_network()

    def test_ipv6_urls(self):
        self.path.write_text(json.dumps({**self.payload, 'client_host': '::1', 'bind_host': '::1'}))
        url = load_backend_network().http_url
        self.assertEqual(url, 'http://[::1]:6100')
        self.assertEqual(HttpWebSocketRobotClient._derive_sensor_ws_url(url), 'ws://[::1]:6403/ws/sensors')

    def test_legacy_endpoint_overrides_rejected(self):
        for key in ('ROBOT_STATE_WS_URL', 'ROBOT_EXECUTION_WS_URL', 'ROBOT_SENSOR_WS_URL'):
            with patch.dict(os.environ, {key: 'ws://different:9999'}):
                with self.assertRaisesRegex(ValueError, 'backend_network.json'):
                    HttpWebSocketRobotClient._derive_state_ws_url(load_backend_network().http_url)
        with patch.dict(os.environ, {'ROBOT_APP_BACKEND_STATUS_URLS': 'http://different:9999'}):
            with self.assertRaises(ValueError):
                _status_urls_from_env()
        with self.assertRaises(ValueError):
            _status_urls_from_env(('http://different:9999',))

    def test_explicit_config_path_must_be_absolute(self):
        with patch.dict(os.environ, {CONFIG_ENV: 'relative.json'}):
            with self.assertRaises(ValueError):
                network_config_path()

    def test_backend_reads_the_same_file(self):
        root = Path(__file__).resolve().parents[4]
        backend = root / 'backend/ros2_ws/eRob_moveit/src/eRob_ROS2_MoveIt/erob_moveit_runtime/scripts/backend_network.py'
        if not backend.exists():
            self.skipTest('Backend checkout not installed alongside platform')
        spec = importlib.util.spec_from_file_location('backend_network_contract_test', backend)
        module = importlib.util.module_from_spec(spec)
        with patch.dict(sys.modules, {spec.name: module}):
            spec.loader.exec_module(module)
            network = module.load_backend_network()
        self.assertEqual(vars(network), vars(load_backend_network()))

    def test_backend_runtime_config_uses_shared_ports(self):
        if importlib.util.find_spec("yaml") is None:
            self.skipTest("Backend runtime integration requires PyYAML; run with backend Python")
        root = Path(__file__).resolve().parents[4] / 'backend/ros2_ws/eRob_moveit/src/eRob_ROS2_MoveIt'
        if not (root / 'erob_moveit_runtime/scripts/backend_network.py').exists():
            self.skipTest('Backend checkout not installed alongside platform')
        code = (
            "import sys, json; "
            f"sys.path[:0] = {[str(root / 'erob_moveit_runtime/scripts'), str(root / 'zeroerr'), *sys.path]!r}; "
            "import config; "
            "print(json.dumps([config.REST_HOST, config.REST_PORT, "
            "config.REST_WS_STATE_HOST, config.REST_WS_STATE_PORT, "
            "config.REST_WS_EXECUTION_HOST, config.REST_WS_EXECUTION_PORT, "
            "config.REST_WS_SENSOR_HOST, config.REST_WS_SENSOR_PORT]))"
        )
        env = {**os.environ, 'AMENT_PREFIX_PATH': '', 'EROB_CONFIG_PACKAGE': 'zeroerr',
               'ZEROERR_ACTIVE_PROFILE': 'paint_tray_dry', 'ROBOT_RELEASE_TARGET': 'paint_tray_dry'}
        result = subprocess.run([sys.executable, '-B', '-c', code], env=env,
                                capture_output=True, text=True, timeout=20)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout),
                         ['127.0.0.1', 6100, '127.0.0.1', 6201,
                          '127.0.0.1', 6302, '127.0.0.1', 6403])
