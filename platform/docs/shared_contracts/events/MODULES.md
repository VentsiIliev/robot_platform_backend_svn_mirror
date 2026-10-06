# Module reference: `src/shared_contracts/events`

[Package guide](README.md) · [Complete source index](../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [glue_overlay_events.py](#glue_overlay_eventspy)
- [glue_process_events.py](#glue_process_eventspy)
- [localization_events.py](#localization_eventspy)
- [notification_events.py](#notification_eventspy)
- [pick_and_place_events.py](#pick_and_place_eventspy)
- [process_events.py](#process_eventspy)
- [robot_events.py](#robot_eventspy)
- [shell_events.py](#shell_eventspy)
- [vision_events.py](#vision_eventspy)
- [weight_events.py](#weight_eventspy)
- [workpiece_events.py](#workpiece_eventspy)

## `glue_overlay_events.py`

Source: [src/shared_contracts/events/glue_overlay_events.py](../../../src/shared_contracts/events/glue_overlay_events.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `dataclasses`, `typing`.

### `GlueOverlayTopics`

```python
class GlueOverlayTopics:
```

Declared fields/defaults:

```python
JOB_LOADED = 'glue/overlay/job_loaded'
```

### `GlueOverlaySegment`

```python
@dataclass(frozen=True)
class GlueOverlaySegment:
```

Declared fields/defaults:

```python
path_index: int
workpiece_id: str
pattern_type: str
segment_index: int
points: list[tuple[float, float]]
```

### `GlueOverlayJobLoadedEvent`

```python
@dataclass(frozen=True)
class GlueOverlayJobLoadedEvent:
```

Declared fields/defaults:

```python
image: Any
image_width: int
image_height: int
segments: list[GlueOverlaySegment]
```

## `glue_process_events.py`

Source: [src/shared_contracts/events/glue_process_events.py](../../../src/shared_contracts/events/glue_process_events.py).

### `GlueProcessTopics`

```python
class GlueProcessTopics:
```

Declared fields/defaults:

```python
DIAGNOSTICS = 'glue/process/diagnostics'
```

## `localization_events.py`

Source: [src/shared_contracts/events/localization_events.py](../../../src/shared_contracts/events/localization_events.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `dataclasses`, `datetime`.

### `LanguageChangedEvent`

```python
@dataclass(frozen=True)
class LanguageChangedEvent:
```

Declared fields/defaults:

```python
language_code: str
timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
```

### `LocalizationTopics`

```python
class LocalizationTopics:
```

Declared fields/defaults:

```python
LANGUAGE_CHANGED = 'localization/language_changed'
```

## `notification_events.py`

Source: [src/shared_contracts/events/notification_events.py](../../../src/shared_contracts/events/notification_events.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `dataclasses`, `datetime`, `enum`, `typing`.

### `NotificationSeverity`

```python
class NotificationSeverity(str, Enum):
```

Declared fields/defaults:

```python
INFO = 'info'
WARNING = 'warning'
ERROR = 'error'
CRITICAL = 'critical'
```

### `UserNotificationEvent`

```python
@dataclass(frozen=True)
class UserNotificationEvent:
```

Declared fields/defaults:

```python
source: str
severity: NotificationSeverity
title_key: str = ''
message_key: str = ''
params: Mapping[str, object] = field(default_factory=dict)
fallback_title: str = ''
fallback_message: str = ''
detail: str | None = None
dedupe_key: str | None = None
timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
```

### `DismissNotificationEvent`

```python
@dataclass(frozen=True)
class DismissNotificationEvent:
```

Declared fields/defaults:

```python
dedupe_key: str
timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
```

### `NotificationTopics`

```python
class NotificationTopics:
```

Declared fields/defaults:

```python
USER = 'ui/notification'
DISMISS = 'ui/notification/dismiss'
```

## `pick_and_place_events.py`

Source: [src/shared_contracts/events/pick_and_place_events.py](../../../src/shared_contracts/events/pick_and_place_events.py).

Imports (including optional/function-local imports; not a startup dependency list): `dataclasses`, `datetime`, `typing`.

### `WorkpiecePlacedEvent`

```python
@dataclass(frozen=True)
class WorkpiecePlacedEvent:
```

Declared fields/defaults:

```python
workpiece_name: str
gripper_id: int
plane_x: float
plane_y: float
width: float
height: float
timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
```

### `MatchedWorkpieceInfo`

```python
@dataclass(frozen=True)
class MatchedWorkpieceInfo:
```

Declared fields/defaults:

```python
workpiece_name: str
workpiece_id: str
gripper_id: int
orientation: float
```

### `PickAndPlaceDiagnosticsEvent`

```python
@dataclass(frozen=True)
class PickAndPlaceDiagnosticsEvent:
```

Declared fields/defaults:

```python
snapshot: dict[str, Any]
timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
```

### `PickAndPlaceTopics`

```python
class PickAndPlaceTopics:
```

Declared fields/defaults:

```python
WORKPIECE_PLACED = 'pick_and_place/workpiece_placed'
PLANE_RESET = 'pick_and_place/plane_reset'
MATCH_RESULT = 'pick_and_place/match_result'
DIAGNOSTICS = 'pick_and_place/diagnostics'
```

## `process_events.py`

Source: [src/shared_contracts/events/process_events.py](../../../src/shared_contracts/events/process_events.py).

Imports (including optional/function-local imports; not a startup dependency list): `dataclasses`, `datetime`, `enum`, `typing`.

### `ProcessState`

```python
class ProcessState(Enum):
```

Declared fields/defaults:

```python
IDLE = 'idle'
RUNNING = 'running'
PAUSED = 'paused'
STOPPED = 'stopped'
ERROR = 'error'
```

### `ProcessStateEvent`

```python
@dataclass(frozen=True)
class ProcessStateEvent:
```

Declared fields/defaults:

```python
process_id: str
state: ProcessState
previous: ProcessState
message: str = ''
timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
```

### `ProcessBusyEvent`

```python
@dataclass(frozen=True)
class ProcessBusyEvent:
```

Declared fields/defaults:

```python
requested_by: str
message: str
timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
```

### `ServiceUnavailableEvent`

```python
@dataclass(frozen=True)
class ServiceUnavailableEvent:
```

Declared fields/defaults:

```python
process_id: str
missing_services: List[str]
timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
```

### `ProcessTopics`

```python
class ProcessTopics:
```

Declared fields/defaults:

```python
ACTIVE = 'process/active/state'
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
@staticmethod
def state(process_id: str) -> str
```

```python
@staticmethod
def error(process_id: str) -> str
```

```python
@staticmethod
def service_unavailable(process_id: str) -> str
```

```python
@staticmethod
def busy(requester_id: str) -> str
```

## `robot_events.py`

Source: [src/shared_contracts/events/robot_events.py](../../../src/shared_contracts/events/robot_events.py).

### `RobotTopics`

```python
class RobotTopics:
```

Declared fields/defaults:

```python
STATE = 'robot/state'
POSITION = 'robot/position'
VELOCITY = 'robot/velocity'
ACCELERATION = 'robot/acceleration'
TARGETING_DEFINITIONS_CHANGED = 'robot/targeting_definitions_changed'
ROBOT_CONFIG_CHANGED = 'robot/config_changed'
```

### `RobotCalibrationTopics`

```python
class RobotCalibrationTopics:
```

EVENTS ARE ONLY USED FOR PROVIDING FEEDBACK TO THE USER

Declared fields/defaults:

```python
ROBOT_CALIBRATION_LOG = 'robot/calibration/log'
ROBOT_CALIBRATION_START = 'robot/calibration/start'
ROBOT_CALIBRATION_STOP = 'robot/calibration/stop'
ROBOT_CALIBRATION_IMAGE = 'robot/calibration/image'
ROBOT_STATE = 'robot/state'
```

## `shell_events.py`

Source: [src/shared_contracts/events/shell_events.py](../../../src/shared_contracts/events/shell_events.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `dataclasses`.

### `ShellTopics`

```python
class ShellTopics:
```

Declared fields/defaults:

```python
NAVIGATE = 'shell/navigate'
VISIBLE_APPLICATIONS = 'shell/visible-applications'
```

### `ApplicationShortcut`

```python
@dataclass(frozen=True)
class ApplicationShortcut:
```

Declared fields/defaults:

```python
app_name: str
label: str
icon: str
folder_id: int = 0
folder_name: str = ''
folder_translation_key: str = ''
```

## `vision_events.py`

Source: [src/shared_contracts/events/vision_events.py](../../../src/shared_contracts/events/vision_events.py).

### `VisionTopics`

```python
class VisionTopics:
```

Vision vision_service and camera topics

Declared fields/defaults:

```python
SERVICE_STATE = 'vision-service/state'
LATEST_IMAGE = 'vision-vision_service/latest-image'
FPS = 'vision-vision_service/fps'
CALIBRATION_IMAGE_CAPTURED = 'vision-vision_service/calibration-image-captured'
BRIGHTNESS_REGION = 'vision-vision_service/brightness-region'
THRESHOLD_REGION = 'vision-vision_service/threshold'
CALIBRATION_FEEDBACK = 'vision-vision_service/calibration-feedback'
THRESHOLD_IMAGE = 'vision-vision_service/threshold-image'
AUTO_BRIGHTNESS = 'vision-vision_service/auto-brightness'
AUTO_BRIGHTNESS_START = 'vison-auto-brightness'
AUTO_BRIGHTNESS_STOP = 'vison-auto-brightness'
TRANSFORM_TO_CAMERA_POINT = 'vision-vision_service/transform-to-camera-point'
```

### `CameraTopics`

```python
class CameraTopics:
```

Named raw camera streams published by their single hardware owner.

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
@staticmethod
def frame(role: str) -> str
```

## `weight_events.py`

Source: [src/shared_contracts/events/weight_events.py](../../../src/shared_contracts/events/weight_events.py).

Imports (including optional/function-local imports; not a startup dependency list): `dataclasses`, `datetime`, `enum`, `typing`.

### `CellState`

```python
class CellState(Enum):
```

Declared fields/defaults:

```python
DISCONNECTED = 'disconnected'
CONNECTING = 'connecting'
CONNECTED = 'connected'
ERROR = 'error'
```

### `WeightReading`

```python
@dataclass(frozen=True)
class WeightReading:
```

Declared fields/defaults:

```python
cell_id: int
value: float
unit: str = 'g'
timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def is_valid(self, min_threshold: float, max_threshold: float) -> bool
```

### `CellStateEvent`

```python
@dataclass(frozen=True)
class CellStateEvent:
```

Declared fields/defaults:

```python
cell_id: int
state: CellState
message: str = ''
timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
```

### `WeightTopics`

```python
class WeightTopics:
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
@staticmethod
def state(cell_id: int) -> str
```

```python
@staticmethod
def reading(cell_id: int) -> str
```

```python
@staticmethod
def all_readings() -> str
```

## `workpiece_events.py`

Source: [src/shared_contracts/events/workpiece_events.py](../../../src/shared_contracts/events/workpiece_events.py).

### `WorkpieceTopics`

```python
class WorkpieceTopics:
```

Declared fields/defaults:

```python
OPEN_IN_EDITOR = 'workpiece/open-in-editor'
```
