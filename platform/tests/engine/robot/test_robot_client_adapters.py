import asyncio
import json
import threading
import unittest
from unittest.mock import MagicMock, patch

from src.engine.robot.drivers.client_adapters import (
    HttpWebSocketRobotClient,
    FakeRobotClient,
    build_robot_client,
)
from src.engine.robot.drivers.ros2_robot import Ros2Robot
from src.engine.robot.motion_sequence import (
    OrderedMotionProfile,
    OrderedMotionType,
    OrderedPositionCommand,
)


class TestSensorWebSocketSession(unittest.IsolatedAsyncioTestCase):

    async def test_incoming_status_frames_do_not_starve_sensor_send(self):
        client = object.__new__(HttpWebSocketRobotClient)
        client._sensor_ws_stop = threading.Event()
        client._sensor_ws_lock = threading.Lock()
        client._conditional_servo_latest = None
        queue = asyncio.Queue()
        await queue.put("sensor-heartbeat")

        class BusyWebSocket:
            def __init__(self):
                self.sent = []

            async def send(inner_self, payload):
                inner_self.sent.append(payload)
                client._sensor_ws_stop.set()

            async def recv(inner_self):
                await asyncio.sleep(0)
                return json.dumps({"conditional_servo": {"state": "moving"}})

        websocket = BusyWebSocket()
        await asyncio.wait_for(
            client._run_sensor_websocket_session(websocket, queue),
            timeout=0.2,
        )

        self.assertEqual(websocket.sent, ["sensor-heartbeat"])


