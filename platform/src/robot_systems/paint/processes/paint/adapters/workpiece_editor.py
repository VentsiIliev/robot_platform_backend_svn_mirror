"""Workpiece-editor contract backed by a paint execution runtime."""
from __future__ import annotations
from typing import TYPE_CHECKING
import numpy as np
from src.applications.workpiece_editor.service.i_workpiece_path_executor import IWorkpiecePathExecutor, WorkpieceProcessAction
from src.engine.robot.path_preparation import WorkpieceExecutionPlan
from src.robot_systems.paint.visualization.i_paint_preview_geometry import IPaintPreviewGeometry

if TYPE_CHECKING:
    from src.robot_systems.paint.processes.paint.production.execution_runtime import PaintExecutionRuntime


class PaintWorkpiecePathExecutor(IWorkpiecePathExecutor):
    """Adapt editor actions and previews without owning production state."""

    supports_paint_motion_states = True

    def __init__(self, runtime: PaintExecutionRuntime, *, preview: IPaintPreviewGeometry) -> None:
        self._runtime = runtime
        self._preview = preview

    def prepare_workpiece_execution_plan(self, workpiece: dict, skip_debug_plot: bool = False) -> WorkpieceExecutionPlan:
        return self._runtime.prepare_workpiece_execution_plan(workpiece, skip_debug_plot=skip_debug_plot)

    def get_last_execution_plan(self) -> WorkpieceExecutionPlan | None:
        return self._runtime.get_last_execution_plan()

    def get_projected_pivot_paths(self, execution_plan: WorkpieceExecutionPlan) -> tuple[list[list[list[float]]], list[float] | None]:
        return self._preview.get_projected_pivot_paths(execution_plan)

    def get_pivot_motion_snapshots(self, execution_plan: WorkpieceExecutionPlan) -> tuple[list[list[np.ndarray]], list[float] | None]:
        return self._preview.get_pivot_motion_snapshots(execution_plan)

    def execute_paint_process(self, execution_plan: WorkpieceExecutionPlan) -> tuple[bool, str]:
        return self._runtime.execute_paint_process(execution_plan)

    def get_supported_execution_modes(self) -> tuple[str, ...]:
        """Report the execution modes supported by the paint executor."""
        return ()

    def get_process_actions(self) -> tuple[WorkpieceProcessAction, ...]:
        """Expose the paint process as one editor-facing action."""
        return (
            WorkpieceProcessAction(
                action_id="paint_process",
                label="Approve Paint Process",
                requires_projected_path_plot=True,
            ),
        )

    def execute_process_action(
        self,
        execution_plan: WorkpieceExecutionPlan,
        action_id: str,
    ) -> tuple[bool, str]:
        """Execute the requested paint process action."""
        action_id = str(action_id or "").strip().lower()
        if action_id != "paint_process":
            return False, f"Unsupported paint process action: {action_id}"
        return self.execute_paint_process(execution_plan)

    def execute_process_paths(
        self,
        execution_plan: WorkpieceExecutionPlan,
        mode: str = "continuous",
    ) -> tuple[bool, str]:
        """Paint no longer supports direct/manual paint-contact path execution."""
        return False, "Direct paint path execution is not supported; use the paint process action"
