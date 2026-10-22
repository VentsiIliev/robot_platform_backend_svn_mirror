"""Compatibility facade composing the four transport-neutral runtime APIs."""
from __future__ import annotations
from typing import Any, Callable
from runtime_api.contracts import ApiResponse, response_error, to_jsonable
from runtime_api.common import ApiSettings, as_dict, http_status_for_state
from runtime_api.motion.responses import motion_error
from runtime_api.configuration.api import ConfigurationApi
from runtime_api.motion.api import MotionApi
from runtime_api.state.api import StateApi
from runtime_api.control.api import ControlApi


class RuntimeApi:
    """Preserves existing entry points while clients migrate to named API groups."""
    def __init__(self, robot_getter=None, node_getter=None, startup_status_getter=None,
                 runtime_state_snapshot_getter=None, *, port=None, gateway=None, conditional_servo=None,
                 settings: ApiSettings | None = None):
        if settings is None:
            import config
            from runtime_api.motion.requests import MotionDefaults
            settings = ApiSettings(port=config.REST_PORT if port is None else port,
                execution_ws_port=config.REST_WS_EXECUTION_PORT,
                drive_verify_timeout_s=float(getattr(config, 'STARTUP_AUTO_ENABLE_DRIVES_VERIFY_TIMEOUT_S', 5.0)),
                motion_defaults=MotionDefaults(config.DEFAULT_VEL_PERCENT, config.DEFAULT_ACC_PERCENT, tuple(config.JOINT_NAMES)))
        if gateway is None:
            from runtime_gateway.local import LocalRuntimeGateway
            gateway = LocalRuntimeGateway(robot_getter=robot_getter, node_getter=node_getter,
                                          conditional_servo=conditional_servo)
        self.configuration = ConfigurationApi(gateway, settings)
        self.motion = MotionApi(gateway, settings)
        self.state = StateApi(gateway, settings, startup_status_getter=startup_status_getter)
        self.control = ControlApi(gateway, settings)

    def move_linear(self, data: dict[str, Any] | None) -> ApiResponse:
        return self.motion.move_linear(data)

    def move_fast_lin(self, data: dict[str, Any] | None) -> ApiResponse:
        return self.motion.move_fast_lin(data)

    def move_ptp(self, data: dict[str, Any] | None) -> ApiResponse:
        return self.motion.move_ptp(data)

    def execute_path(self, data: dict[str, Any] | None) -> ApiResponse:
        return self.motion.execute_path(data)

    def execute_sequence(self, data: dict[str, Any] | None) -> ApiResponse:
        return self.motion.execute_sequence(data)

    def execute_ordered_motion_chain(self, data: dict[str, Any] | None) -> ApiResponse:
        return self.motion.execute_ordered_motion_chain(data)

    def prepare_ordered_motion_chain(self, data: dict[str, Any] | None) -> ApiResponse:
        return self.motion.prepare_ordered_motion_chain(data)

    def execute_prepared_ordered_motion_chain(self, plan_id: str) -> ApiResponse:
        return self.motion.execute_prepared_ordered_motion_chain(plan_id)

    def discard_prepared_ordered_motion_chain(self, plan_id: str) -> ApiResponse:
        return self.motion.discard_prepared_ordered_motion_chain(plan_id)

    def prepared_ordered_motion_chain_status(self, plan_id: str) -> ApiResponse:
        return self.state.prepared_ordered_motion_chain_status(plan_id)

    def unwind_joint6(self, data: dict[str, Any] | None) -> ApiResponse:
        return self.motion.unwind_joint6(data)

    def safety_walls_enabled(self) -> ApiResponse:
        return self.control.safety_walls_enabled()

    def safety_walls_status(self) -> ApiResponse:
        return self.control.safety_walls_status()

    def enable_safety_walls(self) -> ApiResponse:
        return self.control.enable_safety_walls()

    def disable_safety_walls(self) -> ApiResponse:
        return self.control.disable_safety_walls()

    def motion_passage_status(self, passage_id: str | None=None) -> ApiResponse:
        return self.control.motion_passage_status(passage_id)

    def set_motion_passage_closed(self, passage_id: str, data: dict[str, Any] | None) -> ApiResponse:
        return self.control.set_motion_passage_closed(passage_id, data)

    def current_position(self) -> ApiResponse:
        return self.state.current_position()

    def base_tcp_position(self) -> ApiResponse:
        return self.state.base_tcp_position()

    def flange_position(self) -> ApiResponse:
        return self.state.flange_position()

    def tool_registry(self) -> ApiResponse:
        return self.configuration.tool_registry()

    def active_tool(self) -> ApiResponse:
        return self.motion.active_tool()

    def set_active_tool(self, data: dict[str, Any] | None) -> ApiResponse:
        return self.motion.set_active_tool(data)

    def update_tool_registry(self, tool_id: int, data: dict[str, Any] | None) -> ApiResponse:
        return self.configuration.update_tool_registry(tool_id, data)

    def workobject_registry(self) -> ApiResponse:
        return self.configuration.workobject_registry()

    def active_workobject(self) -> ApiResponse:
        return self.motion.active_workobject()

    def set_active_workobject(self, data: dict[str, Any] | None) -> ApiResponse:
        return self.motion.set_active_workobject(data)

    def update_workobject_registry(self, user_id: int, data: dict[str, Any] | None) -> ApiResponse:
        return self.configuration.update_workobject_registry(user_id, data)

    def validate_pose(self, data: dict[str, Any] | None) -> ApiResponse:
        return self.motion.validate_pose(data)

    def current_velocity(self) -> ApiResponse:
        return self.state.current_velocity()

    def stop_motion(self) -> ApiResponse:
        return self.motion.stop_motion()

    def controlled_stop(self, data: dict[str, Any] | None) -> ApiResponse:
        return self.motion.controlled_stop(data)

    def set_workobject(self, data: dict[str, Any] | None) -> ApiResponse:
        return self.motion.set_workobject(data)

    def status(self) -> ApiResponse:
        return self.state.status()

    def ordered_motion_chain_status(self) -> ApiResponse:
        return self.state.ordered_motion_chain_status()

    def state_snapshot(self) -> ApiResponse:
        return self.state.state_snapshot()

    def state_kinematics(self) -> ApiResponse:
        return self.state.state_kinematics()

    def jog(self, data: dict[str, Any] | None) -> ApiResponse:
        return self.motion.jog(data)

    def joint_jog(self, data: dict[str, Any] | None) -> ApiResponse:
        return self.motion.joint_jog(data)

    def servo_jog_start(self, data: dict[str, Any] | None) -> ApiResponse:
        return self.motion.servo_jog_start(data)

    def servo_jog_stop(self, data: dict[str, Any] | None=None) -> ApiResponse:
        return self.motion.servo_jog_stop(data)

    def conditional_servo_start(self, data: dict[str, Any] | None) -> ApiResponse:
        return self.motion.conditional_servo_start(data)

    def conditional_servo_status(self) -> ApiResponse:
        return self.state.conditional_servo_status()

    def conditional_servo_cancel(self) -> ApiResponse:
        return self.motion.conditional_servo_cancel()

    def servo_jog_to_z(self, data: dict[str, Any] | None) -> ApiResponse:
        return self.motion.servo_jog_to_z(data)

    def set_digital_output(self, data: dict[str, Any] | None) -> ApiResponse:
        return self.control.set_digital_output(data)

    def drive_command_response(self, command_result: dict, desired_enabled: bool) -> ApiResponse:
        return self.control.drive_command_response(command_result, desired_enabled)

    def enable_drive_operation(self) -> ApiResponse:
        return self.control.enable_drive_operation()

    def disable_drive_operation(self) -> ApiResponse:
        return self.control.disable_drive_operation()

    def drive_operation_status(self) -> ApiResponse:
        return self.control.drive_operation_status()

    def motion_interlock_status(self) -> ApiResponse:
        return self.control.motion_interlock_status()

    def reset_motion_interlock(self) -> ApiResponse:
        return self.control.reset_motion_interlock()

    def cartesian_servo_start(self, data: dict[str, Any] | None) -> ApiResponse:
        return self.motion.cartesian_servo_start(data)

    def cartesian_servo_update(self, data: dict[str, Any] | None) -> ApiResponse:
        return self.motion.cartesian_servo_update(data)

    def cartesian_servo_stop(self) -> ApiResponse:
        return self.motion.cartesian_servo_stop()
