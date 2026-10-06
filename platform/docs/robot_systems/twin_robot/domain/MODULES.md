# Module reference: `src/robot_systems/twin_robot/domain`

[Package guide](README.md) · [Complete source index](../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [choreography.py](#choreographypy)
- [users.py](#userspy)

## `__init__.py`

Source: [src/robot_systems/twin_robot/domain/__init__.py](../../../../src/robot_systems/twin_robot/domain/__init__.py).

Imports (including optional/function-local imports; not a startup dependency list): `src.robot_systems.twin_robot.domain.choreography`.

Package-level import/export surface:

```python
from src.robot_systems.twin_robot.domain.choreography import ChoreographyDefinition, ChoreographyStep, RobotChoreographyPose, RobotMotionProfile
```

Module declarations (expressions are shown without evaluating them):

```python
__all__ = ['ChoreographyDefinition', 'ChoreographyStep', 'RobotChoreographyPose', 'RobotMotionProfile']
```

## `choreography.py`

Source: [src/robot_systems/twin_robot/domain/choreography.py](../../../../src/robot_systems/twin_robot/domain/choreography.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `dataclasses`, `typing`.

### `_float_list`

```python
def _float_list(values, expected: int) -> List[float]
```

### `RobotChoreographyPose`

```python
@dataclass
class RobotChoreographyPose:
```

Declared fields/defaults:

```python
pose: List[float] = field(default_factory=list)
joints: List[float] = field(default_factory=list)
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
@classmethod
def from_dict(cls, data: Dict[str, Any] | None) -> 'RobotChoreographyPose'
```

```python
def to_dict(self) -> Dict[str, Any]
```

```python
@property
def captured(self) -> bool
```

### `RobotMotionProfile`

```python
@dataclass
class RobotMotionProfile:
```

Motion limits for the segment ending at the owning choreography step.

Declared fields/defaults:

```python
velocity: float = 30.0
acceleration: float = 30.0
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
@classmethod
def from_dict(cls, data: Dict[str, Any] | None) -> 'RobotMotionProfile'
```

```python
def to_dict(self) -> Dict[str, float]
```

### `ChoreographyStep`

```python
@dataclass
class ChoreographyStep:
```

Declared fields/defaults:

```python
name: str
robot1: RobotChoreographyPose = field(default_factory=RobotChoreographyPose)
robot2: RobotChoreographyPose = field(default_factory=RobotChoreographyPose)
robot1_motion: RobotMotionProfile = field(default_factory=RobotMotionProfile)
robot2_motion: RobotMotionProfile = field(default_factory=RobotMotionProfile)
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
@classmethod
def from_dict(cls, data: Dict[str, Any]) -> 'ChoreographyStep'
```

```python
def to_dict(self) -> Dict[str, Any]
```

```python
@property
def complete(self) -> bool
```

### `ChoreographyDefinition`

```python
@dataclass
class ChoreographyDefinition:
```

Declared fields/defaults:

```python
choreography_id: str
name: str
steps: List[ChoreographyStep] = field(default_factory=list)
loop_count: int = 1
VERSION = 1
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
@classmethod
def from_dict(cls, data: Dict[str, Any]) -> 'ChoreographyDefinition'
```

```python
def to_dict(self) -> Dict[str, Any]
```

```python
def validate(self) -> List[str]
```

```python
@property
def start_step(self) -> Optional[ChoreographyStep]
```

## `users.py`

Source: [src/robot_systems/twin_robot/domain/users.py](../../../../src/robot_systems/twin_robot/domain/users.py).

Twin-system account schema for the shared login application.

Imports (including optional/function-local imports; not a startup dependency list): `src.applications.user_management.domain.user_schema`.

### `build_twin_user_schema`

```python
def build_twin_user_schema(role_values: list[str]) -> UserSchema
```
