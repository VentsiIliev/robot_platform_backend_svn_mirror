# Module reference: `src/robot_systems/twin_robot/storage`

[Package guide](README.md) · [Complete source index](../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [choreography_repository.py](#choreography_repositorypy)

## `__init__.py`

Source: [src/robot_systems/twin_robot/storage/__init__.py](../../../../src/robot_systems/twin_robot/storage/__init__.py).

Imports (including optional/function-local imports; not a startup dependency list): `src.robot_systems.twin_robot.storage.choreography_repository`.

Package-level import/export surface:

```python
from src.robot_systems.twin_robot.storage.choreography_repository import ChoreographyRepository
```

Module declarations (expressions are shown without evaluating them):

```python
__all__ = ['ChoreographyRepository']
```

## `choreography_repository.py`

Source: [src/robot_systems/twin_robot/storage/choreography_repository.py](../../../../src/robot_systems/twin_robot/storage/choreography_repository.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `json`, `os`, `pathlib`, `src.robot_systems.twin_robot.domain`, `typing`.

### `ChoreographyRepository`

```python
class ChoreographyRepository:
```

Simple JSON repository owned by the twin robot system.

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, root_dir: str)
```

```python
def list(self) -> List[ChoreographyDefinition]
```

```python
def get(self, choreography_id: str) -> ChoreographyDefinition
```

```python
def save(self, choreography: ChoreographyDefinition) -> None
```

```python
def delete(self, choreography_id: str) -> None
```
