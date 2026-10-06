# Module reference: `src/engine/hardware/motor/interfaces`

[Package guide](README.md) · [Complete source index](../../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [i_motor_error_decoder.py](#i_motor_error_decoderpy)
- [i_motor_service.py](#i_motor_servicepy)
- [i_motor_transport.py](#i_motor_transportpy)

## `__init__.py`

Source: [src/engine/hardware/motor/interfaces/__init__.py](../../../../../src/engine/hardware/motor/interfaces/__init__.py).

No top-level functions, classes or public value declarations; inspect the source for imports or entry-point statements.

## `i_motor_error_decoder.py`

Source: [src/engine/hardware/motor/interfaces/i_motor_error_decoder.py](../../../../../src/engine/hardware/motor/interfaces/i_motor_error_decoder.py).

Imports (including optional/function-local imports; not a startup dependency list): `abc`.

### `IMotorErrorDecoder`

```python
class IMotorErrorDecoder(ABC):
```

Maps driver-specific integer error codes to human-readable descriptions. Implement one per motor controller board/firmware variant. Inject into MotorHealthChecker — the health check logic stays generic.

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
@abstractmethod
def decode(self, error_code: int) -> str
```

Return a description for the given error code. Never raises.

## `i_motor_service.py`

Source: [src/engine/hardware/motor/interfaces/i_motor_service.py](../../../../../src/engine/hardware/motor/interfaces/i_motor_service.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `abc`, `src.engine.core.i_health_checkable`, `src.engine.hardware.motor.models.motor_state`, `typing`.

### `IMotorService`

```python
class IMotorService(IHealthCheckable):
```

High-level motor command interface — communication-agnostic. Can be implemented over Modbus RTU, CAN bus, simulated drivers, etc. open()/close() provide a persistent connection lifetime for hot-path callers (e.g. continuous speed adjustment during glue dispensing). is_healthy() reports whether the service is connected and ready.

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def open(self) -> None
```

Open a persistent connection. No-op if transport manages connections internally.

```python
def close(self) -> None
```

Close the persistent connection.

```python
@abstractmethod
def turn_on(self, motor_address: int, speed: int, ramp_steps: int, initial_ramp_speed: int, initial_ramp_speed_duration: float) -> bool
```

```python
@abstractmethod
def turn_off(self, motor_address: int, speed_reverse: int, reverse_duration: float, ramp_steps: int) -> bool
```

```python
@abstractmethod
def set_speed(self, motor_address: int, speed: int) -> bool
```

Adjust speed without full start/stop sequence. Uses persistent connection if open.

```python
@abstractmethod
def health_check(self, motor_address: int) -> MotorState
```

Query the board for errors on a single motor. Does I/O — not a connection check.

```python
@abstractmethod
def health_check_all(self, motor_addresses: List[int]) -> MotorsSnapshot
```

Query the board for errors on a specific subset of motors.

```python
@abstractmethod
def health_check_all_configured(self) -> MotorsSnapshot
```

Query the board for errors on all motors declared in this service's config.

## `i_motor_transport.py`

Source: [src/engine/hardware/motor/interfaces/i_motor_transport.py](../../../../../src/engine/hardware/motor/interfaces/i_motor_transport.py).

Imports (including optional/function-local imports; not a startup dependency list): `src.engine.hardware.communication.i_register_transport`.

### `IMotorTransport`

```python
class IMotorTransport(IRegisterTransport):
```

Semantic type alias — constrains injection sites to motor-specific transports. All register I/O contract is inherited from IRegisterTransport.
