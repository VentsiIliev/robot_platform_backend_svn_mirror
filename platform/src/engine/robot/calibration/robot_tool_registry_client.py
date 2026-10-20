"""Tool configuration adapter using the platform's configured robot connection."""
from typing import Sequence


class RobotToolRegistryClient:
    def __init__(self, robot_service):
        self._robot = robot_service

    def get_tool_registry(self):
        return self._robot.get_tool_registry()

    def get_configuration(self):
        return self._robot.get_backend_configuration("calibration")

    def update_definition(self, tool_id, changes, expected_revision):
        result = self._robot.update_backend_configuration(
            "calibration", changes, expected_revision, tool_id=int(tool_id))
        if result.get("pending_application"):
            return False, result.get("application_error") or "Saved; application is pending. Restart the backend to apply it."
        return True, "Tool geometry saved and applied"

    def update_tool(self, tool_id: int, name: str | None, transform: Sequence[float], *,
                    persist: bool, collision_profile: str | None = None):
        if not persist:
            return False, "Tool geometry must be saved to the backend profile"
        try:
            snapshot = self.get_configuration()
            changes = {"transform": list(transform)}
            if name is not None:
                changes["name"] = name
            if collision_profile is not None:
                changes["collision_profile"] = collision_profile
            return self.update_definition(tool_id, changes, snapshot["revision"])
        except Exception as exc:
            return False, str(exc)

    def get_current_flange_position(self):
        return self._robot.get_current_flange_position()
