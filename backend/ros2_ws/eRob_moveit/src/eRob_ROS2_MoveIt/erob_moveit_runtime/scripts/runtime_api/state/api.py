from __future__ import annotations
import logging
from runtime_api.contracts import ApiResponse, api_operation, response_error
from runtime_api.common import ApiSettings
from runtime_gateway.base import RuntimeGateway
from .responses import StateResponse


logger = logging.getLogger(__name__)

class StateApi:
    """State operations shared by HTTP and future gateway transports."""

    def __init__(self, gateway: RuntimeGateway, settings: ApiSettings = ApiSettings(), *, startup_status_getter=None):
        self._gateway = gateway
        self._settings = settings
        self._port = settings.port
        self._startup_status_getter = startup_status_getter

    @api_operation("state.prepared_ordered_motion_chain_status")
    def prepared_ordered_motion_chain_status(self, plan_id: str) -> ApiResponse[StateResponse]:
        from .requests import plan_identifier
        plan_id = plan_identifier(plan_id)
        try:
            return ApiResponse({"success": True, **self._gateway.prepared_ordered_motion_chain_status(plan_id)}, 200)
        except KeyError as exc:
            return response_error(str(exc), 404)

    @api_operation("state.current_position_sample")
    def current_position_sample(self) -> ApiResponse[StateResponse]:
        sample = self._gateway.get_current_position_sample()
        if sample is None:
            return response_error("timestamped position feedback unavailable", 503)
        return ApiResponse({"success": True, **sample})

    @api_operation("state.current_position")
    def current_position(self) -> ApiResponse[StateResponse]:
        pos = self._gateway.get_current_position()
        if pos is None:
            return response_error("current position unavailable", 503)
        return ApiResponse({"success": True, "position": pos})

    @api_operation("state.base_tcp_position")
    def base_tcp_position(self) -> ApiResponse[StateResponse]:
        pos = self._gateway.get_current_base_tcp_position()
        if pos is None:
            return response_error("current base TCP position unavailable", 503)
        return ApiResponse({"success": True, "position": pos})

    @api_operation("state.flange_position")
    def flange_position(self) -> ApiResponse[StateResponse]:
        pos = self._gateway.get_current_flange_position()
        if pos is None:
            return response_error("current flange position unavailable", 503)
        return ApiResponse({"success": True, "position": pos})

    @api_operation("state.current_velocity")
    def current_velocity(self) -> ApiResponse[StateResponse]:
        vel = self._gateway.get_current_velocity()
        if vel is None:
            return response_error("current velocity unavailable", 503)
        return ApiResponse({"success": True, "velocity": vel})

    @api_operation("state.status")
    def status(self) -> ApiResponse[StateResponse]:
        return ApiResponse(self._gateway.status())

    @api_operation("state.ordered_motion_chain_status")
    def ordered_motion_chain_status(self) -> ApiResponse[StateResponse]:
        status = self._gateway.ordered_motion_chain_status()
        if status.get("supported") is False:
            return ApiResponse({"success": True, "supported": False, "active": False})
        success = not status.get("error")
        return ApiResponse({**status, "success": success}, 200 if success else 500)

    @api_operation("state.state_snapshot")
    def state_snapshot(self) -> ApiResponse[StateResponse]:
        return ApiResponse(self._gateway.state_snapshot())

    @api_operation("state.state_kinematics")
    def state_kinematics(self) -> ApiResponse[StateResponse]:
        result = self._gateway.state_kinematics()
        if result.get("error") is not None:
            return ApiResponse(result, 503)
        unavailable = result.get("unavailable_fields", [])
        return ApiResponse(result, 200 if not unavailable else 206)

    @api_operation("state.conditional_servo_status")
    def conditional_servo_status(self) -> ApiResponse[StateResponse]:
        return ApiResponse({"success": True, "conditional_servo": self._gateway.conditional_servo_status()})


    @api_operation('state.startup_status')
    def startup_status(self) -> ApiResponse[StateResponse]:
        body = self._startup_status_getter() if self._startup_status_getter else self._gateway.startup_status()
        return ApiResponse(body, 500 if body.get('error') else 200)

    @api_operation('state.health')
    def health(self) -> ApiResponse[StateResponse]:
        response = self.startup_status()
        body = dict(response.body)
        body['status'] = 'error' if body.get('error') else 'ok' if body.get('ready') else body.get('phase', 'starting')
        return ApiResponse(body, response.status)
