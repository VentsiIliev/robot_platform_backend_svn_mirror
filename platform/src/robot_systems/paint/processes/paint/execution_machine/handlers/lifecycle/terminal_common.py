from __future__ import annotations

from dataclasses import replace

from src.robot_systems.paint.processes.paint.execution_machine.context import PaintExecutionContext
from src.robot_systems.paint.processes.paint.results import PaintFailure, PaintOutcome, PaintFailureCode, PaintOperationError, PaintOperationResult


def restore_cycle_resources(
    ctx: PaintExecutionContext,
    *,
    defer_for_next_capture: bool = False,
) -> None:
    from src.robot_systems.paint.processes.paint.execution_machine.handlers.common.motion_handlers import finish_paint_motion

    service = ctx.production_service
    executor = service._path_executor
    actions = [("finish_motion", lambda: finish_paint_motion(ctx, success=ctx.result_ok))]
    if not ctx.result_ok and executor._plate_layout_service is not None:
        actions.append(("cancel_reservation", executor._plate_layout_service.cancel))
    if not defer_for_next_capture:
        actions.extend([
            ("restore_brightness", service._restore_brightness),
            ("restore_live_view", lambda: service._set_dashboard_live_view_paused(
                False, reason="paint cycle finished")),
        ])
    failures: list[tuple[str, Exception]] = []
    for name, action in actions:
        try:
            action()
        except Exception as exc:
            # Attempt every resource restoration, then expose cleanup failure to the boundary.
            failures.append((name, exc))
    if failures:
        message = "; ".join(f"{name}: {exc}" for name, exc in failures)
        cleanup = PaintFailure(PaintFailureCode.INTERNAL, "cycle_cleanup", message)
        if ctx.result.failure is not None:
            failure = replace(ctx.result.failure,
                              secondary_failures=(*ctx.result.failure.secondary_failures, cleanup))
            ctx.set_outcome(PaintOperationResult(PaintOutcome.FAILED,
                            f"{ctx.result.message}; cleanup failed: {message}", failure))
        else:
            ctx.set_outcome(PaintOperationResult(PaintOutcome.FAILED, message, cleanup))
        raise PaintOperationError(ctx.result.failure) from failures[0][1]


def stop_machine(ctx: PaintExecutionContext) -> None:
    if ctx.state_machine is not None:
        ctx.state_machine.stop_execution()
