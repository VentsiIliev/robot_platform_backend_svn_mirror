from __future__ import annotations

import threading
import logging
from uuid import uuid4
from contextvars import copy_context
from src.engine.diagnostics.events import current_context, diagnostic_context, observe
from src.engine.diagnostics.actions import ActionRecorder
from dataclasses import asdict
from time import monotonic, time
from typing import Callable, Optional

from src.engine.hardware.vacuum_pump.interfaces.i_vacuum_pump_controller import IVacuumPumpController
from src.engine.core.i_messaging_service import IMessagingService
from src.engine.robot.interfaces.i_robot_service import IRobotService
from src.engine.process.base_process import BaseProcess
from src.engine.process.process_requirements import ProcessRequirements
from src.shared_contracts.events.process_events import ProcessState
from src.engine.system.i_system_manager import ISystemManager
from src.robot_systems.paint.component_ids import ProcessID
from src.robot_systems.paint.contracts.paint_head_check.interfaces import IPaintHeadAlignmentGuidance
from src.robot_systems.paint.processes.paint.configuration.models import PAINT_PROCESS_CONFIG
from src.robot_systems.paint.processes.paint.adjustment.session import (
    AdjustmentStep,
    PaintAdjustmentSession,
)
from src.robot_systems.paint.processes.paint.tray_dry.errors import TrayError, TrayFailure
from src.robot_systems.paint.processes.paint.results import (
    PaintFailure, PaintFailureCode, PaintOperationError, PaintOperationResult, PaintOutcome,
)


