# Module reference: `src/engine/system`

[Package guide](README.md) · [Complete source index](../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [i_system_manager.py](#i_system_managerpy)
- [system_manager.py](#system_managerpy)
- [system_state.py](#system_statepy)

## `__init__.py`

Source: [src/engine/system/__init__.py](../../../src/engine/system/__init__.py).

Imports (including optional/function-local imports; not a startup dependency list): `src.engine.system.i_system_manager`, `src.engine.system.system_manager`, `src.engine.system.system_state`.

Package-level import/export surface:

```python
from src.engine.system.system_state import SystemBusyState, SystemStateEvent, SystemTopics
from src.engine.system.i_system_manager import ISystemManager
from src.engine.system.system_manager import SystemManager
```

Module declarations (expressions are shown without evaluating them):

```python
__all__ = ['SystemBusyState', 'SystemStateEvent', 'SystemTopics', 'ISystemManager', 'SystemManager']
```

## `i_system_manager.py`

Source: [src/engine/system/i_system_manager.py](../../../src/engine/system/i_system_manager.py).

Imports (including optional/function-local imports; not a startup dependency list): `abc`, `src.engine.system`, `typing`.

### `ISystemManager`

```python
class ISystemManager(ABC):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
@property
@abstractmethod
def is_busy(self) -> bool
```

```python
@property
@abstractmethod
def active_process_id(self) -> Optional[str]
```

```python
@property
@abstractmethod
def state(self) -> SystemBusyState
```

```python
@abstractmethod
def acquire(self, process_id: str) -> bool
```

```python
@abstractmethod
def release(self, process_id: str) -> None
```

## `system_manager.py`

Source: [src/engine/system/system_manager.py](../../../src/engine/system/system_manager.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `logging`, `src.engine.core.i_messaging_service`, `src.engine.system.i_system_manager`, `src.engine.system.system_state`, `threading`, `typing`.

### `SystemManager`

```python
class SystemManager(ISystemManager):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, messaging: IMessagingService)
```

```python
@property
def is_busy(self) -> bool
```

```python
@property
def active_process_id(self) -> Optional[str]
```

```python
@property
def state(self) -> SystemBusyState
```

```python
def acquire(self, process_id: str) -> bool
```

```python
def release(self, process_id: str) -> None
```

## `system_state.py`

Source: [src/engine/system/system_state.py](../../../src/engine/system/system_state.py).

Imports (including optional/function-local imports; not a startup dependency list): `dataclasses`, `datetime`, `enum`, `typing`.

### `SystemBusyState`

```python
class SystemBusyState(Enum):
```

Declared fields/defaults:

```python
IDLE = 'idle'
BUSY = 'busy'
```

### `SystemStateEvent`

```python
@dataclass(frozen=True)
class SystemStateEvent:
```

Declared fields/defaults:

```python
state: SystemBusyState
active_process: Optional[str]
message: str = ''
timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
```

### `SystemTopics`

```python
class SystemTopics:
```

Declared fields/defaults:

```python
STATE = 'vision_service/state'
```
