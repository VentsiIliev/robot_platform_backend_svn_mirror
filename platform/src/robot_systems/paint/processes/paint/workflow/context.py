from __future__ import annotations

import threading
from uuid import uuid4
from dataclasses import dataclass, field
from time import perf_counter
from typing import Callable

from src.robot_systems.paint.processes.paint.tray_dry.errors import TrayFailure
from src.robot_systems.paint.processes.paint.results import (
    PaintFailure, PaintFailureCode, PaintOperationResult, PaintOutcome,
)

from src.robot_systems.paint.processes.paint.configuration.models import PaintMagazineLoadConfig, PaintProcessConfig
from src.robot_systems.paint.processes.paint.production.execution_control import PaintExecutionControl
from src.robot_systems.paint.processes.paint.workflow.state import PaintExecutionState


@dataclass
class PaintExecutionContext:
    """Per-cycle state shared by paint execution-machine handlers."""

    production_service: object
    stop_requested: Callable[[], bool]
    control: PaintExecutionControl
    process_config: PaintProcessConfig | None = None
    raw_process_config: PaintProcessConfig | None = None
    magazine_config: PaintMagazineLoadConfig | None = None
    magazine_group: str = ""
    magazine_index: int = 0
    cycle_index: int = 1
    repeats_after_success: bool = False
    stop_event: threading.Event = field(default_factory=threading.Event)
    run_allowed: threading.Event = field(default_factory=threading.Event)
    state_machine: object | None = None
    current_state: PaintExecutionState | None = None
    paused_from_state: PaintExecutionState | None = None
    resume_state: PaintExecutionState | None = None
    is_resuming: bool = False
    tray_failure: TrayFailure | None = None
    result: PaintOperationResult = field(default_factory=lambda: PaintOperationResult(
        PaintOutcome.CANCELLED, "Paint process stopped"))
    total_started_at: float = field(default_factory=perf_counter)
    snapshot: object | None = None
    contour: object | None = None
    raw_workpiece: object | None = None
    workpiece_description: str = ""
    execution_plan: object | None = None
    paint_started_at: float | None = None
    paint_previous_control: object | None = None
    paint_timing_session: object | None = None
    paint_timing_recorder: object | None = None
    state_timing_recorder: object | None = None
    paint_total_waypoints: int = 0
    paint_ordered_result: PaintOperationResult | None = None
    paint_contact_executed_in_ordered_chain: bool = False
    paint_motion_active: bool = False
    cycle_start_unwind_completed: bool = False
    resume_retry_available: bool = False
    calibration_group: str = ""
    magazine_snapshot: object | None = None
    magazine_contour: object | None = None
    magazine_discovery_contours: list = field(default_factory=list)
    magazine_discovery_active_contour: object | None = None
    magazine_discovery_empty_capture: bool = False
    magazine_pose: list[float] | None = None
    magazine_release_pose: list[float] | None = None
    magazine_target: dict | None = None
    magazine_fixed_pickup_pose: list[float] | None = None
    magazine_stage_only: bool = False
    retry_capture_until_workpiece: bool = False
    adjustment_session: object | None = None
    magazine_nesting_has_more: bool = True
    cached_workpiece_contour: object | None = None

    diagnostic_cycle_id: str = field(default_factory=lambda: uuid4().hex)

    def __post_init__(self) -> None:
        self.run_allowed.set()

    def should_stop(self) -> bool:
        try:
            external_stop = bool(self.stop_requested())
        except Exception:
            external_stop = True
        return self.stop_event.is_set() or external_stop or self.control.should_stop()

    def motion_cancel_requested(self) -> bool:
        return self.should_stop() or not self.run_allowed.is_set() or self.control.pause_requested()

    def pause_from(self, state: PaintExecutionState) -> None:
        self.paused_from_state = state
        self.resume_state = state

    def mark_resuming(self) -> None:
        self.is_resuming = True
        self.resume_retry_available = True

    def consume_resume_retry(self) -> bool:
        if not self.resume_retry_available:
            return False
        self.resume_retry_available = False
        return True

    @property
    def result_ok(self) -> bool:
        return self.result.completed

    @property
    def result_message(self) -> str:
        return self.result.message

    @property
    def operation_failure(self) -> PaintFailure | None:
        return self.result.failure

    @operation_failure.setter
    def operation_failure(self, failure: PaintFailure) -> None:
        self.set_outcome(PaintOperationResult(PaintOutcome.FAILED, failure.message, failure))

    def set_outcome(self, result: PaintOperationResult) -> None:
        self.result = result

    def set_result(self, ok: bool, message: str) -> None:
        """Adapter for handlers with simple completion/failure contracts."""
        text = str(message or "")
        if ok:
            self.set_outcome(PaintOperationResult(PaintOutcome.COMPLETED, text, stop_reason=self.result.stop_reason))
        else:
            failure = self.operation_failure or PaintFailure(
                PaintFailureCode.MOTION,
                self.current_state.name.lower() if self.current_state else "paint_cycle", text,
            )
            self.set_outcome(PaintOperationResult(PaintOutcome.FAILED, text, failure))

    def snapshot_dict(self) -> dict:
        return {
            "current_state": None if self.current_state is None else self.current_state.name,
            "paused_from_state": None if self.paused_from_state is None else self.paused_from_state.name,
            "resume_state": None if self.resume_state is None else self.resume_state.name,
            "stop_requested": self.should_stop(),
            "run_allowed": self.run_allowed.is_set(),
            "outcome": self.result.outcome.value,
            "failure_code": None if self.result.failure is None else self.result.failure.code.value,
            "failure_stage": None if self.result.failure is None else self.result.failure.stage,
            "backend_code": None if self.result.failure is None else self.result.failure.backend_code,
            "stop_reason": None if self.result.stop_reason is None else self.result.stop_reason.value,
            "result_ok": self.result_ok,
            "result_message": self.result_message,
            "cycle_index": self.cycle_index,
            "has_snapshot": self.snapshot is not None,
            "has_contour": self.contour is not None,
            "has_raw_workpiece": self.raw_workpiece is not None,
            "has_execution_plan": self.execution_plan is not None,
            "paint_total_waypoints": self.paint_total_waypoints,
            "paint_contact_executed_in_ordered_chain": self.paint_contact_executed_in_ordered_chain,
            "paint_motion_active": self.paint_motion_active,
            "cycle_start_unwind_completed": self.cycle_start_unwind_completed,
            "resume_retry_available": self.resume_retry_available,
            "magazine_group": self.magazine_group,
            "magazine_index": self.magazine_index,
            "calibration_group": self.calibration_group,
            "has_magazine_snapshot": self.magazine_snapshot is not None,
            "has_magazine_contour": self.magazine_contour is not None,
            "magazine_discovery_queued_piles": len(self.magazine_discovery_contours),
            "has_magazine_discovery_active_pile": self.magazine_discovery_active_contour is not None,
            "has_magazine_target": self.magazine_target is not None,
        }
