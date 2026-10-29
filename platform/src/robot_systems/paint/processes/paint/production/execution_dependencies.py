"""Inputs used to compose a paint execution runtime."""
from __future__ import annotations
from dataclasses import dataclass
from typing import Callable, Optional, TYPE_CHECKING
from src.robot_systems.paint.contracts.dropoff import IDropoffStrategy
from src.robot_systems.paint.contracts.paint_head_check.interfaces import (
    IHeadInspectionControl, IPaintHeadCheckRunFactory,
)
from src.robot_systems.paint.contracts.paint_head_check.results import HeadInspectionMoveResult

if TYPE_CHECKING:
    from .execution_runtime import PaintExecutionRuntime

from src.engine.robot.path_preparation import IWorkpiecePathPreparationService
from src.robot_systems.paint.processes.paint.tray_dry.plate_layout import PlateLayoutService

@dataclass(frozen=True)
class PaintExecutorDependencies:
    """Runtime services and callbacks needed by the paint process executor."""

    robot_service: object
    dropoff_strategy_factory: Callable[[PaintExecutionRuntime], IDropoffStrategy]
    path_preparation_service: Optional[IWorkpiecePathPreparationService] = None
    base_position_provider: Optional[Callable[[], Optional[list[float]]]] = None
    pickup_base_position_provider: Optional[Callable[[], Optional[list[float]]]] = None
    cleanup_base_position_provider: Optional[Callable[[], Optional[list[float]]]] = None
    dropoff_position_provider: Optional[Callable[[], Optional[list[float]]]] = None
    calibration_position_provider: Optional[Callable[[], Optional[list[float]]]] = None
    post_execute_callback: Optional[Callable[[], bool]] = None
    dryer_ready_for_release: Optional[Callable[[], tuple[bool, str]]] = None
    on_workpiece_release_verified: Optional[Callable[[], bool]] = None
    robot_config_provider: Optional[Callable[[], object]] = None
    vacuum_pump: object | None = None
    vacuum_pump_enabled_provider: Optional[Callable[[], bool]] = None
    vacuum_sensor: object | None = None
    pickup_condition: object | None = None
    pickup_condition_provider: Optional[Callable[[], object | None]] = None
    paint_process_config_service: object | None = None
    dropoff_motion_corridor_id: str | None = None
    plate_layout_service: PlateLayoutService | None = None
    head_check_run_factory: IPaintHeadCheckRunFactory | None = None
    head_check_return: Callable[[IHeadInspectionControl], HeadInspectionMoveResult] | None = None


@dataclass(frozen=True)
class PaintExecutorMotionConfig:
    """Robot tool/user and process-motion switches for paint execution."""

    enable_vacuum_pump: bool = True
    pickup_tool: int = 0
    pickup_user: int = 0
    pickup_z_mm: float | None = None
    debug_dump_dir: str | None = None


@dataclass(frozen=True)
class PaintExecutorContactMotionConfig:
    """Configured pivot plane/profile used by paint projection and pickup handoff."""

    motion_plane: str = "xy_z_rz"
    translation_axis: str = "x"
    paint_side: str = "negative"
    translation_direction: str = "forward"
    flip_xz_ry_execution_rotation_direction: bool = False
    mirror_xz_ry_pickup_handoff: bool = False
    apply_camera_to_tcp_for_pickup: bool = False
    camera_to_tcp_x_offset: float = 0.0
    camera_to_tcp_y_offset: float = 0.0
