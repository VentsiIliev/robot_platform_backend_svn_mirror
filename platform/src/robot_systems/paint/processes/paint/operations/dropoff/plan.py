"""Waypoint-plan data and planner contract used by dropoff execution."""
from __future__ import annotations
from dataclasses import dataclass
from typing import Protocol
from src.engine.robot.motion_sequence import OrderedMotionType
from src.engine.robot.path_preparation import WorkpieceExecutionPlan
from src.robot_systems.paint.processes.paint.configuration.models import DropoffStrategy

@dataclass(frozen=True)
class DropoffWaypoint:
    """One dropoff move or release action."""

    label: str
    pose: list[float] | None
    vel_percent: float
    acc_percent: float
    motion_type: OrderedMotionType = OrderedMotionType.PTP
    blendR: float = 0.0
    release_here: bool = False
    corridor_id: str | None = None


@dataclass(frozen=True)
class DropoffPlan:
    """Resolved dropoff sequence for the current held workpiece."""

    strategy_name: DropoffStrategy
    waypoints: tuple[DropoffWaypoint, ...]


class IDropoffWaypointPlanner(Protocol):
    """Build a waypoint plan consumed by the low-level dropoff executor."""

    name: DropoffStrategy

    def build_plan(self, owner, execution_plan: WorkpieceExecutionPlan) -> DropoffPlan:
        """Return the ordered dropoff actions for the active workpiece."""
