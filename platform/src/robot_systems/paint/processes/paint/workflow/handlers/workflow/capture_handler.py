from __future__ import annotations

import logging
from src.engine.diagnostics.events import observe
from time import perf_counter

from src.robot_systems.paint.processes.paint.results import PaintOperationResult, PaintOutcome, PaintFailureCode

from src.robot_systems.paint.processes.paint.workflow.context import PaintExecutionContext
from src.robot_systems.paint.processes.paint.workflow.handlers.common.guards import guard_control
from src.robot_systems.paint.processes.paint.workflow.state import PaintExecutionState
from src.robot_systems.paint.processes.paint.planning import pick_largest_contour
from src.robot_systems.paint.processes.paint.dry_run import DryRunDatasetExhausted


_logger = logging.getLogger(__name__)


def handle_capture_workpiece(ctx: PaintExecutionContext) -> PaintExecutionState:
    guarded = guard_control(ctx, PaintExecutionState.CAPTURE_WORKPIECE)
    if guarded is not None:
        return guarded

    service = ctx.production_service
    if bool(ctx.process_config and ctx.process_config.enable_dry_run_mode):
        try:
            ctx.snapshot = service._dry_run_snapshot_source.capture_for_cycle(
                ctx.cycle_index, work_area_id="paint", placement_key="paint",
            )
            metadata = dict(ctx.dry_run_metadata or {})
            metadata["paint"] = dict(service._dry_run_snapshot_source.last_metadata or {})
            ctx.dry_run_metadata = metadata
        except DryRunDatasetExhausted as exc:
            ctx.set_outcome(PaintOperationResult(PaintOutcome.NO_WORKPIECE, str(exc)))
            return PaintExecutionState.FINISHED
        service._set_dashboard_live_view_paused(
            True, image=ctx.snapshot.frame, reason="dry-run workpiece generated",
        )
        return PaintExecutionState.PREPARE_WORKPIECE
    magazine_enabled = bool(
        ctx.magazine_config is not None and ctx.magazine_config.enabled
    )
    capture_attempt = 0
    while True:
        guarded = guard_control(ctx, PaintExecutionState.CAPTURE_WORKPIECE)
        if guarded is not None:
            return guarded
        service._restore_brightness_for_capture("before paint capture")
        if not magazine_enabled and service._vision_service is not None:
            ready, message = service._wait_for_fresh_capture_frame(
                1.0,
                ctx.motion_cancel_requested,
            )
            if not ready:
                if ctx.motion_cancel_requested():
                    guarded = guard_control(ctx, PaintExecutionState.CAPTURE_WORKPIECE)
                    if guarded is not None:
                        return guarded
                observe(_logger, "vision.capture_not_ready", level=logging.ERROR,
                        metrics={"vision.paint_capture.readiness_failures": 1}, message=message)
                ctx.set_outcome(PaintOperationResult.failed(
                    PaintFailureCode.UNAVAILABLE, "capture_workpiece", message))
                return PaintExecutionState.ERROR
        phase_start = perf_counter()
        observe(_logger, "vision.paint_capture.started", metrics={"vision.paint_capture.attempts": 1})
        try:
            ctx.snapshot = service._capture_snapshot_service.capture_snapshot(source="paint_process")
        except Exception:
            observe(_logger, "vision.paint_capture.failed", level=logging.ERROR,
                    metrics={"vision.paint_capture.failures": 1},
                    duration_s=perf_counter() - phase_start)
            raise
        contour_count = len(ctx.snapshot.contours or [])
        capture_attempt += 1
        observe(_logger, "vision.paint_capture",
                metrics={"vision.paint_capture.duration_seconds": perf_counter() - phase_start},
                contour_count=contour_count, attempt=capture_attempt)
        service._log_phase_timing(
            "paint_capture",
            phase_start,
            contour_count=contour_count,
            cycle=ctx.cycle_index,
        )
        if ctx.should_stop():
            ctx.set_outcome(PaintOperationResult(PaintOutcome.CANCELLED, "Paint process stopped"))
            return PaintExecutionState.STOPPED
        if not ctx.retry_capture_until_workpiece or pick_largest_contour(ctx.snapshot.contours) is not None:
            if ctx.adjustment_session is not None:
                ctx.adjustment_session.workpiece_found()
            break
        if ctx.adjustment_session is not None:
            ctx.adjustment_session.workpiece_not_found()
        _logger.info("No usable workpiece on paint capture attempt %d; retrying", capture_attempt)
        ctx.stop_event.wait(0.5)

    if service._pause_dashboard_live_view_after_capture():
        service._set_dashboard_live_view_paused(
            True,
            image=ctx.snapshot.frame,
            reason="paint capture completed",
        )

    service._freeze_brightness_after_capture()
    return PaintExecutionState.PREPARE_WORKPIECE
