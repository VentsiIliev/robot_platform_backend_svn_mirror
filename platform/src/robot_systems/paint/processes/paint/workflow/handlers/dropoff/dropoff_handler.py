from __future__ import annotations

import logging
from dataclasses import replace
from src.robot_systems.paint.processes.paint.results import PaintOutcome

from src.robot_systems.paint.diagnostics.trajectory import elapsed_s
from src.robot_systems.paint.processes.paint.workflow.context import PaintExecutionContext
from src.robot_systems.paint.processes.paint.workflow.handlers.common.motion_handlers import (
    finish_paint_motion,
    set_paint_result,
    wait_or_guard,
)
from src.robot_systems.paint.processes.paint.workflow.state import PaintExecutionState

_logger = logging.getLogger(__name__)

def handle_dropoff(ctx: PaintExecutionContext) -> PaintExecutionState:
    guarded = wait_or_guard(ctx, PaintExecutionState.DROPOFF)
    if guarded is not None:
        finish_paint_motion(ctx, success=False)
        return guarded

    result = ctx.production_service.release_dropoff(ctx)
    ok, msg = result.success, result.message
    if not ok:
        log_timing(ctx, "pre_release_dropoff")

        set_paint_result(ctx, False, msg)
        finish_paint_motion(ctx, success=False)
        return PaintExecutionState.ERROR

    log_completion(ctx)
    plate_is_full = result.tray_full

    set_paint_result(
        ctx,
        True,
        (
            "Drop-off plate has no space for another workpiece of the same footprint"
            if plate_is_full
            else f"Paint process completed for {len(ctx.execution_plan.execution_jobs)} path(s), "
                 f"{ctx.paint_total_waypoints} waypoints"
        ),
    )
    if plate_is_full:
        ctx.set_outcome(replace(ctx.result, stop_reason=PaintOutcome.TRAY_FULL))
    return PaintExecutionState.POST_RETURN


def log_timing(ctx: PaintExecutionContext, stage: str) -> None:
    _logger.debug(
        "[TIMING] paint_process success=%s stage=%s total_elapsed_s=%.3f",
        ctx.result_ok,
        stage,
        elapsed_s(ctx.paint_started_at),
    )

def log_completion(ctx: PaintExecutionContext) -> None:
    _logger.info(
        "[EXECUTE] Paint process completed: jobs=%d total_waypoints=%d",
        len(ctx.execution_plan.execution_jobs),
        ctx.paint_total_waypoints,
    )
