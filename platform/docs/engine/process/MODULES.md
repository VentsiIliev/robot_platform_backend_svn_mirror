# Module reference: `src/engine/process`

[Package guide](README.md) · [Complete source index](../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [base_process.py](#base_processpy)
- [executable_state_machine.py](#executable_state_machinepy)
- [i_process.py](#i_processpy)
- [process_requirements.py](#process_requirementspy)
- [process_sequence.py](#process_sequencepy)
- [service_health_registry.py](#service_health_registrypy)

## `__init__.py`

Source: [src/engine/process/__init__.py](../../../src/engine/process/__init__.py).

Imports (including optional/function-local imports; not a startup dependency list): `src.engine.process.base_process`, `src.engine.process.i_process`, `src.engine.process.process_requirements`, `src.engine.process.process_sequence`.

Package-level import/export surface:

```python
from src.engine.process.process_requirements import ProcessRequirements
from src.engine.process.i_process import IProcess
from src.engine.process.base_process import BaseProcess
from src.engine.process.process_sequence import ProcessSequence
```

Module declarations (expressions are shown without evaluating them):

```python
__all__ = ['ProcessRequirements', 'IProcess', 'BaseProcess', 'ProcessSequence']
```

## `base_process.py`

Source: [src/engine/process/base_process.py](../../../src/engine/process/base_process.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `logging`, `src.engine.core.i_messaging_service`, `src.engine.process.i_process`, `src.engine.process.process_requirements`, `src.engine.system.i_system_manager`, `src.shared_contracts.events.process_events`, `threading`, `typing`.

### `BaseProcess`

```python
class BaseProcess(IProcess):
```

Thread-safe state machine + broker publishing. Optional ISystemManager enforces single-process exclusivity. Optional ProcessRequirements + service_checker enforces that all required services are available before a RUNNING transition is allowed.

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, process_id: str, messaging: IMessagingService, system_manager: Optional[ISystemManager]=None, requirements: Optional[ProcessRequirements]=None, service_checker: Optional[Callable[[str], bool]]=None)
```

```python
@property
def process_id(self) -> str
```

```python
@property
def state(self) -> ProcessState
```

```python
@property
def requirements(self) -> ProcessRequirements
```

```python
def start(self) -> None
```

```python
def stop(self, message: str='') -> None
```

```python
def pause(self) -> None
```

```python
def resume(self) -> None
```

```python
def reset_errors(self) -> None
```

```python
def set_error(self, message: str='') -> None
```

## `executable_state_machine.py`

Source: [src/engine/process/executable_state_machine.py](../../../src/engine/process/executable_state_machine.py).

Minimal blocking ExecutableStateMachine for the robot calibration pipeline. Provides State, StateRegistry, ExecutableStateMachine, ExecutableStateMachineBuilder.

Imports (including optional/function-local imports; not a startup dependency list): `dataclasses`, `logging`, `time`, `typing`.

### `State`

```python
@dataclass
class State:
```

Declared fields/defaults:

```python
state: Any
handler: Callable
on_enter: Optional[Callable] = field(default=None)
on_exit: Optional[Callable] = field(default=None)
```

### `StateMachineSnapshot`

```python
@dataclass(frozen=True)
class StateMachineSnapshot:
```

Declared fields/defaults:

```python
initial_state: Any
current_state: Any
is_running: bool
step_count: int
last_state: Any = None
last_next_state: Any = None
last_error: Optional[str] = None
last_enter_duration_s: Optional[float] = None
last_handler_duration_s: Optional[float] = None
last_exit_duration_s: Optional[float] = None
last_step_duration_s: Optional[float] = None
```

### `StateRegistry`

```python
class StateRegistry:
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self)
```

```python
def register_state(self, state: State) -> None
```

```python
def get(self, state_enum) -> Optional[State]
```

### `ExecutableStateMachine`

```python
class ExecutableStateMachine:
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, initial_state, transition_rules: Dict[Any, Set[Any]], registry: StateRegistry, context, message_broker=None, state_topic: str=None)
```

```python
@property
def current_state(self)
```

```python
def reset(self) -> None
```

```python
def get_snapshot(self) -> StateMachineSnapshot
```

```python
def stop_execution(self) -> None
```

```python
def step(self) -> bool
```

```python
def start_execution(self, delay: float=0.0) -> None
```

### `ExecutableStateMachineBuilder`

```python
class ExecutableStateMachineBuilder:
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self)
```

```python
def with_initial_state(self, state) -> 'ExecutableStateMachineBuilder'
```

```python
def with_transition_rules(self, rules: Dict) -> 'ExecutableStateMachineBuilder'
```

```python
def with_state_registry(self, registry: StateRegistry) -> 'ExecutableStateMachineBuilder'
```

```python
def with_context(self, context) -> 'ExecutableStateMachineBuilder'
```

```python
def with_message_broker(self, broker) -> 'ExecutableStateMachineBuilder'
```

```python
def with_state_topic(self, topic: str) -> 'ExecutableStateMachineBuilder'
```

```python
def build(self) -> ExecutableStateMachine
```

## `i_process.py`

Source: [src/engine/process/i_process.py](../../../src/engine/process/i_process.py).

Imports (including optional/function-local imports; not a startup dependency list): `abc`, `src.engine.process.process_requirements`, `src.shared_contracts.events.process_events`.

### `IProcess`

```python
class IProcess(ABC):
```

Lifecycle contract for any robot application process. State machine: IDLE → start() → RUNNING RUNNING → pause() → PAUSED RUNNING → stop() → STOPPED PAUSED → start()/resume() → RUNNING PAUSED → stop() → STOPPED STOPPED → start() → RUNNING (restart) ERROR → reset_errors() → IDLE any → set_error() → ERROR

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
@property
@abstractmethod
def process_id(self) -> str
```

```python
@property
@abstractmethod
def state(self) -> ProcessState
```

```python
@property
@abstractmethod
def requirements(self) -> ProcessRequirements
```

```python
@abstractmethod
def start(self) -> None
```

```python
@abstractmethod
def stop(self) -> None
```

```python
@abstractmethod
def pause(self) -> None
```

```python
@abstractmethod
def resume(self) -> None
```

```python
@abstractmethod
def reset_errors(self) -> None
```

## `process_requirements.py`

Source: [src/engine/process/process_requirements.py](../../../src/engine/process/process_requirements.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `dataclasses`, `typing`.

### `ProcessRequirements`

```python
@dataclass(frozen=True)
class ProcessRequirements:
```

Declared fields/defaults:

```python
services: FrozenSet[str] = field(default_factory=frozenset)
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
@classmethod
def requires(cls, *service_names: str) -> ProcessRequirements
```

```python
@classmethod
def none(cls) -> ProcessRequirements
```

```python
def missing_from(self, checker: Callable[[str], bool]) -> List[str]
```

```python
def all_available(self, checker: Callable[[str], bool]) -> bool
```

## `process_sequence.py`

Source: [src/engine/process/process_sequence.py](../../../src/engine/process/process_sequence.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `logging`, `src.engine.core.i_messaging_service`, `src.engine.process.i_process`, `src.shared_contracts.events.process_events`, `threading`, `typing`.

### `ProcessSequence`

```python
class ProcessSequence:
```

Executes a list of IProcess instances in order. On start(): - If current process is PAUSED → resume it - Otherwise → reset index, start from process[0] On natural completion of process[i] (STOPPED state): - Auto-advances to process[i+1].start() - When the last process stops the sequence is done — no further action stop() / pause() always target the currently active process. Cancels any pending auto-advance. Lives in engine/process — has no knowledge of glue, cleaning, or any specific robot application.

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, processes: List[IProcess], messaging: IMessagingService, before_next_start: Optional[Callable[[IProcess, IProcess], bool]]=None) -> None
```

```python
def start(self) -> None
```

```python
def stop(self) -> None
```

```python
def pause(self) -> None
```

```python
def reset_errors(self) -> None
```

```python
@property
def is_running(self) -> bool
```

## `service_health_registry.py`

Source: [src/engine/process/service_health_registry.py](../../../src/engine/process/service_health_registry.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `enum`, `logging`, `src.engine.core.i_health_checkable`, `typing`.

### `ServiceHealthRegistry`

```python
class ServiceHealthRegistry:
```

Maps service names to health check callables. Resolution order when check(name) is called: 1. Explicitly registered callable → called directly 2. Service implements IHealthCheckable → is_healthy() called 3. No check registered, service not health-checkable → False Usage: registry = ServiceHealthRegistry() registry.register("robot", lambda: robot_svc.is_healthy()) registry.register("weight", lambda: weight_svc.is_healthy()) # later passed as service_checker to BaseProcess: GlueProcess(service_checker=registry.check, ...)

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self) -> None
```

```python
def register(self, service_name: Enum, check: Callable[[], bool]) -> ServiceHealthRegistry
```

```python
def register_service(self, service_name: Enum, service: object) -> ServiceHealthRegistry
```

Auto-register a service — uses is_healthy() if IHealthCheckable, else always True.

```python
def check(self, service_name: Enum) -> bool
```
