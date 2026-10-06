# Module reference: `src/engine/hardware/vacuum_pump/interfaces`

[Package guide](README.md) · [Complete source index](../../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [i_vacuum_pump_controller.py](#i_vacuum_pump_controllerpy)
- [i_vacuum_pump_transport.py](#i_vacuum_pump_transportpy)

## `__init__.py`

Source: [src/engine/hardware/vacuum_pump/interfaces/__init__.py](../../../../../src/engine/hardware/vacuum_pump/interfaces/__init__.py).

No top-level functions, classes or public value declarations; inspect the source for imports or entry-point statements.

## `i_vacuum_pump_controller.py`

Source: [src/engine/hardware/vacuum_pump/interfaces/i_vacuum_pump_controller.py](../../../../../src/engine/hardware/vacuum_pump/interfaces/i_vacuum_pump_controller.py).

Imports (including optional/function-local imports; not a startup dependency list): `abc`.

### `IVacuumPumpController`

```python
class IVacuumPumpController(ABC):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
@abstractmethod
def turn_on(self) -> bool
```

```python
@abstractmethod
def turn_off(self) -> bool
```

```python
def turn_off_nonblocking(self) -> bool
```

Turn the pump off without waiting for an optional blow-off pulse. Controllers without asynchronous pulse support retain the safe, blocking behavior.

```python
def read_state(self) -> bool
```

Read the configured hardware output without changing it.

```python
def close(self) -> None
```

Release any transport resources held by the controller.

## `i_vacuum_pump_transport.py`

Source: [src/engine/hardware/vacuum_pump/interfaces/i_vacuum_pump_transport.py](../../../../../src/engine/hardware/vacuum_pump/interfaces/i_vacuum_pump_transport.py).

Imports (including optional/function-local imports; not a startup dependency list): `src.engine.hardware.communication.i_register_transport`.

### `IVacuumPumpTransport`

```python
class IVacuumPumpTransport(IRegisterTransport):
```

Semantic type alias — constrains injection sites to vacuum-pump-specific transports. All register I/O contract is inherited from IRegisterTransport.
