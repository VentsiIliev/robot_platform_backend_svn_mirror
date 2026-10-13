from __future__ import annotations

import math
from dataclasses import dataclass

from src.engine.robot.motion_sequence import OrderedMotionType


@dataclass(frozen=True)
class ConfiguredMotionWaypoint:
    """Validated six-axis waypoint and its complete motion profile."""

    position: tuple[float, float, float, float, float, float]
    velocity_percent: float
    acceleration_percent: float
    motion_type: OrderedMotionType
    blend_radius: float

    def __post_init__(self) -> None:
        if len(self.position) != 6:
            raise ValueError("Configured waypoint position must contain exactly six values")
        for axis, value in zip(("X", "Y", "Z", "RX", "RY", "RZ"), self.position):
            if not math.isfinite(value):
                raise ValueError(f"Configured waypoint position.{axis} must be finite")
        for name, value in (("vel_percent", self.velocity_percent),
                            ("acc_percent", self.acceleration_percent),
                            ("blendR", self.blend_radius)):
            if not math.isfinite(value):
                raise ValueError(f"Configured waypoint {name} must be finite")
