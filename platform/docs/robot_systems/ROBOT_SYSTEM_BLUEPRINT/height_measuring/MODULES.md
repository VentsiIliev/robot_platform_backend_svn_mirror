# Module reference: `src/robot_systems/ROBOT_SYSTEM_BLUEPRINT/height_measuring`

[Package guide](README.md) · [Complete source index](../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [mock_laser_control.py](#mock_laser_controlpy)
- [provider.py](#providerpy)

## `__init__.py`

Source: [src/robot_systems/ROBOT_SYSTEM_BLUEPRINT/height_measuring/__init__.py](../../../../src/robot_systems/ROBOT_SYSTEM_BLUEPRINT/height_measuring/__init__.py).

Imports (including optional/function-local imports; not a startup dependency list): `src.robot_systems.ROBOT_SYSTEM_BLUEPRINT.height_measuring.provider`.

Package-level import/export surface:

```python
from src.robot_systems.ROBOT_SYSTEM_BLUEPRINT.height_measuring.provider import MyRobotSystemHeightMeasuringProvider
```

Module declarations (expressions are shown without evaluating them):

```python
__all__ = ['MyRobotSystemHeightMeasuringProvider']
```

## `mock_laser_control.py`

Source: [src/robot_systems/ROBOT_SYSTEM_BLUEPRINT/height_measuring/mock_laser_control.py](../../../../src/robot_systems/ROBOT_SYSTEM_BLUEPRINT/height_measuring/mock_laser_control.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `logging`, `src.engine.hardware.laser`.

### `MockLaserControl`

```python
class MockLaserControl(ILaserControl):
```

Blueprint-safe laser control used until real hardware wiring exists.

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self) -> None
```

```python
def turn_on(self) -> None
```

```python
def turn_off(self) -> None
```

```python
@property
def is_on(self) -> bool
```

## `provider.py`

Source: [src/robot_systems/ROBOT_SYSTEM_BLUEPRINT/height_measuring/provider.py](../../../../src/robot_systems/ROBOT_SYSTEM_BLUEPRINT/height_measuring/provider.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `src.engine.robot.height_measuring`, `src.robot_systems.ROBOT_SYSTEM_BLUEPRINT.height_measuring.mock_laser_control`.

### `MyRobotSystemHeightMeasuringProvider`

```python
class MyRobotSystemHeightMeasuringProvider(RobotSystemHeightMeasuringProvider):
```

Build the system-specific laser-control implementation.

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, robot_system) -> None
```

```python
def build_laser_control(self)
```
