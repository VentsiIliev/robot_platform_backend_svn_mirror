"""Common stop-strategy contract; submission remains in TrajectoryExecutor."""
from dataclasses import dataclass
from typing import Any, Protocol


@dataclass(frozen=True)
class StopPlan:
    trajectory: Any
    held_joint_names: frozenset = frozenset()
    goal_velocity_tolerance: float = 0.0
    server_timeout_s: float = 0.25
    dispatch_deadline: float | None = None


class StopStrategy(Protocol):
    name: str

    def build(self, executor, *, stop_duration_s=None) -> tuple[StopPlan | None, str]:
        """Return a stop and dispatch requirements, or a refusal with its reason."""
        ...