class PaintProcess(BaseProcess):
    """Run one paint production cycle in the background and report process state changes."""
    _head_guidance: IPaintHeadAlignmentGuidance | None = None
    def __init__(
        self,
        production_service,
        messaging: IMessagingService,
        robot_service: Optional[IRobotService] = None,
        vacuum_pump: Optional[IVacuumPumpController] = None,
        paint_process_config_service=None,
        system_manager: Optional[ISystemManager] = None,
        requirements: Optional[ProcessRequirements] = None,
        service_checker: Optional[Callable[[str], bool]] = None,
        head_guidance: IPaintHeadAlignmentGuidance | None = None,
    ) -> None:
        """Store the production service and process dependencies for a single-run paint process."""
        super().__init__(
            process_id=ProcessID.MAIN_PROCESS,
            messaging=messaging,
            system_manager=system_manager,
            requirements=requirements or ProcessRequirements.none(),
            service_checker=service_checker,
        )
        self._production_service = production_service
        self._head_guidance = head_guidance
        self._robot_service = robot_service
        self._vacuum_pump = vacuum_pump
        self._paint_process_config_service = paint_process_config_service
        self._diagnostic_run_id: str | None = None
        self._diagnostic_run_context: dict = {}
        self._diagnostic_started_at: float | None = None
        self._last_result: PaintOperationResult | None = None
        self._last_failure: TrayFailure | PaintFailure | None = None
        self._thread: Optional[threading.Thread] = None
        self._stop_thread: Optional[threading.Thread] = None
        self._stopping = False
        self._shutdown_requested = False
        self._preserve_vacuum = threading.Event()
        self._run_stop_event = threading.Event()
        self._stop_started_at: float | None = None
        self._manual_single_cycle_requested = False
        self._retry_unmatched_workpiece_requested = False
        self._adjustment_session: PaintAdjustmentSession | None = None
        self._pending_adjustment_session: PaintAdjustmentSession | None = None
        self._collision_recording_active = threading.Event()

    @property
    def last_failure(self) -> TrayFailure | PaintFailure | None:
        """Machine-readable operation or tray failure from the most recent start or cycle."""
        return self._last_failure

    def start(self) -> None:
        self._request_start()

    def start_with_diagnostics(self, context: dict) -> dict:
        """Report admission under the process lock, independently of completion."""
        with diagnostic_context(**context):
            return self._request_start()

    def _request_start(self) -> dict:
        with self._lock:
            previous_thread, previous_state = self._thread, self._state
            self._transition(ProcessState.RUNNING,
                             self._on_resume if previous_state == ProcessState.PAUSED else self._on_start)
            accepted = self._state == ProcessState.RUNNING and (
                self._thread is not previous_thread or previous_state == ProcessState.PAUSED)
            return {'accepted': accepted, 'state': self._state.value,
                    'kind': 'resume' if previous_state == ProcessState.PAUSED else 'start',
                    'run_id': self._diagnostic_run_id if accepted else None,
                    'operation_id': self._diagnostic_run_context.get('operation_id') if accepted else None}

    @property
    def consecutive_completed_cycles(self) -> int:
        """Expose the session cycle streak independently of dashboard lifetime."""
        return self._production_service.consecutive_completed_cycles

    @property
    def last_result(self) -> PaintOperationResult | None:
        """Typed outcome of the last finished production run."""
        return self._last_result

    def _workers_running(self) -> bool:
        return any(
            thread is not None and thread.is_alive()
            for thread in (self._thread, self._stop_thread)
        )

    @property
    def is_stopping(self) -> bool:
        """Report pending cleanup without changing the public process state."""
        return (
            self._state not in (ProcessState.RUNNING, ProcessState.PAUSED)
            and self._workers_running()
        )

    @property
    def stopping_elapsed_seconds(self) -> float:
        started_at = self._stop_started_at
        if started_at is None or not self.is_stopping:
            return 0.0
        return max(0.0, monotonic() - started_at)

    def _transition(
        self, target: ProcessState, action: Callable[[], None], message: str = ""
    ) -> None:
        if target == ProcessState.RUNNING and self._shutdown_requested:
            return
        # All callers hold the process lock. Resume uses the existing worker;
        # every other RUNNING transition must wait for both previous workers.
        if (
            target == ProcessState.RUNNING
            and self._state != ProcessState.PAUSED
            and self._workers_running()
        ):
            self._logger.info("Paint start ignored while previous workers are active")
            return
        if target == ProcessState.RUNNING and self._state != ProcessState.PAUSED:
            try:
                self._production_service.ensure_tray_ready_for_start()
            except TrayError as exc:
                self._last_failure = exc.as_failure()
                raise
            self._last_failure = None
        super()._transition(target, action, message)

    def start_adjustment_cycle(self) -> bool:
        """Start one operator-paced cycle without changing production settings."""
        with self._lock:
            if self._state not in (ProcessState.IDLE, ProcessState.STOPPED):
                return False
            previous_thread = self._thread
            session = PaintAdjustmentSession()
            self._pending_adjustment_session = session
            try:
                self._transition(ProcessState.RUNNING, self._on_start)
            finally:
                self._pending_adjustment_session = None
            started = self._thread is not previous_thread and self._state == ProcessState.RUNNING
            return started

    def paint_next_adjustment_section(self, step: AdjustmentStep) -> bool:
        session = self._adjustment_session
        return bool(
            self.state == ProcessState.RUNNING
            and session is not None
            and session.request_next(step)
        )

    def finish_adjustment_cycle(self) -> bool:
        session = self._adjustment_session
        return bool(
            self.state == ProcessState.RUNNING
            and session is not None
            and session.request_finish()
        )

    def adjustment_status(self) -> tuple[str, float, float]:
        session = self._adjustment_session
        return session.snapshot() if session is not None else ("idle", 0.0, 0.0)

    def start_manual_single_cycle(self) -> bool:
        """Start one calibration-table paint cycle through the normal process state machine."""
        with self._lock:
            if self._state not in (ProcessState.IDLE, ProcessState.STOPPED):
                return False
            previous_thread = self._thread
            self._manual_single_cycle_requested = True
            try:
                self._transition(ProcessState.RUNNING, self._on_start)
            finally:
                self._manual_single_cycle_requested = False
            return self._thread is not previous_thread and self._state == ProcessState.RUNNING

    def retry_unmatched_workpiece(self) -> bool:
        """Restart at paint capture after an expected unmatched-workpiece stop."""
        with self._lock:
            if (
                self._state != ProcessState.STOPPED
                or self._last_result is None
                or self._last_result.outcome is not PaintOutcome.UNMATCHED
                or self._workers_running()
                or not self._production_service.can_retry_unmatched_workpiece()
            ):
                return False
            self._retry_unmatched_workpiece_requested = True
            try:
                self._transition(ProcessState.RUNNING, self._on_start)
            finally:
                self._retry_unmatched_workpiece_requested = False
            return self._state == ProcessState.RUNNING

    def _on_start(self) -> None:
        """Start the background worker thread that performs one production cycle."""
        if self._head_guidance is not None:
            self._head_guidance.cancel()
        self._stopping = False
        self._preserve_vacuum.clear()
        self._diagnostic_run_id = uuid4().hex
        token = current_context()
        if not token.get('operation_id'):
            token = {**ActionRecorder().operation_context(), **token}
        self._diagnostic_run_context = {**token, 'run_id': self._diagnostic_run_id}
        self._diagnostic_started_at = monotonic()
        self._run_stop_event = threading.Event()
        self._stop_started_at = None
        self._adjustment_session = self._pending_adjustment_session
        with diagnostic_context(**self._diagnostic_run_context):
            worker_context = copy_context()
        self._thread = threading.Thread(
            target=worker_context.run,
            args=(
                self._run_in_background,
                self._manual_single_cycle_requested,
                self._pending_adjustment_session,
                self._retry_unmatched_workpiece_requested,
                self._run_stop_event,
            ),
            daemon=True,
            name="PaintProcess",
        )
        self._thread.start()

    def _on_stop(self) -> None:
        """Signal stop and request hardware halt without blocking the process lock."""
        self._stopping = True
        self._run_stop_event.set()
        self._stop_started_at = monotonic()
        try:
            self._production_service.stop_current_phase()
        finally:
            self._request_hardware_stop()

    def _on_fault(self) -> None:
        """Halt motion while retaining vacuum: the held-part state may be unknown."""
        self._preserve_vacuum.set()
        self._stopping = True
        self._run_stop_event.set()
        self._stop_started_at = monotonic()
        try:
            self._production_service.stop_current_phase()
        finally:
            self._production_service.reset_completed_cycle_streak()
            self._request_hardware_stop(release_vacuum=False)

    def set_error(self, message: str = "") -> None:
        """External faults use the same hardware-halt policy as cycle failures."""
        record = None
        with self._lock:
            previous = self._state
            if previous != ProcessState.ERROR:
                record = self._production_service.prepare_failure_record(
                    message=message,
                    failure=PaintFailure(PaintFailureCode.INTERNAL, "external_fault", message),
                    run_id=self._diagnostic_run_id,
                )
            self._state = ProcessState.ERROR
            try:
                self._on_fault()
            finally:
                self._publish(ProcessState.ERROR, previous, message)
        if record is not None:
            self._production_service.write_failure_record(record)

    def shutdown(self, timeout: float = 5.0) -> None:
        """Cancel and join workers outside the state lock before dependencies close."""
        from src.robot_systems.base_robot_system import ShutdownPendingError

        deadline = monotonic() + timeout
        with self._lock:
            if not self._shutdown_requested:
                self._shutdown_requested = True
                # Shutdown must not release a potentially held workpiece on error.
                try:
                    self._on_fault()
                except Exception:
                    self._logger.exception("Paint shutdown phase cancellation failed")
            workers = (self._thread, self._stop_thread)
        for worker in workers:
            if worker is not None and worker is not threading.current_thread():
                worker.join(max(0.0, deadline - monotonic()))
        if self._workers_running():
            raise ShutdownPendingError("Paint workers have not stopped; hardware retained")

    def _request_hardware_stop(self, *, release_vacuum: bool = True) -> None:
        if self._stop_thread is not None and self._stop_thread.is_alive():
            return
        with diagnostic_context(**{**self._diagnostic_run_context, 'run_id': self._diagnostic_run_id}):
            context = copy_context()
        thread = threading.Thread(
            target=context.run,
            args=(self._stop_hardware, release_vacuum),
            daemon=True,
            name="PaintProcessStop",
        )
        self._stop_thread = thread
        thread.start()

    def _stop_hardware(self, release_vacuum: bool = True) -> None:
        if self._robot_service is not None:
            try:
                self._robot_service.stop_motion()
            except Exception:
                self._logger.exception("Paint stop failed to stop robot motion")
        if (release_vacuum and not self._preserve_vacuum.is_set()
                and self._vacuum_pump is not None and self._is_vacuum_enabled()):
            try:
                self._vacuum_pump.turn_off()
            except Exception:
                self._logger.exception("Paint stop failed to turn vacuum pump off")

    def _is_vacuum_enabled(self) -> bool:
        service = self._paint_process_config_service
        if service is None:
            return bool(PAINT_PROCESS_CONFIG.enable_vacuum_pump)
        try:
            return bool(service.get_snapshot().enable_vacuum_pump)
        except Exception:
            self._logger.exception("Paint stop failed to read vacuum pump setting")
            return bool(PAINT_PROCESS_CONFIG.enable_vacuum_pump)

    def _on_pause(self) -> None:
        """Pause the current cooperative Paint phase."""
        observe(self._logger, "paint.run.pause_requested", metrics={"paint.runs.pause_requests": 1},
                run_id=self._diagnostic_run_id)
        self._production_service.pause_current_phase()

    def _on_resume(self) -> None:
        """Resume the current cooperative Paint phase."""
        observe(self._logger, "paint.run.resume_requested", metrics={"paint.runs.resume_requests": 1},
                run_id=self._diagnostic_run_id)
        self._production_service.resume_current_phase()

    def _on_reset_errors(self) -> None:
        """Clear the internal stop flag so a new run can be started after an error reset."""
        self._stopping = False

    def acknowledge_collision(self) -> tuple[bool, str]:
        failure = self._last_failure
        has_collision_failure = (
            isinstance(failure, PaintFailure)
            and failure.stage == "collision_monitor"
        )
        if not has_collision_failure and not self._backend_collision_recovery_required():
            # A queued dialog may outlive a successful release from another view.
            return True, "Collision hold already cleared"
        method = getattr(self._robot_service, "acknowledge_collision_interlock", None)
        if not callable(method):
            return False, "Robot backend does not support collision acknowledgement"
        try:
            result = method()
        except Exception as exc:
            self._logger.exception("Collision acknowledgement request failed")
            return False, str(exc)
        if not isinstance(result, dict) or not bool(result.get("success", False)):
            message = (
                result.get("message") or result.get("error")
                if isinstance(result, dict) else "Invalid backend response")
            return False, str(message)
        self._last_failure = None
        if self.state == ProcessState.ERROR:
            self.reset_errors()
        return True, str(result.get("message") or "Collision hold cleared")

    def collision_acknowledgement_required(self) -> bool:
        failure = self._last_failure
        return (
            isinstance(failure, PaintFailure)
            and failure.stage == "collision_monitor"
        ) or self._backend_collision_recovery_required()

    def collision_detected(self) -> bool:
        """Distinguish confirmed collision evidence from observer availability."""
        if isinstance(self._last_failure, PaintFailure) and self._last_failure.stage == "collision_monitor":
            return True
        if self._robot_service is None:
            return False
        try:
            status = self._robot_service.get_execution_status()
        except Exception:
            self._logger.exception("Failed to read collision evidence")
            return False
        if not isinstance(status, dict):
            return False
        interlock = status.get("motion_interlock")
        collision = status.get("collision_event")
        return (isinstance(interlock, dict) and bool(interlock.get("active", False))
                and isinstance(collision, dict) and bool(collision))

    def _backend_collision_recovery_required(self) -> bool:
        if self._robot_service is None:
            return False
        try:
            status = self._robot_service.get_execution_status()
        except Exception:
            self._logger.exception("Failed to read collision interlock status")
            return False
        if not isinstance(status, dict):
            return False
        interlock = status.get("motion_interlock")
        if not isinstance(interlock, dict):
            return False
        # An observer can lose readiness after a drive fault without latching
        # a collision stop. Explicit recovery must still reach the backend.
        observer_required = interlock.get("collision_monitor_required") is not False
        return bool(interlock.get("active", False)) or (
            observer_required and interlock.get("collision_monitor_ready") is False
        )

    def _run_in_background(self, *args, **kwargs) -> None:
        context = self._diagnostic_run_context or {**ActionRecorder().operation_context(),
                                                  'run_id': self._diagnostic_run_id or uuid4().hex}
        with diagnostic_context(**context):
            observe(self._logger, "paint.run.started", metrics={"paint.runs.attempts": 1})
            self._run_in_background_impl(*args, **kwargs)

    def _run_in_background_impl(
        self,
        manual_single_cycle: bool = False,
        adjustment_session: PaintAdjustmentSession | None = None,
        retry_unmatched_workpiece: bool = False,
        stop_event: threading.Event | None = None,
    ) -> None:
        """Execute one production cycle and translate the result into process state transitions."""
        run_stop_event = stop_event if stop_event is not None else self._run_stop_event
        collision_abort = threading.Event()
        collision_watch_done = threading.Event()
        collision_holder: dict[str, dict] = {}
        should_stop = lambda: run_stop_event.is_set() or collision_abort.is_set()
        failure: TrayFailure | PaintFailure | None = None
        collision_watch_started_at = time()
        collision_event = None
        watcher_context = copy_context()
        collision_watcher = threading.Thread(
            target=watcher_context.run,
            args=(self._watch_for_collision, collision_watch_started_at, collision_abort, collision_watch_done, collision_holder),
            daemon=True,
            name="PaintCollisionWatcher",
        )
        collision_watcher.start()
        self._start_collision_calibration_recording()
        try:
            if retry_unmatched_workpiece:
                result = self._production_service.run_once_result(
                    should_stop, retry_unmatched_workpiece=True
                )
            elif adjustment_session is not None:
                result = self._production_service.run_once_result(
                    should_stop, adjustment_session=adjustment_session
                )
            elif manual_single_cycle:
                result = self._production_service.run_once_result(
                    should_stop, manual_single_cycle=True
                )
            else:
                result = self._production_service.run_once_result(should_stop)
        except TrayError as exc:
            failure = exc.as_failure()
            self._logger.error("Paint tray rejected operation code=%s: %s", exc.code, exc)
            result = PaintOperationResult.failed(PaintFailureCode.INVALID_CONFIGURATION, "tray", str(exc))
        except PaintOperationError as exc:
            failure = exc.failure
            result = PaintOperationResult(PaintOutcome.FAILED, str(exc), exc.failure)
        except Exception as exc:
            self._logger.exception("Paint process failed")
            result = PaintOperationResult.failed(PaintFailureCode.INTERNAL, "paint_process", str(exc))
        finally:
            self._stop_collision_calibration_recording()
            collision_watch_done.set()
            collision_watcher.join(timeout=0.5)

        production_failure = self._production_service.last_failure
        if isinstance(production_failure, (TrayFailure, PaintFailure)):
            failure = production_failure
        collision_event = collision_holder.get("event") or self._collision_event_since(
            collision_watch_started_at)
        if collision_event is not None:
            joint = str(collision_event.get("joint") or "unknown joint")
            detector = str(collision_event.get("detector") or "collision monitor")
            message = f"Collision detected on {joint} by {detector}; robot motion was stopped"
            result = PaintOperationResult.failed(
                PaintFailureCode.MOTION,
                "collision_monitor",
                message,
            )
            failure = result.failure
        if failure is None:
            failure = result.failure
        effective_outcome = PaintOutcome.CANCELLED if run_stop_event.is_set() else result.outcome
        observe(self._logger, "paint.run.ended",
                level=logging.ERROR if result.failure else logging.INFO,
                metrics={f"paint.runs.outcome.{effective_outcome.value}": 1},
                outcome=effective_outcome.value, returned_outcome=result.outcome.value,
                duration_s=None if self._diagnostic_started_at is None else monotonic() - self._diagnostic_started_at,
                failure=None if failure is None else asdict(failure),
                stop_requested=run_stop_event.is_set(), message=result.message,
                stop_reason=None if result.stop_reason is None else result.stop_reason.value)
        msg = result.message
        ended_without_failure = result.completed or result.expected_stop or result.outcome is PaintOutcome.CANCELLED

        # Serialize completion with Stop/reset. A cancelled run cannot publish
        # a late success or error, even if reset has cleared the legacy flag.
        failure_record = None
        with self._lock:
            if (
                run_stop_event is not self._run_stop_event
                or run_stop_event.is_set()
                or self._stopping
                or self._state not in (ProcessState.RUNNING, ProcessState.PAUSED)
            ):
                return
            self._last_result = result
            self._last_failure = failure
            if ended_without_failure:
                self._logger.info("Paint process ended outcome=%s: %s", result.outcome.value, msg)
                self._transition(
                    ProcessState.STOPPED,
                    self._on_stop,
                    msg if result.stop_reason is not None or result.expected_stop else "",
                )
                # Publish after the terminal transition: the popup must describe
                # a stopped run, rather than an operation still being prepared.
                reason = result.stop_reason or result.outcome
                notices = {
                    PaintOutcome.UNMATCHED: (
                        "Unknown Workpiece", "No matching workpiece. Painting stopped.",
                    ),
                    PaintOutcome.TRAY_FULL: (
                        "Tray Full", "The tray is full. Empty the tray and confirm it is empty before starting again.",
                    ),
                    PaintOutcome.WORK_AREA_FULL: (
                        "Work Area Full", "The work area has no space for another workpiece. Clear the area before starting again.",
                    ),
                }
                if reason in notices:
                    title, message = notices[reason]
                    self._production_service.publish_dashboard_message("warning", title, message)
            else:
                self._logger.error("Paint process failed: %s", msg)
                failure_record = self._production_service.prepare_failure_record(
                    message=msg, failure=failure,
                    run_id=self._diagnostic_run_id,
                    collision_event=collision_event,
                )
                self._transition(ProcessState.ERROR, self._on_fault, msg)
        if failure_record is not None:
            self._production_service.write_failure_record(failure_record)

    def _collision_event_since(self, started_at: float) -> dict | None:
        if self._robot_service is None:
            return None
        try:
            status = self._robot_service.get_execution_status()
        except Exception:
            self._logger.exception("Failed to read collision notification from robot backend")
            return None
        if not isinstance(status, dict):
            return None
        event = status.get("collision_event")
        if not isinstance(event, dict) or not bool(event.get("stop_requested", False)):
            return None
        try:
            event_time = float(event.get("timestamp", 0.0))
        except (TypeError, ValueError):
            return None
        return dict(event) if event_time >= started_at else None

    def _watch_for_collision(
        self,
        started_at: float,
        collision_abort: threading.Event,
        done: threading.Event,
        holder: dict[str, dict],
    ) -> None:
        while not done.wait(0.05):
            event = self._collision_event_since(started_at)
            if event is None:
                continue
            holder["event"] = event
            collision_abort.set()
            self._logger.error(
                "Collision notification received during paint execution: %s", event)
            try:
                self._production_service.stop_current_phase()
            except Exception:
                self._logger.exception(
                    "Failed to cancel current paint phase after collision notification")
            return

    def _collision_calibration_recording_enabled(self) -> bool:
        service = self._paint_process_config_service
        if service is None:
            settings = PAINT_PROCESS_CONFIG
        else:
            try:
                settings = service.get_snapshot()
            except Exception:
                self._logger.exception(
                    "Failed to read settings for collision calibration recording"
                )
                return False
        return bool(
            settings.enable_dry_run_mode
            and settings.collect_collision_calibration_data
        )

    def _start_collision_calibration_recording(self) -> None:
        if not self._collision_calibration_recording_enabled() or self._robot_service is None:
            return
        start = getattr(self._robot_service, "start_collision_calibration_recording", None)
        if not callable(start):
            self._logger.warning("Dry-run calibration recording is unsupported by this robot")
            return
        try:
            result = start()
            if isinstance(result, dict) and result.get("success"):
                self._collision_recording_active.set()
                self._logger.info(
                    "[DRY_RUN] Collision calibration recording started: %s",
                    result.get("message", ""),
                )
            else:
                self._logger.warning(
                    "[DRY_RUN] Collision calibration recording did not start: %s",
                    result,
                )
        except Exception:
            self._logger.exception("Dry-run collision calibration recording start failed")

    def _stop_collision_calibration_recording(self) -> None:
        if not self._collision_recording_active.is_set() or self._robot_service is None:
            return
        # Clear first so concurrent process-stop and worker-finally paths cannot
        # finalize the same backend session twice.
        self._collision_recording_active.clear()
        stop = getattr(self._robot_service, "stop_collision_calibration_recording", None)
        if not callable(stop):
            return
        try:
            result = stop()
            if not (isinstance(result, dict) and result.get("success")):
                self._logger.warning(
                    "[DRY_RUN] Collision calibration recording stop failed: %s",
                    result,
                )
            else:
                self._logger.info(
                    "[DRY_RUN] Collision calibration recording finalized: %s",
                    result.get("message", ""),
                )
        except Exception:
            self._logger.exception("Dry-run collision calibration recording stop failed")
