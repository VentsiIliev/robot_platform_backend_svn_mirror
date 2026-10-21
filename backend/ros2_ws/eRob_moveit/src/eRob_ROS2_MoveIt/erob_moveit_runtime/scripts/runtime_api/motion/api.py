from __future__ import annotations
import logging
import math
import time
from typing import Any
from runtime_api.contracts import ApiResponse, api_operation, response_error
from runtime_api.common import ApiSettings
from runtime_gateway.base import RuntimeGateway
from runtime_gateway.errors import GatewayError
from runtime_api.control.requests import identifier
from .responses import MotionResponse
from .requests import (
    parse_cartesian_servo_start_request,
    parse_cartesian_servo_update_request,
    parse_execute_ordered_motion_chain_request,
    parse_execute_path_request,
    parse_execute_sequence_request,
    parse_jog_request,
    parse_joint_jog_request,
    parse_move_linear_request,
    parse_prepare_ordered_motion_chain_request,
    parse_servo_jog_start_request,
    parse_servo_jog_to_z_request,
)
from .responses import motion_error
from motion.servo.cartesian_servo.i_cartesian_servo import CartesianServoResult
from status.servo_stop_timing import register_stop


logger = logging.getLogger(__name__)

class MotionApi:
    """Motion operations shared by HTTP and future gateway transports."""

    def __init__(self, gateway: RuntimeGateway, settings: ApiSettings = ApiSettings()):
        self._gateway = gateway
        self._settings = settings
        self._port = settings.port

    def _task_id(self):
        return self._gateway.last_submitted_task_id()

    def _motion_result(self, result: int, *, blocking: bool = True) -> ApiResponse[MotionResponse]:
        task_id = self._task_id()
        if result > 0:
            return ApiResponse({
                "result": result,
                "success": True,
                "queued": True,
                "accepted": True,
                "final": False,
                "queue_position": result,
                "task_id": task_id,
            }, 202)
        if result == 0:
            return ApiResponse({
                "result": result,
                "success": True,
                "queued": False,
                "accepted": True,
                "final": bool(blocking),
                "task_id": task_id,
            }, 200 if blocking else 202)
        return motion_error(result, **({"detail": self._gateway.last_motion_error()} if self._gateway.last_motion_error() else {}))

    def _fast_lin_result(self, result: int, *, blocking: bool) -> ApiResponse[MotionResponse]:
        gateway = self._gateway
        task_id = gateway.last_submitted_task_id()
        if result < 0:
            detail = gateway.last_motion_error()
            outcome_unknown = bool(detail and "eventual outcome is unknown" in detail)
            return motion_error(
                result,
                queued=False,
                task_id=task_id,
                accepted=outcome_unknown,
                final=not outcome_unknown,
                **({"detail": detail} if detail else {}),
            )
        if blocking:
            return ApiResponse({
                "result": 0,
                "success": True,
                "queued": False,
                "task_id": task_id,
                "accepted": True,
                "final": True,
                "message": "Fast LIN planning and trajectory execution completed successfully",
            }, 200)

        queued = result > 0
        body = {
            "result": result,
            "success": True,
            "queued": queued,
            "task_id": task_id,
            "accepted": True,
            "final": False,
            "message": (
                "Fast LIN request queued; planning and execution have not completed"
                if queued else
                "Fast LIN request accepted; planning and execution have not completed"
            ),
        }
        if queued:
            body["queue_position"] = result
        return ApiResponse(body, 202)

    def _require_motion_stack_ready(self) -> ApiResponse[MotionResponse] | None:
        gateway = self._gateway
        if not gateway.is_runtime_initialized():
            return response_error("robot runtime is still starting", 503)
        if gateway.is_motion_stack_ready():
            return None
        return response_error(
            "motion stack is not ready",
            503,
            motion_stack_ready=False,
            motion_stack_fault=gateway.get_motion_stack_fault_reason(),
            startup=self._gateway.startup_status(),
            runtime=self._gateway.runtime_state_snapshot(),
        )

    @api_operation("motion.move_linear")
    def move_linear(self, data: dict[str, Any] | None) -> ApiResponse[MotionResponse]:
        payload = parse_move_linear_request(data, defaults=self._settings.motion_defaults)
        not_ready = self._require_motion_stack_ready()
        if not_ready is not None:
            return not_ready

        logger.info("Received move/linear request with data %s", data)
        result = self._gateway.move_linear(
            payload["position"],
            tool=payload["tool"],
            user=payload["user"],
            vel=payload["vel"],
            acc=payload["acc"],
            blocking=payload["blocking"],
            trajectory_optimizer=payload["trajectory_optimizer"],
            allow_collision_recovery=payload["allow_collision_recovery"],
        )
        return self._motion_result(result, blocking=payload["blocking"])

    @api_operation("motion.move_fast_lin")
    def move_fast_lin(self, data: dict[str, Any] | None) -> ApiResponse[MotionResponse]:
        """Run the same LIN request through Pilz instead of CartesianPath."""
        payload = parse_move_linear_request(data, defaults=self._settings.motion_defaults)
        not_ready = self._require_motion_stack_ready()
        if not_ready is not None:
            return not_ready

        logger.info("Received move/fast_lin request with data %s", data)
        result = self._gateway.move_fast_lin(
            payload["position"],
            tool=payload["tool"],
            user=payload["user"],
            vel=payload["vel"],
            acc=payload["acc"],
            blocking=payload["blocking"],
            trajectory_optimizer=payload["trajectory_optimizer"],
        )
        return self._fast_lin_result(result, blocking=bool(payload["blocking"]))

    @api_operation("motion.move_ptp")
    def move_ptp(self, data: dict[str, Any] | None) -> ApiResponse[MotionResponse]:
        payload = parse_move_linear_request(data, defaults=self._settings.motion_defaults)
        not_ready = self._require_motion_stack_ready()
        if not_ready is not None:
            return not_ready

        logger.info("Received move/ptp request with data %s", data)
        result = self._gateway.move_ptp(
            payload["position"],
            tool=payload["tool"],
            user=payload["user"],
            vel=payload["vel"],
            acc=payload["acc"],
            blocking=payload["blocking"],
            trajectory_optimizer=payload["trajectory_optimizer"],
        )
        return self._motion_result(result, blocking=payload["blocking"])

    @api_operation("motion.execute_path")
    def execute_path(self, data: dict[str, Any] | None) -> ApiResponse[MotionResponse]:
        payload = parse_execute_path_request(data, defaults=self._settings.motion_defaults)
        not_ready = self._require_motion_stack_ready()
        if not_ready is not None:
            return not_ready

        logger.info(
            f"Executing path with {len(payload['path'])} waypoints, vel={payload['vel']}, acc={payload['acc']}"
        )
        result = self._gateway.execute_path(
            payload["path"],
            rx=payload["rx"],
            ry=payload["ry"],
            rz=payload["rz"],
            vel=payload["vel"],
            acc=payload["acc"],
            blocking=payload["blocking"],
            trajectory_optimizer=payload["trajectory_optimizer"],
            orientation_mode=payload["orientation_mode"],
        )
        return self._motion_result(result, blocking=payload["blocking"])

    @api_operation("motion.execute_sequence")
    def execute_sequence(self, data: dict[str, Any] | None) -> ApiResponse[MotionResponse]:
        payload = parse_execute_sequence_request(data, defaults=self._settings.motion_defaults)
        not_ready = self._require_motion_stack_ready()
        if not_ready is not None:
            return not_ready

        logger.info(f"Executing sequence with {len(payload['segments'])} segments")
        result = self._gateway.execute_sequence(
            payload["segments"],
            tool=payload["tool"],
            user=payload["user"],
            blocking=payload["blocking"],
        )

        task_id = self._task_id()
        if result > 0:
            return ApiResponse({
                "result": result,
                "success": True,
                "accepted": True,
                "final": False,
                "state": "QUEUED",
                "queued": True,
                "queue_position": result,
                "task_id": task_id,
                "status_ws": "/ws/execution",
                "status_ws_port": self._settings.execution_ws_port,
                "message": "sequence queued; subscribe to /ws/execution for current_task_id, last_completed_task_id, and last_completed_result",
            }, 202)
        if result == 0:
            if payload["blocking"]:
                return ApiResponse({
                    "result": result,
                    "success": True,
                    "accepted": True,
                    "final": True,
                    "state": "COMPLETED",
                    "queued": False,
                    "task_id": task_id,
                }, 200)
            return ApiResponse({
                "result": result,
                "success": True,
                "accepted": True,
                "final": False,
                "state": "ACCEPTED_ASYNC",
                "queued": False,
                "task_id": task_id,
                "status_ws": "/ws/execution",
                "status_ws_port": self._settings.execution_ws_port,
                "message": "sequence accepted; planning/execution completes asynchronously, subscribe to /ws/execution for final result",
            }, 202)
        return motion_error(result, accepted=False, final=True, state="REJECTED", queued=False, task_id=task_id)

    @api_operation("motion.execute_ordered_motion_chain")
    def execute_ordered_motion_chain(self, data: dict[str, Any] | None) -> ApiResponse[MotionResponse]:
        payload = parse_execute_ordered_motion_chain_request(data, defaults=self._settings.motion_defaults)
        not_ready = self._require_motion_stack_ready()
        if not_ready is not None:
            return not_ready

        logger.info(
            f"Executing ordered motion chain with {len(payload['segments'])} segments"
        )
        result = self._gateway.execute_ordered_motion_chain(
            segments=payload["segments"],
            tool=payload["tool"],
            user=payload["user"],
            blocking=payload["blocking"],
            trajectory_optimizer=payload["trajectory_optimizer"],
        )
        return self._motion_result(result, blocking=payload["blocking"])

    @api_operation("motion.prepare_ordered_motion_chain")
    def prepare_ordered_motion_chain(self, data: dict[str, Any] | None) -> ApiResponse[MotionResponse]:
        try:
            payload = parse_prepare_ordered_motion_chain_request(data, defaults=self._settings.motion_defaults)
            result = self._gateway.prepare_ordered_motion_chain(
                segments=payload["segments"], start_position=payload["start_position"],
                tool=payload["tool"], user=payload["user"],
                trajectory_optimizer=payload["trajectory_optimizer"],
                allow_servo_during_prepare=payload["allow_servo_during_prepare"],
            )
            return ApiResponse({"success": True, **result}, 202)
        except GatewayError:
            raise
        except (ValueError, RuntimeError) as exc:
            return response_error(str(exc), 409 if isinstance(exc, RuntimeError) else 400)

    @api_operation("motion.execute_prepared_ordered_motion_chain")
    def execute_prepared_ordered_motion_chain(self, plan_id: str) -> ApiResponse[MotionResponse]:
        from runtime_api.state.requests import plan_identifier
        plan_id = plan_identifier(plan_id)
        try:
            result = self._gateway.execute_prepared_ordered_motion_chain(plan_id)
            success = result.get("state") == "completed" and result.get("result") == 0
            return ApiResponse({"success": success, **result}, 200 if success else 500)
        except GatewayError:
            raise
        except KeyError as exc:
            return response_error(str(exc), 404)
        except RuntimeError as exc:
            return response_error(str(exc), 409)

    @api_operation("motion.discard_prepared_ordered_motion_chain")
    def discard_prepared_ordered_motion_chain(self, plan_id: str) -> ApiResponse[MotionResponse]:
        from runtime_api.state.requests import plan_identifier
        plan_id = plan_identifier(plan_id)
        try:
            return ApiResponse({"success": True, **self._gateway.discard_prepared_ordered_motion_chain(plan_id)}, 200)
        except GatewayError:
            raise
        except KeyError as exc:
            return response_error(str(exc), 404)
        except RuntimeError as exc:
            return response_error(str(exc), 409)

    @api_operation("motion.unwind_joint6")
    def unwind_joint6(self, data: dict[str, Any] | None) -> ApiResponse[MotionResponse]:
        from .requests import parse_unwind_request
        payload = parse_unwind_request(data, defaults=self._settings.motion_defaults)
        blocking, queue_if_busy = payload['blocking'], payload['queue_if_busy']
        vel, acc = payload['vel'], payload['acc']
        not_ready = self._require_motion_stack_ready()
        if not_ready is not None:
            return not_ready

        result = self._gateway.unwind_joint6(
            blocking=blocking,
            queue_if_busy=queue_if_busy,
            vel=vel,
            acc=acc,
        )
        return self._motion_result(result, blocking=blocking)

    @api_operation("motion.active_tool")
    def active_tool(self) -> ApiResponse[MotionResponse]:
        return ApiResponse({"success": True, "tool_name": self._gateway.active_tool_name()})

    @api_operation("motion.set_active_tool")
    def set_active_tool(self, data: dict[str, Any] | None) -> ApiResponse[MotionResponse]:
        payload = data or {}
        if "tool_id" in payload:
            tool_name = self._gateway.set_active_tool_by_id(payload.get("tool_id"))
        else:
            tool_name = str(payload.get("name") or payload.get("tool_name") or "").strip()
            if not tool_name:
                raise ValueError("tool_id or tool_name is required")
            tool_name = self._gateway.set_active_tool(tool_name)
        return ApiResponse({"success": True, "tool_name": tool_name})

    @api_operation("motion.active_workobject")
    def active_workobject(self) -> ApiResponse[MotionResponse]:
        return ApiResponse({"success": True, **self._gateway.active_workobject()})

    @api_operation("motion.set_active_workobject")
    def set_active_workobject(self, data: dict[str, Any] | None) -> ApiResponse[MotionResponse]:
        payload = data or {}
        if "user_id" not in payload:
            raise ValueError("user_id is required")
        active = self._gateway.set_active_workobject(identifier(payload.get("user_id"), "user_id"))
        return ApiResponse({"success": True, **active})

    @api_operation("motion.validate_pose")
    def validate_pose(self, data: dict[str, Any] | None) -> ApiResponse[MotionResponse]:
        payload = data or {}
        target_position = payload.get("target_position") or payload.get("position")
        start_position = payload.get("start_position")
        logger.info(
            "REST /reachability/pose request: "
            f"start={start_position} target={target_position} "
            f"tool={payload.get('tool', 0)} user={payload.get('user', 0)} "
            f"has_seed_joint_state={bool(payload.get('start_joint_state'))}"
        )
        if not target_position or len(target_position) != 6:
            return response_error("Invalid target_position format", 400, reachable=False)
        if start_position is None:
            start_position = self._gateway.get_current_position()
        if not start_position or len(start_position) != 6:
            return response_error("Invalid or unavailable start_position", 400, reachable=False)

        result = self._gateway.validate_pose(
            start_position=start_position,
            target_position=target_position,
            tool=payload.get("tool", 0),
            user=payload.get("user", 0),
            start_joint_state_payload=payload.get("start_joint_state"),
        )
        http_status = 200 if result.get("reachable") else 409 if result.get("reason") == "cartesian_path_partial" else 400
        log_fn = logger.info if result.get("reachable") else logger.warning
        log_fn(f"REST /reachability/pose response: http={http_status} result={result}")
        return ApiResponse({**result, "success": bool(result.get("reachable"))}, http_status)

    @api_operation("motion.stop_motion")
    def stop_motion(self) -> ApiResponse[MotionResponse]:
        body = self._gateway.stop_motion()
        return ApiResponse(body, 200 if body.get('success') else 409)

    @api_operation("motion.controlled_stop")
    def controlled_stop(self, data: dict[str, Any] | None) -> ApiResponse[MotionResponse]:
        from .requests import parse_controlled_stop_request
        payload = parse_controlled_stop_request(data)
        task_id, stop_duration_s = payload['expected_task_id'], payload['stop_duration_s']
        result = self._gateway.controlled_stop(
            task_id, stop_duration_s=stop_duration_s
        )
        return ApiResponse(result, 200 if result.get("success") else 409)

    @api_operation("motion.set_workobject")
    def set_workobject(self, data: dict[str, Any] | None) -> ApiResponse[MotionResponse]:
        from .requests import _coerce_pose6
        payload = data or {}
        origin = _coerce_pose6(payload.get('origin'), 'origin')
        user_id = identifier(payload.get('user_id', 0), 'user_id')
        self._gateway.set_workobject(origin, user_id=user_id)
        return ApiResponse({"success": True, "origin": origin, "user_id": user_id})

    @api_operation("motion.jog")
    def jog(self, data: dict[str, Any] | None) -> ApiResponse[MotionResponse]:
        payload = parse_jog_request(data, defaults=self._settings.motion_defaults)
        not_ready = self._require_motion_stack_ready()
        if not_ready is not None:
            return not_ready
        result = self._gateway.jog(
            payload["axis"],
            payload["direction"],
            payload["step"],
            payload["vel"],
            payload["acc"],
            frame=payload["frame"],
            tool=payload["tool"],
            user=payload["user"],
        )
        if result == 0:
            return ApiResponse({"result": result, "success": True})
        return motion_error(result)

    @api_operation("motion.joint_jog")
    def joint_jog(self, data: dict[str, Any] | None) -> ApiResponse[MotionResponse]:
        payload = parse_joint_jog_request(data, defaults=self._settings.motion_defaults)
        not_ready = self._require_motion_stack_ready()
        if not_ready is not None:
            return not_ready
        result = self._gateway.joint_jog(
            payload["joint"],
            payload["direction"],
            payload["step"],
            payload["vel"],
            payload["acc"],
            blocking=payload["blocking"],
        )
        if result == 0:
            return ApiResponse({"result": result, "success": True})
        return motion_error(result)

    @api_operation("motion.servo_jog_start")
    def servo_jog_start(self, data: dict[str, Any] | None) -> ApiResponse[MotionResponse]:
        payload = parse_servo_jog_start_request(data, defaults=self._settings.motion_defaults)
        not_ready = self._require_motion_stack_ready()
        if not_ready is not None:
            return not_ready
        result = self._gateway.servo_jog_start(
            payload["axis"],
            payload["direction"],
            payload["vel"],
            payload["acc"],
            frame=payload["frame"],
            tool=payload["tool"],
            user=payload["user"],
            linear_mm_s=payload["linear_mm_s"],
            angular_deg_s=payload["angular_deg_s"],
            disable_collision_checking=payload["disable_collision_checking"],
        )
        if result == 0:
            return ApiResponse({"result": result, "success": True, "state": "running"})
        return motion_error(result)

    @api_operation("motion.servo_jog_stop")
    def servo_jog_stop(self, data: dict[str, Any] | None = None) -> ApiResponse[MotionResponse]:
        payload = data or {}
        handler_enter_ns = time.monotonic_ns()
        trace_id = str(payload.get("timing_trace_id") or f"servo-stop-{handler_enter_ns}")
        route_enter_ns = payload.get("_ros_http_route_enter_ns")
        if not isinstance(route_enter_ns, int):
            route_enter_ns = handler_enter_ns
        timing = {
            "ros_http_route_enter_ns": route_enter_ns,
            "ros_handler_enter_ns": handler_enter_ns,
        }
        restore_collision_checking = payload.get("restore_collision_checking", True)
        if not isinstance(restore_collision_checking, bool):
            return ApiResponse(
                {"result": -1, "success": False, "error": "Invalid 'restore_collision_checking'; expected boolean"},
                400,
            )
        register_stop(trace_id, timing)
        timing["backend_stop_call_ns"] = time.monotonic_ns()
        result = self._gateway.servo_jog_stop(
            restore_collision_checking=restore_collision_checking
        )
        timing["backend_stop_return_ns"] = time.monotonic_ns()
        logger.info(
            "[SERVO_STOP_TIMING] trace_id=%s event=stop_handler_complete "
            "monotonic_ns=%d since_ros_receive_ms=%.3f details=%s",
            trace_id,
            timing["backend_stop_return_ns"],
            (timing["backend_stop_return_ns"] - route_enter_ns) / 1_000_000.0,
            timing,
        )
        if result == 0:
            return ApiResponse({
                "result": result,
                "success": True,
                "state": "stopped",
                "timing_trace_id": trace_id,
                "timing": timing,
            })
        return motion_error(result)

    @api_operation("motion.conditional_servo_start")
    def conditional_servo_start(self, data: dict[str, Any] | None) -> ApiResponse[MotionResponse]:
        payload = dict(data or {})
        execution_mode = str(payload.get('execution_mode') or 'servo').strip().lower()
        if execution_mode not in {'servo', 'fast_lin'}:
            raise ValueError('execution_mode must be servo or fast_lin')
        servo = parse_servo_jog_start_request(payload.get('servo'), defaults=self._settings.motion_defaults)
        not_ready = self._require_motion_stack_ready()
        if not_ready is not None:
            return not_ready
        restore = payload.get('restore_collision_checking', True)
        if type(restore) is not bool:
            raise ValueError('restore_collision_checking must be a boolean')
        snapshot = self._gateway.conditional_servo_start({
            'servo': servo, 'execution_mode': execution_mode,
            'fast_lin': dict(payload.get('fast_lin') or {}), 'condition': dict(payload.get('condition') or {}),
            'boundary': payload.get('boundary'), 'timeout_s': payload.get('timeout_s', 10.0),
            'sensor_stale_timeout_s': payload.get('sensor_stale_timeout_s', 0.5),
            'restore_collision_checking': restore,
        })
        success = snapshot.get('state') not in {'start_failed', 'stop_failed'}
        return ApiResponse({'result': 0 if success else -1, 'success': success, 'conditional_servo': snapshot}, 200 if success else 409)


    @api_operation("motion.conditional_servo_cancel")
    def conditional_servo_cancel(self) -> ApiResponse[MotionResponse]:
        return ApiResponse({"success": True, "conditional_servo": self._gateway.conditional_servo_cancel()})


    @api_operation("motion.servo_jog_to_z")
    def servo_jog_to_z(self, data: dict[str, Any] | None) -> ApiResponse[MotionResponse]:
        payload = parse_servo_jog_to_z_request(data, defaults=self._settings.motion_defaults)
        not_ready = self._require_motion_stack_ready()
        if not_ready is not None:
            return not_ready
        result = self._gateway.servo_jog_to_z(**payload)
        return ApiResponse(result, 200 if result.get("success") else 409)

    def _cartesian_servo_result(
            self,
            result: CartesianServoResult,
    ) -> ApiResponse[MotionResponse]:

        status = self._gateway.cartesian_servo_status()

        status_body = None
        if status is not None:
            status_body = {
                "state": status.state.value,
                "frame": status.frame.value if status.frame else None,
                "tool": status.tool,
                "command": (
                    {
                        "linear_mm_s": list(status.command.linear_mm_s),
                        "angular_deg_s": list(status.command.angular_deg_s),
                    }
                    if status.command is not None
                    else None
                ),
                "error": status.error,
            }

        body = {
            "success": result == CartesianServoResult.OK,
            "result": result.value,
            "servo": status_body,
        }

        if result == CartesianServoResult.OK:
            return ApiResponse(body, 200)

        if result in {
            CartesianServoResult.ALREADY_RUNNING,
            CartesianServoResult.NOT_STARTED,
        }:
            return ApiResponse(body, 409)

        if result in {
            CartesianServoResult.INVALID_FRAME,
            CartesianServoResult.INVALID_TOOL,
            CartesianServoResult.INVALID_COMMAND,
        }:
            return ApiResponse(body, 400)

        return ApiResponse(body, 500)

    @api_operation("motion.cartesian_servo_start")
    def cartesian_servo_start(
        self,
        data: dict[str, Any] | None,
    ) -> ApiResponse[MotionResponse]:
        payload = parse_cartesian_servo_start_request(data, defaults=self._settings.motion_defaults)

        not_ready = self._require_motion_stack_ready()
        if not_ready is not None:
            return not_ready

        gateway = self._gateway
        if not gateway.cartesian_servo_available():
            return response_error(
                "Cartesian Servo is not available",
                503,
            )

        logger.info(
            "Received Cartesian Servo start frame=%s tool=%s user=%s",
            payload["frame"].value,
            payload["tool"],
            payload["user"],
        )

        result = gateway.cartesian_servo_start(
            frame=payload["frame"],
            tool=payload["tool"],
            user=payload["user"],
        )

        return self._cartesian_servo_result(result)

    @api_operation("motion.cartesian_servo_update")
    def cartesian_servo_update(
        self,
        data: dict[str, Any] | None,
    ) -> ApiResponse[MotionResponse]:
        payload = parse_cartesian_servo_update_request(data, defaults=self._settings.motion_defaults)

        gateway = self._gateway
        if not gateway.cartesian_servo_available():
            return response_error(
                "Cartesian Servo is not available",
                503,
            )

        result = gateway.cartesian_servo_update(
            linear_mm_s=payload["linear_mm_s"],
            angular_deg_s=payload["angular_deg_s"],
        )

        return self._cartesian_servo_result(result)

    @api_operation("motion.cartesian_servo_stop")
    def cartesian_servo_stop(self) -> ApiResponse[MotionResponse]:
        gateway = self._gateway
        if not gateway.cartesian_servo_available():
            return response_error(
                "Cartesian Servo is not available",
                503,
            )

        logger.info("Received Cartesian Servo stop")

        result = gateway.cartesian_servo_stop()

        return self._cartesian_servo_result(result)
