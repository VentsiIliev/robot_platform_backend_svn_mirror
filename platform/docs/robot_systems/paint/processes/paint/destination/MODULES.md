# Module reference: `src/robot_systems/paint/processes/paint/destination`

[Package guide](README.md) · [Complete source index](../../../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [i_workpiece_destination.py](#i_workpiece_destinationpy)
- [pass_through_destination.py](#pass_through_destinationpy)

## `__init__.py`

Source: [src/robot_systems/paint/processes/paint/destination/__init__.py](../../../../../../src/robot_systems/paint/processes/paint/destination/__init__.py).

Imports (including optional/function-local imports; not a startup dependency list): `.i_workpiece_destination`, `.pass_through_destination`.

Package-level import/export surface:

```python
from .i_workpiece_destination import IWorkpieceDestination
from .pass_through_destination import PassThroughWorkpieceDestination
```

Module declarations (expressions are shown without evaluating them):

```python
__all__ = ['IWorkpieceDestination', 'PassThroughWorkpieceDestination']
```

## `i_workpiece_destination.py`

Source: [src/robot_systems/paint/processes/paint/destination/i_workpiece_destination.py](../../../../../../src/robot_systems/paint/processes/paint/destination/i_workpiece_destination.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `abc`.

### `IWorkpieceDestination`

```python
class IWorkpieceDestination(ABC):
```

Machine-specific handoff performed around verified workpiece release.

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
@abstractmethod
def check_ready_for_release(self) -> tuple[bool, str]
```

Return whether the destination can accept the next workpiece.

```python
@abstractmethod
def on_release_verified(self) -> bool
```

Handle a workpiece after the robot has verified its release.

## `pass_through_destination.py`

Source: [src/robot_systems/paint/processes/paint/destination/pass_through_destination.py](../../../../../../src/robot_systems/paint/processes/paint/destination/pass_through_destination.py).

Imports (including optional/function-local imports; not a startup dependency list): `.i_workpiece_destination`, `__future__`.

### `PassThroughWorkpieceDestination`

```python
class PassThroughWorkpieceDestination(IWorkpieceDestination):
```

Destination for cells that need no external handoff coordination.

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def check_ready_for_release(self) -> tuple[bool, str]
```

```python
def on_release_verified(self) -> bool
```
