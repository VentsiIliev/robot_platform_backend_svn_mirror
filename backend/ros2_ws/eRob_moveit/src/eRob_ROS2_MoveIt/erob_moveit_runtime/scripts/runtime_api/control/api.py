from __future__ import annotations
import logging
import time
from typing import Any
from runtime_api.contracts import ApiResponse, api_operation, response_error, to_jsonable
from runtime_api.common import ApiSettings, as_dict, http_status_for_state
from runtime_gateway.base import RuntimeGateway
from .responses import ControlResponse


logger = logging.getLogger(__name__)

class ControlApi:
    """Control operations shared by HTTP and future gateway transports."""

    def __init__(self, gateway: RuntimeGateway, settings: ApiSettings = ApiSettings()):
        self._gateway = gateway
        self._settings = settings
        self._port = settings.port

    @api_operation("control.safety_walls_enabled")
    def safety_walls_enabled(self) -> ApiResponse[ControlResponse]:
        body = as_dict(self._gateway.get_safety_walls_status(), "invalid safety wall status")
        success = not body.get("error")
        return ApiResponse({**body, "success": success, "enabled": bool(body.get("enabled", False))}, 200 if success else 503)

    @api_operation("control.safety_walls_status")
    def safety_walls_status(self) -> ApiResponse[ControlResponse]:
        body = as_dict(self._gateway.get_safety_walls_status(), "invalid safety wall status")
        success = not body.get("error")
        return ApiResponse({**body, "success": success}, 200 if success else 503)

    @api_operation("control.enable_safety_walls")
    def enable_safety_walls(self) -> ApiResponse[ControlResponse]:
        body = as_dict(self._gateway.enable_safety_walls(), "invalid safety wall status")
        success = bool(body.get("enabled", False)) and not body.get("error")
        return ApiResponse({**body, "success": success}, 200 if success else 500)

    @api_operation("control.disable_safety_walls")
    def disable_safety_walls(self) -> ApiResponse[ControlResponse]:
        body = as_dict(self._gateway.disable_safety_walls(), "invalid safety wall status")
        success = not bool(body.get("enabled", True)) and not body.get("error")
        return ApiResponse({**body, "success": success}, 200 if success else 500)

    @api_operation("control.motion_passage_status")
    def motion_passage_status(self, passage_id: str | None = None) -> ApiResponse[ControlResponse]:
        body = as_dict(
            self._gateway.get_motion_passage_status(passage_id),
            "invalid motion passage status",
        )
        return ApiResponse(body, 200 if body.get("success") else 404)

    @api_operation("control.set_motion_passage_closed")
    def set_motion_passage_closed(self, passage_id: str, data: dict[str, Any] | None) -> ApiResponse[ControlResponse]:
        if not isinstance(data, dict) or not isinstance(data.get("closed"), bool):
            return response_error("request requires boolean 'closed'", 400)
        body = as_dict(
            self._gateway.set_motion_passage_closed(passage_id, data["closed"]),
            "invalid motion passage status",
        )
        return ApiResponse(body, 200 if body.get("success") else 404)

    @api_operation("control.set_digital_output")
    def set_digital_output(self, data: dict[str, Any] | None) -> ApiResponse[ControlResponse]:
        from .requests import DigitalOutputRequest
        request = DigitalOutputRequest.parse(data)
        port, value = request.port, request.value

        result = self._gateway.set_digital_output(port, value)
        if result == 0:
            return ApiResponse({"result": 0, "success": True, "port": port, "value": value})
        return ApiResponse({"result": result, "success": False, "port": port, "value": value}, 500)

    @api_operation("control.drive_command_response")
    def drive_command_response(self, command_result: dict, desired_enabled: bool) -> ApiResponse[ControlResponse]:
        command_result = to_jsonable(command_result)
        if not isinstance(command_result, dict):
            return ApiResponse({
                "success": False,
                "command_accepted": False,
                "desired_enabled": bool(desired_enabled),
                "error": f"unexpected drive command result type: {type(command_result).__name__}",
            }, 500)
        command_accepted = bool(command_result.get("success", False))
        if command_result.get("state") == "NOT_REQUIRED_FAKE_HARDWARE":
            return ApiResponse({
                **command_result,
                "success": True,
                "command_accepted": True,
                "desired_enabled": bool(desired_enabled),
                "verified": True,
                "verification_skipped": True,
                "message": "Drive enable verification is not required in fake hardware mode",
            }, 200)
        verify_timeout_s = max(self._settings.drive_verify_timeout_s, 0.1)
        verify_deadline = time.monotonic() + verify_timeout_s
        drive_status = self._gateway.drive_operation_status()

        while command_accepted and time.monotonic() < verify_deadline:
            actual_enabled = bool(drive_status.get("actual_enabled", False))
            requested_enabled = bool(drive_status.get("requested_enabled", False))
            if desired_enabled and actual_enabled and requested_enabled:
                break
            if not desired_enabled and not actual_enabled and not requested_enabled:
                break
            time.sleep(0.05)
            drive_status = self._gateway.drive_operation_status()
            if not drive_status.get("success", True):
                break

        actual_enabled = bool(drive_status.get("actual_enabled", False))
        requested_enabled = bool(drive_status.get("requested_enabled", False))
        verified = actual_enabled and requested_enabled if desired_enabled else not actual_enabled and not requested_enabled
        response = {
            **drive_status,
            "success": bool(command_accepted and verified),
            "command_accepted": command_accepted,
            "desired_enabled": bool(desired_enabled),
            "request": command_result,
        }
        if response["success"]:
            return ApiResponse(response)
        if not command_accepted:
            response["error"] = str(command_result.get("error") or "drive command was rejected")
            return ApiResponse(response, http_status_for_state(command_result.get("state")))
        response["error"] = (
            "drive enable command accepted, but drives are not operation_enabled"
            if desired_enabled
            else "drive disable command accepted, but drives still report operation_enabled"
        )
        return response_error(response['error'], 202, code='drive_verification_pending', source='controller',
                              outcome_unknown=True, details={'actual_enabled': actual_enabled,
                              'requested_enabled': requested_enabled, 'desired_enabled': desired_enabled},
                              **{key: value for key, value in response.items() if key not in {'error', 'success'}})

    @api_operation("control.enable_drive_operation")
    def enable_drive_operation(self) -> ApiResponse[ControlResponse]:
        result = self._gateway.set_drive_operation_enabled(True)
        return self.drive_command_response(result, desired_enabled=True)

    @api_operation("control.disable_drive_operation")
    def disable_drive_operation(self) -> ApiResponse[ControlResponse]:
        result = self._gateway.set_drive_operation_enabled(False)
        return self.drive_command_response(result, desired_enabled=False)

    @api_operation("control.drive_operation_status")
    def drive_operation_status(self) -> ApiResponse[ControlResponse]:
        return ApiResponse(self._gateway.drive_operation_status())

    @api_operation("control.motion_interlock_status")
    def motion_interlock_status(self) -> ApiResponse[ControlResponse]:
        return ApiResponse({"success": True, **self._gateway.motion_interlock_status()})

    @api_operation("control.reset_motion_interlock")
    def reset_motion_interlock(self) -> ApiResponse[ControlResponse]:
        body = self._gateway.reset_motion_interlock()
        return ApiResponse(body, 200 if body.get('success') else 409)

    @api_operation('control.start_collision_recording')
    def start_collision_recording(self) -> ApiResponse[ControlResponse]:
        body = self._gateway.start_collision_recording()
        return ApiResponse(body, 200 if body.get('success') else 409)

    @api_operation('control.stop_collision_recording')
    def stop_collision_recording(self) -> ApiResponse[ControlResponse]:
        body = self._gateway.stop_collision_recording()
        return ApiResponse(body, 200 if body.get('success') else 409)

    @api_operation('control.set_collision_suppression')
    def set_collision_suppression(self, data: dict[str, Any] | None) -> ApiResponse[ControlResponse]:
        from .requests import boolean_field
        return ApiResponse(self._gateway.set_collision_suppressed(boolean_field(data, 'suppressed')))

    @api_operation('control.rviz_status')
    def rviz_status(self) -> ApiResponse[ControlResponse]:
        return ApiResponse(self._gateway.rviz_status())

    @api_operation('control.set_rviz_enabled')
    def set_rviz_enabled(self, data: dict[str, Any] | None) -> ApiResponse[ControlResponse]:
        from .requests import boolean_field
        body = self._gateway.set_rviz_enabled(boolean_field(data, 'enabled'))
        return ApiResponse(body, 200 if body.get('success') else 503)

    @api_operation('control.open_collision_diagnostics')
    def open_collision_diagnostics(self) -> ApiResponse[ControlResponse]:
        return ApiResponse(self._gateway.open_collision_diagnostics())
