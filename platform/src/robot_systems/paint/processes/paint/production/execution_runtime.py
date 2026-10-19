"""Execution state, configuration, and operation composition for paint cycles."""

from __future__ import annotations

from src.robot_systems.paint.processes.paint.tray_dry.plate_layout import PlateLayoutService
from src.robot_systems.paint.contracts.dropoff import DropoffResult

import logging
import math
from dataclasses import replace
from typing import Callable, Optional

import numpy as np

from src.engine.geometry.planar import (
    axis_equivalent_shift_degrees,
)
from src.engine.robot.path_preparation import WorkpieceExecutionPlan
from src.engine.robot.motion_sequence import OrderedMotionType
from src.robot_systems.paint.processes.paint.configuration.models import (
    PAINT_PROCESS_CONFIG,
    PaintProcessConfig,
    scale_paint_process_accelerations,
    PaintSimulationConfig,
)
from src.robot_systems.paint.processes.paint.motion.waypoint import (
    ConfiguredMotionWaypoint,
)
from src.robot_systems.paint.processes.paint.planning import (
    build_paint_contact_source_plan,
    PaintPickupTransferPlanner,
    PickupTransferPlan,
)
from src.robot_systems.paint.processes.paint.operations.edge_cleanup.executor import PaintEdgeCleanupExecutor

from src.robot_systems.paint.processes.paint.planning.projection.planes import (
    get_execution_plane_strategy,
)
from src.robot_systems.paint.processes.paint.operations.painting.executor import PaintingExecutor
from src.robot_systems.paint.processes.paint.motion.executor import PaintMotionExecutor
from src.robot_systems.paint.processes.paint.operations.pickup.executor import PaintPickupExecutor
from src.robot_systems.paint.processes.paint.planning.projection import (
    project_paint_contact_motion_continuous,
    rebase_contact_motion_path_to_zero_start_rotation,
)
from src.robot_systems.paint.processes.paint.planning.projection.inputs import PaintProjectionContext
from src.robot_systems.paint.processes.paint.motion.path_geometry import shift_path_rotation
from src.robot_systems.paint.timing import timed_block

from src.robot_systems.paint.processes.paint.production.execution_dependencies import (
    PaintExecutorDependencies, PaintExecutorMotionConfig, PaintExecutorContactMotionConfig,
)
from src.robot_systems.paint.processes.paint.planning.pose_helpers import (
    _paint_axis_staging_offset_pose,
)
from src.robot_systems.paint.processes.paint.planning.projection.config import (
    _normalize_contact_motion_config, _xz_ry_projection_rotation_sign,
)
from src.robot_systems.paint.processes.paint.motion.recovery import PaintMotionRecovery
from src.robot_systems.paint.hardware.vacuum_control import PaintVacuumControl
from src.robot_systems.paint.processes.paint.production.prepared_cycle import run_prepared_paint_cycle

_logger = logging.getLogger(__name__)


