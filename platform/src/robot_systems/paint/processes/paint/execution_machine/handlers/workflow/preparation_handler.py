from __future__ import annotations

from time import perf_counter

from src.robot_systems.paint.processes.paint.match.results import NoMatch
from src.robot_systems.paint.processes.paint.results import Failed, PaintOperationResult, PaintOutcome

from src.robot_systems.paint.processes.paint.execution_machine.context import PaintExecutionContext
from src.robot_systems.paint.processes.paint.execution_machine.state import PaintExecutionState
from src.robot_systems.paint.processes.paint.plan import pick_largest_contour


def handle_prepare_workpiece(ctx: PaintExecutionContext) -> PaintExecutionState:
    if ctx.should_stop():
        ctx.set_outcome(PaintOperationResult(PaintOutcome.CANCELLED, "Paint process stopped"))
        return PaintExecutionState.STOPPED
    if ctx.snapshot is None:
        ctx.set_result(False, "Paint capture is not available")
        return PaintExecutionState.ERROR

    ctx.contour = (
        ctx.cached_workpiece_contour
        if ctx.cached_workpiece_contour is not None
        else pick_largest_contour(ctx.snapshot.contours)
    )
    if ctx.contour is None:
        ctx.set_outcome(PaintOperationResult(PaintOutcome.NO_WORKPIECE, "No usable contour detected"))
        return PaintExecutionState.FINISHED

    service = ctx.production_service
    phase_start = perf_counter()
    prepared = service._workpiece_preparation.prepare_result(
        ctx.contour, ctx.snapshot.frame,
        enable_matching=bool(ctx.process_config.enable_workpiece_matching),
        default_settings_override=_cycle_default_paint_settings(ctx),
    )
    if isinstance(prepared, NoMatch):
        ctx.workpiece_description = "Unknown workpiece"
        ctx.set_outcome(PaintOperationResult(PaintOutcome.UNMATCHED, "Unknown workpiece"))
    elif isinstance(prepared, Failed):
        ctx.operation_failure = prepared.failure
        ctx.workpiece_description = prepared.failure.message
        service.publish_dashboard_message(
            "error", "Workpiece preparation failed", prepared.failure.message,
        )
    else:
        ctx.raw_workpiece = prepared.value.raw
        ctx.workpiece_description = prepared.value.description
    service._log_phase_timing("workpiece_preparation", phase_start, cycle=ctx.cycle_index)
    if ctx.should_stop():
        ctx.set_outcome(PaintOperationResult(PaintOutcome.CANCELLED, "Paint process stopped"))
        return PaintExecutionState.STOPPED
    if isinstance(prepared, NoMatch):
        return PaintExecutionState.FINISHED
    if ctx.raw_workpiece is None:
        if not isinstance(prepared, NoMatch):
            ctx.set_result(False, ctx.workpiece_description or "No matched workpiece")
        return PaintExecutionState.ERROR
    return PaintExecutionState.BUILD_EXECUTION_PLAN


def _cycle_default_paint_settings(ctx: PaintExecutionContext) -> dict | None:
    config = ctx.raw_process_config
    if config is None:
        return None
    return {
        "velocity": float(config.default_paint_velocity_percent),
        "acceleration": float(config.default_paint_acceleration_percent),
        "offset": float(config.default_paint_offset_mm),
    }
