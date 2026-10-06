# Module reference: `src/engine/hardware/peripherals`

[Package guide](README.md) · [Complete source index](../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [device_control_adapters.py](#device_control_adapterspy)
- [peripherals.py](#peripheralspy)

## `__init__.py`

Source: [src/engine/hardware/peripherals/__init__.py](../../../../src/engine/hardware/peripherals/__init__.py).

Imports (including optional/function-local imports; not a startup dependency list): `src.engine.hardware.peripherals.peripherals`.

Package-level import/export surface:

```python
from src.engine.hardware.peripherals.peripherals import PeripheralBinding, PeripheralConfig, PeripheralConfigSerializer
```

Module declarations (expressions are shown without evaluating them):

```python
__all__ = ['PeripheralBinding', 'PeripheralConfig', 'PeripheralConfigSerializer']
```

## `device_control_adapters.py`

Source: [src/engine/hardware/peripherals/device_control_adapters.py](../../../../src/engine/hardware/peripherals/device_control_adapters.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `collections.abc`, `logging`, `src.engine.core.i_health_checkable`, `src.engine.hardware.peripherals.peripherals`, `time`, `typing`.

### `BinaryDeviceAdapter`

```python
class BinaryDeviceAdapter:
```

Expose a device with turn_on/turn_off through the shared app contract.

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, key: str, label: str, device: Any, *, enabled: bool=True, persist_enabled: Callable[[str, bool], None] | None=None, enable_check: Callable[[], object] | None=None, commands: Mapping[str, int] | None=None) -> None
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

```python
def actions(self) -> Mapping[str, str]
```

```python
def execute(self, action: str) -> bool
```

```python
def read_state(self) -> Mapping[str, object]
```

### `VacuumSensorDeviceAdapter`

```python
class VacuumSensorDeviceAdapter:
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, device: Any, *, enabled: bool=True, persist_enabled: Callable[[str, bool], None] | None=None) -> None
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

```python
def actions(self) -> Mapping[str, str]
```

```python
def execute(self, action: str) -> bool
```

```python
def read_state(self) -> Mapping[str, object]
```

### `PhysicalButtonsDeviceAdapter`

```python
class PhysicalButtonsDeviceAdapter:
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, device: Any, output_names: Mapping[str, str] | None=None, *, enabled: bool=True, persist_enabled: Callable[[str, bool], None] | None=None, commands: Mapping[str, int] | None=None) -> None
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

```python
def actions(self) -> Mapping[str, str]
```

```python
def execute(self, action: str) -> bool
```

```python
def read_state(self) -> Mapping[str, object]
```

### `DryerDeviceAdapter`

```python
class DryerDeviceAdapter:
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, device: Any, persist_enabled: Callable[[str, bool], None] | None=None, commands: Mapping[str, int] | None=None) -> None
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

```python
def actions(self) -> Mapping[str, str]
```

```python
def execute(self, action: str) -> bool
```

```python
def read_state(self) -> Mapping[str, object]
```

### `build_device_control_adapters`

```python
def build_device_control_adapters(peripheral_config: PeripheralConfig, services: Mapping[str, object], persist_enabled: Callable[[str, bool], None] | None=None) -> list[object]
```

Build shared-app adapters for configured, already-constructed devices.

## `peripherals.py`

Source: [src/engine/hardware/peripherals/peripherals.py](../../../../src/engine/hardware/peripherals/peripherals.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `dataclasses`, `src.engine.repositories.interfaces.settings_serializer`, `typing`.

### `PeripheralBinding`

```python
@dataclass(frozen=True)
class PeripheralBinding:
```

Logical device mapping to one configured Modbus slave.

Declared fields/defaults:

```python
slave_id: int
enabled: bool = True
inputs: dict[str, str] = field(default_factory=dict)
outputs: dict[str, str] = field(default_factory=dict)
commands: dict[str, int] = field(default_factory=dict)
statuses: dict[str, int] = field(default_factory=dict)
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
@classmethod
def from_dict(cls, data: dict[str, Any]) -> 'PeripheralBinding'
```

```python
def to_dict(self) -> dict[str, Any]
```

### `PeripheralConfig`

```python
@dataclass(frozen=True)
class PeripheralConfig:
```

Logical Paint peripheral bindings, independent of transport protocol.

Declared fields/defaults:

```python
peripherals: dict[str, PeripheralBinding] = field(default_factory=dict)
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
@classmethod
def from_dict(cls, data: dict[str, Any]) -> 'PeripheralConfig'
```

```python
def to_dict(self) -> dict[str, Any]
```

```python
def get(self, name: str) -> PeripheralBinding | None
```

### `PeripheralConfigSerializer`

```python
class PeripheralConfigSerializer(ISettingsSerializer[PeripheralConfig]):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
@property
def settings_type(self) -> str
```

```python
def get_default(self) -> PeripheralConfig
```

```python
def to_dict(self, settings: PeripheralConfig) -> dict[str, Any]
```

```python
def from_dict(self, data: dict[str, Any]) -> PeripheralConfig
```
