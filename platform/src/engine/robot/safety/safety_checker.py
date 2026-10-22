import math
from enum import Enum
from typing import List

from ..interfaces.i_safety_checker import ISafetyChecker


class InvalidSettingsServiceError(Exception):
    pass


class SafetyLimitsNotFoundError(Exception):
    pass


class SafetyChecker(ISafetyChecker):

    def __init__(self, settings_key, settings_service=None):
        if not isinstance(settings_key, Enum):
            raise TypeError(
                f"SafetyChecker: settings_key must be an Enum value, got {type(settings_key).__name__!r}. "
                f"Use a constant from settings_ids, not a bare string."
            )

        if settings_service is None:
            raise InvalidSettingsServiceError("SafetyChecker: settings_service cannot be None; it is required for safety limit checks")

        self._settings = settings_service
        self.settings_key = settings_key

    def _compute_violations(self, position: List[float]) -> List[str]:
        if not position or len(position) < 3:
            raise ValueError("Position is empty or has fewer than 3 coordinates")
        if self._settings is None:
            raise InvalidSettingsServiceError("SafetyChecker: settings_service is None; cannot check safety limits")
        config = self._settings.get(self.settings_key)
        limits = getattr(config, "safety_limits", None)
        if limits is None:
            raise SafetyLimitsNotFoundError("SafetyChecker: safety_limits not found in settings")

        # Validate the live snapshot on every admission: settings can change at runtime.
        for axis in ("x", "y", "z"):
            lower = getattr(limits, f"{axis}_min", None)
            upper = getattr(limits, f"{axis}_max", None)
            if not all(self._is_finite_number(value) for value in (lower, upper)):
                raise ValueError(f"SafetyChecker: {axis.upper()} limits must be finite numbers")
            if lower > upper:
                raise ValueError(f"SafetyChecker: {axis.upper()} minimum exceeds maximum")
        if not all(self._is_finite_number(value) for value in position):
            raise ValueError("SafetyChecker: position must contain only finite numbers")

        x, y, z = position[0], position[1], position[2]
        violations = []

        if not (limits.x_min <= x <= limits.x_max):
            violations.append(f"X={x:.2f} not in [{limits.x_min}, {limits.x_max}]")
        if not (limits.y_min <= y <= limits.y_max):
            violations.append(f"Y={y:.2f} not in [{limits.y_min}, {limits.y_max}]")
        if not (limits.z_min <= z <= limits.z_max):
            violations.append(f"Z={z:.2f} not in [{limits.z_min}, {limits.z_max}]")

        return violations

    def get_violations(self, position: List[float]) -> List[str]:
        return self._compute_violations(position)

    def is_within_safety_limits(self, position: List[float]) -> bool:
        return len(self._compute_violations(position)) == 0

    def is_escape_move(self, current: List[float], target: List[float]) -> bool:
        """Do not authorize generic escapes; recovery belongs to explicit motion policies."""
        return False

    @staticmethod
    def _is_finite_number(value) -> bool:
        return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)
