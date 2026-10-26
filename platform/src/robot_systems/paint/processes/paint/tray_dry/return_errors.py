"""Configuration errors shared by normal dropoff and start recovery routes."""
from src.robot_systems.paint.processes.paint.results import PaintConfigurationError


class MissingReturnWaypointsError(PaintConfigurationError):
    def __init__(self) -> None:
        super().__init__(
            "Plate-layout next-cycle waypoints are enabled but none are configured",
            stage="plate_return_waypoints",
        )


class InvalidReturnWaypointError(PaintConfigurationError):
    def __init__(self, index: int, detail: str) -> None:
        self.waypoint_index = index
        super().__init__(
            f"Plate-layout next-cycle waypoint {index + 1}: {detail}",
            stage="plate_return_waypoints",
        )


class InvalidPlateMotionProfileError(PaintConfigurationError):
    def __init__(self, key: str, detail: str) -> None:
        self.profile_key = key
        super().__init__(
            f"dropoff.plate_motion_profiles[{key}]: {detail}", stage="plate_motion_profile",
        )
