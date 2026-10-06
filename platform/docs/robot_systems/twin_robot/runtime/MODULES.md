# Module reference: `src/robot_systems/twin_robot/runtime`

[Package guide](README.md) · [Complete source index](../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [i_twin_choreography_runtime.py](#i_twin_choreography_runtimepy)

## `__init__.py`

Source: [src/robot_systems/twin_robot/runtime/__init__.py](../../../../src/robot_systems/twin_robot/runtime/__init__.py).

Imports (including optional/function-local imports; not a startup dependency list): `src.robot_systems.twin_robot.runtime.i_twin_choreography_runtime`.

Package-level import/export surface:

```python
from src.robot_systems.twin_robot.runtime.i_twin_choreography_runtime import ITwinChoreographyRuntime
```

Module declarations (expressions are shown without evaluating them):

```python
__all__ = ['ITwinChoreographyRuntime']
```

## `i_twin_choreography_runtime.py`

Source: [src/robot_systems/twin_robot/runtime/i_twin_choreography_runtime.py](../../../../src/robot_systems/twin_robot/runtime/i_twin_choreography_runtime.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `abc`, `typing`.

### `ITwinChoreographyRuntime`

```python
class ITwinChoreographyRuntime(ABC):
```

Transport-neutral runtime contract used by TwinRobotSystem. The platform owns choreography authoring/orchestration. The concrete robot stack owns planning, timing synchronization and controller execution.

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
@abstractmethod
def robot(self, robot_name: str) -> Any
```

Return the robot-scoped gateway used for jog/state operations.

```python
@abstractmethod
def prepare_choreography(self, choreography) -> Any
```

Plan both robots without executing either trajectory. The result must expose ``robot1_ready`` and ``robot2_ready`` (attributes or dict keys) and retain the two prepared trajectories plus their exact start-joint anchors.

```python
@abstractmethod
def execute_prepared(self, prepared, loop_count: int=1)
```

Execute an already prepared pair only after both sides are ready. Implementations are responsible for moving both robots to the exact saved start-joint anchors, verifying the branch anchors, releasing both controller goals through the synchronization barrier, and reusing the same prepared pair for subsequent loops.

```python
@abstractmethod
def stop(self)
```

Request controlled stop of both robots.
