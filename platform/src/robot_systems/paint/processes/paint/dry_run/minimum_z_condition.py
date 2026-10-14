from __future__ import annotations

import logging

_logger = logging.getLogger(__name__)


def accepts_minimum_z_result(*, enabled: bool, result: object) -> bool:
    """Return whether a dry-run descent boundary represents simulated contact."""
    return bool(
        enabled
        and str(getattr(result, "message", ""))
        in {"minimum_z_reached", "minimum_z_reached_before_servo"}
    )


class DryRunMinimumZPickupCondition:
    """Latch pickup success when real robot Z reaches the configured lower limit."""

    def __init__(self, robot_service, minimum_z_mm: float, tolerance_mm: float = 0.5) -> None:
        self._robot = robot_service
        self._minimum_z_mm = float(minimum_z_mm)
        self._tolerance_mm = max(0.0, float(tolerance_mm))
        self._latched = False

    def on_servo_start(self) -> None:
        self._latched = False
        _logger.warning(
            "[DRY_RUN] Minimum-Z pickup condition armed limit_z=%.3f",
            self._minimum_z_mm,
        )

    def is_active(self) -> bool:
        if self._latched:
            return True
        pose = self._robot.get_current_position()
        if pose is None or len(pose) < 3:
            raise RuntimeError("Dry-run pickup could not read the robot Z position")
        self._latched = float(pose[2]) <= self._minimum_z_mm + self._tolerance_mm
        return self._latched
