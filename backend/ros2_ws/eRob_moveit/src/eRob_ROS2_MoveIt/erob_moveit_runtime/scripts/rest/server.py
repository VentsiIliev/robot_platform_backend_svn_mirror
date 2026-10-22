#!/usr/bin/env python3
"""
ROS2 Bridge Server - Exposes the shared MoveIt robot backend via REST API.
"""
import os
import atexit
import logging
import socket
import sys
import threading
import time

from flask import Flask, Response, jsonify, request
import rclpy
from rclpy.executors import MultiThreadedExecutor

from robot_controller import RobotController
from backend.backend_factory import create_robot_backend
from backend.i_robot_backend import IRobotBackend
from runtime_api.handlers import RuntimeApi
from runtime_api.contracts import response_error
from rest.routes.common import install_http_contract, to_http
from runtime_gateway.local import LocalRuntimeGateway
from runtime_websockets.execution_server import start_execution_websocket_server
from runtime_websockets.state_server import start_state_websocket_server
from runtime_websockets.sensor_server import start_sensor_websocket_server
from motion.servo.conditional_servo import ConditionalServoSupervisor
from rest.openapi import OPENAPI_SPEC, SWAGGER_HTML
from runtime_gateway.adapters.rviz_process import RvizProcessManager
import config

LOG_FILE = config.REST_LOG
logger = logging.getLogger("erob_moveit_rest_server")
logger.setLevel(logging.INFO)
logging.getLogger("werkzeug").setLevel(logging.WARNING)

