# Module reference: `src/robot_systems/paint/hardware`

[Package guide](README.md) · [Complete source index](../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [paint_head_availability_adapter.py](#paint_head_availability_adapterpy)
- [paint_head_device.py](#paint_head_devicepy)

## `__init__.py`

Source: [src/robot_systems/paint/hardware/__init__.py](../../../../src/robot_systems/paint/hardware/__init__.py).

Paint-specific hardware adapters.

No top-level functions, classes or public value declarations; inspect the source for imports or entry-point statements.

## `paint_head_availability_adapter.py`

Source: [src/robot_systems/paint/hardware/paint_head_availability_adapter.py](../../../../src/robot_systems/paint/hardware/paint_head_availability_adapter.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `collections.abc`.

### `PaintHeadAvailabilityAdapter`

```python
class PaintHeadAvailabilityAdapter:
```

Devices-app toggle for the paint head; does not touch hardware.

Declared fields/defaults:

```python
key = 'paint_head'
label = 'Paint Head'
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, enabled_provider: Callable[[], bool], persist_enabled: Callable[[str, bool], None]) -> None
```

```python
def actions(self) -> Mapping[str, str]
```

```python
def execute(self, action: str) -> bool
```

```python
def read_state(self) -> Mapping[str, object]
```

```python
def set_enabled(self, enabled: bool) -> bool
```

```python
def is_enabled(self) -> bool
```

```python
def last_error(self) -> str | None
```

## `paint_head_device.py`

Source: [src/robot_systems/paint/hardware/paint_head_device.py](../../../../src/robot_systems/paint/hardware/paint_head_device.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `src.engine.hardware.communication.i_register_transport`.

### `PaintHeadRangeError`

```python
class PaintHeadRangeError(ValueError):
```

A requested paint-head target exceeds its configured safe range.

### `PaintHeadDevice`

```python
class PaintHeadDevice:
```

Apply paint-head presets or relative degree moves and verify writes.

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, transport: IRegisterTransport, register: int, *, min_value: int, max_value: int, preset_spacing: int, preset_count: int, degree_units_numerator: int, degree_units_denominator: int) -> None
```

```python
def go_to_setting(self, setting: int) -> int
```

Write the script's absolute preset: min + spacing × (count − setting).

```python
def go_to_position(self, position: int) -> int
```

Write a calibrated register position and verify the readback.

```python
def validate_position(self, position: int) -> int
```

Validate an absolute target without device I/O for dry runs.

```python
def register_for_setting(self, setting: int) -> int
```

Calculate an absolute preset without accessing hardware.

```python
def move_degrees(self, delta_degrees: int) -> int
```

Move signed whole degrees from the current register position.

```python
def move_register_delta(self, delta_register: int) -> int
```

Move a signed register distance after reading the current position.

```python
def register_delta_for_setting_tenths(self, tenths: int) -> int
```

Convert a positive tenth-of-setting step to register units.

```python
def move_setting_tenths(self, signed_tenths: int) -> int
```

Advance the displayed setting by exact tenths in register direction.

```python
def read_position(self) -> int
```

Read and validate the current register position.

```python
def register_delta_for_degrees(self, delta_degrees: int) -> int
```

Calculate a signed relative delta without accessing hardware.
