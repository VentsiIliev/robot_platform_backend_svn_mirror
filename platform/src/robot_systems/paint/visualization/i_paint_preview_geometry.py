"""Replaceable provider of editor preview geometry."""
from __future__ import annotations
from typing import Protocol, TYPE_CHECKING

if TYPE_CHECKING:
    import numpy as np
    from src.engine.robot.path_preparation import WorkpieceExecutionPlan


class IPaintPreviewGeometry(Protocol):
    """Compute display geometry without executing robot or hardware commands."""

    def get_projected_pivot_paths(
        self, execution_plan: WorkpieceExecutionPlan,
    ) -> tuple[list[list[list[float]]], list[float] | None]:
        """Return paths and their pivot pose for the editor plot."""
        ...

    def get_pivot_motion_snapshots(
        self, execution_plan: WorkpieceExecutionPlan,
    ) -> tuple[list[list[np.ndarray]], list[float] | None]:
        """Return workpiece-shape snapshots and their pivot pose."""
        ...
