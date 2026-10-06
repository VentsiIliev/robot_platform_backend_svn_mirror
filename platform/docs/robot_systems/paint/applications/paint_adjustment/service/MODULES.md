# Module reference: `src/robot_systems/paint/applications/paint_adjustment/service`

[Package guide](README.md) · [Complete source index](../../../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [i_paint_adjustment_service.py](#i_paint_adjustment_servicepy)
- [paint_adjustment_service.py](#paint_adjustment_servicepy)
- [stub_paint_adjustment_service.py](#stub_paint_adjustment_servicepy)

## `__init__.py`

Source: [src/robot_systems/paint/applications/paint_adjustment/service/__init__.py](../../../../../../src/robot_systems/paint/applications/paint_adjustment/service/__init__.py).

Service contract and adapters for Paint Adjustment.

No top-level functions, classes or public value declarations; inspect the source for imports or entry-point statements.

## `i_paint_adjustment_service.py`

Source: [src/robot_systems/paint/applications/paint_adjustment/service/i_paint_adjustment_service.py](../../../../../../src/robot_systems/paint/applications/paint_adjustment/service/i_paint_adjustment_service.py).

Imports (including optional/function-local imports; not a startup dependency list): `abc`, `dataclasses`.

### `PaintHeadCommandResult`

```python
@dataclass(frozen=True)
class PaintHeadCommandResult:
```

Verified write, or a disabled-device dry-run calculation.

Declared fields/defaults:

```python
value: int
register: int
wrote: bool
relative: bool
```

### `PaintHeadDialConfig`

```python
@dataclass(frozen=True)
class PaintHeadDialConfig:
```

Declared fields/defaults:

```python
minimum: int
spacing: int
count: int
enabled: bool
```

### `PaintAdjustmentOptions`

```python
@dataclass(frozen=True)
class PaintAdjustmentOptions:
```

Declared fields/defaults:

```python
length_mm: float
paint_axis_offset_mm: float
perpendicular_axis_offset_mm: float
```

### `IPaintAdjustmentService`

```python
class IPaintAdjustmentService(ABC):
```

Provide the camera role and verified paint-head commands.

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
@abstractmethod
def get_camera_role(self) -> str
```

```python
@abstractmethod
def get_preset_count(self) -> int
```

```python
@abstractmethod
def is_paint_head_available(self) -> bool
```

```python
@abstractmethod
def get_dial_config(self) -> PaintHeadDialConfig
```

```python
@abstractmethod
def read_current_position(self) -> int | None
```

Read hardware when enabled; return None without I/O when disabled.

```python
@abstractmethod
def start_single_paint_cycle(self) -> bool
```

Start one paint cycle without magazine loading or repetition.

```python
@abstractmethod
def get_paint_cycle_state(self) -> str
```

Return the shared paint process state for initial UI display.

```python
@abstractmethod
def get_adjustment_options(self) -> PaintAdjustmentOptions
```

```python
@abstractmethod
def start_adjustment_cycle(self, options: PaintAdjustmentOptions) -> bool
```

```python
@abstractmethod
def paint_next_section(self, options: PaintAdjustmentOptions) -> bool
```

```python
@abstractmethod
def finish_adjustment_cycle(self) -> bool
```

```python
@abstractmethod
def get_adjustment_status(self) -> tuple[str, float, float]
```

```python
@abstractmethod
def adjust_paint(self, direction: str, degrees: int) -> PaintHeadCommandResult
```

Move relative whole degrees, or calculate a dry-run delta.

```python
@abstractmethod
def adjust_paint_by_register_units(self, direction: str, units: int) -> PaintHeadCommandResult
```

Move by signed register units, or calculate a dry-run delta.

```python
@abstractmethod
def go_to_setting(self, setting: int) -> PaintHeadCommandResult
```

Write an absolute preset, or calculate its dry-run register value.

```python
@abstractmethod
def go_to_position(self, position: int) -> PaintHeadCommandResult
```

Write any calibrated register position, or preview it without I/O.

## `paint_adjustment_service.py`

Source: [src/robot_systems/paint/applications/paint_adjustment/service/paint_adjustment_service.py](../../../../../../src/robot_systems/paint/applications/paint_adjustment/service/paint_adjustment_service.py).

Imports (including optional/function-local imports; not a startup dependency list): `.i_paint_adjustment_service`, `__future__`, `logging`, `src.engine.common_settings_ids`, `src.engine.hardware.communication.modbus.modbus`, `src.engine.hardware.communication.transport_registry`, `src.engine.hardware.peripherals`, `src.engine.repositories.interfaces.i_settings_service`, `src.robot_systems.paint.component_ids`, `src.robot_systems.paint.hardware.paint_head_device`, `src.robot_systems.paint.processes.paint.incremental_adjustment`, `typing`.

### `PaintAdjustmentService`

```python
class PaintAdjustmentService(IPaintAdjustmentService):
```

Resolve the paint-head binding from live settings for each command.

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, settings: ISettingsService, transport_registry: TransportRegistry=DEFAULT_TRANSPORT_REGISTRY, start_single_cycle: Callable[[], bool] | None=None, get_cycle_state: Callable[[], str] | None=None, start_adjustment: Callable[[], bool] | None=None, paint_next: Callable[[AdjustmentStep], bool] | None=None, finish_adjustment: Callable[[], bool] | None=None, get_adjustment_status: Callable[[], tuple[str, float, float]] | None=None) -> None
```

```python
def get_camera_role(self) -> str
```

```python
def get_preset_count(self) -> int
```

```python
def is_paint_head_available(self) -> bool
```

```python
def get_dial_config(self) -> PaintHeadDialConfig
```

```python
def read_current_position(self) -> int | None
```

```python
def start_single_paint_cycle(self) -> bool
```

```python
def get_paint_cycle_state(self) -> str
```

```python
def get_adjustment_options(self) -> PaintAdjustmentOptions
```

```python
def start_adjustment_cycle(self, options: PaintAdjustmentOptions) -> bool
```

```python
def paint_next_section(self, options: PaintAdjustmentOptions) -> bool
```

```python
def finish_adjustment_cycle(self) -> bool
```

```python
def get_adjustment_status(self) -> tuple[str, float, float]
```

```python
def adjust_paint(self, direction: str, degrees: int) -> PaintHeadCommandResult
```

```python
def adjust_paint_by_register_units(self, direction: str, units: int) -> PaintHeadCommandResult
```

```python
def go_to_setting(self, setting: int) -> PaintHeadCommandResult
```

```python
def go_to_position(self, position: int) -> PaintHeadCommandResult
```

## `stub_paint_adjustment_service.py`

Source: [src/robot_systems/paint/applications/paint_adjustment/service/stub_paint_adjustment_service.py](../../../../../../src/robot_systems/paint/applications/paint_adjustment/service/stub_paint_adjustment_service.py).

Imports (including optional/function-local imports; not a startup dependency list): `.i_paint_adjustment_service`.

### `StubPaintAdjustmentService`

```python
class StubPaintAdjustmentService(IPaintAdjustmentService):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self) -> None
```

```python
def get_camera_role(self) -> str
```

```python
def get_preset_count(self) -> int
```

```python
def is_paint_head_available(self) -> bool
```

```python
def get_dial_config(self) -> PaintHeadDialConfig
```

```python
def read_current_position(self) -> int
```

```python
def start_single_paint_cycle(self) -> bool
```

```python
def get_paint_cycle_state(self) -> str
```

```python
def get_adjustment_options(self) -> PaintAdjustmentOptions
```

```python
def start_adjustment_cycle(self, options: PaintAdjustmentOptions) -> bool
```

```python
def paint_next_section(self, options: PaintAdjustmentOptions) -> bool
```

```python
def finish_adjustment_cycle(self) -> bool
```

```python
def get_adjustment_status(self) -> tuple[str, float, float]
```

```python
def adjust_paint(self, direction: str, degrees: int) -> PaintHeadCommandResult
```

```python
def adjust_paint_by_register_units(self, direction: str, units: int) -> PaintHeadCommandResult
```

```python
def go_to_setting(self, setting: int) -> PaintHeadCommandResult
```

```python
def go_to_position(self, position: int) -> PaintHeadCommandResult
```