if not logger.handlers:
    file_handler = logging.FileHandler(LOG_FILE)
    formatter = logging.Formatter(
        "%(asctime)s [%(levelname)s] %(message)s"
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

def _to_jsonable(value):
    """Convert nested ROS / numpy-ish values into plain JSON-safe Python types."""
    if isinstance(value, dict):
        return {str(k): _to_jsonable(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_to_jsonable(v) for v in value]
    if hasattr(value, "item") and callable(getattr(value, "item")):
        try:
            return _to_jsonable(value.item())
        except Exception:
            pass
    return value

def _response_error(message: str, status_code: int, **extra):
    return to_http(response_error(message, status_code, **extra))

def _http_status_for_state(state: str | None, default: int = 500) -> int:
    if state in {"HARDWARE_NOT_READY"}:
        return 503
    if state in {"UNSUPPORTED"}:
        return 501
    return default

def _as_dict(value, error_message: str) -> dict:
    value = _to_jsonable(value)
    if isinstance(value, dict):
        return value
    return {"success": False, "error": error_message}

def _configured_tcp_servers(host: str, port: int) -> list[tuple[str, str, int]]:
    servers = [("REST HTTP", str(host), int(port))]
    if bool(getattr(config, "REST_WS_STATE_ENABLED", True)):
        servers.append((
            "state WebSocket",
            config.REST_WS_STATE_HOST,
            config.REST_WS_STATE_PORT,
        ))
    if bool(getattr(config, "REST_WS_EXECUTION_ENABLED", True)):
        servers.append((
            "execution WebSocket",
            config.REST_WS_EXECUTION_HOST,
            config.REST_WS_EXECUTION_PORT,
        ))
    if bool(getattr(config, "REST_WS_SENSOR_ENABLED", True)):
        servers.append((
            "sensor WebSocket",
            config.REST_WS_SENSOR_HOST,
            config.REST_WS_SENSOR_PORT,
        ))
    return servers

def _assert_tcp_servers_available(servers: list[tuple[str, str, int]]) -> None:
    seen: set[tuple[str, int]] = set()
    conflicts = []
    for name, bind_host, bind_port in servers:
        key = (bind_host, bind_port)
        if key in seen:
            continue
        seen.add(key)
        family = socket.AF_INET6 if ":" in bind_host else socket.AF_INET
        with socket.socket(family, socket.SOCK_STREAM) as probe:
            probe.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            try:
                probe.bind((bind_host, bind_port))
            except OSError as exc:
                conflicts.append(f"{name} {bind_host}:{bind_port} ({exc.strerror or exc})")
    if conflicts:
        conflict_text = "; ".join(conflicts)
        raise RuntimeError(
            "REST runtime cannot start because required TCP port(s) are unavailable: "
            f"{conflict_text}"
        )

def start_rest_server(
    robot: IRobotBackend | None = None,
    node: RobotController | None = None,
    host: str = config.REST_HOST,
    port: int = config.REST_PORT,
    start_ros: bool = True,
    runtime_initializer=None,
    allow_starting_without_robot: bool = False,
):
    """
    Start REST server.

    Modes:
    - Standalone: start_ros=True, robot=None
    - Embedded:   start_ros=False, robot provided
    """

    app = Flask(__name__)
    install_http_contract(app)
    def update_rviz_markers(running):
        if node is not None and rclpy.ok():
            node.set_rviz_visualization_enabled(running)

    rviz_manager = RvizProcessManager(on_state_changed=update_rviz_markers)
    # Gateway owns injected diagnostic resources and closes them on shutdown.

    def start_initial_rviz():
        if os.environ.get("ZEROERR_USE_RVIZ", "false").strip().lower() in {"1", "true", "yes", "on"}:
            result = rviz_manager.set_enabled(True)
            if not result.get("success"):
                logger.warning("RViz startup failed: %s", result.get("error"))

    startup_lock = threading.Lock()
    startup_state = {
        "phase": "initializing_http",
        "message": "HTTP server is starting",
        "ready": False,
        "error": None,
        "started_at": time.time(),
        "updated_at": time.time(),
    }

    def update_startup_status(phase: str, message: str | None = None, **extra):
        with startup_lock:
            startup_state.update({
                "phase": phase,
                "message": message if message is not None else phase,
                "updated_at": time.time(),
            })
            startup_state.update(extra)

    conditional_servo = ConditionalServoSupervisor(
        lambda: robot,
        logger=logger,
        monitor_rate_hz=50.0,
    )

    gateway = LocalRuntimeGateway(
        robot_getter=lambda: robot,
        node_getter=lambda: node,
        conditional_servo=conditional_servo,
        rviz_manager=rviz_manager,
    )

    atexit.register(gateway.close)

    try:
        _assert_tcp_servers_available(_configured_tcp_servers(host, port))
    except RuntimeError as exc:
        update_startup_status("error", str(exc), ready=False, error=str(exc))
        logger.error(str(exc))
        raise

    def get_startup_status():
        with startup_lock:
            status = dict(startup_state)
        status['robot_release'] = {'target': os.environ.get('ROBOT_RELEASE_TARGET'),
                                   'profile': os.environ.get('ZEROERR_ACTIVE_PROFILE')}
        runtime_status = gateway.startup_status()
        status["ros2_active"] = bool(runtime_status.get("ros2_active", False))
        if status.get("error") is not None:
            return status
        if runtime_status.get("ros2_active"):
            motion_stack_ready = bool(runtime_status.get("motion_stack_ready", False))
            status["motion_stack_ready"] = motion_stack_ready
            if motion_stack_ready:
                status["phase"] = "ready"
                status["message"] = "Robot runtime is ready"
                status["ready"] = True
                status["motion_stack_fault"] = None
            else:
                status["phase"] = "motion_stack_warming"
                status["message"] = "Robot runtime is initialized; motion stack is still warming up"
                status["ready"] = False
                status["motion_stack_fault"] = runtime_status.get("motion_stack_fault")
        return status

    # ------------------------------------------------------------------
    # ROS2 initialization (standalone mode)
    # ------------------------------------------------------------------

    executor = None

    if start_ros:
        rclpy.init()
        node = RobotController()

        executor = MultiThreadedExecutor()
        executor.add_node(node)

        def ros_spin():
            executor.spin()

        threading.Thread(target=ros_spin, daemon=True).start()

        node.wait_for_monitor(timeout_sec=config.MONITOR_WAIT_TIMEOUT_S)

        robot = create_robot_backend(node=node, workobject=None, ip="0.0.0.0")

        time.sleep(1.0)

    if runtime_initializer is not None:
        def initialize_runtime():
            nonlocal robot, node
            try:
                update_startup_status(
                    "initializing_runtime",
                    "ROS runtime is initializing",
                )
                initialized = runtime_initializer(update_startup_status)
                if initialized is not None:
                    robot, node = initialized
                if robot is None or node is None:
                    raise RuntimeError("runtime initializer did not return a robot and node")
                start_initial_rviz()
                update_startup_status(
                    "runtime_initialized",
                    "Robot runtime is initialized; waiting for motion stack",
                    ready=False,
                    error=None,
                )
            except Exception as exc:
                update_startup_status(
                    "error",
                    f"Runtime initialization failed: {exc}",
                    ready=False,
                    error=str(exc),
                )
                logger.exception("Runtime initialization failed")

        threading.Thread(
            target=initialize_runtime,
            daemon=True,
            name="RuntimeInitializer",
        ).start()

    if runtime_initializer is None and node is not None:
        start_initial_rviz()

    if robot is None and runtime_initializer is None and not allow_starting_without_robot:
        raise RuntimeError("REST server started without a robot instance")

    @app.before_request
    def require_runtime_ready():
        if request.url_rule is None:
            return None
        allowed_endpoints = {"health", "startup_status", "swagger_docs", "openapi_json", "static"}
        endpoint = (request.endpoint or "").rsplit(".", 1)[-1]
        if (request.blueprint == "backend_configuration"
                or endpoint in allowed_endpoints
                or request.method == "GET" and endpoint in {"get_tool_registry", "get_workobject_registry"}):
            return None
        if robot is None or node is None:
            return to_http(response_error('Robot runtime is still starting', 503,
                                          code='runtime_unavailable', retryable=True,
                                          startup=get_startup_status()))
        return None

    # ------------------------------------------------------------------
    # Routes
    # ------------------------------------------------------------------

    @app.route("/docs", methods=["GET"])
    @app.route("/api/docs", methods=["GET"])
    def swagger_docs():
        return Response(SWAGGER_HTML, mimetype="text/html")

    @app.route("/openapi.json", methods=["GET"])
    def openapi_json():
        return jsonify(OPENAPI_SPEC)

    runtime_api = RuntimeApi(
        robot_getter=lambda: robot,
        node_getter=lambda: node,
        startup_status_getter=get_startup_status,
        runtime_state_snapshot_getter=gateway.runtime_state_snapshot,
        port=port,
        gateway=gateway,
        conditional_servo=conditional_servo,
    )

    from rest.routes.configuration import configuration_blueprint
    from rest.routes.motion import motion_blueprint
    from rest.routes.state import state_blueprint
    from rest.routes.control import control_blueprint
    app.register_blueprint(configuration_blueprint(runtime_api.configuration))
    app.register_blueprint(motion_blueprint(runtime_api.motion))
    app.register_blueprint(state_blueprint(runtime_api.state))
    app.register_blueprint(control_blueprint(runtime_api.control))

    # ------------------------------------------------------------------
    # Run server
    # ------------------------------------------------------------------

    logger.info("=" * 60)
    logger.info("eRob MoveIt Runtime Server")
    logger.info(f"Server running on http://{host}:{port}")
    update_startup_status("http_ready", "HTTP server is ready for startup polling")
    start_state_websocket_server(
        robot=robot,
        node=node,
        config=config,
        fallback_host=host,
        fallback_port=port,
        robot_getter=lambda: robot,
        node_getter=lambda: node,
    )
    start_execution_websocket_server(
        robot=robot,
        node=node,
        config=config,
        fallback_host=host,
        fallback_port=port,
        robot_getter=lambda: robot,
        node_getter=lambda: node,
        conditional_servo=conditional_servo,
    )
    start_sensor_websocket_server(
        supervisor=conditional_servo,
        config=config,
        fallback_host=host,
        fallback_port=port,
    )
    logger.info("=" * 60)

    with open(LOG_FILE, "a") as f:
        sys.stdout = f
        sys.stderr = f
        try:
            app.run(host=host, port=port, threaded=True, use_reloader=False)
        finally:
            gateway.close()
