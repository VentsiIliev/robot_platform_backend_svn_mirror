# Module reference: `src/engine/hardware/motor`

[Package guide](README.md) · [Complete source index](../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [mock_runner.py](#mock_runnerpy)
- [motor_cli.py](#motor_clipy)
- [motor_service.py](#motor_servicepy)
- [utils.py](#utilspy)

## `__init__.py`

Source: [src/engine/hardware/motor/__init__.py](../../../../src/engine/hardware/motor/__init__.py).

Imports (including optional/function-local imports; not a startup dependency list): `src.engine.hardware.motor.interfaces.i_motor_error_decoder`, `src.engine.hardware.motor.interfaces.i_motor_service`, `src.engine.hardware.motor.interfaces.i_motor_transport`, `src.engine.hardware.motor.models.motor_config`, `src.engine.hardware.motor.models.motor_state`, `src.engine.hardware.motor.motor_service`.

Package-level import/export surface:

```python
from src.engine.hardware.motor.interfaces.i_motor_service import IMotorService
from src.engine.hardware.motor.interfaces.i_motor_transport import IMotorTransport
from src.engine.hardware.motor.interfaces.i_motor_error_decoder import IMotorErrorDecoder
from src.engine.hardware.motor.models.motor_config import MotorConfig
from src.engine.hardware.motor.models.motor_state import MotorState, MotorsSnapshot
from src.engine.hardware.motor.motor_service import MotorService
```

Module declarations (expressions are shown without evaluating them):

```python
__all__ = ['IMotorService', 'IMotorTransport', 'IMotorErrorDecoder', 'MotorConfig', 'MotorState', 'MotorsSnapshot', 'MotorService']
```

## `mock_runner.py`

Source: [src/engine/hardware/motor/mock_runner.py](../../../../src/engine/hardware/motor/mock_runner.py).

Motor service mock runner — manual integration / smoke test. Run with: python src/engine/hardware/motor/mock_runner.y_pixels No serial port required. MockMotorTransport intercepts all register I/O and prints what would be sent over the wire. Use it to verify MotorService logic, ramp sequences, health-check parsing, and error filtering without any hardware attached. Configurable sections at the bottom of this file: SCENARIO — which scenario to run ADDRESSES — motor addresses to test

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `logging`, `src.engine.hardware.motor.interfaces.i_motor_transport`, `src.engine.hardware.motor.models.motor_config`, `src.engine.hardware.motor.motor_service`, `sys`, `typing`.

### `MockMotorTransport`

```python
class MockMotorTransport(IMotorTransport):
```

In-memory transport. All register writes are recorded; reads return values from a configurable register bank. Attributes set before running a scenario: register_bank – dict[address → int \| list[int]] returned by reads raise_on_write – if True, write_registers raises IOError raise_on_read – if True, reads raise IOError call_log – list of (method, address, value) for assertions

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self) -> None
```

```python
def write_registers(self, address: int, values: List[int]) -> None
```

```python
def read_register(self, address: int) -> int
```

```python
def read_registers(self, address: int, count: int) -> List[int]
```

```python
def connect(self) -> None
```

```python
def disconnect(self) -> None
```

```python
def set_healthy(self) -> None
```

Configure: health check returns 0 errors.

```python
def set_errors(self, error_codes: List[int]) -> None
```

Configure: health check returns given error codes.

```python
def reset(self) -> None
```

### `_section`

```python
def _section(title: str) -> None
```

### `_make_service`

```python
def _make_service(transport: MockMotorTransport) -> MotorService
```

### `scenario_turn_on_off`

```python
def scenario_turn_on_off(t: MockMotorTransport, motor_addr: int=0) -> None
```

Full start-ramp-run-stop sequence for one motor.

### `scenario_persistent_connection`

```python
def scenario_persistent_connection(t: MockMotorTransport, motor_addr: int=0) -> None
```

Open → repeated set_speed (hot path) → close.

### `scenario_health_check_healthy`

```python
def scenario_health_check_healthy(t: MockMotorTransport, motor_addr: int=0) -> None
```

Health check when board reports 0 errors.

### `scenario_health_check_with_errors`

```python
def scenario_health_check_with_errors(t: MockMotorTransport, motor_addr: int, error_codes: List[int]) -> None
```

Health check when board reports specific error codes.

### `scenario_health_check_all`

```python
def scenario_health_check_all(t: MockMotorTransport, motor_addrs: List[int], error_codes: List[int]) -> None
```

Bulk health check across multiple motors.

### `scenario_transport_failure`

```python
def scenario_transport_failure(t: MockMotorTransport, motor_addr: int=0) -> None
```

Verify controller returns False / records comm error on transport failure.

## `motor_cli.py`

Source: [src/engine/hardware/motor/motor_cli.py](../../../../src/engine/hardware/motor/motor_cli.py).

motor_cli.y_pixels — interactive terminal runner for MotorService. Usage: python src/engine/hardware/motor/motor_cli.y_pixels --port COM5 --slave 10 python src/engine/hardware/motor/motor_cli.y_pixels --port /dev/ttyUSB0 --slave 10 --motors 0 2 4 6 Commands (once the REPL starts): open open persistent connection close close persistent connection status show connection state list list configured motor addresses on <addr> [speed] turn motor on (default speed 10000) off <addr> turn motor off speed <addr> <speed> set speed without full start/stop health <addr> health check single motor health_all health check all configured motors help show this list quit / exit / q exit

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `argparse`, `os`, `src.engine.hardware.communication.modbus.modbus`, `src.engine.hardware.motor.modbus.modbus_motor_factory`, `src.engine.hardware.motor.models.motor_config`, `sys`.

### `_build_service`

```python
def _build_service(args)
```

### `_run_repl`

```python
def _run_repl(svc)
```

### `main`

```python
def main()
```

## `motor_service.py`

Source: [src/engine/hardware/motor/motor_service.py](../../../../src/engine/hardware/motor/motor_service.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `logging`, `src.engine.hardware.motor.health.motor_health_checker`, `src.engine.hardware.motor.interfaces.i_motor_error_decoder`, `src.engine.hardware.motor.interfaces.i_motor_service`, `src.engine.hardware.motor.interfaces.i_motor_transport`, `src.engine.hardware.motor.models.motor_config`, `src.engine.hardware.motor.models.motor_state`, `src.engine.hardware.motor.utils`, `time`, `typing`.

### `MotorService`

```python
class MotorService(IMotorService):
```

IMotorService implementation — uses IMotorTransport for all I/O. Has no knowledge of Modbus, serial ports, or any communication protocol.

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, transport: IMotorTransport, config: MotorConfig, error_decoder: Optional[IMotorErrorDecoder]=None) -> None
```

```python
def is_healthy(self) -> bool
```

Returns True when the service has an open connection and is ready for commands.

```python
@property
def motor_addresses(self) -> List[int]
```

The motor addresses declared in this service's MotorConfig.

```python
def open(self) -> None
```

```python
def close(self) -> None
```

```python
def turn_on(self, motor_address: int, speed: int, ramp_steps: int, initial_ramp_speed: int, initial_ramp_speed_duration: float) -> bool
```

```python
def turn_off(self, motor_address: int, speed_reverse: int, reverse_duration: float, ramp_steps: int) -> bool
```

```python
def set_speed(self, motor_address: int, speed: int) -> bool
```

```python
def health_check(self, motor_address: int) -> MotorState
```

```python
def health_check_all(self, motor_addresses: List[int]) -> MotorsSnapshot
```

```python
def health_check_all_configured(self) -> MotorsSnapshot
```

## `utils.py`

Source: [src/engine/hardware/motor/utils.py](../../../../src/engine/hardware/motor/utils.py).

Imports (including optional/function-local imports; not a startup dependency list): `typing`.

### `split_into_16bit`

```python
def split_into_16bit(value: int) -> Tuple[int, int]
```

Split a signed integer into two 16-bit unsigned halves for Modbus register writes. Returns (high16, low16).

### `int_to_hex32`

```python
def int_to_hex32(value: int) -> str
```
