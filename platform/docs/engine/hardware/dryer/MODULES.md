# Module reference: `src/engine/hardware/dryer`

[Package guide](README.md) · [Complete source index](../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [dryer_controller.py](#dryer_controllerpy)
- [dryer_service.py](#dryer_servicepy)
- [mock_runner.py](#mock_runnerpy)
- [next_position_runner.py](#next_position_runnerpy)
- [read_registers.py](#read_registerspy)

## `__init__.py`

Source: [src/engine/hardware/dryer/__init__.py](../../../../src/engine/hardware/dryer/__init__.py).

Imports (including optional/function-local imports; not a startup dependency list): `src.engine.hardware.dryer.dryer_controller`, `src.engine.hardware.dryer.dryer_service`, `src.engine.hardware.dryer.interfaces.i_dryer_controller`, `src.engine.hardware.dryer.interfaces.i_dryer_service`, `src.engine.hardware.dryer.interfaces.i_dryer_transport`, `src.engine.hardware.dryer.models.dryer_commands`, `src.engine.hardware.dryer.models.dryer_config`, `src.engine.hardware.dryer.models.dryer_modbus_registers`, `src.engine.hardware.dryer.models.dryer_state`, `src.engine.hardware.dryer.models.dryer_status`, `src.engine.hardware.dryer.models.dryer_write_data`.

Package-level import/export surface:

```python
from src.engine.hardware.dryer.dryer_controller import DryerController
from src.engine.hardware.dryer.interfaces.i_dryer_controller import IDryerController
from src.engine.hardware.dryer.interfaces.i_dryer_transport import IDryerTransport
from src.engine.hardware.dryer.interfaces.i_dryer_service import IDryerService
from src.engine.hardware.dryer.dryer_service import DryerService
from src.engine.hardware.dryer.models.dryer_commands import DEFAULT_DRYER_COMMANDS, DryerCommand, dryer_commands
from src.engine.hardware.dryer.models.dryer_status import DEFAULT_DRYER_STATUSES, DryerStatus, dryer_statuses
from src.engine.hardware.dryer.models.dryer_config import DryerConfig, DryerConfigSerializer
from src.engine.hardware.dryer.models.dryer_state import DryerState
from src.engine.hardware.dryer.models.dryer_write_data import DryerWriteData
from src.engine.hardware.dryer.models.dryer_modbus_registers import DryerDefaults, DryerModbusRegister, DryerRegisterMap
```

Module declarations (expressions are shown without evaluating them):

```python
__all__ = ['DryerController', 'IDryerController', 'IDryerTransport', 'IDryerService', 'DryerService', 'DryerCommand', 'DryerStatus', 'DEFAULT_DRYER_COMMANDS', 'DEFAULT_DRYER_STATUSES', 'dryer_commands', 'dryer_statuses', 'DryerConfig', 'DryerConfigSerializer', 'DryerState', 'DryerWriteData', 'DryerDefaults', 'DryerModbusRegister', 'DryerRegisterMap']
```

## `dryer_controller.py`

Source: [src/engine/hardware/dryer/dryer_controller.py](../../../../src/engine/hardware/dryer/dryer_controller.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `logging`, `src.engine.hardware.dryer.interfaces.i_dryer_controller`, `src.engine.hardware.dryer.interfaces.i_dryer_transport`, `src.engine.hardware.dryer.models.dryer_commands`, `src.engine.hardware.dryer.models.dryer_config`, `src.engine.hardware.dryer.models.dryer_modbus_registers`, `src.engine.hardware.dryer.models.dryer_state`, `src.engine.hardware.dryer.models.dryer_status`, `src.engine.hardware.dryer.models.dryer_write_data`, `threading`, `time`, `typing`.

### `DryerController`

```python
class DryerController(IDryerController):
```

High-level dryer controller backed by register-block writes.

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, transport: IDryerTransport, config: DryerConfig | None=None, register_map: DryerRegisterMap | None=None, commands: Mapping[str, int] | None=None, statuses: Mapping[str, int] | None=None, next_position_timeout_s: float=10.0, status_poll_interval_s: float=0.1, command_settle_s: float=0.03, max_retries: int=0) -> None
```

```python
def initialize(self) -> bool
```

Write persisted defaults, then command the dryer to its next position.

```python
def shutdown(self) -> None
```

```python
def update_config(self, config: DryerConfig) -> None
```

```python
def write_data(self, data: DryerWriteData) -> bool
```

```python
def get_state(self) -> DryerState
```

```python
def move_servos(self, data: DryerWriteData | None=None) -> bool
```

```python
def eject(self, data: DryerWriteData | None=None) -> bool
```

```python
def open_plate(self, data: DryerWriteData | None=None) -> bool
```

```python
def close_plage(self, data: DryerWriteData | None=None) -> bool
```

```python
def close_plate(self, data: DryerWriteData | None=None) -> bool
```

Compatibility-correct alias for the historical close_plage method.

```python
def next_position(self, data: DryerWriteData | None=None) -> bool
```

```python
def execute_command(self, command: int, data: DryerWriteData | None=None) -> bool
```

Write a command supplied by the robot-system peripheral config.

## `dryer_service.py`

Source: [src/engine/hardware/dryer/dryer_service.py](../../../../src/engine/hardware/dryer/dryer_service.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `collections.abc`, `logging`, `src.engine.hardware.dryer.interfaces.i_dryer_controller`, `src.engine.hardware.dryer.interfaces.i_dryer_service`, `src.engine.hardware.dryer.models.dryer_config`, `src.engine.hardware.dryer.models.dryer_state`, `src.engine.hardware.dryer.models.dryer_write_data`, `threading`.

### `DryerService`

```python
class DryerService(IDryerService):
```

Keeps a stable service reference while dryer hardware is cycled.

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, controller_factory: Callable[[DryerConfig], IDryerController], config: DryerConfig) -> None
```

```python
@property
def last_error(self) -> str | None
```

```python
def enable(self) -> bool
```

```python
def enable_async(self) -> bool
```

Schedule initialization and return as soon as the worker starts.

```python
def disable(self) -> None
```

```python
def is_enabled(self) -> bool
```

```python
def is_healthy(self) -> bool
```

```python
def initialize(self) -> bool
```

```python
def shutdown(self) -> None
```

```python
def disconnect(self) -> None
```

```python
def update_config(self, config: DryerConfig) -> None
```

```python
def write_data(self, data: DryerWriteData) -> bool
```

```python
def get_state(self) -> DryerState
```

```python
def move_servos(self, data: DryerWriteData | None=None) -> bool
```

```python
def eject(self, data: DryerWriteData | None=None) -> bool
```

```python
def open_plate(self, data: DryerWriteData | None=None) -> bool
```

```python
def close_plate(self, data: DryerWriteData | None=None) -> bool
```

```python
def next_position(self, data: DryerWriteData | None=None) -> bool
```

```python
def execute_command(self, command: int, data: DryerWriteData | None=None) -> bool
```

## `mock_runner.py`

Source: [src/engine/hardware/dryer/mock_runner.py](../../../../src/engine/hardware/dryer/mock_runner.py).

Dryer controller mock runner — manual integration / smoke example. No serial port required. MockDryerTransport intercepts register I/O while the controller is constructed with the same config objects used by real wiring.

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `dataclasses`, `pathlib`, `src.engine.hardware.communication.modbus.modbus`, `src.engine.hardware.dryer.dryer_controller`, `src.engine.hardware.dryer.interfaces.i_dryer_transport`, `src.engine.hardware.dryer.models.dryer_config`, `src.engine.hardware.dryer.models.dryer_status`, `src.engine.hardware.dryer.models.dryer_write_data`, `sys`, `typing`.

### `MockDryerTransport`

```python
class MockDryerTransport(IDryerTransport):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self) -> None
```

```python
def read_register(self, address: int) -> int
```

```python
def write_register(self, address: int, value: int) -> None
```

```python
def write_registers(self, address: int, values: List[int]) -> None
```

```python
def connect(self) -> None
```

```python
def disconnect(self) -> None
```

### `_print_section`

```python
def _print_section(title: str) -> None
```

### `_print_mapping`

```python
def _print_mapping(mapping: Dict[str, Any]) -> None
```

### `_print_dataclass`

```python
def _print_dataclass(title: str, value: Any) -> None
```

### `run_mock`

```python
def run_mock() -> None
```

## `next_position_runner.py`

Source: [src/engine/hardware/dryer/next_position_runner.py](../../../../src/engine/hardware/dryer/next_position_runner.py).

Run and verify consecutive real dryer NEXT_POSITION cycles without the robot. This uses the same Modbus, peripheral/register, command/status, and dryer settings as the paint platform. It requires a fresh movement cycle before accepting DONE. Press Ctrl-C to stop waiting; EJECT is never sent by this runner.

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `argparse`, `json`, `logging`, `pathlib`, `src.engine.hardware.communication.modbus.modbus`, `src.engine.hardware.communication.transport_registry`, `src.engine.hardware.dryer.dryer_controller`, `src.engine.hardware.dryer.models.dryer_config`, `src.engine.hardware.dryer.models.dryer_modbus_registers`, `src.engine.hardware.peripherals`, `sys`, `time`.

Module declarations (expressions are shown without evaluating them):

```python
REPOSITORY_ROOT = Path(__file__).resolve().parents[4]
SETTINGS_ROOT = REPOSITORY_ROOT / 'src/robot_systems/paint/storage/settings'
```

### `_load_json`

```python
def _load_json(path: Path) -> dict
```

### `run_next_position`

```python
def run_next_position(modbus_path: Path, peripherals_path: Path, dryer_settings_path: Path, *, cycles: int, cycle_delay_s: float, acknowledgement_timeout_s: float, poll_interval_s: float) -> bool
```

### `main`

```python
def main() -> int
```

## `read_registers.py`

Source: [src/engine/hardware/dryer/read_registers.py](../../../../src/engine/hardware/dryer/read_registers.py).

Write diagnostic value 2 to address 2, then print all dryer registers. It uses the same Paint Modbus and peripheral settings, transport registry, and dryer register map as the runtime.

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `argparse`, `json`, `pathlib`, `src.engine.hardware.communication.modbus.modbus`, `src.engine.hardware.communication.transport_registry`, `src.engine.hardware.dryer.models.dryer_modbus_registers`, `src.engine.hardware.dryer.models.dryer_status`, `src.engine.hardware.peripherals`, `sys`.

Module declarations (expressions are shown without evaluating them):

```python
REPOSITORY_ROOT = Path(__file__).resolve().parents[4]
DEFAULT_MODBUS_PATH = REPOSITORY_ROOT / 'src/robot_systems/paint/storage/settings/hardware/modbus.json'
DEFAULT_PERIPHERALS_PATH = REPOSITORY_ROOT / 'src/robot_systems/paint/storage/settings/hardware/peripherals.json'
```

### `_load_json`

```python
def _load_json(path: Path) -> dict
```

### `read_all_registers`

```python
def read_all_registers(modbus_path: Path, peripherals_path: Path) -> None
```

### `main`

```python
def main() -> int
```
