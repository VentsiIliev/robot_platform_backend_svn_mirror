"""Shared inputs and transform hooks for paint path projection."""
from __future__ import annotations
from dataclasses import dataclass
from typing import Callable, TYPE_CHECKING
from src.engine.robot.path_preparation import WorkpieceExecutionPlan
from src.robot_systems.paint.processes.paint.configuration.models import PaintSimulationConfig
if TYPE_CHECKING:
    from src.robot_systems.paint.processes.paint.planning.pickup.transfer_planner import PickupTransferPlan


def pivot_source_path(job: dict, pivot_config: PaintSimulationConfig) -> list[list[float]]:
    """Return the path used as geometric source for pivot projection."""
    path = job.get("pivot_source_path") or job.get("execution_path") or job.get("path") or []
    if isinstance(path, list):
        return path
    return [list(point) for point in path]


def projection_tool_anchor_xy(job: dict, pivot_config: PaintSimulationConfig) -> tuple[float, float] | None:
    """Return the selected tool/workpiece anchor used by pivot projection."""
    if tuple(pivot_config.source_planar_coordinate_indices) != (0, 1):
        return None
    pickup_xy = job.get("pickup_xy")
    if not pickup_xy or len(pickup_xy) < 2:
        return None
    try:
        return float(pickup_xy[0]), float(pickup_xy[1])
    except (TypeError, ValueError):
        return None


@dataclass(frozen=True)
class PaintProjectionContext:
    """Prepared projection inputs and shared command-space transformations.

    The context contains no visualization policy or hardware commands.
    Consumers may choose how to project and present these inputs.
    """

    pivot_config: PaintSimulationConfig
    base_pivot_pose: list[float] | None
    pickup_plan: PickupTransferPlan | None
    apply_pivot_offset: Callable[[list[float] | None, float], list[float] | None]
    resolve_pivot_offset_mm: Callable[[dict | None, WorkpieceExecutionPlan | None], float]
    align_projected_path_to_pickup_plan: Callable[[list[list[float]], PickupTransferPlan | None], list[list[float]]]
    pivot_execution_command_path: Callable[..., list[list[float]]]
