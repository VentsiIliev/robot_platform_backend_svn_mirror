# Module reference: `src/robot_systems/ROBOT_SYSTEM_BLUEPRINT/processes`

[Package guide](README.md) · [Complete source index](../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [demo_process.py](#demo_processpy)

## `__init__.py`

Source: [src/robot_systems/ROBOT_SYSTEM_BLUEPRINT/processes/__init__.py](../../../../src/robot_systems/ROBOT_SYSTEM_BLUEPRINT/processes/__init__.py).

Imports (including optional/function-local imports; not a startup dependency list): `src.robot_systems.ROBOT_SYSTEM_BLUEPRINT.processes.demo_process`.

Package-level import/export surface:

```python
from src.robot_systems.ROBOT_SYSTEM_BLUEPRINT.processes.demo_process import DemoProcess
```

Module declarations (expressions are shown without evaluating them):

```python
__all__ = ['DemoProcess']
```

## `demo_process.py`

Source: [src/robot_systems/ROBOT_SYSTEM_BLUEPRINT/processes/demo_process.py](../../../../src/robot_systems/ROBOT_SYSTEM_BLUEPRINT/processes/demo_process.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `src.engine.core.i_messaging_service`, `src.engine.process.base_process`, `src.engine.process.process_requirements`, `src.engine.system.i_system_manager`, `src.robot_systems.ROBOT_SYSTEM_BLUEPRINT.component_ids`, `threading`, `typing`.

### `DemoProcess`

```python
class DemoProcess(BaseProcess):
```

Minimal runnable blueprint process. TODO for a real robot system: 1. replace the timer simulation with real coordinator/process work 2. add meaningful ProcessRequirements if specific services must be healthy 3. publish additional domain events if the dashboard needs richer state

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, messaging: IMessagingService, system_manager: Optional[ISystemManager]=None, requirements: Optional[ProcessRequirements]=None, service_checker: Optional[Callable[[str], bool]]=None, simulation_duration_s: float=_SIMULATION_DURATION_S) -> None
```
