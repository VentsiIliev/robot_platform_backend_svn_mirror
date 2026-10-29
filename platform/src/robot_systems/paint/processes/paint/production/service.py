from __future__ import annotations

from src.robot_systems.paint.contracts.dropoff import IDropoffExecution, DropoffResult
from src.robot_systems.paint.processes.paint.start_recovery import (
    StartRecoveryService, StartRecoveryResult, StartRecoveryOutcome,
)
from src.robot_systems.paint.processes.paint.start_recovery.errors import RecoveryInternalError
from src.engine.robot.motion_sequence import OrderedPositionCommand

import logging
import math
import threading
from time import monotonic, perf_counter, sleep
from typing import Callable, Optional
from functools import partial
from src.robot_systems.paint.contracts.paint_head_check.interfaces import (
    IHeadInspectionControl, IPaintHeadCheckRun, IPaintHeadCheckRunFactory,
)
from src.robot_systems.paint.contracts.paint_head_check.models import HeadCheckOperatingMode
from src.robot_systems.paint.contracts.paint_head_check.errors import (
    HeadInspectionFailure, HeadInspectionFailureCode, PaintHeadCheckError,
)
from src.robot_systems.paint.contracts.paint_head_check.results import (
    HeadInspectionMoveFailed, HeadInspectionMoveResult,
)
from src.robot_systems.paint.processes.paint.head_check_support import (
    PaintHeadReturnRoute, head_check_failed,
)

from src.robot_systems.paint.processes.paint.results import (
    PaintFailure, PaintFailureCode, PaintOperationResult, PaintOutcome,
)

from src.engine.hardware.vacuum_pump.interfaces.i_vacuum_pump_controller import IVacuumPumpController
from src.robot_systems.paint.processes.paint.production.execution_control import PaintExecutionControl
from src.robot_systems.paint.contracts.events.dashboard_events import (
    PaintDashboardLiveViewEvent,
    PaintDashboardLiveViewTopics,
    PaintDashboardMessageEvent,
    PaintDashboardMessageTopics,
)
from src.robot_systems.paint.processes.paint.workflow import (
    PaintExecutionContext,
)
from src.robot_systems.paint.processes.paint.production.cycle_runner import run_paint_cycle
from src.robot_systems.paint.diagnostics.operation import observed_operation
from src.engine.diagnostics.events import current_context
from src.robot_systems.paint.processes.paint.workflow.state import PaintExecutionState
from src.robot_systems.paint.processes.paint.production.magazine.outcomes import (
    ALL_MAGAZINES_EMPTY,
    MAGAZINE_EMPTY,
    NO_WORKPIECE_AT_MAGAZINE,
)
from src.robot_systems.paint.processes.paint.motion.pose_sampling import (
    FreshPoseReadError,
    read_fresh_pose,
)
from src.robot_systems.paint.contracts.next_cycle_target import NextCycleTarget
from src.robot_systems.paint.processes.paint.configuration.models import (
    MAGAZINE_PROCESSING_STRATEGY_BATCH_NESTING,
    MAGAZINE_PICKUP_MODE_AUTO_DISCOVERY_SENSOR_CONTROLLED_FAST_LIN,
    MAGAZINE_PICKUP_MODE_FIXED_GROUP_SENSOR_CONTROLLED_FAST_LIN,
    DropoffStrategy,
    PaintProcessConfig, PaintMagazineLoadConfig,
    PAINT_PROCESS_CONFIG,
    scale_paint_process_accelerations,
)

from src.robot_systems.paint.processes.paint.tray_dry.plate_layout import PlateLayoutService
from src.robot_systems.paint.processes.paint.tray_dry.errors import TrayFailure, TrayUnavailableError

_logger = logging.getLogger(__name__)

# TODO - I started flagging some things to consider but maybe in general this needs attention in relation to error handling and maybe introduce structured results ?

