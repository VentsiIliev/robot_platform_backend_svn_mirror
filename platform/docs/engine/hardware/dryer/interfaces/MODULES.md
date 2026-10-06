# Module reference: `src/engine/hardware/dryer/interfaces`

[Package guide](README.md) · [Complete source index](../../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [i_dryer_controller.py](#i_dryer_controllerpy)
- [i_dryer_service.py](#i_dryer_servicepy)
- [i_dryer_transport.py](#i_dryer_transportpy)

## `__init__.py`

Source: [src/engine/hardware/dryer/interfaces/__init__.py](../../../../../src/engine/hardware/dryer/interfaces/__init__.py).

Imports (including optional/function-local imports; not a startup dependency list): `src.engine.hardware.dryer.interfaces.i_dryer_controller`, `src.engine.hardware.dryer.interfaces.i_dryer_service`, `src.engine.hardware.dryer.interfaces.i_dryer_transport`.

Package-level import/export surface:

```python
from src.engine.hardware.dryer.interfaces.i_dryer_controller import IDryerController
from src.engine.hardware.dryer.interfaces.i_dryer_transport import IDryerTransport
from src.engine.hardware.dryer.interfaces.i_dryer_service import IDryerService
```

Module declarations (expressions are shown without evaluating them):

```python
__all__ = ['IDryerController', 'IDryerTransport', 'IDryerService']
```

## `i_dryer_controller.py`

Source: [src/engine/hardware/dryer/interfaces/i_dryer_controller.py](../../../../../src/engine/hardware/dryer/interfaces/i_dryer_controller.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `abc`, `src.engine.hardware.dryer.models.dryer_config`, `src.engine.hardware.dryer.models.dryer_state`, `src.engine.hardware.dryer.models.dryer_write_data`.

### `IDryerController`

```python
class IDryerController(ABC):
```

High-level dryer controller interface.

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
@abstractmethod
def initialize(self) -> bool
```

Write the current defaults to the dryer and report success.

```python
@abstractmethod
def shutdown(self) -> None
```

Release controller transport resources.

```python
@abstractmethod
def update_config(self, config: DryerConfig) -> None
```

Replace the defaults used by subsequent dryer commands.

```python
@abstractmethod
def write_data(self, data: DryerWriteData) -> bool
```

Write the full dryer command/configuration register block.

```python
@abstractmethod
def get_state(self) -> DryerState
```

Read and decode the dryer status register.

```python
@abstractmethod
def execute_command(self, command: int, data: DryerWriteData | None=None) -> bool
```

Execute a configured numeric dryer command.

```python
@abstractmethod
def move_servos(self, data: DryerWriteData | None=None) -> bool
```

Compatibility alias for eject().

```python
@abstractmethod
def eject(self, data: DryerWriteData | None=None) -> bool
```

Eject the loaded detail.

```python
@abstractmethod
def open_plate(self, data: DryerWriteData | None=None) -> bool
```

Compatibility alias for close_plate().

```python
@abstractmethod
def close_plate(self, data: DryerWriteData | None=None) -> bool
```

Start the close-plate command.

```python
@abstractmethod
def next_position(self, data: DryerWriteData | None=None) -> bool
```

Start the move-to-next-position command.

## `i_dryer_service.py`

Source: [src/engine/hardware/dryer/interfaces/i_dryer_service.py](../../../../../src/engine/hardware/dryer/interfaces/i_dryer_service.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `abc`, `src.engine.core.i_health_checkable`, `src.engine.hardware.dryer.interfaces.i_dryer_controller`.

### `IDryerService`

```python
class IDryerService(IDryerController, IHealthCheckable):
```

Stable lifecycle and command boundary for dryer hardware.

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
@abstractmethod
def enable(self) -> bool
```

Construct and initialize the configured dryer controller.

```python
@abstractmethod
def enable_async(self) -> bool
```

Start controller construction and initialization without blocking.

```python
@abstractmethod
def disable(self) -> None
```

Release dryer hardware resources and reject commands.

```python
@abstractmethod
def is_enabled(self) -> bool
```

Return whether the dryer is enabled or currently initializing.

```python
@abstractmethod
def is_healthy(self) -> bool
```

Return the cached dryer availability without performing I/O.

```python
@property
@abstractmethod
def last_error(self) -> str | None
```

Return the most recent lifecycle or command error.

## `i_dryer_transport.py`

Source: [src/engine/hardware/dryer/interfaces/i_dryer_transport.py](../../../../../src/engine/hardware/dryer/interfaces/i_dryer_transport.py).

Imports (including optional/function-local imports; not a startup dependency list): `src.engine.hardware.communication.i_register_transport`.

### `IDryerTransport`

```python
class IDryerTransport(IRegisterTransport):
```

Semantic type alias — constrains injection sites to dryer-specific transports. All register I/O contracts are inherited from IRegisterTransport.
