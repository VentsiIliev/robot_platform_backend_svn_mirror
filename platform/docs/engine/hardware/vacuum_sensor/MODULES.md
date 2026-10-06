# Module reference: `src/engine/hardware/vacuum_sensor`

[Package guide](README.md) · [Complete source index](../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [dummy_vacuum_sensor_transport.py](#dummy_vacuum_sensor_transportpy)
- [mock_runner.py](#mock_runnerpy)
- [vacuum_sensor_service.py](#vacuum_sensor_servicepy)

## `__init__.py`

Source: [src/engine/hardware/vacuum_sensor/__init__.py](../../../../src/engine/hardware/vacuum_sensor/__init__.py).

Imports (including optional/function-local imports; not a startup dependency list): `src.engine.hardware.vacuum_sensor.dummy_vacuum_sensor_transport`, `src.engine.hardware.vacuum_sensor.interfaces.i_vacuum_sensor_service`, `src.engine.hardware.vacuum_sensor.interfaces.i_vacuum_sensor_transport`, `src.engine.hardware.vacuum_sensor.modbus.modbus_vacuum_sensor_factory`, `src.engine.hardware.vacuum_sensor.modbus.modbus_vacuum_sensor_transport`, `src.engine.hardware.vacuum_sensor.models.vacuum_sensor_config`, `src.engine.hardware.vacuum_sensor.vacuum_sensor_service`.

Package-level import/export surface:

```python
from src.engine.hardware.vacuum_sensor.dummy_vacuum_sensor_transport import DummyVacuumSensorTransport
from src.engine.hardware.vacuum_sensor.interfaces.i_vacuum_sensor_service import IVacuumSensorService
from src.engine.hardware.vacuum_sensor.interfaces.i_vacuum_sensor_transport import IVacuumSensorTransport
from src.engine.hardware.vacuum_sensor.models.vacuum_sensor_config import VacuumSensorConfig
from src.engine.hardware.vacuum_sensor.modbus.modbus_vacuum_sensor_factory import build_modbus_vacuum_sensor_service
from src.engine.hardware.vacuum_sensor.modbus.modbus_vacuum_sensor_transport import ModbusVacuumSensorTransport
from src.engine.hardware.vacuum_sensor.vacuum_sensor_service import VacuumSensorService
```

Module declarations (expressions are shown without evaluating them):

```python
__all__ = ['DummyVacuumSensorTransport', 'IVacuumSensorService', 'IVacuumSensorTransport', 'ModbusVacuumSensorTransport', 'VacuumSensorConfig', 'VacuumSensorService', 'build_modbus_vacuum_sensor_service']
```

## `dummy_vacuum_sensor_transport.py`

Source: [src/engine/hardware/vacuum_sensor/dummy_vacuum_sensor_transport.py](../../../../src/engine/hardware/vacuum_sensor/dummy_vacuum_sensor_transport.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `logging`, `src.engine.hardware.vacuum_sensor.interfaces.i_vacuum_sensor_transport`, `threading`.

### `DummyVacuumSensorTransport`

```python
class DummyVacuumSensorTransport(IVacuumSensorTransport):
```

Simulated vacuum-sensor transport for testing and manual simulation. Every read is logged so you can observe what the service asks for. Toggle `simulated_value` to simulate vacuum present (e.g. 1) or absent (0), and set `raise_on_read = True` to simulate a dead/failed sensor. - simulated_value: int — the value returned by read_register(). - raise_on_read: bool — if True, every read raises IOError. - call_log: list — ("read_register", address, value) per call.

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, simulated_value: int=0) -> None
```

```python
def read_register(self, address: int) -> int
```

```python
def set_simulated_value(self, value: int) -> None
```

```python
def set_vacuum_detected(self, detected: bool, *, detected_value: int=1, clear_value: int=0) -> None
```

## `mock_runner.py`

Source: [src/engine/hardware/vacuum_sensor/mock_runner.py](../../../../src/engine/hardware/vacuum_sensor/mock_runner.py).

Imports (including optional/function-local imports; not a startup dependency list): `PyQt6.QtCore`, `PyQt6.QtWidgets`, `__future__`, `json`, `logging`, `os`, `pathlib`, `src.engine.hardware.communication.modbus.modbus`, `src.engine.hardware.communication.transport_registry`, `src.engine.hardware.peripherals`, `src.engine.hardware.vacuum_sensor.models.vacuum_sensor_config`, `src.engine.hardware.vacuum_sensor.vacuum_sensor_service`, `src.engine.hardware.xinje`, `sys`, `time`.

Module declarations (expressions are shown without evaluating them):

```python
ROOT = Path(__file__).resolve().parents[4]
TRAY_DRY_STORAGE = ROOT / 'src' / 'robot_systems' / 'paint' / 'profiles' / 'tray_dryer' / 'storage'
MODBUS_CONFIG_PATH = TRAY_DRY_STORAGE / 'settings' / 'hardware' / 'modbus.json'
PERIPHERALS_CONFIG_PATH = TRAY_DRY_STORAGE / 'settings' / 'hardware' / 'peripherals.json'
READ_RETRIES = 3
READ_COUNT = 100000
READ_DELAY_S = 0.1
```

### `_build_sensor`

```python
def _build_sensor() -> tuple[VacuumSensorService, object, str, int, object]
```

### `_load_modbus_config`

```python
def _load_modbus_config(path: Path) -> ModbusConfig
```

### `_load_peripherals`

```python
def _load_peripherals(path: Path) -> PeripheralConfig
```

### `_build_transport`

```python
def _build_transport(config: ModbusConfig, slave_id: int)
```

### `run_real_sensor`

```python
def run_real_sensor() -> None
```

### `SensorMonitorWindow`

```python
class SensorMonitorWindow(QWidget):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, service: VacuumSensorService, transport: object) -> None
```

```python
def closeEvent(self, event) -> None
```

### `run_gui`

```python
def run_gui() -> None
```

## `vacuum_sensor_service.py`

Source: [src/engine/hardware/vacuum_sensor/vacuum_sensor_service.py](../../../../src/engine/hardware/vacuum_sensor/vacuum_sensor_service.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `logging`, `src.engine.hardware.vacuum_sensor.interfaces.i_vacuum_sensor_service`, `src.engine.hardware.vacuum_sensor.interfaces.i_vacuum_sensor_transport`, `src.engine.hardware.vacuum_sensor.models.vacuum_sensor_config`, `src.engine.hardware.xinje`, `time`.

### `VacuumSensorService`

```python
class VacuumSensorService(IVacuumSensorService):
```

IVacuumSensorService implementation — reads a register via IVacuumSensorTransport. Answers one question: is_vacuum_detected(). A read failure is treated as "no vacuum" (fail-safe) and is reflected in the is_healthy() flag.

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, transport: IVacuumSensorTransport, config: VacuumSensorConfig) -> None
```

```python
def is_vacuum_detected(self) -> bool
```

```python
def get_read_diagnostics(self) -> dict[str, object] | None
```

Return a snapshot of measured sensor I/O, without performing I/O.

```python
def close(self) -> None
```

Release the sensor's persistent transport connection.

```python
@property
def last_raw_value(self) -> int | None
```

Raw value returned by the most recent read, if any.

```python
def is_healthy(self) -> bool
```

True when the last sensor read succeeded. No I/O.
