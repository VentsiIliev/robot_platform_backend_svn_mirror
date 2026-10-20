from abc import ABC, abstractmethod
from typing import Optional
from src.engine.core.i_health_checkable import IHealthCheckable
from .i_motion_service import IMotionService
from .i_robot_lifecycle import IRobotLifecycle
from ..motion_sequence import OrderedMotionInput


class IRobotService(IMotionService, IRobotLifecycle, IHealthCheckable, ABC):
    """Full robot service interface."""

    @abstractmethod
    def get_current_velocity(self) -> float: ...

    @abstractmethod
    def get_current_acceleration(self) -> float: ...

    @abstractmethod
    def get_state(self) -> str: ...

    @abstractmethod
    def get_state_topic(self) -> str: ...

    @abstractmethod
    def execute_trajectory(
        self,
        path,
        rx: float = 180,
        ry: float = 0,
        rz: float = 0,
        vel: float = 0.1,
        acc: float = 0.1,
        blocking: bool = False,
        orientation_mode: str = "constant",
    ) -> int:
        """Return an integer motion code (never bool or None).

        Blocking: 0 means completed; negative means failure. Nonblocking:
        0 means accepted for immediate execution, positive means queue position,
        and negative means failure. Acceptance does not establish completion.
        """
        ...

    def execute_ordered_motion_chain(
        self,
        segments: list[OrderedMotionInput],
        tool: int,
        user: int,
        blocking: bool = False,
    ) -> int:
        """Return an integer motion code (never bool or None).

        Blocking: 0 means completed; negative means failure. Nonblocking:
        0 means accepted for immediate execution, positive means queue position,
        and negative means failure. Acceptance does not establish completion.
        """
        return -1

    def prepare_ordered_motion_chain(self, segments: list[OrderedMotionInput], start_position, tool, user, *,
                                     allow_servo_during_prepare=False):
        return None

    def execute_prepared_ordered_motion_chain(self, plan_id):
        return None

    def discard_prepared_ordered_motion_chain(self, plan_id):
        return None

    def get_prepared_ordered_motion_chain(self, plan_id):
        return None

    def get_execution_status(self):
        return None

    def get_last_trajectory_command_info(self):
        return None

    def start_collision_calibration_recording(self) -> dict:
        return {"success": False, "error": "recording_not_supported"}

    def stop_collision_calibration_recording(self) -> dict:
        return {"success": False, "error": "recording_not_supported"}

    def set_collision_detection_suppressed(self, suppressed: bool) -> dict:
        """Temporarily suppress sensorless collision detection for recovery motion."""
        return {"success": False, "error": "collision_suppression_unsupported"}

    def get_collision_monitor_config(self) -> dict:
        return {"success": False, "error": "collision_monitor_config_unsupported"}

    def update_collision_monitor_config(self, config: dict) -> dict:
        return {"success": False, "error": "collision_monitor_config_unsupported"}

    def get_rviz_status(self) -> dict:
        """Read the backend-owned RViz process state without changing robot motion."""
        return {"success": False, "error": "rviz_control_unsupported"}

    def set_rviz_enabled(self, enabled: bool) -> dict:
        """Start or stop only the backend-owned visualization process."""
        return {"success": False, "error": "rviz_control_unsupported"}

    def open_collision_monitor_diagnostics(self) -> dict:
        return {"success": False, "error": "collision_monitor_diagnostics_unsupported"}

    def unwind_joint6(
        self,
        blocking: bool = True,
        queue_if_busy: bool = True,
        vel: float | None = None,
        acc: float | None = None,
    ) -> bool:
        return False

    @abstractmethod
    def enable_safety_walls(self) -> bool: ...

    @abstractmethod
    def disable_safety_walls(self) -> bool: ...

    @abstractmethod
    def are_safety_walls_enabled(self) -> Optional[bool]: ...

    @abstractmethod
    def get_safety_walls_status(self) -> dict: ...

    @abstractmethod
    def validate_pose(
        self,
        start_position,
        target_position,
        tool: int = 0,
        user: int = 0,
        start_joint_state: dict | None = None,
    ) -> dict: ...

    @abstractmethod
    def set_active_tool(self, tool: int) -> bool: ...

    def get_backend_configuration(self, section):
        raise NotImplementedError("Backend configuration is unsupported")

    def update_backend_configuration(self, section, changes, expected_revision, *, tool_id=None):
        raise NotImplementedError("Backend configuration is unsupported")

    def get_tool_registry(self):
        return None

    def set_active_workobject(self, user: int) -> bool:
        return True

    def get_workobject_registry(self):
        return None

    def update_workobject_registry(self, user_id, name=None, transform=None, persist=False):
        return -1

    def is_healthy(self) -> bool:
        """Healthy = robot is not in error state."""
        return self.get_connection_state() not in ("disconnected", "starting", "error", "fault")

    def get_connection_state(self) -> str:
        """Optional lifecycle/availability state for the underlying transport."""
        return self.get_state()

    def get_connection_details(self) -> dict:
        """Optional diagnostic details about the underlying transport state."""
        return {}

    def get_drive_status(self) -> dict:
        """Optional drive/fieldbus status from the underlying robot transport."""
        return {}

    @abstractmethod
    def set_digital_output(self, port_id: int, value: bool) -> bool: ...