class PaintExecutionRuntime:
    """Own execution state and compose operations for a paint cycle.

    Editor contracts live in adapters; prepared-cycle sequencing lives in
    prepared_cycle. Platform hardware services are injected at composition.
    """

    supports_paint_motion_states = True
    def __init__(
        self,
        *,
        dependencies: PaintExecutorDependencies,
        motion_config: PaintExecutorMotionConfig | None = None,
        contact_motion_config: PaintExecutorContactMotionConfig | None = None,
    ) -> None:
        """Store robot dependencies and initialize the pivot/pickup execution configuration."""
        motion_config = motion_config or PaintExecutorMotionConfig()
        contact_motion_config = contact_motion_config or PaintExecutorContactMotionConfig()

        # Dependencies.
        self._robot_service = dependencies.robot_service
        self._path_preparation_service = dependencies.path_preparation_service
        self._base_position_provider = dependencies.base_position_provider
        self._pickup_base_position_provider = dependencies.pickup_base_position_provider or dependencies.base_position_provider
        self._cleanup_base_position_provider = dependencies.cleanup_base_position_provider
        self._dropoff_position_provider = dependencies.dropoff_position_provider
        self._calibration_position_provider = dependencies.calibration_position_provider
        self._post_execute_callback = dependencies.post_execute_callback
        self._dryer_ready_for_release = dependencies.dryer_ready_for_release
        self._on_workpiece_release_verified = dependencies.on_workpiece_release_verified
        self._robot_config_provider = dependencies.robot_config_provider
        self._vacuum_pump = dependencies.vacuum_pump
        self._vacuum_pump_enabled_provider = dependencies.vacuum_pump_enabled_provider
        self._vacuum_sensor = dependencies.vacuum_sensor
        self._pickup_condition = dependencies.pickup_condition
        self._pickup_condition_provider = dependencies.pickup_condition_provider
        self._paint_process_config_service = dependencies.paint_process_config_service
        self._dropoff_motion_corridor_id = dependencies.dropoff_motion_corridor_id

        # Motion settings.
        self._enable_vacuum_pump = bool(motion_config.enable_vacuum_pump)
        self._pickup_tool = int(motion_config.pickup_tool)
        self._pickup_user = int(motion_config.pickup_user)
        self._pickup_z_mm = None if motion_config.pickup_z_mm is None else float(motion_config.pickup_z_mm)
        self._pickup_safety_z_min_mm = 100.0
        self._debug_dump_dir = motion_config.debug_dump_dir

        # Paint contact-motion settings.
        self._configured_contact_motion_plane = str(contact_motion_config.motion_plane or "xy_z_rz").strip().lower()
        self._configured_contact_translation_axis = str(contact_motion_config.translation_axis or "x").strip().lower()
        self._configured_contact_side = str(contact_motion_config.paint_side or "negative").strip().lower()
        self._configured_contact_translation_direction = str(contact_motion_config.translation_direction or "forward").strip().lower()
        self._apply_camera_to_tcp_for_pickup = bool(contact_motion_config.apply_camera_to_tcp_for_pickup)
        self._flip_xz_ry_execution_rotation_direction = bool(contact_motion_config.flip_xz_ry_execution_rotation_direction)
        self._mirror_xz_ry_pickup_handoff = bool(contact_motion_config.mirror_xz_ry_pickup_handoff)
        self._contact_motion_config = _normalize_contact_motion_config(
            motion_plane=contact_motion_config.motion_plane,
            translation_axis=contact_motion_config.translation_axis,
            pivot_side=contact_motion_config.paint_side,
            translation_direction=contact_motion_config.translation_direction,
            apply_camera_to_tcp_for_pickup=contact_motion_config.apply_camera_to_tcp_for_pickup,
            camera_to_tcp_x_offset=contact_motion_config.camera_to_tcp_x_offset,
            camera_to_tcp_y_offset=contact_motion_config.camera_to_tcp_y_offset,
            rotation_direction_sign=_xz_ry_projection_rotation_sign(
                contact_motion_config.motion_plane,
                self._flip_xz_ry_execution_rotation_direction,
            ),
        )
        self._pickup_contact_motion_config = _normalize_contact_motion_config(
            motion_plane="xy_z_rz",
            translation_axis=contact_motion_config.translation_axis,
            pivot_side=contact_motion_config.paint_side,
            translation_direction=contact_motion_config.translation_direction,
            apply_camera_to_tcp_for_pickup=contact_motion_config.apply_camera_to_tcp_for_pickup,
            camera_to_tcp_x_offset=contact_motion_config.camera_to_tcp_x_offset,
            camera_to_tcp_y_offset=contact_motion_config.camera_to_tcp_y_offset,
        )
        self._contact_motion_strategy = get_execution_plane_strategy(self._contact_motion_config.motion_plane)

        # Per-run state and phase executors.
        self._last_execution_plan: WorkpieceExecutionPlan | None = None
        self._last_pickup_plan: PickupTransferPlan | None = None
        self.diagnostic_motion_commands: list[dict] = []
        self._plate_layout_service = (
            dependencies.plate_layout_service
            if dependencies.plate_layout_service is not None else PlateLayoutService()
        )
        self._pending_stage_pose: list[float] | None = None
        self._edge_cleanup = PaintEdgeCleanupExecutor(self)
        self._pickup = PaintPickupExecutor(self)
        self._paint_contact = PaintingExecutor(self)
        self._motion_recovery = PaintMotionRecovery(self._robot_service, self._execution_control)
        self._motion = PaintMotionExecutor(
            self._robot_service, tool_provider=self._motion_tool,
            user_provider=self._motion_user, recovery=self._motion_recovery,
            command_recorder=self._record_motion_command,
        )
        self._vacuum = PaintVacuumControl(
            self._vacuum_pump,
            enabled_provider=self._is_vacuum_pump_enabled,
            dry_run_provider=self._is_dry_run_mode_enabled,
        )
        self._pickup_transfer_planner = PaintPickupTransferPlanner(self)
        self._active_contact_base_z_offset_mm: float = 0.0
        self._last_process_start_rz: float | None = None
        self._last_paint_contact_end_rz: float | None = None
        self._last_process_end_pose: list[float] | None = None
        self._dropoff_unwind_prepared: bool = False
        self._last_prepositioned_start_group: str | None = None
        self._plate_entry_completed_in_paint_chain: bool = False
        self._last_pickup_contact_mode: str | None = None
        self._last_safe_travel_error: str = ""
        self._paint_process_config_snapshot: PaintProcessConfig = PAINT_PROCESS_CONFIG
        self._cycle_dropoff_strategy: str | None = None
        self._active_execution_control = None
        self._dropoff_strategy = dependencies.dropoff_strategy_factory(self)

    def prepare_dropoff(self) -> tuple[bool, str]:
        """Delegate destination preparation to the injected strategy."""
        return self._dropoff_strategy.prepare_dropoff()

    def release_dropoff(self, next_cycle_start=None) -> DropoffResult:
        """Delegate verified release and exit motion to the injected strategy."""
        return self._dropoff_strategy.release_dropoff(next_cycle_start)

    def _is_vacuum_pump_enabled(self) -> bool:
        """Return whether both process settings and live peripheral settings allow pump use."""
        if not self._enable_vacuum_pump:
            return False
        if self._vacuum_pump_enabled_provider is None:
            return True
        try:
            return bool(self._vacuum_pump_enabled_provider())
        except Exception:
            _logger.exception("[PICKUP] Failed to read live vacuum-pump enabled state")
            return False

    def _is_dry_run_mode_enabled(self) -> bool:
        """Return the dry-run state frozen for the active workpiece cycle."""
        return bool(self._paint_process_config_snapshot.enable_dry_run_mode)

    # -------------------------------------------------------------------------
    # Runtime Configuration And Plan Preparation
    # -------------------------------------------------------------------------
    # Refresh the execution snapshot before preparing or running a plan.

    def prepare_workpiece_execution_plan(self, workpiece: dict, skip_debug_plot: bool = False) -> WorkpieceExecutionPlan:
        """Build and cache the execution plan for a paint workpiece."""
        if self._path_preparation_service is None:
            raise RuntimeError("Path preparation service is not available")

        self._refresh_paint_process_config_snapshot()
        self._apply_paint_process_contact_config()
        generic_plan = self._path_preparation_service.build_execution_plan(workpiece, skip_debug_plot=skip_debug_plot)
        self._last_execution_plan = build_paint_contact_source_plan(generic_plan, self._contact_motion_config)
        return self._last_execution_plan

    def get_last_execution_plan(self) -> WorkpieceExecutionPlan | None:
        """Return the last paint execution plan prepared by this executor."""
        return self._last_execution_plan

    def _refresh_runtime_config(self) -> None:
        """Refresh robot-dependent pickup settings from the latest robot configuration."""
        if self._robot_config_provider is None:
            return
        robot_config = self._robot_config_provider()
        if robot_config is None:
            return
        self._pickup_tool = int(robot_config.robot_tool)
        self._pickup_user = int(robot_config.robot_user)
        self._pickup_safety_z_min_mm = float(robot_config.safety_limits.z_min)
        self._contact_motion_config = _normalize_contact_motion_config(
            motion_plane=self._contact_motion_config.motion_plane,
            translation_axis=self._contact_motion_config.translation_axis,
            pivot_side=self._contact_motion_config.paint_side,
            translation_direction=self._contact_motion_config.translation_direction,
            apply_camera_to_tcp_for_pickup=self._contact_motion_config.apply_camera_to_tcp_for_pickup,
            camera_to_tcp_x_offset=float(robot_config.camera_to_tcp_x_offset),
            camera_to_tcp_y_offset=float(robot_config.camera_to_tcp_y_offset),
            rotation_direction_sign=_xz_ry_projection_rotation_sign(
                self._contact_motion_config.motion_plane,
                self._flip_xz_ry_execution_rotation_direction,
            ),
            closed_contour_overlap_mm=self._contact_motion_config.closed_contour_overlap_mm,
        )
        self._pickup_contact_motion_config = _normalize_contact_motion_config(
            motion_plane="xy_z_rz",
            translation_axis=self._pickup_contact_motion_config.translation_axis,
            pivot_side=self._pickup_contact_motion_config.paint_side,
            translation_direction=self._pickup_contact_motion_config.translation_direction,
            apply_camera_to_tcp_for_pickup=self._pickup_contact_motion_config.apply_camera_to_tcp_for_pickup,
            camera_to_tcp_x_offset=float(robot_config.camera_to_tcp_x_offset),
            camera_to_tcp_y_offset=float(robot_config.camera_to_tcp_y_offset),
        )
        self._contact_motion_strategy = get_execution_plane_strategy(self._contact_motion_config.motion_plane)

    def _refresh_paint_process_config_snapshot(self) -> PaintProcessConfig:
        service = self._paint_process_config_service
        if service is None:
            self._paint_process_config_snapshot = PAINT_PROCESS_CONFIG
            self._apply_cycle_dropoff_strategy()
            return PAINT_PROCESS_CONFIG
        try:
            raw_config = service.get_snapshot()
            self._paint_process_config_snapshot = scale_paint_process_accelerations(
                raw_config
            )
            self._apply_cycle_dropoff_strategy()
            self._enable_vacuum_pump = bool(self._paint_process_config_snapshot.enable_vacuum_pump)
            if self._pickup_condition_provider is not None:
                self._pickup_condition = self._pickup_condition_provider()
            return raw_config
        except Exception:
            _logger.debug("[PAINT_CONFIG] Failed to refresh paint process settings", exc_info=True)
            self._paint_process_config_snapshot = PAINT_PROCESS_CONFIG
            self._apply_cycle_dropoff_strategy()
            return PAINT_PROCESS_CONFIG

    def _set_cycle_process_config_snapshot(self, config) -> None:
        """Freeze one raw settings snapshot for the active workpiece cycle."""
        self.diagnostic_motion_commands.clear()
        if config is None:
            self._paint_process_config_snapshot = PAINT_PROCESS_CONFIG
        else:
            self._paint_process_config_snapshot = scale_paint_process_accelerations(config)
        if self._paint_process_config_snapshot.enable_dry_run_mode:
            from src.robot_systems.paint.processes.paint.configuration.models import (
                PICKUP_CONTACT_MODE_SENSOR_CONTROLLED_FAST_LIN,
            )
            self._paint_process_config_snapshot = replace(
                self._paint_process_config_snapshot,
                pickup_motion=replace(
                    self._paint_process_config_snapshot.pickup_motion,
                    pickup_contact_mode=PICKUP_CONTACT_MODE_SENSOR_CONTROLLED_FAST_LIN,
                ),
            )
        self._apply_cycle_dropoff_strategy()
        self._enable_vacuum_pump = bool(self._paint_process_config_snapshot.enable_vacuum_pump)
        if self._pickup_condition_provider is not None:
            self._pickup_condition = self._pickup_condition_provider()

    def _apply_cycle_dropoff_strategy(self) -> None:
        if self._cycle_dropoff_strategy is None:
            return
        self._paint_process_config_snapshot = replace(
            self._paint_process_config_snapshot,
            dropoff=replace(
                self._paint_process_config_snapshot.dropoff,
                strategy=self._cycle_dropoff_strategy,
            ),
        )

    def set_cycle_dropoff_strategy(self, strategy: str | None) -> None:
        """Override the persisted strategy for one production cycle."""
        self._cycle_dropoff_strategy = str(strategy).strip().lower() if strategy else None
        self._refresh_paint_process_config_snapshot()

    def _paint_process_config(self) -> PaintProcessConfig:
        return self._paint_process_config_snapshot or PAINT_PROCESS_CONFIG

    def _scale_process_acceleration(self, acceleration: float) -> float:
        scale = max(
            0.0,
            min(
                100.0,
                float(
                    self._paint_process_config().paint_process_acceleration_scale_percent
                ),
            ),
        )
        return float(acceleration) * scale / 100.0

    def _apply_paint_process_contact_config(self) -> None:
        """Apply the latest Paint process settings to the active contact-motion profile."""
        config = self._paint_process_config()
        plane = str(config.pivot_motion_plane or self._configured_contact_motion_plane).strip().lower()
        translation_axis = str(config.pivot_axis or self._configured_contact_translation_axis).strip().lower()
        side = str(config.pivot_contact_side or self._configured_contact_side).strip().lower()
        direction = str(config.pivot_direction or self._configured_contact_translation_direction).strip().lower()
        mirror_execution_rotation = (
            plane == "xz_y_ry"
            and bool(config.mirror_xz_ry_execution_rotation_value)
        )

        self._configured_contact_motion_plane = plane
        self._configured_contact_translation_axis = translation_axis
        self._configured_contact_side = side
        self._configured_contact_translation_direction = direction
        self._apply_camera_to_tcp_for_pickup = bool(config.apply_camera_to_tcp_for_pickup)
        self._flip_xz_ry_execution_rotation_direction = mirror_execution_rotation
        self._contact_motion_config = _normalize_contact_motion_config(
            motion_plane=plane,
            translation_axis=translation_axis,
            pivot_side=side,
            translation_direction=direction,
            apply_camera_to_tcp_for_pickup=self._apply_camera_to_tcp_for_pickup,
            camera_to_tcp_x_offset=self._contact_motion_config.camera_to_tcp_x_offset,
            camera_to_tcp_y_offset=self._contact_motion_config.camera_to_tcp_y_offset,
            rotation_direction_sign=_xz_ry_projection_rotation_sign(
                plane,
                self._flip_xz_ry_execution_rotation_direction,
            ),
            closed_contour_overlap_mm=config.closed_contour_overlap_mm,
        )
        self._pickup_contact_motion_config = _normalize_contact_motion_config(
            motion_plane="xy_z_rz",
            translation_axis=translation_axis,
            pivot_side=side,
            translation_direction=direction,
            apply_camera_to_tcp_for_pickup=self._apply_camera_to_tcp_for_pickup,
            camera_to_tcp_x_offset=self._pickup_contact_motion_config.camera_to_tcp_x_offset,
            camera_to_tcp_y_offset=self._pickup_contact_motion_config.camera_to_tcp_y_offset,
        )
        self._contact_motion_strategy = get_execution_plane_strategy(self._contact_motion_config.motion_plane)

    def _make_runtime_contact_motion_config(self, motion_plane: str) -> PaintSimulationConfig:
        """Build a projection config for a requested execution plane."""
        plane = str(motion_plane or "xy_z_rz").strip().lower()
        return _normalize_contact_motion_config(
            motion_plane=plane,
            translation_axis=self._configured_contact_translation_axis,
            pivot_side=self._configured_contact_side,
            translation_direction=self._configured_contact_translation_direction,
            apply_camera_to_tcp_for_pickup=self._apply_camera_to_tcp_for_pickup,
            camera_to_tcp_x_offset=self._contact_motion_config.camera_to_tcp_x_offset,
            camera_to_tcp_y_offset=self._contact_motion_config.camera_to_tcp_y_offset,
            rotation_direction_sign=_xz_ry_projection_rotation_sign(
                plane,
                self._flip_xz_ry_execution_rotation_direction,
            ),
            closed_contour_overlap_mm=self._contact_motion_config.closed_contour_overlap_mm,
        )

    def _set_runtime_contact_motion_config(self, pivot_config: PaintSimulationConfig) -> None:
        """Switch the active projection config used by executor helper methods."""
        self._contact_motion_config = pivot_config
        self._contact_motion_strategy = get_execution_plane_strategy(pivot_config.motion_plane)

    # -------------------------------------------------------------------------
    # Shared Pose And Settings Resolvers
    # -------------------------------------------------------------------------
    # Phase executors call back into these helpers to resolve movement-group
    # poses, configured waypoint lists, safe-travel settings, and pivot offsets.

    @staticmethod
    def _read_provider_position(provider: Optional[Callable[[], Optional[list[float]]]]) -> Optional[list[float]]:
        """Read and normalize a movement-group position provider result."""
        if provider is None:
            return None
        try:
            position = provider()
        except Exception:
            _logger.debug("PaintExecutionRuntime: base position provider failed", exc_info=True)
            return None
        if not position or len(position) < 3:
            return None
        try:
            return [float(position[i]) for i in range(6 if len(position) >= 6 else len(position))]
        except (TypeError, ValueError):
            return None

    def _resolve_base_position(self) -> Optional[list[float]]:
        """Resolve the configured pivot/base pose used to project paint motion."""
        provider = self._base_position_provider
        if self._contact_motion_config.motion_plane == "xy_z_rz" and self._pickup_base_position_provider is not None:
            provider = self._pickup_base_position_provider
        resolved = self._read_provider_position(provider)
        if resolved is None:
            return None
        if abs(float(self._active_contact_base_z_offset_mm)) > 1e-9:
            while len(resolved) < 3:
                resolved.append(0.0)
            resolved[2] = float(resolved[2]) + float(self._active_contact_base_z_offset_mm)
        return resolved

    def _resolve_cleanup_base_position(self) -> Optional[list[float]]:
        """Resolve the dedicated XY/RZ cleanup base pose."""
        return self._read_provider_position(self._cleanup_base_position_provider)

    @staticmethod
    def _read_configured_pose(position: object) -> Optional[list[float]]:
        if isinstance(position, dict):
            if "position" not in position:
                raise ValueError("Configured waypoint is missing 'position'")
            position = position["position"]
        if not position:
            return None
        try:
            values = [float(value) for value in list(position)]
        except (TypeError, ValueError) as exc:
            raise ValueError("Configured waypoint position must be numeric") from exc
        if len(values) != 6:
            raise ValueError("Configured waypoint position must contain exactly six values")
        for axis, value in zip(("X", "Y", "Z", "RX", "RY", "RZ"), values):
            if not math.isfinite(value):
                raise ValueError(f"Configured waypoint position.{axis} must be finite")
        return values

    @classmethod
    def _read_configured_waypoints(
        cls,
        positions: object,
        default_vel: float = 50.0,
        default_acc: float = 20.0,
        default_motion_type: OrderedMotionType = OrderedMotionType.PTP,
    ) -> list[ConfiguredMotionWaypoint]:
        resolved: list[ConfiguredMotionWaypoint] = []
        if positions:
            raw_positions = list(positions)
            for index, item in enumerate(raw_positions, start=1):
                try:
                    waypoint = cls._read_configured_waypoint(item, default_vel, default_acc, default_motion_type)
                    if waypoint is None:
                        raise ValueError("Configured waypoint cannot be empty")
                except ValueError as exc:
                    raise ValueError(f"Configured waypoint {index}: {exc}") from exc
                resolved.append(waypoint)
        return resolved

    @classmethod
    def _read_configured_waypoint(
        cls,
        value: object,
        default_vel: float,
        default_acc: float,
        default_motion_type: OrderedMotionType = OrderedMotionType.PTP,
    ) -> ConfiguredMotionWaypoint | None:
        pose = cls._read_configured_pose(value)
        if pose is None:
            return None
        vel = float(default_vel)
        acc = float(default_acc)
        motion_type = OrderedMotionType.parse(
            default_motion_type,
            field_name="default_motion_type",
        )
        blend_r = 0.0
        if isinstance(value, dict):
            required = {"position", "vel_percent", "acc_percent", "motion_type", "blendR"}
            missing = required.difference(value)
            if missing:
                raise ValueError(f"Configured waypoint is missing {sorted(missing)}")
            vel = float(value["vel_percent"])
            acc = float(value["acc_percent"])
            blend_r = float(value["blendR"])
            motion_type = OrderedMotionType.parse(
                value["motion_type"],
                field_name="configured waypoint motion_type",
            )
        else:
            raw = list(value)
            if len(raw) != 6:
                raise ValueError("Configured waypoint pose must contain exactly six values")
        # Validate before clamping: max(0.0, NaN) would hide an invalid radius.
        if not math.isfinite(blend_r):
            raise ValueError("Configured waypoint blendR must be finite")
        return ConfiguredMotionWaypoint(
            position=tuple(pose),
            velocity_percent=vel,
            acceleration_percent=acc,
            motion_type=motion_type,
            blend_radius=max(0.0, blend_r),
        )

    def _apply_pivot_offset(self, pivot_pose: list[float] | None, offset_mm: float) -> list[float] | None:
        """Apply the editor-configured pivot offset in the active pivot plane."""
        if pivot_pose is None:
            return None
        try:
            offset_value = float(offset_mm or 0.0)
        except (TypeError, ValueError):
            offset_value = 0.0
        adjusted_pose = list(pivot_pose)
        if abs(offset_value) <= 1e-9:
            return adjusted_pose
        target_index = self._contact_motion_strategy.pivot_offset_position_index
        while len(adjusted_pose) <= target_index:
            adjusted_pose.append(0.0)
        adjusted_pose[target_index] = float(adjusted_pose[target_index]) + offset_value
        return adjusted_pose

    @staticmethod
    def _resolve_pivot_offset_mm(job: dict | None, execution_plan: WorkpieceExecutionPlan | None = None) -> float:
        """Resolve the persisted pivot-offset setting from job or workpiece data."""
        if job is not None:
            try:
                return float(job.get("pivot_offset_mm", 0.0) or 0.0)
            except (TypeError, ValueError):
                pass
        if execution_plan is not None:
            try:
                return float((execution_plan.workpiece or {}).get("offset", 0.0) or 0.0)
            except (AttributeError, TypeError, ValueError):
                pass
        return 0.0

    def _paint_start_staging_offset_pose(
        self,
        contact_pose: list[float],
    ) -> list[float]:
        """Return the configured plane-aware pre-contact staging pose."""
        return self._paint_staging_offset_pose(contact_pose, detach=False)

    def _paint_detach_staging_offset_pose(
        self,
        contact_pose: list[float],
        *,
        additional_paint_axis_offset_mm: float = 0.0,
    ) -> list[float]:
        """Return the configured plane-aware post-contact staging pose."""
        return self._paint_staging_offset_pose(
            contact_pose,
            detach=True,
            additional_paint_axis_offset_mm=additional_paint_axis_offset_mm,
        )

    def _paint_staging_offset_pose(
        self,
        contact_pose: list[float],
        *,
        detach: bool,
        additional_paint_axis_offset_mm: float = 0.0,
    ) -> list[float]:
        staging = self._paint_process_config().contact_staging
        if detach:
            z_offset_mm = float(staging.detach_z_offset_mm)
            paint_axis_offset_mm = float(staging.detach_paint_axis_offset_mm)
            perpendicular_axis_offset_mm = float(staging.detach_perpendicular_axis_offset_mm)
            paint_axis_offset_mm += max(0.0, float(additional_paint_axis_offset_mm))
        else:
            z_offset_mm = float(staging.attach_z_offset_mm)
            paint_axis_offset_mm = float(staging.attach_paint_axis_offset_mm)
            perpendicular_axis_offset_mm = float(staging.attach_perpendicular_axis_offset_mm)
        return _paint_axis_staging_offset_pose(
            contact_pose,
            self._contact_motion_config,
            z_offset_mm=z_offset_mm,
            paint_axis_offset_mm=paint_axis_offset_mm,
            perpendicular_axis_offset_mm=perpendicular_axis_offset_mm,
        )

    def _resolve_pickup_base_position(self) -> Optional[list[float]]:
        """Resolve the pickup/staging base pose used for XY/RZ pickup alignment."""
        provider = self._pickup_base_position_provider
        if provider is None:
            return None
        try:
            position = provider()
        except Exception:
            _logger.debug("PaintExecutionRuntime: pickup base position provider failed", exc_info=True)
            return None
        if not position or len(position) < 3:
            return None
        try:
            return [float(position[i]) for i in range(6 if len(position) >= 6 else len(position))]
        except (TypeError, ValueError):
            return None

    # -------------------------------------------------------------------------
    # Paint-Contact Projection Inputs And Geometry
    # -------------------------------------------------------------------------
    # Prepare shared geometry inputs without choosing a visualization policy.


    def prepare_projection_context(self, execution_plan: WorkpieceExecutionPlan) -> PaintProjectionContext:
        """Resolve the current configuration, pivot, and pickup geometry."""
        self._refresh_paint_process_config_snapshot()
        self._apply_paint_process_contact_config()
        self._refresh_runtime_config()
        base_pivot_pose = self._resolve_base_position()
        pickup_plan = (
            self._pickup_transfer_planner.build_plan(execution_plan)
            if base_pivot_pose is not None and len(base_pivot_pose) >= 3 else None
        )
        return PaintProjectionContext(
            pivot_config=self._contact_motion_config,
            base_pivot_pose=base_pivot_pose,
            pickup_plan=pickup_plan,
            apply_pivot_offset=self._apply_pivot_offset,
            resolve_pivot_offset_mm=self._resolve_pivot_offset_mm,
            align_projected_path_to_pickup_plan=self._align_projected_path_to_pickup_plan,
            pivot_execution_command_path=self._paint_contact_command_path,
        )

    def _build_paint_contact_path(
        self,
        spline: list[list[float]],
        *,
        pivot_offset_mm: float = 0.0,
        align_start_to_zero_rz: bool = False,
        anchor_xy: tuple[float, float] | None = None,
        source_rotation_deg: float = 0.0,
        enforce_open_path_side: bool = False,
    ) -> tuple[
        list[list[float]],
        list[np.ndarray] | None,
        list[dict[str, float | int]] | None,
        list[float] | None,
    ] | None:
        """Project one prepared spline into the real paint-contact trajectory."""
        with timed_block(_logger, "pivot_path_prepare", label="resolve_base_and_offset"):
            pivot_pose = self._apply_pivot_offset(self._resolve_base_position(), pivot_offset_mm)
        if pivot_pose is None or len(pivot_pose) < 3:
            return None
        with timed_block(_logger, "pivot_path_prepare", label="project_execution_path"):
            pivot_path, snapshots, diagnostics = project_paint_contact_motion_continuous(
                spline,
                pivot_pose,
                self._contact_motion_config,
                anchor_xy=anchor_xy,
                source_rotation_deg=source_rotation_deg,
                enforce_open_path_side=enforce_open_path_side,
            )
        _logger.debug("Simulated pivot path has %d points", len(pivot_path))
        if align_start_to_zero_rz:
            with timed_block(_logger, "pivot_path_prepare", label="rebase_start_rotation"):
                pivot_path = rebase_contact_motion_path_to_zero_start_rotation(
                    pivot_path,
                    self._contact_motion_config,
                )
        return pivot_path, snapshots, diagnostics, list(pivot_pose)

    # -------------------------------------------------------------------------
    # Pause / Resume Support For Ordered Non-Contact Motion
    # -------------------------------------------------------------------------
    # Paint-contact path segments are protected. Non-contact ordered motion can
    # be interrupted, then resumed from the current ordered-chain segment.

    def pause_current_execution(self) -> None:
        self._motion_recovery.pause_current_execution()

    # -------------------------------------------------------------------------
    # Paint-Contact Command Pose Helpers
    # -------------------------------------------------------------------------
    # These adapt projected paint-contact geometry into robot command poses and
    # add the retreat waypoint that moves the held part off the paint axis.

    def _paint_contact_staging_command_pose(self, pose: list[float], reference_pose: list[float]) -> list[float]:
        """Return the robot command pose for moving the held workpiece into XZ/RY pivot contact."""
        if self._contact_motion_config.motion_plane != "xz_y_ry":
            return list(pose)
        command_pose = list(pose)
        _logger.info(
            "[PICKUP] xz/ry pivot staging command mapped: planned_xz=(%.3f, %.3f) planned_ry=%.3f planned_rz=%.3f reference_xz=(%.3f, %.3f) reference_ry=%.3f command_xz=(%.3f, %.3f) command_ry=%.3f command_rz=%.3f projection_rotation_sign=%.0f",
            float(pose[0]) if len(pose) >= 1 else 0.0,
            float(pose[2]) if len(pose) >= 3 else 0.0,
            float(pose[4]) if len(pose) >= 5 else 0.0,
            float(pose[5]) if len(pose) >= 6 else 0.0,
            float(self._last_pickup_plan.paint_pivot_pose[0]) if self._last_pickup_plan is not None else float(reference_pose[0]) if len(reference_pose) >= 1 else 0.0,
            float(self._last_pickup_plan.paint_pivot_pose[2]) if self._last_pickup_plan is not None else float(reference_pose[2]) if len(reference_pose) >= 3 else 0.0,
            float(reference_pose[4]) if len(reference_pose) >= 5 else 0.0,
            float(command_pose[0]) if len(command_pose) >= 1 else 0.0,
            float(command_pose[2]) if len(command_pose) >= 3 else 0.0,
            float(command_pose[4]),
            float(command_pose[5]),
            float(self._contact_motion_config.rotation_direction_sign),
        )
        return command_pose

    def _align_projected_path_to_pickup_plan(
        self,
        path: list[list[float]],
        pickup_plan: PickupTransferPlan | None,
    ) -> list[list[float]]:
        """Apply the same first-rotation alignment used before pivot execution."""
        if not path or pickup_plan is None:
            return [list(pose) for pose in path]
        rotation_index = self._contact_motion_config.rotation_index
        if len(path[0]) <= rotation_index or len(pickup_plan.staged_pose) <= rotation_index:
            return [list(pose) for pose in path]
        if self._contact_motion_config.motion_plane == "xy_z_rz":
            staged_rotation = float(pickup_plan.staged_pose[rotation_index])
            raw_start_rotation = float(path[0][rotation_index])
            rotation_shift = axis_equivalent_shift_degrees(staged_rotation, raw_start_rotation)
        elif self._contact_motion_config.motion_plane == "xz_y_ry":
            staged_rotation = float(pickup_plan.staged_pose[rotation_index])
            raw_start_rotation = float(path[0][rotation_index])
            rotation_shift = staged_rotation - raw_start_rotation
        else:
            rotation_shift = 0.0
        return shift_path_rotation(path, rotation_index, rotation_shift)

    def _paint_contact_command_path(
        self,
        path: list[list[float]],
        *,
        pickup_plan: PickupTransferPlan | None = None,
    ) -> list[list[float]]:
        """Return robot command poses for XZ/RY pivot execution without changing planned geometry."""
        if not path:
            return []
        command_path = [list(pose) for pose in path]
        plan = pickup_plan or self._last_pickup_plan
        if (
            self._contact_motion_config.motion_plane == "xz_y_ry"
            and plan is not None
            and len(plan.change_plane_pose) >= 5
        ):
            reference_ry = float(plan.change_plane_pose[4])
            _logger.info(
                "[PIVOT_PATH] xz/ry execution command mapped: planned_start_xz=(%.3f, %.3f) planned_start_ry=%.3f planned_start_rz=%.3f command_start_xz=(%.3f, %.3f) command_start_ry=%.3f command_start_rz=%.3f planned_end_xz=(%.3f, %.3f) planned_end_ry=%.3f planned_end_rz=%.3f command_end_xz=(%.3f, %.3f) command_end_ry=%.3f command_end_rz=%.3f reference_xz=(%.3f, %.3f) reference_ry=%.3f projection_rotation_sign=%.0f",
                float(path[0][0]) if len(path[0]) >= 1 else 0.0,
                float(path[0][2]) if len(path[0]) >= 3 else 0.0,
                float(path[0][4]) if len(path[0]) >= 5 else 0.0,
                float(path[0][5]) if len(path[0]) >= 6 else 0.0,
                float(command_path[0][0]) if len(command_path[0]) >= 1 else 0.0,
                float(command_path[0][2]) if len(command_path[0]) >= 3 else 0.0,
                float(command_path[0][4]) if len(command_path[0]) >= 5 else 0.0,
                float(command_path[0][5]) if len(command_path[0]) >= 6 else 0.0,
                float(path[-1][0]) if len(path[-1]) >= 1 else 0.0,
                float(path[-1][2]) if len(path[-1]) >= 3 else 0.0,
                float(path[-1][4]) if len(path[-1]) >= 5 else 0.0,
                float(path[-1][5]) if len(path[-1]) >= 6 else 0.0,
                float(command_path[-1][0]) if len(command_path[-1]) >= 1 else 0.0,
                float(command_path[-1][2]) if len(command_path[-1]) >= 3 else 0.0,
                float(command_path[-1][4]) if len(command_path[-1]) >= 5 else 0.0,
                float(command_path[-1][5]) if len(command_path[-1]) >= 6 else 0.0,
                float(plan.paint_pivot_pose[0]) if len(plan.paint_pivot_pose) >= 1 else 0.0,
                float(plan.paint_pivot_pose[2]) if len(plan.paint_pivot_pose) >= 3 else 0.0,
                reference_ry,
                float(self._contact_motion_config.rotation_direction_sign),
            )
        return command_path

    # -------------------------------------------------------------------------
    # Process Control And Diagnostics
    # -------------------------------------------------------------------------

    @staticmethod
    def _wait_for_paint_resume(control) -> bool:
        return bool(control.wait_if_paused())

    def _diagnostics_artifacts_enabled(self) -> bool:
        config = self._paint_process_config()
        return (
            bool(config.enable_path_debug_plots)
            or bool(config.enable_pivot_debug_plot)
            or bool(config.enable_execution_motion_trace)
        )

    def _execution_control(self):
        return self._active_execution_control

    def _record_motion_command(self, payload: dict) -> None:
        self.diagnostic_motion_commands.append(dict(payload))

    def _motion_tool(self) -> int:
        return self._pickup_tool

    def _motion_user(self) -> int:
        return self._pickup_user

    def execute_paint_process(self, prepared_workpiece: WorkpieceExecutionPlan, *, control=None) -> tuple[bool, str]:
        """Run the prepared cycle with this runtime's configuration and operations."""
        return run_prepared_paint_cycle(self, prepared_workpiece, control=control)
