"""Run a prepared workpiece through the shared production workflow."""
from __future__ import annotations
from typing import TYPE_CHECKING
from src.engine.robot.path_preparation import WorkpieceExecutionPlan
from src.robot_systems.paint.contracts.dropoff import DropoffResult
from src.robot_systems.paint.processes.paint.configuration.models import DropoffStrategy
from src.robot_systems.paint.contracts.paint_head_check.models import HeadCheckOperatingMode
if TYPE_CHECKING:
    from .execution_runtime import PaintExecutionRuntime

class _PreparedPaintProcessAdapter:
    """Minimal production-service shape for editor execution of an already prepared plan."""

    def __init__(self, path_executor: "PaintExecutionRuntime") -> None:
        self._path_executor = path_executor

    def prepare_dropoff(self) -> tuple[bool, str]:
        return self._path_executor.prepare_dropoff()

    def release_dropoff(self, context) -> DropoffResult:
        return self._path_executor.release_dropoff()

    @staticmethod
    def _restore_brightness() -> None:
        return None

    @staticmethod
    def _set_dashboard_live_view_paused(_paused: bool, *, reason: str = "", image: object | None = None) -> None:
        return None

    @staticmethod
    def _log_phase_timing(_label: str, _started_at: float, **_fields: object) -> None:
        return None

    @staticmethod
    def _next_cycle_start_target(_ctx: object) -> None:
        """A single prepared-plan execution has no following production cycle."""
        return None


def run_prepared_paint_cycle(
    runtime: PaintExecutionRuntime,
    prepared_workpiece: WorkpieceExecutionPlan,
    *,
    control=None,
) -> tuple[bool, str]:
    """Run a prepared workpiece plan through the paint execution state machine."""
    from src.robot_systems.paint.processes.paint.production.execution_control import PaintExecutionControl
    from src.robot_systems.paint.processes.paint.workflow.context import PaintExecutionContext
    from src.robot_systems.paint.processes.paint.production.cycle_runner import run_paint_cycle
    from src.robot_systems.paint.processes.paint.workflow.state import PaintExecutionState

    raw_config = runtime._refresh_paint_process_config_snapshot()
    if not raw_config.enable_dry_run_mode and (
        raw_config.dropoff.strategy is DropoffStrategy.PLATE_LAYOUT
        or raw_config.dropoff.alternate_drying_demo
    ):
        runtime._plate_layout_service.ensure_ready(raw_config.dropoff)
    runtime._refresh_runtime_config()
    control = control or PaintExecutionControl()
    context = PaintExecutionContext(
        production_service=_PreparedPaintProcessAdapter(runtime),
        stop_requested=lambda: False,
        control=control,
        process_config=runtime._paint_process_config(),
        raw_process_config=raw_config,
        magazine_config=None,
    )
    context.execution_plan = prepared_workpiece
    if raw_config.head_check.enabled and not raw_config.stop_after_calibration_pickup:
        mode = (
            HeadCheckOperatingMode.DRY_RUN if raw_config.enable_dry_run_mode
            else HeadCheckOperatingMode.PRODUCTION
        )
        context.head_check_run = runtime.create_head_check_run(raw_config.head_check, mode)
        context.head_check_return = runtime.return_from_head_check
        context.head_check_pause_request = control.request_pause

    try:
        execution = run_paint_cycle(
            context,
            initial_state=PaintExecutionState.PICKUP,
        )
        if execution.machine_error is not None:
            return False, execution.machine_error
        if execution.result.completed and context.head_check_run is not None:
            context.head_check_run.record_completed_cycle()
        return execution.result.as_legacy_pair()
    finally:
        if context.head_check_run is not None:
            context.head_check_run.close()
