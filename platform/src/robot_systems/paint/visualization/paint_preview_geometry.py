"""Calculate editor preview geometry using shared paint projection mathematics."""
from __future__ import annotations

from typing import Callable

import numpy as np

from src.engine.robot.path_preparation import WorkpieceExecutionPlan
from src.robot_systems.paint.processes.paint.configuration.models import PaintSimulationConfig
from src.robot_systems.paint.processes.paint.planning.projection import (
    project_paint_contact_motion_continuous,
)


from src.robot_systems.paint.processes.paint.planning.projection.inputs import (
    PaintProjectionContext, pivot_source_path, projection_tool_anchor_xy,
)
from src.robot_systems.paint.visualization.i_paint_preview_geometry import IPaintPreviewGeometry

def project_pivot_paths_for_editor(
    *,
    execution_plan: WorkpieceExecutionPlan,
    pivot_config: PaintSimulationConfig,
    base_pivot_pose: list[float],
    pickup_plan,
    apply_pivot_offset: Callable[[list[float] | None, float], list[float] | None],
    resolve_pivot_offset_mm: Callable[[dict | None, WorkpieceExecutionPlan | None], float],
    align_projected_path_to_pickup_plan: Callable[[list[list[float]], object | None], list[list[float]]],
    pivot_execution_command_path: Callable[..., list[list[float]]],
    project_motion_geometry: Callable[..., tuple[list[list[float]], list[np.ndarray], list[dict[str, float | int]]]] = project_paint_contact_motion_continuous,
) -> tuple[list[list[list[float]]], list[float] | None]:
    """Project editor-visible pivot center paths for each prepared execution job."""
    paths = []
    last_pivot_pose = list(base_pivot_pose)
    for job in execution_plan.execution_jobs:
        source_path = pivot_source_path(job, pivot_config)
        if not source_path:
            continue
        pivot_pose = apply_pivot_offset(
            base_pivot_pose,
            resolve_pivot_offset_mm(job, execution_plan),
        )
        if pivot_pose is None or len(pivot_pose) < 3:
            continue
        last_pivot_pose = list(pivot_pose)
        anchor_xy = projection_tool_anchor_xy(job, pivot_config)
        center_path, _, _ = project_motion_geometry(
            source_path,
            pivot_pose,
            pivot_config,
            anchor_xy=anchor_xy,
            source_rotation_deg=(
                float(pickup_plan.source_rotation_deg)
                if pickup_plan is not None else 0.0
            ),
            enforce_open_path_side=bool(job.get("paint_selection_cut_applied")),
        )
        center_path = align_projected_path_to_pickup_plan(center_path, pickup_plan)
        center_path = pivot_execution_command_path(center_path, pickup_plan=pickup_plan)
        paths.append(center_path)
    return paths, last_pivot_pose


def project_pivot_motion_snapshots_for_editor(
    *,
    execution_plan: WorkpieceExecutionPlan,
    pivot_config: PaintSimulationConfig,
    base_pivot_pose: list[float],
    pickup_plan,
    apply_pivot_offset: Callable[[list[float] | None, float], list[float] | None],
    resolve_pivot_offset_mm: Callable[[dict | None, WorkpieceExecutionPlan | None], float],
    project_motion_geometry: Callable[..., tuple[list[list[float]], list[np.ndarray], list[dict[str, float | int]]]] = project_paint_contact_motion_continuous,
) -> tuple[list[list[np.ndarray]], list[float] | None]:
    """Return per-step projected shape snapshots for pivot motion plotting."""
    motion = []
    last_pivot_pose = list(base_pivot_pose)
    for job in execution_plan.execution_jobs:
        source_path = pivot_source_path(job, pivot_config)
        if not source_path:
            continue
        pivot_pose = apply_pivot_offset(
            base_pivot_pose,
            resolve_pivot_offset_mm(job, execution_plan),
        )
        if pivot_pose is None or len(pivot_pose) < 3:
            continue
        last_pivot_pose = list(pivot_pose)
        anchor_xy = projection_tool_anchor_xy(job, pivot_config)
        _, snapshots, _ = project_motion_geometry(
            source_path,
            pivot_pose,
            pivot_config,
            anchor_xy=anchor_xy,
            source_rotation_deg=(
                float(pickup_plan.source_rotation_deg)
                if pickup_plan is not None else 0.0
            ),
            enforce_open_path_side=bool(job.get("paint_selection_cut_applied")),
        )
        motion.append(snapshots)
    return motion, last_pivot_pose


class PaintPreviewGeometry(IPaintPreviewGeometry):
    """Default preview provider, injected with planning inputs rather than a process."""

    def __init__(
        self,
        context_provider: Callable[[WorkpieceExecutionPlan], PaintProjectionContext],
    ) -> None:
        self._context_provider = context_provider

    def get_projected_pivot_paths(
        self, execution_plan: WorkpieceExecutionPlan,
    ) -> tuple[list[list[list[float]]], list[float] | None]:
        context = self._context_provider(execution_plan)
        if context.base_pivot_pose is None or len(context.base_pivot_pose) < 3:
            return [], context.base_pivot_pose
        return project_pivot_paths_for_editor(
            execution_plan=execution_plan,
            pivot_config=context.pivot_config,
            base_pivot_pose=context.base_pivot_pose,
            pickup_plan=context.pickup_plan,
            apply_pivot_offset=context.apply_pivot_offset,
            resolve_pivot_offset_mm=context.resolve_pivot_offset_mm,
            align_projected_path_to_pickup_plan=context.align_projected_path_to_pickup_plan,
            pivot_execution_command_path=context.pivot_execution_command_path,
            project_motion_geometry=project_paint_contact_motion_continuous,
        )

    def get_pivot_motion_snapshots(
        self, execution_plan: WorkpieceExecutionPlan,
    ) -> tuple[list[list[np.ndarray]], list[float] | None]:
        context = self._context_provider(execution_plan)
        if context.base_pivot_pose is None or len(context.base_pivot_pose) < 3:
            return [], context.base_pivot_pose
        return project_pivot_motion_snapshots_for_editor(
            execution_plan=execution_plan,
            pivot_config=context.pivot_config,
            base_pivot_pose=context.base_pivot_pose,
            pickup_plan=context.pickup_plan,
            apply_pivot_offset=context.apply_pivot_offset,
            resolve_pivot_offset_mm=context.resolve_pivot_offset_mm,
            project_motion_geometry=project_paint_contact_motion_continuous,
        )
