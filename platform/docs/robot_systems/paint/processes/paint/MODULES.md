# Module reference: `src/robot_systems/paint/processes/paint`

[Package guide](README.md) · [Complete source index](../../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [adjustment_settings_serializer.py](#adjustment_settings_serializerpy)
- [config.py](#configpy)
- [configured_motion_waypoint.py](#configured_motion_waypointpy)
- [dashboard_live_view_events.py](#dashboard_live_view_eventspy)
- [dryer_cycle_simulation_runner.py](#dryer_cycle_simulation_runnerpy)
- [execution_control.py](#execution_controlpy)
- [incremental_adjustment.py](#incremental_adjustmentpy)
- [magazine_load_result.py](#magazine_load_resultpy)
- [magazine_load_service.py](#magazine_load_servicepy)
- [next_cycle_target.py](#next_cycle_targetpy)
- [paint_contact_job.py](#paint_contact_jobpy)
- [paint_process.py](#paint_processpy)
- [paint_process_config_serializer.py](#paint_process_config_serializerpy)
- [paint_process_config_service.py](#paint_process_config_servicepy)
- [paint_production_service.py](#paint_production_servicepy)
- [work_area_nesting.py](#work_area_nestingpy)

## `__init__.py`

Source: [src/robot_systems/paint/processes/paint/__init__.py](../../../../../src/robot_systems/paint/processes/paint/__init__.py).

No top-level functions, classes or public value declarations; inspect the source for imports or entry-point statements.

## `adjustment_settings_serializer.py`

Source: [src/robot_systems/paint/processes/paint/adjustment_settings_serializer.py](../../../../../src/robot_systems/paint/processes/paint/adjustment_settings_serializer.py).

Imports (including optional/function-local imports; not a startup dependency list): `.incremental_adjustment`, `dataclasses`, `src.engine.repositories.interfaces`.

### `PaintAdjustmentSettingsSerializer`

```python
class PaintAdjustmentSettingsSerializer(ISettingsSerializer[AdjustmentStep]):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
@property
def settings_type(self) -> str
```

```python
def get_default(self) -> AdjustmentStep
```

```python
def to_dict(self, settings: AdjustmentStep) -> dict
```

```python
def from_dict(self, data: dict) -> AdjustmentStep
```

## `config.py`

Source: [src/robot_systems/paint/processes/paint/config.py](../../../../../src/robot_systems/paint/processes/paint/config.py).

Imports (including optional/function-local imports; not a startup dependency list): `dataclasses`, `enum`, `src.engine.robot.motion_sequence`, `src.engine.robot.path_preparation`.

Module declarations (expressions are shown without evaluating them):

```python
PICKUP_CONTACT_MODE_PLANNED = PickupContactMode.PLANNED
PICKUP_CONTACT_MODE_SENSOR_CONTROLLED_FAST_LIN = PickupContactMode.SENSOR_CONTROLLED_FAST_LIN
PICKUP_CONTACT_MODE_HEIGHT_MEASURE = PickupContactMode.HEIGHT_MEASURE
PICKUP_CONTACT_MODES = (PICKUP_CONTACT_MODE_PLANNED, PICKUP_CONTACT_MODE_SENSOR_CONTROLLED_FAST_LIN, PICKUP_CONTACT_MODE_HEIGHT_MEASURE)
PICKUP_SENSOR_EXECUTION_MODE_PLATFORM = PickupSensorExecutionMode.PLATFORM
PICKUP_SENSOR_EXECUTION_MODE_ROS_MANAGED = PickupSensorExecutionMode.ROS_MANAGED
PICKUP_SENSOR_EXECUTION_MODES = (PICKUP_SENSOR_EXECUTION_MODE_PLATFORM, PICKUP_SENSOR_EXECUTION_MODE_ROS_MANAGED)
MAGAZINE_PICKUP_MODE_VISION_PLANNED = MagazinePickupMode.VISION_PLANNED
MAGAZINE_PICKUP_MODE_VISION_SENSOR_CONTROLLED_FAST_LIN = MagazinePickupMode.VISION_SENSOR_CONTROLLED_FAST_LIN
MAGAZINE_PICKUP_MODE_AUTO_DISCOVERY_SENSOR_CONTROLLED_FAST_LIN = MagazinePickupMode.AUTO_DISCOVERY_SENSOR_CONTROLLED_FAST_LIN
MAGAZINE_PICKUP_MODE_FIXED_GROUP_SENSOR_CONTROLLED_FAST_LIN = MagazinePickupMode.FIXED_GROUP_SENSOR_CONTROLLED_FAST_LIN
MAGAZINE_PICKUP_MODES = (MAGAZINE_PICKUP_MODE_VISION_PLANNED, MAGAZINE_PICKUP_MODE_VISION_SENSOR_CONTROLLED_FAST_LIN, MAGAZINE_PICKUP_MODE_AUTO_DISCOVERY_SENSOR_CONTROLLED_FAST_LIN, MAGAZINE_PICKUP_MODE_FIXED_GROUP_SENSOR_CONTROLLED_FAST_LIN)
MAGAZINE_PROCESSING_STRATEGY_DIRECT = MagazineProcessingStrategy.DIRECT
MAGAZINE_PROCESSING_STRATEGY_BATCH_NESTING = MagazineProcessingStrategy.BATCH_NESTING
MAGAZINE_PROCESSING_STRATEGIES = (MAGAZINE_PROCESSING_STRATEGY_DIRECT, MAGAZINE_PROCESSING_STRATEGY_BATCH_NESTING)
PAINT_PROJECTION_RULES = PaintProjectionRules()
PAINT_PROJECTION_TUNING = PaintProjectionTuning()
PAINT_PROCESS_CONFIG = PaintProcessConfig()
```

### `PickupContactMode`

```python
class PickupContactMode(StrEnum):
```

Declared fields/defaults:

```python
PLANNED = 'planned'
SENSOR_CONTROLLED_FAST_LIN = 'sensor_controlled_fast_lin'
HEIGHT_MEASURE = 'height_measure'
```

### `PickupSensorExecutionMode`

```python
class PickupSensorExecutionMode(StrEnum):
```

Declared fields/defaults:

```python
PLATFORM = 'sensor_controlled_fast_lin'
ROS_MANAGED = 'ros_managed'
```

### `MagazinePickupMode`

```python
class MagazinePickupMode(StrEnum):
```

Declared fields/defaults:

```python
VISION_PLANNED = 'vision_planned'
VISION_SENSOR_CONTROLLED_FAST_LIN = 'vision_sensor_controlled_fast_lin'
AUTO_DISCOVERY_SENSOR_CONTROLLED_FAST_LIN = 'auto_discovery_sensor_controlled_fast_lin'
FIXED_GROUP_SENSOR_CONTROLLED_FAST_LIN = 'fixed_group_sensor_controlled_fast_lin'
```

### `MagazineProcessingStrategy`

```python
class MagazineProcessingStrategy(StrEnum):
```

Declared fields/defaults:

```python
DIRECT = 'direct'
BATCH_NESTING = 'batch_nesting'
```

### `DropoffStrategy`

```python
class DropoffStrategy(StrEnum):
```

Declared fields/defaults:

```python
MOVEMENT_GROUP = 'movement_group'
PLATE_LAYOUT = 'plate_layout'
```

### `normalize_pickup_contact_mode`

```python
def normalize_pickup_contact_mode(value: object) -> PickupContactMode
```

### `normalize_magazine_pickup_mode`

```python
def normalize_magazine_pickup_mode(value: object) -> MagazinePickupMode
```

### `PickupMotionConfig`

```python
@dataclass(frozen=True)
class PickupMotionConfig:
```

Pickup/staging motion tuning. Values are robot velocity/acceleration percentages unless the suffix is ``_mm``. Each phase exposes its own ``vel_percent`` / ``acc_percent`` pair so cycle-time tuning can be done without changing the pickup sequence.

Declared fields/defaults:

```python
approach_offset_mm: float = 100.0
contact_offset_mm: float = 5.0
initial_lift_clearance_mm: float = 20.0
approach_vel_percent: float = 60.0
approach_acc_percent: float = 50.0
approach_motion_type: OrderedMotionType = OrderedMotionType.PTP
approach_blendR: float = 20.0
descend_vel_percent: float = 60.0
descend_acc_percent: float = 40.0
descend_motion_type: OrderedMotionType = OrderedMotionType.LINEAR
descend_blendR: float = 0.0
lift_align_vel_percent: float = 80.0
lift_align_acc_percent: float = 40.0
lift_align_motion_type: OrderedMotionType = OrderedMotionType.PTP
lift_align_blendR: float = 20.0
change_plane_vel_percent: float = 80.0
change_plane_acc_percent: float = 40.0
change_plane_motion_type: OrderedMotionType = OrderedMotionType.PTP
change_plane_blendR: float = 20.0
combine_change_plane_with_first_contact: bool = True
stage_transition_vel_percent: float = 50.0
stage_transition_acc_percent: float = 20.0
stage_transition_motion_type: OrderedMotionType = OrderedMotionType.PTP
stage_transition_blendR: float = 20.0
first_contact_vel_percent: float = 80.0
first_contact_acc_percent: float = 30.0
first_contact_motion_type: OrderedMotionType = OrderedMotionType.PTP
first_contact_blendR: float = 0.0
pickup_contact_mode: PickupContactMode = PICKUP_CONTACT_MODE_PLANNED
calibration_contact_execution_mode: PickupSensorExecutionMode = PICKUP_SENSOR_EXECUTION_MODE_PLATFORM
magazine_contact_execution_mode: PickupSensorExecutionMode = PICKUP_SENSOR_EXECUTION_MODE_PLATFORM
servo_contact_linear_mm_s: float = 10.0
servo_contact_min_z_mm: float = 0.0
servo_contact_fast_lin_velocity_percent: float = 10.0
servo_contact_fast_lin_acceleration_percent: float = 30.0
servo_contact_timeout_s: float = 5.0
servo_contact_poll_interval_s: float = 0.02
servo_contact_controlled_stop_duration_s: float = 0.2
servo_contact_stop_confirmation_timeout_s: float = 3.0
servo_contact_preflight_read_attempts: int = 2
servo_contact_read_failure_limit: int = 3
magazine_post_retract_confirmation_samples: int = 2
magazine_post_retract_confirmation_interval_s: float = 0.05
servo_contact_dummy_sensor_enabled: bool = False
servo_contact_dummy_detect_after_s: float = 1.0
```

### `PaintContactStagingConfig`

```python
@dataclass(frozen=True)
class PaintContactStagingConfig:
```

Plane-aware offsets used immediately before and after paint contact.

Declared fields/defaults:

```python
attach_vel_percent: float = 10.0
attach_acc_percent: float = 5.0
attach_z_offset_mm: float = 0.0
attach_paint_axis_offset_mm: float = 0.0
attach_perpendicular_axis_offset_mm: float = 0.0
detach_z_offset_mm: float = 0.0
detach_paint_axis_offset_mm: float = 0.0
detach_perpendicular_axis_offset_mm: float = 0.0
```

### `UnmatchedSecondPassConfig`

```python
@dataclass(frozen=True)
class UnmatchedSecondPassConfig:
```

Optional second coat for captured contours that were not library-matched.

Declared fields/defaults:

```python
use_pass_1_settings: bool = True
velocity_percent: float = 10.0
acceleration_percent: float = 10.0
offset_mm: float = 0.0
```

### `PaintEdgeCleanupConfig`

```python
@dataclass(frozen=True)
class PaintEdgeCleanupConfig:
```

Optional XY/RZ cleanup pass tuning used after XZ/RY paint.

Declared fields/defaults:

```python
enabled_after_xz_ry: bool = False
enabled_after_xy_rz: bool = False
enable_second_pass: bool = False
vel_percent: float = 80.0
acc_percent: float = 60.0
motion_type: OrderedMotionType = OrderedMotionType.LINEAR
blendR: float = 0.0
spacing_mm: float = 3.0
z_offset_mm: float = 0.0
perpendicular_retreat_offset_mm: float = -50.0
second_pass_pivot_z_offset_mm: float = -15.0
```

### `PaintDropoffConfig`

```python
@dataclass(frozen=True)
class PaintDropoffConfig:
```

Dropoff/release motion tuning after paint and Joint 6 unwind.

Declared fields/defaults:

```python
strategy: DropoffStrategy = DropoffStrategy.MOVEMENT_GROUP
alternate_drying_demo: bool = False
allow_sub_zero_dropoff: bool = False
corridor_x_margin_mm: float = 70.0
corridor_y_margin_mm: float = 70.0
corridor_z_tolerance_mm: float = 1.0
corridor_entry_z_max_mm: float = 100.0
corridor_maximum_velocity_percent: float = 80.0
corridor_maximum_acceleration_percent: float = 60.0
sub_zero_approach_z_mm: float = 50.0
sub_zero_exit_blendR_mm: float = 10.0
release_align_vel_percent: float = 60.0
release_align_acc_percent: float = 40.0
release_align_motion_type: OrderedMotionType = OrderedMotionType.PTP
release_align_blendR: float = 0.0
plate_corners: list[list[float]] = field(default_factory=list)
plate_release_z_offset_mm: float = 0.0
plate_approach_clearance_mm: float = 50.0
plate_margin_left_mm: float = 10.0
plate_margin_right_mm: float = 10.0
plate_margin_bottom_mm: float = 10.0
plate_margin_top_mm: float = 10.0
plate_spacing_x_mm: float = 10.0
plate_spacing_y_mm: float = 10.0
plate_robot_tool: int = -1
plate_robot_user: int = -1
plate_passage_gate_pose: list[float] = field(default_factory=list)
plate_use_entry_gate_as_detach_pose: bool = False
plate_exit_gate_pose: list[float] = field(default_factory=list)
plate_next_cycle_midpoint_enabled: bool = False
plate_next_cycle_waypoints: list[dict] = field(default_factory=list)
plate_next_cycle_midpoint_pose: list[float] = field(default_factory=list)
plate_use_center_waypoint: bool = True
plate_auto_center_near_corner: bool = True
plate_distribute_unwind: bool = False
plate_motion_profiles: list[dict] = field(default_factory=lambda: [{'key': 'entry_gate', 'vel_percent': 70.0, 'acc_percent': 50.0, 'motion_type': OrderedMotionType.PTP, 'blendR': 20.0}, {'key': 'entry_center', 'vel_percent': 70.0, 'acc_percent': 50.0, 'motion_type': OrderedMotionType.PTP, 'blendR': 20.0}, {'key': 'center_to_dropoff', 'vel_percent': 70.0, 'acc_percent': 50.0, 'motion_type': OrderedMotionType.PTP, 'blendR': 0.0}, {'key': 'exit_center', 'vel_percent': 70.0, 'acc_percent': 50.0, 'motion_type': OrderedMotionType.PTP, 'blendR': 20.0}, {'key': 'exit_gate', 'vel_percent': 70.0, 'acc_percent': 50.0, 'motion_type': OrderedMotionType.PTP, 'blendR': 20.0}, {'key': 'gate_to_next_midpoint', 'vel_percent': 60.0, 'acc_percent': 40.0, 'motion_type': OrderedMotionType.PTP, 'blendR': 20.0}, {'key': 'gate_to_next_start', 'vel_percent': 60.0, 'acc_percent': 40.0, 'motion_type': OrderedMotionType.PTP, 'blendR': 0.0}])
```

### `PaintMagazineLoadConfig`

```python
@dataclass(frozen=True)
class PaintMagazineLoadConfig:
```

Optional pre-run transfer from magazine capture station to calibration table.

Declared fields/defaults:

```python
enabled: bool = False
recapture_after_pile_done: bool = False
recapture_every_cycle: bool = False
processing_strategy: MagazineProcessingStrategy = MAGAZINE_PROCESSING_STRATEGY_DIRECT
nesting_margin_mm: float = 10.0
nesting_padding_mm: float = 10.0
pickup_mode: MagazinePickupMode = MAGAZINE_PICKUP_MODE_VISION_PLANNED
fixed_pickup_group_id: str = 'Magazine Fixed Pickup'
fixed_pickup_group_ids: list[str] = field(default_factory=list)
fixed_pickup_sources: list[dict] = field(default_factory=list)
fixed_pickup_position_tolerance_mm: float = 2.0
fixed_pickup_orientation_tolerance_deg: float = 1.0
full_retract_before_release: bool = True
full_retract_z_mm: float = 120.0
short_retract_distance_mm: float = 10.0
magazine_group_id: str = 'Magazine'
calibration_group_id: str = 'CALIBRATION'
move_to_magazine_vel_percent: float = 30.0
move_to_magazine_acc_percent: float = 30.0
move_to_magazine_motion_type: OrderedMotionType = OrderedMotionType.PTP
move_to_magazine_blendR: float = 0.0
transfer_to_calibration_vel_percent: float = 30.0
transfer_to_calibration_acc_percent: float = 30.0
transfer_to_calibration_motion_type: OrderedMotionType = OrderedMotionType.PTP
transfer_to_calibration_blendR: float = 0.0
release_z_mm: float = 50.0
camera_settle_s: float = 0.5
release_settle_s: float = 0.5
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def effective_fixed_pickup_group_ids(self) -> tuple[str, ...]
```

```python
def effective_fixed_pickup_sources(self) -> tuple[dict, ...]
```

### `PaintSafeTravelConfig`

```python
@dataclass(frozen=True)
class PaintSafeTravelConfig:
```

Optional safe waypoints used while carrying the workpiece from calibration to paint.

Declared fields/defaults:

```python
enabled: bool = False
position: list[float] = field(default_factory=list)
positions: list[object] = field(default_factory=list)
movement_group_id: str = ''
```

### `PaintToDropoffSafeTravelConfig`

```python
@dataclass(frozen=True)
class PaintToDropoffSafeTravelConfig:
```

Optional safe waypoints used while carrying the workpiece from paint to dropoff.

Declared fields/defaults:

```python
enabled: bool = False
position: list[float] = field(default_factory=list)
positions: list[object] = field(default_factory=list)
```

### `PaintNavigationReturnConfig`

```python
@dataclass(frozen=True)
class PaintNavigationReturnConfig:
```

Navigation-return motion tuning for paint-system cleanup moves.

Declared fields/defaults:

```python
unwind_vel_percent: float = 100.0
unwind_acc_percent: float = 60.0
unwind_queue_if_busy: bool = True
calibration_move_vel_percent: float = 30.0
calibration_move_acc_percent: float = 40.0
calibration_move_motion_type: OrderedMotionType = OrderedMotionType.PTP
calibration_move_blendR: float = 0.0
```

### `PaintProjectionTuning`

```python
@dataclass(frozen=True)
class PaintProjectionTuning:
```

Numeric tuning values for projected paint-path geometry.

Declared fields/defaults:

```python
smooth_max_linear_step_mm: float = 1.0
smooth_max_angular_step_deg: float = 1.0
rotation_deadband_deg: float = 0.5
```

### `PaintMotionPlaneSpec`

```python
@dataclass(frozen=True)
class PaintMotionPlaneSpec:
```

Axis and orientation mapping for one supported paint motion plane.

Declared fields/defaults:

```python
planar_axes: tuple[str, str]
source_planar_coordinate_indices: tuple[int, int]
planar_coordinate_indices: tuple[int, int]
orthogonal_position_index: int
rotation_index: int
orientation_overrides_deg: dict[str, float] = field(default_factory=dict)
axis_offsets_deg: dict[str, float] = field(default_factory=dict)
```

### `PaintProjectionRules`

```python
@dataclass(frozen=True)
class PaintProjectionRules:
```

Projection-time domain mappings used by `PaintSimulationConfig`.

Declared fields/defaults:

```python
motion_plane_specs: dict[str, PaintMotionPlaneSpec] = field(default_factory=lambda: {'xy_z_rz': PaintMotionPlaneSpec(planar_axes=('x', 'y'), source_planar_coordinate_indices=(0, 1), planar_coordinate_indices=(0, 1), orthogonal_position_index=2, rotation_index=5, axis_offsets_deg={'x': 0.0, 'y': 90.0}), 'xz_y_ry': PaintMotionPlaneSpec(planar_axes=('x', 'z'), source_planar_coordinate_indices=(0, 1), planar_coordinate_indices=(0, 2), orthogonal_position_index=1, rotation_index=4, axis_offsets_deg={'x': 0.0, 'z': 90.0})})
side_signs: dict[str, float] = field(default_factory=lambda: {'positive': -1.0, 'negative': 1.0})
translation_direction_signs: dict[str, float] = field(default_factory=lambda: {'forward': 1.0, 'reverse': -1.0})
default_motion_plane: str = 'xy_z_rz'
default_paint_side: str = 'negative'
default_translation_direction: str = 'forward'
```

### `PaintPivotProfile`

```python
@dataclass(frozen=True)
class PaintPivotProfile:
```

Derived low-level pivot settings consumed by the paint executor.

Declared fields/defaults:

```python
motion_plane: str
translation_axis: str
translation_direction: str
paint_side: str
mirror_execution_rotation: bool
mirror_pickup_handoff: bool
pickup_axis_alignment_sign: float
```

### `PaintProcessConfig`

```python
@dataclass(frozen=True)
class PaintProcessConfig:
```

Single source of truth for platform-side paint process behavior.

Declared fields/defaults:

```python
enable_z_shift_pixel_compensation: bool = False
contour_pixel_to_mm_mode: str = PIXEL_TO_MM_MODE_GEOMETRY_PPM_ANCHOR
enable_execution_motion_trace: bool = False
execution_motion_trace_sample_period_s: float = 0.05
pivot_motion_plane: str = 'xz_y_ry'
primary_group_id: str = 'Vertical Shaft'
secondary_group_id: str = 'Horizontal Shaft'
cleanup_group_id: str = 'Clean'
pivot_axis: str = 'x'
pivot_direction: str = 'reverse'
pivot_contact_side: str = 'positive'
mirror_xz_ry_execution_rotation_value: bool = True
pickup_axis_alignment_sign_value: float = 1.0
enable_vacuum_pump: bool = True
stop_after_calibration_pickup: bool = False
run_while_workpiece_found: bool = True
enable_workpiece_matching: bool = True
default_paint_velocity_percent: float = 10.0
default_paint_acceleration_percent: float = 10.0
paint_process_acceleration_scale_percent: float = 100.0
default_paint_offset_mm: float = 0.0
unmatched_paint_pass_count: int = 1
unmatched_second_pass: UnmatchedSecondPassConfig = field(default_factory=UnmatchedSecondPassConfig)
closed_contour_overlap_mm: float = 0.0
enable_execution_state_timing: bool = True
pause_dashboard_live_view_after_capture: bool = True
apply_camera_to_tcp_for_pickup: bool = True
pickup_motion: PickupMotionConfig = field(default_factory=PickupMotionConfig)
contact_staging: PaintContactStagingConfig = field(default_factory=PaintContactStagingConfig)
edge_cleanup: PaintEdgeCleanupConfig = field(default_factory=PaintEdgeCleanupConfig)
dropoff: PaintDropoffConfig = field(default_factory=PaintDropoffConfig)
magazine_load: PaintMagazineLoadConfig = field(default_factory=PaintMagazineLoadConfig)
safe_travel: PaintSafeTravelConfig = field(default_factory=PaintSafeTravelConfig)
dropoff_safe_travel: PaintToDropoffSafeTravelConfig = field(default_factory=PaintToDropoffSafeTravelConfig)
navigation_return: PaintNavigationReturnConfig = field(default_factory=PaintNavigationReturnConfig)
enable_pivot_debug_plot: bool = False
enable_path_debug_plots: bool = False
```

### `scale_paint_process_accelerations`

```python
def scale_paint_process_accelerations(config: PaintProcessConfig) -> PaintProcessConfig
```

Return a cycle-local config with every configured acceleration scaled.

### `PaintSimulationConfig`

```python
@dataclass(frozen=True)
class PaintSimulationConfig:
```

Normalized settings that control projected paint motion geometry.

Declared fields/defaults:

```python
motion_plane: str = 'xy_z_rz'
translation_axis: str = 'x'
paint_side: str = 'negative'
translation_direction: str = 'reverse'
apply_camera_to_tcp_for_pickup: bool = False
camera_to_tcp_x_offset: float = 0.0
camera_to_tcp_y_offset: float = 0.0
rotation_direction_sign: float = 1.0
closed_contour_overlap_mm: float = 0.0
save_projection_snapshots: bool = False
rules: PaintProjectionRules = field(init=False, repr=False)
plane_spec: PaintMotionPlaneSpec = field(init=False, repr=False)
planar_axes: tuple[str, str] = field(init=False)
planar_coordinate_indices: tuple[int, int] = field(init=False)
source_planar_coordinate_indices: tuple[int, int] = field(init=False)
orthogonal_position_index: int = field(init=False)
rotation_index: int = field(init=False)
orientation_overrides_deg: dict[str, float] = field(init=False)
valid_translation_axes: tuple[str, ...] = field(init=False)
paint_axis_offset_deg: float = field(init=False)
side_sign: float = field(init=False)
direction_sign: float = field(init=False)
```

## `configured_motion_waypoint.py`

Source: [src/robot_systems/paint/processes/paint/configured_motion_waypoint.py](../../../../../src/robot_systems/paint/processes/paint/configured_motion_waypoint.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `dataclasses`, `src.engine.robot.motion_sequence`.

### `ConfiguredMotionWaypoint`

```python
@dataclass(frozen=True)
class ConfiguredMotionWaypoint:
```

Validated six-axis waypoint and its complete motion profile.

Declared fields/defaults:

```python
position: tuple[float, float, float, float, float, float]
velocity_percent: float
acceleration_percent: float
motion_type: OrderedMotionType
blend_radius: float
```

## `dashboard_live_view_events.py`

Source: [src/robot_systems/paint/processes/paint/dashboard_live_view_events.py](../../../../../src/robot_systems/paint/processes/paint/dashboard_live_view_events.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `dataclasses`.

### `PaintDashboardLiveViewEvent`

```python
@dataclass(frozen=True)
class PaintDashboardLiveViewEvent:
```

Declared fields/defaults:

```python
paused: bool
image: object | None = None
reason: str = ''
```

### `PaintDashboardLiveViewTopics`

```python
class PaintDashboardLiveViewTopics:
```

Declared fields/defaults:

```python
STATE = 'paint/dashboard/live-view/state'
```

### `PaintDashboardMessageEvent`

```python
@dataclass(frozen=True)
class PaintDashboardMessageEvent:
```

Declared fields/defaults:

```python
level: str
title: str
message: str
```

### `PaintDashboardMessageTopics`

```python
class PaintDashboardMessageTopics:
```

Declared fields/defaults:

```python
MESSAGE = 'paint/dashboard/message'
```

## `dryer_cycle_simulation_runner.py`

Source: [src/robot_systems/paint/processes/paint/dryer_cycle_simulation_runner.py](../../../../../src/robot_systems/paint/processes/paint/dryer_cycle_simulation_runner.py).

Simulate consecutive paint/dryer release cycles without robot or hardware. Each cycle starts with stale NEXT_POSITION_DONE from the previous cycle, then simulates a fresh MOVING transition, fresh DONE, and EJECT. Movement duration is configurable to prove that slow dryer/RPM settings do not cause a false timeout.

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `argparse`, `logging`, `pathlib`, `src.robot_systems.paint.processes.paint.auto_dryer.dryer_release_coordinator`, `sys`, `threading`, `time`, `types`.

Module declarations (expressions are shown without evaluating them):

```python
REPOSITORY_ROOT = Path(__file__).resolve().parents[5]
paint_package = types.ModuleType('src.robot_systems.paint')
```

### `SimulatedDryer`

```python
class SimulatedDryer:
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, *, move_duration_s: float, eject_duration_s: float, start_delay_s: float) -> None
```

```python
def next_position(self) -> bool
```

```python
def eject(self) -> bool
```

```python
def get_state(self)
```

### `run_cycles`

```python
def run_cycles(*, cycles: int, move_duration_s: float, eject_duration_s: float) -> bool
```

### `main`

```python
def main() -> int
```

## `execution_control.py`

Source: [src/robot_systems/paint/processes/paint/execution_control.py](../../../../../src/robot_systems/paint/processes/paint/execution_control.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `contextlib`, `threading`, `typing`.

### `PaintExecutionControl`

```python
class PaintExecutionControl:
```

Cooperative pause/resume state for a single paint execution run.

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self) -> None
```

```python
def request_pause(self) -> None
```

```python
def resume(self) -> None
```

```python
def request_stop(self) -> None
```

```python
def reset(self) -> None
```

```python
def should_stop(self) -> bool
```

```python
def pause_requested(self) -> bool
```

```python
def in_protected_phase(self) -> bool
```

```python
def wait_if_paused(self) -> bool
```

```python
@contextmanager
def protected_phase(self) -> Iterator[None]
```

## `incremental_adjustment.py`

Source: [src/robot_systems/paint/processes/paint/incremental_adjustment.py](../../../../../src/robot_systems/paint/processes/paint/incremental_adjustment.py).

Operator-paced paint-contact execution; no Qt or application dependencies.

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `dataclasses`, `math`, `threading`, `typing`.

Module declarations (expressions are shown without evaluating them):

```python
DEFAULT_ADJUSTMENT_STEP = AdjustmentStep(10.0, 0.0, 0.0)
```

### `AdjustmentStep`

```python
@dataclass(frozen=True)
class AdjustmentStep:
```

Declared fields/defaults:

```python
length_mm: float
paint_axis_offset_mm: float
perpendicular_axis_offset_mm: float
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def validate(self) -> None
```

### `PaintPathCursor`

```python
class PaintPathCursor:
```

Consume a six-axis command path by Cartesian XYZ arc length.

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, path: Sequence[Sequence[float]]) -> None
```

```python
@property
def complete(self) -> bool
```

```python
@property
def current_pose(self) -> tuple[float, ...]
```

```python
def take(self, length_mm: float) -> list[tuple[float, ...]]
```

### `PaintAdjustmentSession`

```python
class PaintAdjustmentSession:
```

Single operator command slot with explicit inspect and finish states.

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self) -> None
```

```python
def snapshot(self) -> tuple[str, float, float]
```

```python
def workpiece_not_found(self) -> None
```

```python
def workpiece_found(self) -> None
```

```python
def inspection_ready(self, travelled_mm: float, total_mm: float, *, complete: bool) -> None
```

```python
def request_next(self, step: AdjustmentStep) -> bool
```

```python
def request_finish(self) -> bool
```

```python
def wait_for_command(self, should_stop) -> tuple[str, AdjustmentStep | None] | None
```

```python
def fail(self) -> None
```

## `magazine_load_result.py`

Source: [src/robot_systems/paint/processes/paint/magazine_load_result.py](../../../../../src/robot_systems/paint/processes/paint/magazine_load_result.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`.

Module declarations (expressions are shown without evaluating them):

```python
NO_WORKPIECE_AT_MAGAZINE = 'No workpiece at magazine'
ALL_MAGAZINES_EMPTY = 'All magazines are empty'
MAGAZINE_EMPTY = 'Magazine is empty'
NO_WORKPIECE_AT_CALIBRATION = 'No workpiece at calibration'
```

## `magazine_load_service.py`

Source: [src/robot_systems/paint/processes/paint/magazine_load_service.py](../../../../../src/robot_systems/paint/processes/paint/magazine_load_service.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `cv2`, `logging`, `math`, `numpy`, `src.engine.robot.motion_sequence`, `src.engine.robot.path_preparation.geometry`, `src.engine.robot.targeting.vision_pose_request`, `src.robot_systems.paint.processes.paint.config`, `src.robot_systems.paint.processes.paint.motion.pose_sampling`, `src.robot_systems.paint.processes.paint.work_area_nesting`, `time`, `typing`.

### `PaintMagazineLoadService`

```python
class PaintMagazineLoadService:
```

Move a workpiece from the magazine capture station to calibration before painting.

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, *, navigation, capture_snapshot_service, path_executor, resolver_getter=None, work_area_service=None, release_image_size_getter=None, target_point_name: str='tool', camera_point_name: str='camera', frame_name: str='magazine', release_work_area_id: str='paint', release_frame_name: str='calibration') -> None
```

```python
def clear_work_area_nesting(self) -> None
```

```python
def commit_work_area_nesting(self) -> None
```

```python
def cancel_work_area_nesting(self) -> None
```

### `_contour_points_array`

```python
def _contour_points_array(contour) -> np.ndarray
```

### `_contour_center_px`

```python
def _contour_center_px(points: np.ndarray) -> tuple[float, float] | None
```

## `next_cycle_target.py`

Source: [src/robot_systems/paint/processes/paint/next_cycle_target.py](../../../../../src/robot_systems/paint/processes/paint/next_cycle_target.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `dataclasses`, `math`, `src.engine.robot.motion_sequence`.

### `NextCycleTarget`

```python
@dataclass(frozen=True)
class NextCycleTarget:
```

Validated robot target used to preposition for the next paint cycle.

Declared fields/defaults:

```python
group_id: str
position: tuple[float, ...]
velocity_percent: float
acceleration_percent: float
motion_type: OrderedMotionType
```

## `paint_contact_job.py`

Source: [src/robot_systems/paint/processes/paint/paint_contact_job.py](../../../../../src/robot_systems/paint/processes/paint/paint_contact_job.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `dataclasses`.

### `PaintContactCommandJob`

```python
@dataclass(frozen=True)
class PaintContactCommandJob:
```

Motion settings for one generated paint-contact path.

Declared fields/defaults:

```python
job_index: int
pattern_type: str
velocity_percent: float
acceleration_percent: float
```

## `paint_process.py`

Source: [src/robot_systems/paint/processes/paint/paint_process.py](../../../../../src/robot_systems/paint/processes/paint/paint_process.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `src.engine.core.i_messaging_service`, `src.engine.hardware.vacuum_pump.interfaces.i_vacuum_pump_controller`, `src.engine.process.base_process`, `src.engine.process.process_requirements`, `src.engine.robot.interfaces.i_robot_service`, `src.engine.system.i_system_manager`, `src.robot_systems.paint.component_ids`, `src.robot_systems.paint.processes.paint.config`, `src.robot_systems.paint.processes.paint.incremental_adjustment`, `src.shared_contracts.events.process_events`, `threading`, `typing`.

### `PaintProcess`

```python
class PaintProcess(BaseProcess):
```

Run one paint production cycle in the background and report process state changes.

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, production_service, messaging: IMessagingService, robot_service: Optional[IRobotService]=None, vacuum_pump: Optional[IVacuumPumpController]=None, paint_process_config_service=None, system_manager: Optional[ISystemManager]=None, requirements: Optional[ProcessRequirements]=None, service_checker: Optional[Callable[[str], bool]]=None) -> None
```

Store the production service and process dependencies for a single-run paint process.

```python
def start_adjustment_cycle(self) -> bool
```

Start one operator-paced cycle without changing production settings.

```python
def paint_next_adjustment_section(self, step: AdjustmentStep) -> bool
```

```python
def finish_adjustment_cycle(self) -> bool
```

```python
def adjustment_status(self) -> tuple[str, float, float]
```

```python
def start_manual_single_cycle(self) -> bool
```

Start one calibration-table paint cycle through the normal process state machine.

```python
def retry_unmatched_workpiece(self) -> bool
```

Restart at paint capture only after an unmatched-workpiece error.

## `paint_process_config_serializer.py`

Source: [src/robot_systems/paint/processes/paint/paint_process_config_serializer.py](../../../../../src/robot_systems/paint/processes/paint/paint_process_config_serializer.py).

Imports (including optional/function-local imports; not a startup dependency list): `copy`, `dataclasses`, `src.engine.repositories.interfaces`, `src.robot_systems.paint.processes.paint.config`, `typing`.

Module declarations (expressions are shown without evaluating them):

```python
T = TypeVar('T')
```

### `_section`

```python
def _section(raw: Dict[str, Any], key: str) -> Dict[str, Any]
```

### `_build_dataclass`

```python
def _build_dataclass(cls: Type[T], raw: Dict[str, Any], default: T) -> T
```

### `PaintProcessConfigSerializer`

```python
class PaintProcessConfigSerializer(ISettingsSerializer[PaintProcessConfig]):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, default_config: PaintProcessConfig=PAINT_PROCESS_CONFIG)
```

```python
@property
def settings_type(self) -> str
```

```python
def get_default(self) -> PaintProcessConfig
```

```python
def to_dict(self, settings: PaintProcessConfig) -> Dict[str, Any]
```

```python
def from_dict(self, data: Dict[str, Any]) -> PaintProcessConfig
```

### `_normalize_group_ids`

```python
def _normalize_group_ids(value: object) -> list[str]
```

### `_normalize_magazine_sources`

```python
def _normalize_magazine_sources(value: object) -> list[dict]
```

## `paint_process_config_service.py`

Source: [src/robot_systems/paint/processes/paint/paint_process_config_service.py](../../../../../src/robot_systems/paint/processes/paint/paint_process_config_service.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `abc`, `logging`, `src.engine.repositories.interfaces.i_settings_service`, `src.robot_systems.paint.component_ids`, `src.robot_systems.paint.processes.paint.config`, `threading`, `typing`.

### `IPaintProcessConfigService`

```python
class IPaintProcessConfigService(ABC):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
@abstractmethod
def get_snapshot(self) -> PaintProcessConfig
```

```python
@abstractmethod
def reload(self) -> PaintProcessConfig
```

```python
@abstractmethod
def save(self, settings: PaintProcessConfig) -> None
```

### `PaintProcessConfigService`

```python
class PaintProcessConfigService(IPaintProcessConfigService):
```

Runtime access point for persisted Paint process settings.

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, settings_service: ISettingsService, *, allowed_dropoff_strategies: tuple[str, ...]=('movement_group', 'plate_layout'))
```

```python
def get_snapshot(self) -> PaintProcessConfig
```

```python
def reload(self) -> PaintProcessConfig
```

```python
def save(self, settings: PaintProcessConfig) -> None
```

```python
def add_change_listener(self, listener: Callable[[PaintProcessConfig], None]) -> None
```

Notify a runtime consumer immediately after settings are saved in memory.

## `paint_production_service.py`

Source: [src/robot_systems/paint/processes/paint/paint_production_service.py](../../../../../src/robot_systems/paint/processes/paint/paint_production_service.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `logging`, `math`, `src.engine.hardware.vacuum_pump.interfaces.i_vacuum_pump_controller`, `src.robot_systems.paint.processes.paint.config`, `src.robot_systems.paint.processes.paint.dashboard_live_view_events`, `src.robot_systems.paint.processes.paint.execution_control`, `src.robot_systems.paint.processes.paint.execution_machine`, `src.robot_systems.paint.processes.paint.execution_machine.state`, `src.robot_systems.paint.processes.paint.magazine_load_result`, `src.robot_systems.paint.processes.paint.motion.pose_sampling`, `src.robot_systems.paint.processes.paint.next_cycle_target`, `threading`, `time`, `typing`.

### `PaintProductionService`

```python
class PaintProductionService:
```

Own the end-to-end paint production flow outside the editor UI.

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, *, workpiece_preparation_service, capture_snapshot_service, path_preparation_service, path_executor, vacuum_pump: Optional[IVacuumPumpController]=None, paint_process_config_service=None, magazine_load_service=None, navigation_service=None, vision_service=None, messaging_service=None) -> None
```

Store the services needed to capture, prepare, plan, and execute one paint cycle.

```python
def pause_current_phase(self) -> None
```

```python
def resume_current_phase(self) -> None
```

```python
def stop_current_phase(self) -> None
```

```python
def can_retry_unmatched_workpiece(self) -> bool
```

Only a failed match at the paint capture position can be recaptured.

```python
def run_once(self, stop_requested: Optional[Callable[[], bool]]=None, *, manual_single_cycle: bool=False, adjustment_session=None, retry_unmatched_workpiece: bool=False) -> tuple[bool, str]
```

Run production, optionally forcing one calibration-table cycle without magazine load.

```python
def publish_dashboard_message(self, level: str, title: str, message: str) -> None
```

Publish a production notice into the paint dashboard message queue.

## `work_area_nesting.py`

Source: [src/robot_systems/paint/processes/paint/work_area_nesting.py](../../../../../src/robot_systems/paint/processes/paint/work_area_nesting.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `dataclasses`, `math`, `threading`, `typing`.

### `WorkAreaNestingReservation`

```python
@dataclass(frozen=True)
class WorkAreaNestingReservation:
```

Declared fields/defaults:

```python
center_xy: tuple[float, float]
width_mm: float
height_mm: float
has_space_for_same_footprint: bool
```

### `WorkAreaNestingService`

```python
class WorkAreaNestingService:
```

Reserve deterministic shelf positions inside an existing work area.

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self) -> None
```

```python
def clear(self) -> None
```

```python
def reserve(self, boundary_xy: Sequence[Sequence[float]], *, width_mm: float, height_mm: float, margin_mm: float, padding_mm: float) -> tuple[WorkAreaNestingReservation | None, str]
```

```python
def commit(self) -> None
```

```python
def cancel(self) -> None
```

### `_finite_points`

```python
def _finite_points(points) -> list[tuple[float, float]]
```

### `_polygon_area`

```python
def _polygon_area(points: Sequence[tuple[float, float]]) -> float
```
