# Module reference: `tests/robot_systems/twin_robot`

[Package guide](README.md) · [Complete source index](../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [test_choreography.py](#test_choreographypy)

## `__init__.py`

Source: [tests/robot_systems/twin_robot/__init__.py](../../../../tests/robot_systems/twin_robot/__init__.py).

No top-level functions, classes or public value declarations; inspect the source for imports or entry-point statements.

## `test_choreography.py`

Source: [tests/robot_systems/twin_robot/test_choreography.py](../../../../tests/robot_systems/twin_robot/test_choreography.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `src.robot_systems.twin_robot.domain`, `src.robot_systems.twin_robot.storage`, `tempfile`, `unittest`.

### `ChoreographyDefinitionTests`

```python
class ChoreographyDefinitionTests(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_start_step_requires_exact_joint_anchors(self)
```

```python
def test_complete_choreography_round_trips_through_json_repository(self)
```