class PaintProductionService:
    """Own the end-to-end paint production flow outside the editor UI."""
    def __init__(
        self,
        *,
        workpiece_preparation_service,
        capture_snapshot_service,
        path_preparation_service,
        path_executor,
        vacuum_pump: Optional[IVacuumPumpController] = None,
        paint_process_config_service=None,
        magazine_load_service=None,
        navigation_service=None,
        vision_service=None,
        messaging_service=None,
        plate_layout_service: PlateLayoutService | None = None,
        dry_run_snapshot_source=None,
        failure_artifact_root=None,
        start_recovery_service: StartRecoveryService | None = None,
        head_check_run_factory: IPaintHeadCheckRunFactory | None = None,
    ) -> None:
        """Store the services needed to capture, prepare, plan, and execute one paint cycle."""
        self._workpiece_preparation = workpiece_preparation_service
        self._capture_snapshot_service = capture_snapshot_service
        self._path_preparation_service = path_preparation_service
        self._dropoff_executor: IDropoffExecution = path_executor
        self._path_executor = path_executor
        self._start_recovery = start_recovery_service or StartRecoveryService(
            read_pose=self._read_start_recovery_pose,
            execute_route=self._execute_start_recovery_route,
        )
        self._plate_layout_service = plate_layout_service
        self.last_failure: TrayFailure | PaintFailure | None = None
        self._vacuum_pump = vacuum_pump
        self._paint_process_config_service = paint_process_config_service
        self._magazine_load_service = magazine_load_service
        self._navigation_service = navigation_service
        self._vision_service = vision_service
        self._messaging_service = messaging_service
        self._brightness_locked = False
        self._paint_control = PaintExecutionControl()
        self._active_context_lock = threading.Lock()
        self._consecutive_completed_cycles = 0
        self._active_execution_context: PaintExecutionContext | None = None
        self._last_execution_context: PaintExecutionContext | None = None
        self._prepositioned_start_group: str | None = None
        self._dry_run_snapshot_source = dry_run_snapshot_source
        self._failure_artifact_root = failure_artifact_root
        self._failure_register_context = None
        self._failure_register_observation = {}
        self._failure_register_streak: int | None = None
        self._failure_bundle_path = None
        self._head_check_run_factory = head_check_run_factory
        self._head_check_run: IPaintHeadCheckRun | None = None
        self._head_check_pause_handler: Callable[[], None] | None = None

    def bind_head_check_pause_handler(self, handler: Callable[[], None]) -> None:
        """Bind the owning process pause operation without exposing process internals."""
        self._head_check_pause_handler = handler

    def return_from_head_check(
        self, context: PaintExecutionContext, control: IHeadInspectionControl,
    ) -> HeadInspectionMoveResult:
        if self._navigation_service is None:
            return HeadInspectionMoveFailed(HeadInspectionFailure(
                HeadInspectionFailureCode.RETURN_TARGET_INVALID,
                "Paint-head inspection requires the paint navigation service for return",
            ))
        return PaintHeadReturnRoute(
            self._navigation_service, partial(self._production_start_target, context),
        ).move(control)

    def prepare_failure_record(
        self, *, message: str, failure: TrayFailure | PaintFailure | None = None,
        run_id: str | None = None, collision_event: dict | None = None,
    ) -> dict:
        """Snapshot failure evidence and the pre-reset streak without performing file I/O."""
        from dataclasses import asdict
        from datetime import datetime, timezone
        from src.robot_systems.paint.diagnostics.failure_register import summarize_failure_workpiece

        with self._active_context_lock:
            context = self._failure_register_context
            observation = context.diagnostic_context if context is not None else (
                self._failure_register_observation or current_context())
            streak = self._failure_register_streak
            return {
                "schema_version": 1,
                "recorded_at_utc": datetime.now(timezone.utc).isoformat(),
                "run_id": run_id,
                "context": dict(observation),
                "cycle_id": context.diagnostic_cycle_id if context is not None else observation.get('cycle_id'),
                "cycle_index": context.cycle_index if context is not None else observation.get('cycle_index'),
                "consecutive_completed_cycles": (
                    self._consecutive_completed_cycles if streak is None else streak
                ),
                "message": message,
                "workpiece": (
                    summarize_failure_workpiece(
                        context.workpiece_description, context.raw_workpiece, context.dry_run_metadata,
                    )
                    if context is not None else None
                ),
                "failure": asdict(failure) if failure is not None else None,
                "cycle_failure": (
                    asdict(context.operation_failure)
                    if context is not None and context.operation_failure is not None else None
                ),
                "collision_event": dict(collision_event) if collision_event is not None else None,
                "failure_bundle": (
                    str(self._failure_bundle_path) if self._failure_bundle_path is not None else None
                ),
            }

    def write_failure_record(self, record: dict) -> None:
        """Persist a prepared failure snapshot outside process/state locks."""
        if self._failure_artifact_root is None:
            return
        from pathlib import Path
        from src.robot_systems.paint.diagnostics.failure_register import append_paint_failure_record

        append_paint_failure_record(Path(self._failure_artifact_root).parent, record)

    @property
    def consecutive_completed_cycles(self) -> int:
        """Session-only count of full paint cycles completed since the last failure."""
        with self._active_context_lock:
            return self._consecutive_completed_cycles

    def reset_completed_cycle_streak(self) -> None:
        """Clear the diagnostic streak after a process fault."""
        with self._active_context_lock:
            self._consecutive_completed_cycles = 0

    def ensure_tray_ready_for_start(self, config: PaintProcessConfig | None = None) -> None:
        """Enforce tray readiness for UI, physical buttons and direct production."""
        if config is None:
            config = (
                self._paint_process_config_service.get_snapshot()
                if self._paint_process_config_service is not None
                else PAINT_PROCESS_CONFIG
            )
        if config.enable_dry_run_mode:
            return
        dropoff = config.dropoff
        if dropoff.strategy is DropoffStrategy.PLATE_LAYOUT or dropoff.alternate_drying_demo:
            if self._plate_layout_service is None:
                raise TrayUnavailableError()
            self._plate_layout_service.ensure_ready(dropoff)

    def pause_current_phase(self) -> None:
        with self._active_context_lock:
            context = self._active_execution_context
        if context is not None:
            context.run_allowed.clear()
        self._paint_control.request_pause()
        self._stop_active_magazine_navigation_motion()
        self._path_executor.pause_current_execution()

    def resume_current_phase(self) -> None:
        self._clear_prepositioned_start_group()
        with self._active_context_lock:
            context = self._active_execution_context
        if context is not None:
            context.run_allowed.set()
        self._paint_control.resume()

    def stop_current_phase(self) -> None:
        self._clear_prepositioned_start_group()
        with self._active_context_lock:
            context = self._active_execution_context
        if context is not None:
            context.stop_event.set()
            context.run_allowed.set()
        self._paint_control.request_stop()

    def can_retry_unmatched_workpiece(self) -> bool:
        """Only a failed match at the paint capture position can be recaptured."""
        with self._active_context_lock:
            context = self._last_execution_context
            return bool(
                self._active_execution_context is None
                and context is not None
                and context.raw_workpiece is None
                and context.result.outcome is PaintOutcome.UNMATCHED
                and not context.magazine_stage_only
                and context.cached_workpiece_contour is None
            )

    def prepare_dropoff(self) -> tuple[bool, str]:
        """Prepare the active workpiece through the public execution contract."""
        return self._dropoff_executor.prepare_dropoff()

    def release_dropoff(self, context) -> DropoffResult:
        """Release and remember successful prepositioning for the next cycle."""
        result = self._dropoff_executor.release_dropoff(self._next_cycle_start_target(context))
        if result.success and result.prepositioned_group:
            self._mark_prepositioned_start_group(result.prepositioned_group)
        return result

    def run_once(
        self, stop_requested: Optional[Callable[[], bool]] = None, *,
        manual_single_cycle: bool = False, adjustment_session=None,
        retry_unmatched_workpiece: bool = False,
    ) -> tuple[bool, str]:
        """Legacy production adapter; normal exhaustion is successful termination."""
        result = self.run_once_result(
            stop_requested, manual_single_cycle=manual_single_cycle,
            adjustment_session=adjustment_session,
            retry_unmatched_workpiece=retry_unmatched_workpiece,
        )
        return result.as_legacy_pair()

    @observed_operation('paint.production')
    def run_once_result(
        self,
        stop_requested: Optional[Callable[[], bool]] = None,
        *,
        manual_single_cycle: bool = False,
        adjustment_session=None,
        retry_unmatched_workpiece: bool = False,
    ) -> PaintOperationResult:
        """Run production, optionally forcing one calibration-table cycle without magazine load."""
        self.last_failure = None
        with self._active_context_lock:
            self._failure_register_context = None
            self._failure_register_observation = current_context()
            self._failure_register_streak = None
            self._failure_bundle_path = None
        self.ensure_tray_ready_for_start()
        self._clear_prepositioned_start_group()
        should_stop = stop_requested or (lambda: False)
        self._paint_control.reset()
        process_config_result = self._get_process_config()

        if not process_config_result[0]:
            return PaintOperationResult.failed(PaintFailureCode.INVALID_CONFIGURATION, 'process_settings', process_config_result[1])

        process_config = process_config_result[2]
        self._head_check_run = None
        if process_config is not None and process_config.head_check.enabled:
            mode = (
                HeadCheckOperatingMode.PICKUP_ONLY if process_config.stop_after_calibration_pickup else
                HeadCheckOperatingMode.ADJUSTMENT if adjustment_session is not None else
                HeadCheckOperatingMode.DRY_RUN if process_config.enable_dry_run_mode else
                HeadCheckOperatingMode.PRODUCTION
            )
            if mode is not HeadCheckOperatingMode.PICKUP_ONLY:
                if self._head_check_run_factory is None:
                    return head_check_failed(HeadInspectionFailure(
                        HeadInspectionFailureCode.SERVICE_UNAVAILABLE,
                        "Paint-head checks are enabled, but their inspection service is not configured",
                    ))
                try:
                    self._head_check_run = self._head_check_run_factory.create_run(
                        process_config.head_check, mode,
                    )
                except PaintHeadCheckError as error:
                    return head_check_failed(error.failure)
        if process_config is not None and process_config.enable_dry_run_mode:
            if self._dry_run_snapshot_source is None:
                return PaintOperationResult.failed(
                    PaintFailureCode.INVALID_CONFIGURATION,
                    "dry_run",
                    "Dry-run mode is enabled but its dataset source is unavailable",
                )
            self._dry_run_snapshot_source.start_run()
            _logger.warning(
                "[DRY_RUN] Starting synthetic production; camera workpiece "
                "detection and physical pickup sensing are bypassed; vacuum "
                "pump operation remains enabled"
            )
        magazine_config = process_config.magazine_load if process_config is not None else None
        if retry_unmatched_workpiece:
            if not self.can_retry_unmatched_workpiece():
                return PaintOperationResult.failed(PaintFailureCode.UNAVAILABLE, 'workpiece_recapture', 'No unmatched workpiece is ready for recapture')
            return self.run_cycle_result(
                should_stop,
                process_config=process_config,
                magazine_config=None,
                cycle_index=1,
                suppress_magazine_load=True,
                initial_state=PaintExecutionState.CAPTURE_WORKPIECE,
            )
        if manual_single_cycle or adjustment_session is not None:
            if magazine_config is None:
                return PaintOperationResult.failed(PaintFailureCode.UNAVAILABLE, "calibration_navigation", "Paint magazine calibration settings are unavailable")
            navigation_result = self._move_to_calibration_before_manual_cycle(magazine_config, should_stop, process_config=process_config)
            if not navigation_result.completed:
                return navigation_result
            result = self.run_cycle_result(
                should_stop,
                process_config=process_config,
                magazine_config=None,
                cycle_index=1,
                suppress_magazine_load=True,
                retry_capture_until_workpiece=True,
                adjustment_session=adjustment_session,
            )
            return result
        run_while_found = bool(
            (process_config or PAINT_PROCESS_CONFIG).run_while_workpiece_found
        )

        if self._magazine_load_service is not None and magazine_config is not None and magazine_config.enabled:
            fixed_groups = self._fixed_magazine_groups(magazine_config)
            fixed_sources = self._fixed_magazine_sources(magazine_config)
            pickup_mode = magazine_config.pickup_mode
            if (
                magazine_config.processing_strategy == MAGAZINE_PROCESSING_STRATEGY_BATCH_NESTING
            ):
                if pickup_mode != MAGAZINE_PICKUP_MODE_AUTO_DISCOVERY_SENSOR_CONTROLLED_FAST_LIN:
                    return PaintOperationResult.failed(PaintFailureCode.INVALID_CONFIGURATION, 'magazine_settings', 'Batch nesting currently requires the auto-discovery sensor-controlled magazine pickup mode')
                return self._run_magazine_batch_loop_result(
                    magazine_config,
                    process_config,
                    should_stop,
                    fixed_sources=fixed_sources,
                )
            if pickup_mode == MAGAZINE_PICKUP_MODE_FIXED_GROUP_SENSOR_CONTROLLED_FAST_LIN and not fixed_sources:
                return PaintOperationResult.failed(PaintFailureCode.INVALID_CONFIGURATION, 'magazine_settings', 'No fixed magazines are enabled')
            if (
                run_while_found
                or pickup_mode
                == MAGAZINE_PICKUP_MODE_AUTO_DISCOVERY_SENSOR_CONTROLLED_FAST_LIN
            ):
                return self._run_magazine_loop_result(
                    magazine_config,
                    process_config,
                    should_stop,
                    fixed_sources=fixed_sources,
                )

            result = self.run_cycle_result(
                should_stop,
                process_config=process_config,
                magazine_config=magazine_config,
                magazine_group=fixed_groups[0] if fixed_groups else None,
                magazine_source=fixed_sources[0] if fixed_sources else None,
                cycle_index=1,
            )
            ok, msg = result.completed, result.message

            if result.outcome is PaintOutcome.NO_WORKPIECE:
                return PaintOperationResult(PaintOutcome.COMPLETED, NO_WORKPIECE_AT_MAGAZINE, stop_reason=PaintOutcome.NO_WORKPIECE)
            return result

        if run_while_found and magazine_config is not None:
            return self._run_manual_loop_result(magazine_config, process_config, should_stop)

        if magazine_config is not None:
            navigation_result = self._move_to_calibration_before_manual_cycle(magazine_config, should_stop, process_config=process_config)
            if not navigation_result.completed:
                return navigation_result
        return self.run_cycle_result(
            should_stop,
            process_config=process_config,
            magazine_config=None,
            cycle_index=1,
        )

    def _run_manual_loop(self, *args, **kwargs) -> tuple[bool, str]:
        """Compatibility adapter for normal production-loop termination."""
        result = self._run_manual_loop_result(*args, **kwargs)
        return result.as_legacy_pair()

    def _run_manual_loop_result(self, magazine_config, process_config, should_stop: Callable[[], bool]) -> PaintOperationResult:
        total_start = perf_counter()
        completed_cycles = 0
        while not should_stop():
            navigation_result = self._move_to_calibration_before_manual_cycle(magazine_config, should_stop, process_config=process_config)
            if not navigation_result.completed:
                self._log_phase_timing(
                    "manual_loop_total",
                    total_start,
                    success=False,
                    completed_cycles=completed_cycles,
                )
                return navigation_result
            result = self.run_cycle_result(
                should_stop,
                process_config=process_config,
                magazine_config=None,
                cycle_index=completed_cycles + 1,
                repeats_after_success=True,
            )
            ok, msg = result.completed, result.message
            if result.outcome is PaintOutcome.NO_WORKPIECE:
                self._log_phase_timing(
                    "manual_loop_total",
                    total_start,
                    success=True,
                    completed_cycles=completed_cycles,
                )
                if completed_cycles == 0:
                    return PaintOperationResult(PaintOutcome.COMPLETED, 'No usable contour detected', stop_reason=PaintOutcome.NO_WORKPIECE)
                return PaintOperationResult(PaintOutcome.COMPLETED, f'No workpiece detected after {completed_cycles} paint cycle(s)', stop_reason=PaintOutcome.NO_WORKPIECE)
            if result.outcome is PaintOutcome.TRAY_FULL:
                return PaintOperationResult(PaintOutcome.COMPLETED, msg, stop_reason=PaintOutcome.TRAY_FULL)
            if not ok:
                self._log_phase_timing(
                    "manual_loop_total",
                    total_start,
                    success=False,
                    completed_cycles=completed_cycles,
                )
                return result
            completed_cycles += 1
            if process_config.stop_after_calibration_pickup:
                return result
            if result.stop_reason is PaintOutcome.TRAY_FULL:
                return result
        self._log_phase_timing(
            "manual_loop_total",
            total_start,
            success=False,
            stopped=True,
            completed_cycles=completed_cycles,
        )
        return PaintOperationResult(PaintOutcome.CANCELLED, 'Paint process stopped')

    def _run_magazine_loop(self, *args, **kwargs) -> tuple[bool, str]:
        """Compatibility adapter for normal production-loop termination."""
        result = self._run_magazine_loop_result(*args, **kwargs)
        return result.as_legacy_pair()

    def _run_magazine_loop_result(
        self,
        magazine_config,
        process_config,
        should_stop: Callable[[], bool],
        *,
        fixed_sources: tuple[dict, ...] | None = None,
    ) -> PaintOperationResult:
        total_start = perf_counter()
        completed_cycles = 0
        sources = fixed_sources if fixed_sources is not None else self._fixed_magazine_sources(magazine_config)
        group_index = 0
        consecutive_empty_groups = 0
        discovery_contours: list = []
        discovery_active_contour = None
        discovery_snapshot = None
        pickup_mode = magazine_config.pickup_mode
        auto_discovery = (
            pickup_mode == MAGAZINE_PICKUP_MODE_AUTO_DISCOVERY_SENSOR_CONTROLLED_FAST_LIN
        )
        while not should_stop():
            active_source = sources[group_index] if sources else None
            active_group = (
                str(magazine_config.magazine_group_id).strip()
                if auto_discovery
                else self._magazine_source_group(active_source, magazine_config)
            )
            self._last_execution_context = None
            result = self.run_cycle_result(
                should_stop,
                process_config=process_config,
                magazine_config=magazine_config,
                magazine_group=active_group,
                magazine_source=active_source,
                magazine_index=group_index,
                cycle_index=completed_cycles + 1,
                repeats_after_success=True,
                magazine_discovery_contours=discovery_contours,
                magazine_discovery_active_contour=discovery_active_contour,
                magazine_discovery_snapshot=discovery_snapshot,
            )
            ok, msg = result.completed, result.message

            context = self._last_execution_context
            if auto_discovery and context is not None:
                discovery_contours = list(context.magazine_discovery_contours)
                discovery_active_contour = context.magazine_discovery_active_contour
                discovery_snapshot = context.magazine_snapshot

            if result.outcome is PaintOutcome.NO_WORKPIECE:
                if auto_discovery:
                    if context is not None and context.magazine_discovery_empty_capture:
                        self._log_phase_timing(
                            "magazine_loop_total",
                            total_start,
                            success=True,
                            completed_cycles=completed_cycles,
                        )
                        return PaintOperationResult(PaintOutcome.COMPLETED, MAGAZINE_EMPTY, stop_reason=PaintOutcome.NO_WORKPIECE)
                    discovery_active_contour = None
                    active_magazine_config = (
                        context.magazine_config
                        if context is not None
                        else magazine_config
                    )
                    if active_magazine_config.recapture_after_pile_done:
                        discovery_contours = []
                        discovery_snapshot = None
                        _logger.info(
                            "[MAGAZINE_LOAD] Active pile is empty; clearing cached "
                            "discovery so the magazine is recaptured"
                        )
                    self._clear_prepositioned_start_group()
                    continue
                consecutive_empty_groups += 1
                if sources and consecutive_empty_groups < len(sources):
                    next_index = (group_index + 1) % len(sources)
                    next_group = self._magazine_source_group(sources[next_index], magazine_config)
                    _logger.info(
                        "[MAGAZINE_LOAD] Magazine group '%s' is empty; advancing to '%s'",
                        active_group,
                        next_group,
                    )
                    group_index = next_index
                    self._clear_prepositioned_start_group()
                    continue
                self._log_phase_timing(
                    "magazine_loop_total",
                    total_start,
                    success=True,
                    completed_cycles=completed_cycles,
                )
                _logger.info(
                    "[MAGAZINE_LOAD] All %d configured magazine(s) are empty",
                    len(sources) or 1,
                )
                return PaintOperationResult(PaintOutcome.COMPLETED, ALL_MAGAZINES_EMPTY, stop_reason=PaintOutcome.NO_WORKPIECE)
            if result.outcome is PaintOutcome.TRAY_FULL:
                return PaintOperationResult(PaintOutcome.COMPLETED, msg, stop_reason=PaintOutcome.TRAY_FULL)
            if not ok:
                self._log_phase_timing(
                    "magazine_loop_total",
                    total_start,
                    success=False,
                    completed_cycles=completed_cycles,
                )
                return result
            completed_cycles += 1
            active_magazine_config = (
                context.magazine_config
                if context is not None
                else magazine_config
            )
            if auto_discovery and active_magazine_config.recapture_every_cycle:
                discovery_contours = []
                discovery_active_contour = None
                discovery_snapshot = None
                _logger.info(
                    "[MAGAZINE_LOAD] Cycle completed; clearing cached discovery "
                    "so the magazine is recaptured before the next pickup"
                )
            if process_config.stop_after_calibration_pickup:
                return result
            consecutive_empty_groups = 0
            if result.stop_reason is PaintOutcome.TRAY_FULL:
                return result
        self._log_phase_timing(
            "magazine_loop_total",
            total_start,
            success=False,
            stopped=True,
            completed_cycles=completed_cycles,
        )
        return PaintOperationResult(PaintOutcome.CANCELLED, 'Paint process stopped')

    def _run_magazine_batch_loop(self, *args, **kwargs) -> tuple[bool, str]:
        """Compatibility adapter for normal production-loop termination."""
        result = self._run_magazine_batch_loop_result(*args, **kwargs)
        return result.as_legacy_pair()

    def _run_magazine_batch_loop_result(
        self,
        magazine_config,
        process_config,
        should_stop: Callable[[], bool],
        *,
        fixed_sources: tuple[dict, ...] | None = None,
    ) -> PaintOperationResult:
        """Fill the paint work area, then process one cached capture as a batch."""
        completed = 0
        discovery_contours: list = []
        discovery_active = None
        discovery_snapshot = None
        sources = fixed_sources if fixed_sources is not None else self._fixed_magazine_sources(magazine_config)
        group_index = 0
        while not should_stop():
            self._magazine_load_service.clear_work_area_nesting()
            staged = 0
            while not should_stop():
                source = sources[group_index] if sources else None
                mode = magazine_config.pickup_mode
                group = (
                    str(magazine_config.magazine_group_id or "Magazine").strip()
                    if mode == MAGAZINE_PICKUP_MODE_AUTO_DISCOVERY_SENSOR_CONTROLLED_FAST_LIN
                    else self._magazine_source_group(source, magazine_config)
                )
                self._last_execution_context = None
                result = self.run_cycle_result(
                    should_stop,
                    process_config=process_config,
                    magazine_config=magazine_config,
                    magazine_group=group,
                    magazine_source=source,
                    magazine_index=group_index,
                    cycle_index=completed + staged + 1,
                    magazine_discovery_contours=discovery_contours,
                    magazine_discovery_active_contour=discovery_active,
                    magazine_discovery_snapshot=discovery_snapshot,
                    magazine_stage_only=True,
                )
                ok, message = result.completed, result.message
                context = self._last_execution_context
                if context is not None:
                    discovery_contours = list(context.magazine_discovery_contours)
                    discovery_active = context.magazine_discovery_active_contour
                    discovery_snapshot = context.magazine_snapshot
                if not ok:
                    if result.outcome is PaintOutcome.NO_WORKPIECE:
                        discovery_active = None
                        active_magazine_config = (
                            context.magazine_config
                            if context is not None
                            else magazine_config
                        )
                        if active_magazine_config.recapture_after_pile_done:
                            discovery_contours = []
                            discovery_snapshot = None
                            _logger.info(
                                "[MAGAZINE_LOAD] Active pile is empty during batch "
                                "staging; clearing cached discovery so the magazine "
                                "is recaptured"
                            )
                        break
                    if result.outcome is PaintOutcome.WORK_AREA_FULL:
                        break
                    return result
                staged += 1
                active_magazine_config = (
                    context.magazine_config
                    if context is not None
                    else magazine_config
                )
                if active_magazine_config.recapture_every_cycle:
                    discovery_contours = []
                    discovery_active = None
                    discovery_snapshot = None
                    _logger.info(
                        "[MAGAZINE_LOAD] Batch staging pickup completed; clearing "
                        "cached discovery so the magazine is recaptured"
                    )
                if context is not None and not context.magazine_nesting_has_more:
                    break

            if should_stop():
                return PaintOperationResult(PaintOutcome.CANCELLED, 'Paint process stopped')
            if staged == 0:
                if context is not None and context.magazine_discovery_empty_capture:
                    return PaintOperationResult(PaintOutcome.COMPLETED, MAGAZINE_EMPTY, stop_reason=PaintOutcome.NO_WORKPIECE)
                continue

            navigation_result = self._move_to_calibration_before_manual_cycle(
                magazine_config, should_stop, process_config=process_config,
            )
            if not navigation_result.completed:
                return navigation_result
            snapshot = self._capture_snapshot_service.capture_snapshot(source="paint_batch_staging")
            contours = list(snapshot.contours or ())
            if not contours:
                return PaintOperationResult.failed(PaintFailureCode.MOTION, '_run_magazine_batch_loop', 'Batch nesting staged workpieces but calibration capture found none')
            _logger.info("[BATCH_NESTING] captured staged batch workpieces=%d", len(contours))
            for index, contour in enumerate(contours):
                remaining = index + 1 < len(contours)
                result = self.run_cycle_result(
                    should_stop,
                    process_config=process_config,
                    magazine_config=None,
                    cycle_index=completed + 1,
                    repeats_after_success=remaining,
                    cached_snapshot=snapshot,
                    cached_workpiece_contour=contour,
                    suppress_magazine_load=True,
                )
                ok, message = result.completed, result.message
                if not ok:
                    return result
                completed += 1
            self._magazine_load_service.clear_work_area_nesting()
        return PaintOperationResult(PaintOutcome.CANCELLED, 'Paint process stopped')

    @staticmethod
    def _fixed_magazine_groups(magazine_config) -> tuple[str, ...]:
        mode = magazine_config.pickup_mode
        if mode != MAGAZINE_PICKUP_MODE_FIXED_GROUP_SENSOR_CONTROLLED_FAST_LIN:
            return ()
        return magazine_config.effective_fixed_pickup_group_ids()

    @staticmethod
    def _fixed_magazine_sources(magazine_config) -> tuple[dict, ...]:
        mode = magazine_config.pickup_mode
        if mode != MAGAZINE_PICKUP_MODE_FIXED_GROUP_SENSOR_CONTROLLED_FAST_LIN:
            return ()
        return magazine_config.effective_fixed_pickup_sources()

    @staticmethod
    def _magazine_source_group(source: dict | None, magazine_config) -> str:
        if not isinstance(source, dict) or "movement_group_id" not in source:
            raise ValueError("Fixed magazine source requires movement_group_id")
        group_id = str(source["movement_group_id"] or "").strip()
        if not group_id:
            raise ValueError("Fixed magazine source movement_group_id cannot be empty")
        return group_id

    def _run_single_cycle(self, should_stop: Callable[[], bool], **kwargs) -> tuple[bool, str]:
        """Legacy single-cycle adapter; internal orchestration uses run_cycle_result."""
        return self.run_cycle_result(should_stop, **kwargs).as_legacy_pair()

    @observed_operation('paint.cycle', cycle=True)
    def run_cycle_result(
        self,
        should_stop: Callable[[], bool],
        *,
        process_config,
        magazine_config,
        magazine_group: str | None = None,
        magazine_source: dict | None = None,
        magazine_index: int = 0,
        cycle_index: int,
        repeats_after_success: bool = False,
        magazine_discovery_contours: list | None = None,
        magazine_discovery_active_contour=None,
        magazine_discovery_snapshot=None,
        magazine_stage_only: bool = False,
        cached_snapshot=None,
        cached_workpiece_contour=None,
        suppress_magazine_load: bool = False,
        retry_capture_until_workpiece: bool = False,
        adjustment_session=None,
        initial_state: PaintExecutionState = PaintExecutionState.STARTING,
    ) -> PaintOperationResult:
        with self._active_context_lock:
            # A failed new preparation must never inherit the previous part/bundle.
            self._failure_register_context = None
            self._failure_register_observation = current_context()
            self._failure_register_streak = None
            self._failure_bundle_path = None
        raw_process_config = process_config or PAINT_PROCESS_CONFIG
        process_config = scale_paint_process_accelerations(raw_process_config)
        if self._paint_process_config_service is not None:
            try:
                raw_process_config = self._paint_process_config_service.get_snapshot()
                process_config = scale_paint_process_accelerations(raw_process_config)
            except Exception:
                _logger.exception("Failed to capture settings for paint cycle %d", cycle_index)
                return PaintOperationResult.failed(PaintFailureCode.INVALID_CONFIGURATION, 'process_settings', 'Failed to read paint process settings')
        latest_magazine_config = process_config.magazine_load
        if latest_magazine_config is not None and not suppress_magazine_load:
            magazine_config = latest_magazine_config
            pickup_mode = magazine_config.pickup_mode
            if pickup_mode != MAGAZINE_PICKUP_MODE_FIXED_GROUP_SENSOR_CONTROLLED_FAST_LIN:
                # Vision strategies always acquire from the camera observer.
                # Do not let a fixed-source choice made from an older settings
                # snapshot leak into this cycle.
                magazine_group = str(magazine_config.magazine_group_id).strip()
                magazine_source = None
        self.ensure_tray_ready_for_start(raw_process_config)
        cycle_strategy = self._effective_dropoff_strategy(process_config, cycle_index)
        self._path_executor.set_cycle_dropoff_strategy(cycle_strategy)
        _logger.info(
            "[DRYING_MODE] cycle=%d effective_dropoff_strategy=%s alternating_demo=%s",
            cycle_index,
            cycle_strategy or "configured",
            process_config.dropoff.alternate_drying_demo,
        )
        context = PaintExecutionContext(
            production_service=self,
            stop_requested=should_stop,
            control=self._paint_control,
            process_config=process_config,
            raw_process_config=raw_process_config,
            magazine_config=magazine_config,
            magazine_group=str(magazine_group or "").strip(),
            magazine_index=int(magazine_index),
            cycle_index=cycle_index,
            head_check_run=self._head_check_run,
            head_check_pause_request=self._head_check_pause_handler,
            repeats_after_success=repeats_after_success,
            total_started_at=perf_counter(),
            magazine_discovery_contours=list(magazine_discovery_contours or ()),
            magazine_discovery_active_contour=magazine_discovery_active_contour,
            magazine_snapshot=magazine_discovery_snapshot,
            magazine_stage_only=bool(magazine_stage_only),
            retry_capture_until_workpiece=retry_capture_until_workpiece,
            adjustment_session=adjustment_session,
            snapshot=cached_snapshot,
            cached_workpiece_contour=cached_workpiece_contour,
            diagnostic_cycle_id=current_context()['cycle_id'],
            diagnostic_context=current_context(),
        )
        if context.head_check_run is not None:
            context.head_check_return = partial(self.return_from_head_check, context)
        if isinstance(magazine_source, dict) and "position" in magazine_source:
            context.magazine_fixed_pickup_pose = [
                float(value) for value in list(magazine_source["position"])[:6]
            ]
        with self._active_context_lock:
            self._active_execution_context = context
            self._failure_register_context = context
        raised_exception = None
        execution = None
        try:
            execution = run_paint_cycle(context, initial_state=initial_state)
            if execution.result.failure is not None and context.operation_failure is None:
                context.set_outcome(execution.result)
        except Exception as exc:
            raised_exception = exc
            raise
        finally:
            self._last_execution_context = context
            self._log_execution_state_timing(context)
            has_failure = bool(
                context.operation_failure is not None
                or context.tray_failure is not None
                or raised_exception is not None
                or (execution is not None and execution.result.failure is not None)
            )
            completed_cycle = bool(
                execution is not None
                and execution.result.completed
                and not magazine_stage_only
                and not process_config.stop_after_calibration_pickup
                and not should_stop()
            )
            with self._active_context_lock:
                if has_failure:
                    self._failure_register_streak = self._consecutive_completed_cycles
                    self._consecutive_completed_cycles = 0
                # stop_machine() sets context.stop_event on successful completion
                # too; only the production control represents a cancellation here.
                elif completed_cycle and not self._paint_control.should_stop():
                    self._consecutive_completed_cycles += 1
                if self._active_execution_context is context:
                    self._active_execution_context = None
            if has_failure:
                self._store_failure_bundle(context, raised_exception)
            self._path_executor.set_cycle_dropoff_strategy(None)

        self.last_failure = context.tray_failure or context.operation_failure
        if execution.machine_error is not None:
            self._clear_prepositioned_start_group()
            self._restore_brightness()
            self._set_dashboard_live_view_paused(False, reason="paint cycle finished")
        if (
            completed_cycle and not has_failure and not self._paint_control.should_stop()
            and context.head_check_run is not None
        ):
            context.head_check_run.record_completed_cycle()
        return execution.result

    def _store_failure_bundle(self, context, raised_exception=None) -> None:
        if self._failure_artifact_root is None:
            return
        from src.robot_systems.paint.diagnostics.failure_bundle import write_paint_failure_bundle
        destination = write_paint_failure_bundle(
            context,
            self._path_executor,
            self._failure_artifact_root,
            raised_exception=raised_exception,
        )
        with self._active_context_lock:
            self._failure_bundle_path = destination / "failure_bundle.json" if destination is not None else None

    @staticmethod
    def _effective_dropoff_strategy(process_config, cycle_index: int) -> str | None:
        dropoff = process_config.dropoff
        if dropoff.alternate_drying_demo:
            return (
                DropoffStrategy.MOVEMENT_GROUP
                if int(cycle_index) % 2 == 1
                else DropoffStrategy.PLATE_LAYOUT
            )
        return dropoff.strategy

    def _read_start_recovery_pose(self) -> list[float]:
        return read_fresh_pose(
            self._path_executor._robot_service,
            error_message="Cannot determine robot area before startup",
        )

    def _execute_start_recovery_route(self, label: str, segments: list[OrderedPositionCommand]) -> bool:
        return self._path_executor._motion.move_ordered_pickup_sequence(label, segments)

    def prepare_start_recovery(self, ctx: PaintExecutionContext) -> StartRecoveryResult:
        """Apply regional routing before unwind or any production navigation."""
        executor = self._path_executor
        previous_control = executor._active_execution_control
        executor._active_execution_control = ctx.control
        try:
            config = ctx.process_config or executor._paint_process_config()
            executor._refresh_runtime_config()
            return self._start_recovery.prepare(
                dropoff=config.dropoff,
                target_provider=lambda: self._production_start_target(ctx),
                should_stop=ctx.motion_cancel_requested,
                tool=executor._motion_tool(), user=executor._motion_user(),
            )
        except Exception as exc:
            _logger.exception("Failed to prepare start recovery dependencies")
            return StartRecoveryResult(
                StartRecoveryOutcome.FAILED, RecoveryInternalError(str(exc)).failure,
            )
        finally:
            executor._active_execution_control = previous_control

    def _next_cycle_start_target(self, ctx: PaintExecutionContext) -> NextCycleTarget | None:
        if not ctx.repeats_after_success:
            return None
        return self._production_start_target(ctx)

    def _production_start_target(self, ctx: PaintExecutionContext) -> NextCycleTarget | None:
        """Resolve the first production destination, including single-cycle runs."""
        magazine = ctx.magazine_config
        configured_magazine = magazine or ctx.process_config.magazine_load
        if magazine is not None and magazine.enabled:
            group_id = ctx.magazine_group or (
                magazine.fixed_pickup_group_id
                if magazine.pickup_mode == MAGAZINE_PICKUP_MODE_FIXED_GROUP_SENSOR_CONTROLLED_FAST_LIN
                else magazine.magazine_group_id
            )
            velocity = float(magazine.move_to_magazine_vel_percent)
            acceleration = float(magazine.move_to_magazine_acc_percent)
            motion_type = magazine.move_to_magazine_motion_type
        else:
            group_id = str(configured_magazine.calibration_group_id)
            nav = ctx.process_config.navigation_return
            velocity = float(nav.calibration_move_vel_percent)
            acceleration = float(nav.calibration_move_acc_percent)
            motion_type = nav.calibration_move_motion_type
        group_id = str(group_id or "").strip()
        navigation = self._navigation_service
        if navigation is None:
            _logger.error("[NEXT_CYCLE] Paint navigation service is unavailable")
            return None
        pose = ctx.magazine_fixed_pickup_pose
        if pose is None:
            pose = navigation.get_group_position(group_id) if group_id else None
        if pose is None or len(pose) < 6:
            _logger.error("[NEXT_CYCLE] Cannot resolve start movement group '%s'", group_id)
            # TODO - consider returning a structured result instead of None to indicate a missing start target
            return None
        return NextCycleTarget(
            group_id=group_id,
            position=tuple(float(value) for value in pose[:6]),
            velocity_percent=velocity,
            acceleration_percent=acceleration,
            motion_type=motion_type,
        )

    def _mark_prepositioned_start_group(self, group_id: str) -> None:
        self._prepositioned_start_group = str(group_id or "").strip() or None

    def _clear_prepositioned_start_group(self) -> None:
        self._prepositioned_start_group = None

    def _consume_verified_prepositioned_start_group(
        self,
        group_id: str,
        *,
        expected_position: list[float] | None = None,
        position_tolerance_mm: float = 2.0,
        orientation_tolerance_deg: float = 2.0,
    ) -> bool:
        expected_group = str(group_id or "").strip()
        if not expected_group or self._prepositioned_start_group != expected_group:
            return False
        self._prepositioned_start_group = None
        navigation = self._magazine_load_service._navigation
        expected = expected_position
        if expected is None:
            expected = navigation.get_group_position(expected_group)
        try:
            actual = read_fresh_pose(
                self._path_executor._robot_service,
                error_message=f"Failed to verify prepositioned group '{expected_group}'",
            )
        except FreshPoseReadError as exc:
            _logger.error("[NEXT_CYCLE] %s", exc)
            # If we cannot read the current pose, we cannot verify the prepositioned start group.
            # TODO - consider returning a structured result instead of False to indicate a failed verification due to pose read error.
            # TODO - continuation from above - and maybe masking it as False is not the best idea, because if we can not read the pose maybe should fail loud and clear in order to investigate and fix the cause of the pose read error.
            return False
        if expected is None or actual is None or len(expected) < 6 or len(actual) < 6:
            return False
        xyz_error = math.sqrt(sum((float(actual[i]) - float(expected[i])) ** 2 for i in range(3)))
        angle_error = max(
            abs((float(actual[i]) - float(expected[i]) + 180.0) % 360.0 - 180.0)
            for i in range(3, 6)
        )
        verified = xyz_error <= float(position_tolerance_mm) and angle_error <= float(orientation_tolerance_deg)
        _logger.info(
            "[NEXT_CYCLE] Preposition verification group='%s' verified=%s xyz_error_mm=%.3f angle_error_deg=%.3f",
            expected_group,
            verified,
            xyz_error,
            angle_error,
        )
        return verified

    def _stop_active_magazine_navigation_motion(self) -> None:
        with self._active_context_lock:
            context = self._active_execution_context
        if context is None or context.current_state is None:
            return
        if not context.current_state.name.startswith("MAGAZINE_"):
            return
        try:
            self._magazine_load_service._navigation.stop_motion()
        except Exception:
            _logger.exception("[MAGAZINE_LOAD] Failed to stop robot motion during pause")
            # TODO - is simply logging this enough? Should we raise an exception or return a failure result to the caller?

    def _freeze_brightness_after_capture(self) -> None:
        """Freeze auto-brightness after the workpiece capture so exposure stays stable while painting.

        Mirrors the robot-calibration pattern (lock_auto_brightness_adjustment); the
        lock is restored by _restore_brightness() in the cycle's finally block.
        """
        vision = self._vision_service
        if vision is None:
            return
        try:
            if not vision.get_auto_brightness_enabled():
                return
            vision.lock_auto_brightness_adjustment()
            self._brightness_locked = True
            _logger.info("Freezing auto brightness adjustment after workpiece capture")
        except Exception:
            # TODO - is simply logging this enough? Should we raise an exception or return a failure result to the caller?

            _logger.exception("Failed to freeze auto brightness adjustment after capture")

    def _restore_brightness(self) -> None:
        """Restore adaptive auto brightness after the paint cycle finishes."""
        if not self._brightness_locked:
            return
        self._brightness_locked = False
        vision = self._vision_service
        if vision is None:
            return
        try:
            vision.unlock_auto_brightness_adjustment()
            _logger.info("Restoring adaptive auto brightness adjustment after paint cycle")
        except Exception:
            # TODO - is simply logging this enough? Should we raise an exception or return a failure result to the caller?

            _logger.exception("Failed to restore auto brightness adjustment after paint cycle")

    def _restore_brightness_for_capture(self, reason: str) -> None:
        """Resume auto-brightness before camera captures that need fresh correction."""
        if not self._brightness_locked:
            return
        _logger.info("Restoring adaptive auto brightness adjustment %s", reason)
        self._restore_brightness()

    def _restore_capture_view(self, reason: str) -> None:
        """Resume live vision only after the robot reaches a camera capture location."""
        self._set_dashboard_live_view_paused(False, reason=reason)
        self._restore_brightness_for_capture(reason)

    def _restore_magazine_capture_view(self, reason: str) -> None:
        """Resume magazine vision while preserving a locked known-good correction."""
        self._set_dashboard_live_view_paused(False, reason=reason)
        if self._brightness_locked:
            _logger.info(
                "Keeping auto brightness adjustment locked while restoring the "
                "saved magazine correction"
            )
            return
        self._restore_brightness_for_capture(reason)

    def _get_process_config(self) -> tuple[bool, str, object | None]:
        config_service = self._paint_process_config_service
        if config_service is None:
            return True, "", None
        try:
            config = scale_paint_process_accelerations(config_service.get_snapshot())
        except Exception:
            _logger.exception("Failed to read paint process settings")
            return False, "Failed to read paint process settings", None
        return True, "", config

    def _move_to_calibration_before_manual_cycle(
        self,
        magazine_config: PaintMagazineLoadConfig,
        should_stop: Callable[[], bool],
        *,
        process_config: PaintProcessConfig | None = None,
    ) -> PaintOperationResult:
        if should_stop():
            return PaintOperationResult(PaintOutcome.CANCELLED, "Paint process stopped")
        if self._head_check_run is not None:
            try:
                if self._head_check_run.prepare_retry_in_place():
                    return PaintOperationResult(PaintOutcome.COMPLETED, "Inspection retry position verified")
            except PaintHeadCheckError as error:
                return head_check_failed(error.failure)
        recovery_context = PaintExecutionContext(
            production_service=self, stop_requested=should_stop, control=self._paint_control,
            process_config=process_config or PAINT_PROCESS_CONFIG,
        )
        recovery = self.prepare_start_recovery(recovery_context)
        if not recovery.succeeded:
            return recovery.to_operation_result()
        navigation = self._navigation_service
        if navigation is None:
            return PaintOperationResult.failed(PaintFailureCode.UNAVAILABLE, "calibration_navigation", "Navigation service unavailable for calibration move")
        group_id = str(magazine_config.calibration_group_id)
        if self._consume_verified_prepositioned_start_group(group_id):
            self._restore_capture_view("after verifying prepositioned calibration pickup")
            return PaintOperationResult(PaintOutcome.COMPLETED, "")

        phase_start = perf_counter()
        ok = bool(navigation.move_to_calibration_position(wait_cancelled=should_stop))
        self._log_phase_timing("move_to_calibration", phase_start, success=ok, cycle=1)
        if should_stop():
            return PaintOperationResult(PaintOutcome.CANCELLED, "Paint process stopped")
        if not ok:
            return PaintOperationResult.failed(PaintFailureCode.MOTION, "calibration_navigation", f"Failed to move to calibration position '{group_id}'")
        self._restore_capture_view("after reaching calibration pickup")
        settle_s = float(magazine_config.release_settle_s)
        settle_start = perf_counter()
        if not self._wait_for_capture_settle(settle_s, should_stop):
            return PaintOperationResult(PaintOutcome.CANCELLED, "Paint process stopped")
        self._log_phase_timing(
            "calibration_camera_settle",
            settle_start,
            configured_s=settle_s,
            cycle=1,
        )
        return PaintOperationResult(PaintOutcome.COMPLETED, "")

    def _wait_for_capture_settle(
        self,
        seconds: float,
        should_stop: Callable[[], bool],
    ) -> bool:
        deadline = monotonic() + max(0.0, seconds)
        while monotonic() < deadline:
            if should_stop() or self._paint_control.should_stop():
                return False
            if not self._paint_control.wait_if_paused():
                return False
            sleep(min(0.05, max(0.0, deadline - monotonic())))
        return not should_stop() and not self._paint_control.should_stop()

    def _wait_for_fresh_capture_frame(
        self,
        timeout_s: float,
        should_stop: Callable[[], bool],
    ) -> tuple[bool, str]:
        """Wait until resumed vision has published a genuinely fresh frame."""
        started = perf_counter()
        deadline = monotonic() + max(0.0, float(timeout_s))
        last_message = "No fresh camera frame available"
        while True:
            if should_stop() or self._paint_control.should_stop():
                return False, "Paint process stopped while waiting for a fresh camera frame"
            try:
                details = self._vision_service.get_health_details()
            except Exception as exc:
                return False, f"Failed to query camera frame readiness: {exc}"
            if bool(details.get("frame_fresh", False)):
                _logger.debug(
                    "[CAPTURE_TIMING] fresh_frame_ready elapsed_s=%.3f",
                    perf_counter() - started,
                )
                return True, ""
            last_message = str(details.get("message") or last_message)
            remaining_s = deadline - monotonic()
            if remaining_s <= 0.0:
                return False, f"Fresh camera frame unavailable after {timeout_s:.3f}s: {last_message}"
            sleep(min(0.02, remaining_s))

    def _path_debug_plots_enabled(self) -> bool:
        config_service = self._paint_process_config_service
        if config_service is None:
            return False
        return bool(config_service.get_snapshot().enable_path_debug_plots)

    def _pause_dashboard_live_view_after_capture(self) -> bool:
        config_service = self._paint_process_config_service
        if config_service is None:
            return True
        return bool(config_service.get_snapshot().pause_dashboard_live_view_after_capture)

    def _set_dashboard_live_view_paused(
        self,
        paused: bool,
        *,
        image: object | None = None,
        reason: str = "",
    ) -> None:
        vision = self._vision_service
        if vision is not None:
            lifecycle_method = vision.pause_processing if paused else vision.resume_processing
            try:
                lifecycle_method()
            except Exception:
                _logger.exception(
                    "Failed to %s vision processing: %s",
                    "pause" if paused else "resume",
                    reason,
                )
        messaging = self._messaging_service
        if messaging is None:
            return
        try:
            messaging.publish(
                PaintDashboardLiveViewTopics.STATE,
                PaintDashboardLiveViewEvent(
                    paused=bool(paused),
                    image=image,
                    reason=reason,
                ),
            )
        except Exception:
            _logger.exception("Failed to publish paint dashboard live-view state")

    def publish_dashboard_message(self, level: str, title: str, message: str) -> None:
        """Publish a production notice into the paint dashboard message queue."""
        if self._messaging_service is None:
            return
        try:
            self._messaging_service.publish(
                PaintDashboardMessageTopics.MESSAGE,
                PaintDashboardMessageEvent(
                    level=str(level or "info"),
                    title=str(title or ""),
                    message=str(message or ""),
                ),
            )
        except Exception:
            _logger.exception("Failed to publish paint dashboard message")

    @staticmethod
    def _log_execution_state_timing(context: PaintExecutionContext) -> None:
        recorder = context.state_timing_recorder
        if recorder is None:
            return
        try:
            recorder.log_state_summary(_logger)
        except Exception:
            _logger.exception("Failed to log paint execution state timing summary")

    @staticmethod
    def _log_phase_timing(label: str, started_at: float, **fields: object) -> None:
        suffix = " ".join(f"{key}={value}" for key, value in fields.items())
        if suffix:
            suffix = f" {suffix}"
        _logger.info("[PRODUCTION_TIMING] phase=%s elapsed_s=%.3f%s", label, perf_counter() - started_at, suffix)