class TestRobotClientAdapters(unittest.TestCase):
    @patch("src.engine.robot.drivers.client_adapters.http_websocket.requests.post")
    def test_move_linear_preserves_backend_velocity_rejection(self, post_mock):
        reason = "vel must be greater than zero and at most 100 percent"
        response = MagicMock(status_code=400)
        response.json.return_value = {"success": False, "error": reason}
        post_mock.return_value = response
        client = object.__new__(HttpWebSocketRobotClient)
        client.server_url = "http://localhost:5000"
        client._drive_enabled = True
        client.set_active_tool = MagicMock(return_value=True)
        client._motion_preflight_error = MagicMock(return_value=None)
        client._mark_execution_request_sent = MagicMock(return_value=0)
        client._mark_execution_request_response = MagicMock()
        client._last_execute_path_response = {"error": "old planning error"}
        self.assertEqual(-1, client.move_liner([0]*6, vel=0, acc=0))
        self.assertEqual(reason, client.get_last_motion_error())


    @patch("src.engine.robot.drivers.client_adapters.http_websocket.requests.get")
    def test_timestamped_pose_reaches_service_with_http_duration(self, get_mock):
        from src.engine.robot.services.robot_service import RobotService

        sample = {"success": True, "position": [120, 430, 30, 180, 0, 0],
                  "sample_timestamp_ns": 1_000_000_000, "observation_timestamp_ns": 1_010_000_000}
        get_mock.return_value = MagicMock(status_code=200)
        get_mock.return_value.json.return_value = sample
        client = object.__new__(HttpWebSocketRobotClient)
        client.server_url = "http://localhost:5000"
        robot = object.__new__(Ros2Robot)
        robot._client = client
        service = object.__new__(RobotService)
        service._robot = robot
        with patch("src.engine.robot.drivers.client_adapters.http_websocket.time.monotonic", side_effect=[10.0, 10.012]):
            result = service.get_current_position_sample()
        self.assertEqual(sample["position"], result["position"])
        self.assertEqual(sample["sample_timestamp_ns"], result["sample_timestamp_ns"])
        self.assertAlmostEqual(0.012, result["transport_elapsed_s"])
        get_mock.assert_called_once_with("http://localhost:5000/position/current/sample", timeout=2)

    def test_status_errors_are_throttled_and_reset_after_recovery(self):
        module = "src.engine.robot.drivers.client_adapters.http_websocket"
        for recovery_transport in ("http", "websocket"):
            with self.subTest(recovery_transport=recovery_transport):
                client = object.__new__(HttpWebSocketRobotClient)
                client.server_url = "http://localhost:5000"
                client._last_status_error = None
                client._last_status_error_logged_at = 0.0
                client._get_execution_ws_status = MagicMock(return_value=None)
                client._mark_unavailable = MagicMock()
                client._mark_available = MagicMock()
                with (
                    patch(f"{module}.requests.get") as get,
                    patch(f"{module}.time.monotonic", return_value=0.0) as clock,
                    patch(f"{module}.logger") as log,
                ):
                    get.side_effect = ConnectionError("bridge down")
                    self.assertIsNone(client.get_status())
                    clock.return_value = 9.9
                    self.assertIsNone(client.get_status())
                    self.assertEqual(log.error.call_count, 1)
                    clock.return_value = 10.0
                    self.assertIsNone(client.get_status())
                    self.assertEqual(log.error.call_count, 2)
                    get.side_effect = TimeoutError("bridge timeout")
                    self.assertIsNone(client.get_status())
                    self.assertEqual(log.error.call_count, 3)
                    self.assertEqual(client._mark_unavailable.call_count, 4)

                    status = {"is_executing": False}
                    if recovery_transport == "websocket":
                        client._get_execution_ws_status.return_value = status
                    else:
                        get.side_effect = None
                        get.return_value = MagicMock(status_code=200)
                        get.return_value.json.return_value = status
                    self.assertEqual(client.get_status(), status)

                    client._get_execution_ws_status.return_value = None
                    get.side_effect = TimeoutError("bridge timeout")
                    self.assertIsNone(client.get_status())
                    self.assertEqual(log.error.call_count, 4)
                    self.assertTrue(log.error.call_args.kwargs["exc_info"])

    def test_execution_methods_enforce_integer_completion_contract(self):
        robot = object.__new__(Ros2Robot)
        robot._client = MagicMock()
        operations = [
            (lambda blocking: robot.execute_trajectory([], blocking=blocking), "execute_path"),
            (lambda blocking: robot.execute_motion_sequence([], 0, 0, blocking=blocking), "execute_sequence"),
            (lambda blocking: robot.execute_custom_motion_sequence([], 0, 0, blocking=blocking), "execute_ordered_motion_chain"),
            (lambda blocking: robot.execute_ordered_motion_chain([], 0, 0, blocking=blocking), "execute_ordered_motion_chain"),
        ]
        for invoke, client_method in operations:
            for value in (None, False, True, "0", 0.0, 1, 2, -12, 0):
                with self.subTest(method=client_method, value=value):
                    getattr(robot._client, client_method).return_value = value
                    expected = value if type(value) is int and value <= 0 else -1
                    self.assertEqual(invoke(True), expected)
            getattr(robot._client, client_method).return_value = 2
            self.assertEqual(invoke(False), 2)

    def test_motion_response_rejects_contradictions_and_non_integer_codes(self):
        client = object.__new__(HttpWebSocketRobotClient)
        client._mark_available = MagicMock()
        client._mark_startup_failure_if_present = MagicMock()
        for status, raw, blocking, expected in [
            (500, {"result": 0}, True, -1),
            (200, {"result": 0, "success": False}, True, -1),
            (200, {"result": 1}, True, -1),
            (202, {"result": 2, "queued": True}, False, 2),
            (200, {"result": "0"}, True, -1),
            (200, {"result": 0.0}, True, -1),
            (200, {"result": None}, True, -1),
            (200, {"result": False}, True, -1),
            (200, {"result": True}, True, 0),
            (503, {"result": -12, "success": False}, True, -12),
            (200, {"result": 0}, True, 0),
        ]:
            with self.subTest(status=status, raw=raw, blocking=blocking):
                response = MagicMock(status_code=status)
                self.assertEqual(client._parse_motion_response("execute_path", response, raw, blocking=blocking), expected)

    def test_legacy_trajectory_and_simulation_follow_interface(self):
        from src.engine.robot.drivers.fairino.fairino_robot import FairinoRobot
        from src.engine.robot.drivers.fairino.test_robot import TestRobotWrapper

        robot = object.__new__(FairinoRobot)
        robot.robot = MagicMock()
        self.assertEqual(robot.execute_trajectory([], blocking=True, orientation_mode="per_waypoint"), -1)
        robot.robot.execute_path.assert_not_called()
        self.assertEqual(TestRobotWrapper().execute_trajectory([], blocking=True, orientation_mode="per_waypoint"), 0)

    def test_conditional_status_ignores_uncorrelated_execution_snapshot(self):
        client = object.__new__(HttpWebSocketRobotClient)
        client._sensor_ws_lock = threading.Lock()
        client._conditional_servo_latest = {
            "operation_id": "current-operation",
            "state": "moving",
        }
        client._get_execution_ws_status = MagicMock(return_value={
            "conditional_servo": {"operation_id": None, "state": "idle"},
        })

        status = client.get_conditional_servo_status()

        self.assertEqual(status["operation_id"], "current-operation")
        self.assertEqual(status["state"], "moving")

    @patch("src.engine.robot.drivers.client_adapters.http_websocket.requests.get")
    def test_init_sets_disconnected_state_when_bridge_is_unavailable(self, get_mock):
        get_mock.side_effect = ConnectionError("bridge down")

        client = HttpWebSocketRobotClient(server_url="http://localhost:5000")

        self.assertEqual(client.get_connection_state(), "disconnected")
        self.assertIn("bridge down", client.get_connection_details()["last_error"])

    @patch("src.engine.robot.drivers.client_adapters.http_websocket.requests.get")
    def test_successful_health_check_marks_client_available(self, get_mock):
        response = MagicMock()
        response.json.return_value = {"status": "ok"}
        get_mock.return_value = response

        client = HttpWebSocketRobotClient(server_url="http://localhost:5000")

        self.assertEqual(client.get_connection_state(), "idle")
        self.assertIsNone(client.get_connection_details()["last_error"])

    @patch("src.engine.robot.drivers.client_adapters.http_websocket.requests.post")
    @patch("src.engine.robot.drivers.client_adapters.http_websocket.requests.get")
    def test_rejected_active_tool_is_available_to_state_reporting(self, get_mock, post_mock):
        health = MagicMock()
        health.status_code = 200
        health.json.return_value = {"status": "ok"}
        get_mock.return_value = health
        response = MagicMock()
        response.status_code = 400
        response.json.return_value = {
            "success": False,
            "error": "tool_id 1 maps to unknown tool 'TOOL_1'",
        }
        post_mock.return_value = response

        client = HttpWebSocketRobotClient(server_url="http://localhost:5000")

        self.assertFalse(client.set_active_tool(1))
        self.assertEqual(
            client.get_connection_details()["last_command_error"],
            "tool_id 1 maps to unknown tool 'TOOL_1'",
        )

    @patch("src.engine.robot.drivers.client_adapters.http_websocket.requests.get")
    def test_starting_health_check_reports_starting_state(self, get_mock):
        response = MagicMock()
        response.json.return_value = {
            "status": "initializing_runtime",
            "phase": "initializing_runtime",
            "message": "ROS runtime is initializing",
            "ready": False,
            "error": None,
        }
        get_mock.return_value = response

        client = HttpWebSocketRobotClient(server_url="http://localhost:5000")

        self.assertEqual(client.get_connection_state(), "starting")
        details = client.get_connection_details()
        self.assertEqual(details["startup"]["phase"], "initializing_runtime")
        self.assertIn("ROS runtime is initializing", details["last_error"])

    @patch("src.engine.robot.drivers.client_adapters.http_websocket.requests.post")
    @patch("src.engine.robot.drivers.client_adapters.http_websocket.requests.get")
    def test_stop_motion_treats_no_active_motion_as_benign(self, get_mock, post_mock):
        health = MagicMock()
        health.status_code = 200
        health.json.return_value = {"status": "ok"}
        get_mock.return_value = health
        response = MagicMock()
        response.json.return_value = {
            "stop_state": "NO_ACTIVE_MOTION",
            "stopped": False,
            "result": -1,
            "success": True,
        }
        post_mock.return_value = response

        client = HttpWebSocketRobotClient(server_url="http://localhost:5000")

        self.assertEqual(client.stop_motion(), 0)
        self.assertEqual(client.get_last_stop_response()["stop_state"], "NO_ACTIVE_MOTION")

    @patch("src.engine.robot.drivers.client_adapters.http_websocket.requests.post")
    @patch("src.engine.robot.drivers.client_adapters.http_websocket.requests.get")
    def test_stop_motion_returns_unconfirmed_code_when_stop_not_confirmed(self, get_mock, post_mock):
        health = MagicMock()
        health.json.return_value = {"status": "ok"}
        get_mock.return_value = health
        response = MagicMock()
        response.json.return_value = {
            "stop_state": "STOP_REQUESTED_BUT_UNCONFIRMED",
            "stopped": False,
            "result": 1,
            "success": False,
            "error": "robot executing but no cancellable goal handle was available",
        }
        post_mock.return_value = response

        client = HttpWebSocketRobotClient(server_url="http://localhost:5000")

        self.assertEqual(client.stop_motion(), -2)
        self.assertEqual(client.get_last_stop_response()["stop_state"], "STOP_REQUESTED_BUT_UNCONFIRMED")

    @patch("src.engine.robot.drivers.client_adapters.http_websocket.requests.post")
    @patch("src.engine.robot.drivers.client_adapters.http_websocket.requests.get")
    def test_move_linear_sets_active_tool_before_motion(self, get_mock, post_mock):
        health = MagicMock()
        health.status_code = 200
        health.json.return_value = {"status": "ok"}
        drive_status = MagicMock()
        drive_status.status_code = 200
        drive_status.json.return_value = {
            "success": True,
            "actual_enabled": True,
            "motion_allowed_by_drive_enable": True,
        }
        get_mock.side_effect = [health, drive_status]
        active_response = MagicMock()
        active_response.status_code = 200
        active_response.json.return_value = {"success": True, "tool_name": "TOOL_1"}
        enable_response = MagicMock()
        enable_response.status_code = 200
        enable_response.json.return_value = {
            "success": True,
            "result": 0,
            "actual_enabled": True,
            "motion_allowed_by_drive_enable": True,
        }
        move_response = MagicMock()
        move_response.status_code = 200
        move_response.text = '{"success": true, "result": 0}'
        move_response.json.return_value = {"success": True, "result": 0}
        post_mock.side_effect = [active_response, enable_response, move_response]

        client = HttpWebSocketRobotClient(server_url="http://localhost:5000")

        self.assertEqual(client.move_liner([1, 2, 3, 4, 5, 6], tool=1), 0)
        self.assertEqual(post_mock.call_args_list[0].args[0], "http://localhost:5000/tool/active")
        self.assertEqual(post_mock.call_args_list[0].kwargs["json"], {"tool_id": 1})
        self.assertEqual(post_mock.call_args_list[1].args[0], "http://localhost:5000/drive/enable")
        self.assertEqual(post_mock.call_args_list[2].args[0], "http://localhost:5000/move/linear")

    @patch("src.engine.robot.drivers.client_adapters.http_websocket.requests.post")
    def test_recovery_jog_marker_is_sent_only_for_explicit_recovery(self, post_mock):
        client = object.__new__(HttpWebSocketRobotClient)
        client.server_url = "http://localhost:5000"
        client._drive_enabled = True
        client.set_active_tool = MagicMock(return_value=True)
        client._motion_preflight_error = MagicMock(return_value=None)
        client._mark_execution_request_sent = MagicMock(return_value=0.0)
        client._mark_execution_request_response = MagicMock()
        client._parse_motion_response = MagicMock(return_value=0)
        post_mock.return_value.json.return_value = {"success": True, "result": 0}
        post_mock.return_value.text = "{}"

        for recovery in (False, True):
            with self.subTest(recovery=recovery):
                result = client.move_liner(
                    [1, 2, 3, 4, 5, 6],
                    allow_collision_recovery=True, recovery_jog=recovery,
                )
                self.assertEqual(result, 0)
                payload = post_mock.call_args.kwargs["json"]
                self.assertTrue(payload["allow_collision_recovery"])
                self.assertEqual(payload.get("recovery_jog", False), recovery)
                self.assertEqual("recovery_jog" in payload, recovery)

    @patch("src.engine.robot.drivers.client_adapters.http_websocket.requests.get")
    def test_current_position_failure_does_not_mark_client_available(self, get_mock):
        health = MagicMock()
        health.status_code = 200
        health.json.return_value = {"status": "ok"}
        unavailable = MagicMock()
        unavailable.status_code = 503
        unavailable.json.return_value = {"success": False, "error": "current position unavailable"}
        get_mock.side_effect = [health, unavailable]

        client = HttpWebSocketRobotClient(server_url="http://localhost:5000")
        client._mark_unavailable("starting", state="starting")

        self.assertIsNone(client.get_current_position())
        self.assertEqual(client._connection_state, "starting")

    @patch("src.engine.robot.drivers.client_adapters.http_websocket.requests.post")
    @patch("src.engine.robot.drivers.client_adapters.http_websocket.requests.get")
    def test_blocking_ordered_chain_rejects_non_final_response(self, get_mock, post_mock):
        health = MagicMock()
        health.status_code = 200
        health.json.return_value = {"status": "ok"}
        drive = MagicMock()
        drive.status_code = 200
        drive.json.return_value = {
            "success": True,
            "actual_enabled": True,
            "motion_allowed_by_drive_enable": True,
        }
        get_mock.side_effect = [health, drive]

        response = MagicMock()
        response.status_code = 202
        response.json.return_value = {
            "success": True,
            "accepted": True,
            "final": False,
            "queued": False,
            "result": 0,
            "task_id": 42,
        }
        post_mock.return_value = response

        client = HttpWebSocketRobotClient(server_url="http://localhost:5000")
        client._drive_enabled = True

        result = client.execute_ordered_motion_chain(
            [{"type": "linear", "position": [1, 2, 3, 4, 5, 6]}],
            blocking=True,
        )

        self.assertEqual(result, -1)
        self.assertEqual(client.get_last_execute_path_response()["task_id"], 42)
        self.assertFalse(client.get_last_execute_path_response()["final"])

    @patch("src.engine.robot.drivers.client_adapters.http_websocket.requests.post")
    @patch("src.engine.robot.drivers.client_adapters.http_websocket.requests.get")
    def test_ordered_chain_preserves_explicit_ik_planning_rejection(self, get_mock, post_mock):
        error = "ordered-chain planning failed: Ordered PTP segment 'Plate entry: passage gate to plate center' rejected: no IK candidates found"
        response = MagicMock(status_code=500)
        response.json.return_value = {
            "success": False, "result": -1, "error": error, "detail": error,
            "error_info": {"code": "motion_error_1", "message": error},
        }
        post_mock.return_value = response
        client = object.__new__(HttpWebSocketRobotClient)
        client.server_url = "http://localhost:5000"
        client._drive_enabled = True
        client._motion_preflight_error = MagicMock(return_value=None)
        client._mark_execution_request_sent = MagicMock(return_value=0.0)
        client._mark_execution_request_response = MagicMock()
        client._execution_ws_lock = threading.Lock()
        client._execution_ws_latest = {"is_executing": False}
        client._execution_ws_last_at = 100.0
        client._mark_available = MagicMock()
        terminal = {"is_executing": False, "ordered_motion_chain": {
            "active": False, "phase": "error", "error": error,
            "planned_segments_count": 0, "executed_segments_count": 0,
        }}
        get_mock.return_value = MagicMock(status_code=200)
        get_mock.return_value.json.return_value = terminal

        with patch("src.engine.robot.drivers.client_adapters.http_websocket.time.monotonic", return_value=100.01):
            result = client.execute_ordered_motion_chain(
                [{"type": "ptp", "position": [0, 0, 200, 180, 0, 0]}], blocking=True,
            )
            status = client.get_status()

        self.assertEqual(-1, result)
        self.assertEqual(error, client.get_last_motion_error())
        self.assertEqual(terminal, status)
        get_mock.assert_called_once_with("http://localhost:5000/status", timeout=2)

    @patch("src.engine.robot.drivers.client_adapters.http_websocket.requests.post")
    @patch("src.engine.robot.drivers.client_adapters.http_websocket.requests.get")
    def test_prepared_start_mismatch_response_is_preserved(self, get_mock, post_mock):
        health = MagicMock()
        health.status_code = 200
        health.json.return_value = {"status": "ok"}
        get_mock.return_value = health
        response = MagicMock()
        response.status_code = 409
        response.json.return_value = {
            "success": False,
            "error": "prepared chain start mismatch: xyz_error_mm=2.557",
        }
        post_mock.return_value = response

        client = HttpWebSocketRobotClient(server_url="http://localhost:5000")

        result = client.execute_prepared_ordered_motion_chain("plan-1")

        self.assertEqual(result["error"], "prepared chain start mismatch: xyz_error_mm=2.557")

    @patch("src.engine.robot.drivers.client_adapters.http_websocket.requests.post")
    @patch("src.engine.robot.drivers.client_adapters.http_websocket.requests.get")
    def test_controlled_stop_sends_optional_duration(self, get_mock, post_mock):
        health = MagicMock()
        health.status_code = 200
        health.json.return_value = {"status": "ok"}
        get_mock.return_value = health
        response = MagicMock()
        response.status_code = 200
        response.json.return_value = {
            "success": True,
            "stopped": True,
            "future_work_preserved": True,
        }
        post_mock.return_value = response

        client = HttpWebSocketRobotClient(server_url="http://localhost:5000")
        client.controlled_stop(42, stop_duration_s=0.20)

        self.assertEqual(
            post_mock.call_args.kwargs["json"],
            {"expected_task_id": 42, "stop_duration_s": 0.20},
        )

    @patch("src.engine.robot.drivers.client_adapters.http_websocket.requests.Session.get")
    @patch("src.engine.robot.drivers.client_adapters.http_websocket.requests.get")
    def test_partial_kinematics_snapshot_is_returned(self, get_mock, session_get_mock):
        health = MagicMock()
        health.status_code = 200
        health.json.return_value = {"status": "ok"}
        get_mock.return_value = health

        response = MagicMock()
        response.status_code = 206
        response.json.return_value = {
            "success": False,
            "partial": True,
            "position": [1, 2, 3, 4, 5, 6],
            "unavailable_fields": ["velocity"],
        }
        session_get_mock.return_value = response

        client = HttpWebSocketRobotClient(server_url="http://localhost:5000")

        self.assertEqual(client.get_state_snapshot()["position"], [1, 2, 3, 4, 5, 6])

    def test_fake_client_factory_selects_fake_backend(self):
        client = build_robot_client(server_url="fake://local")

        self.assertIsInstance(client, FakeRobotClient)
        self.assertEqual(client.get_connection_state(), "idle")

    def test_fake_client_updates_position_and_reports_execution_info(self):
        client = build_robot_client(server_url="fake://local")

        self.assertEqual(client.move_liner([1, 2, 3, 4, 5, 6], blocking=True), 0)
        self.assertEqual(client.get_current_position(), [1.0, 2.0, 3.0, 4.0, 5.0, 6.0])

        self.assertEqual(client.execute_path([[1, 2, 3, 4, 5, 6], [7, 8, 9, 10, 11, 12]], blocking=False), 0)
        self.assertEqual(client.get_last_execute_path_response()["task_id"], 1)
        self.assertTrue(client.get_status()["is_executing"])

        self.assertEqual(client.stop_motion(), 0)
        self.assertFalse(client.get_status()["is_executing"])

    def test_fake_robot_exposes_state_snapshot_for_platform_polling(self):
        robot = Ros2Robot(server_url="fake://local")

        snapshot = robot.get_state_snapshot()

        self.assertEqual(snapshot["position"], [0.0] * 6)
        self.assertEqual(snapshot["velocity"], [0.0] * 3)
        self.assertEqual(snapshot["velocity_magnitude"], 0.0)
        self.assertEqual(snapshot["acceleration"], 0.0)

    def test_ros2_robot_forwards_scoped_servo_collision_override(self):
        robot = object.__new__(Ros2Robot)
        robot._client = MagicMock()
        robot._client.start_servo_jog.return_value = 0

        result = robot.start_servo_jog(
            "Z",
            "PLUS",
            linear_mm_s=5.0,
            frame="user",
            tool=1,
            user=1,
            disable_collision_checking=True,
        )

        self.assertEqual(0, result)
        robot._client.start_servo_jog.assert_called_once_with(
            "Z",
            "PLUS",
            linear_mm_s=5.0,
            angular_deg_s=None,
            frame="user",
            tool=1,
            user=1,
            disable_collision_checking=True,
        )

    def test_ros2_robot_serializes_typed_ordered_commands_at_client_boundary(self):
        robot = object.__new__(Ros2Robot)
        robot._client = MagicMock()
        robot._client.execute_ordered_motion_chain.return_value = 0
        command = OrderedPositionCommand(
            label="approach",
            motion_type=OrderedMotionType.PTP,
            position=(1.0, 2.0, 3.0, 4.0, 5.0, 6.0),
            profile=OrderedMotionProfile(20.0, 30.0, 0.0),
        )

        result = robot.execute_ordered_motion_chain([command], tool=1, user=2)

        self.assertEqual(result, 0)
        robot._client.execute_ordered_motion_chain.assert_called_once_with(
            segments=[{
                "label": "approach",
                "vel": 20.0,
                "acc": 30.0,
                "blendR": 0.0,
                "type": "ptp",
                "position": [1.0, 2.0, 3.0, 4.0, 5.0, 6.0],
            }],
            tool=1,
            user=2,
            blocking=False,
            trajectory_optimizer="Ruckig",
        )

    def test_health_check_error_logging_is_throttled_across_client_instances(self):
        HttpWebSocketRobotClient._GLOBAL_LAST_HEALTH_ERROR = None
        HttpWebSocketRobotClient._GLOBAL_LAST_HEALTH_ERROR_LOGGED_AT = 0.0
        first = object.__new__(HttpWebSocketRobotClient)
        second = object.__new__(HttpWebSocketRobotClient)
        first._last_health_error = None
        first._last_health_error_logged_at = 0.0
        second._last_health_error = None
        second._last_health_error_logged_at = 0.0

        with patch("src.engine.robot.drivers.client_adapters.http_websocket.logger") as log:
            first._log_health_check_error(ConnectionError("bridge down"))
            second._log_health_check_error(ConnectionError("bridge down"))

        log.warning.assert_called_once()
        log.debug.assert_called_once()
