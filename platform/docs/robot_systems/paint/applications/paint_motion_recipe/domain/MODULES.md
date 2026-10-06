# Module reference: `src/robot_systems/paint/applications/paint_motion_recipe/domain`

[Package guide](README.md) · [Complete source index](../../../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [recipe.py](#recipepy)

## `recipe.py`

Source: [src/robot_systems/paint/applications/paint_motion_recipe/domain/recipe.py](../../../../../../src/robot_systems/paint/applications/paint_motion_recipe/domain/recipe.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `dataclasses`, `typing`, `uuid`.

Module declarations (expressions are shown without evaluating them):

```python
Pose6D = list[float]
```

### `MotionRecipeStep`

```python
@dataclass(frozen=True)
class MotionRecipeStep:
```

Declared fields/defaults:

```python
id: str
label: str
action: str
group_id: str = ''
pose: Pose6D | None = None
enabled: bool = True
note: str = ''
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
@staticmethod
def new(*, label: str, action: str, group_id: str='', pose: Pose6D | None=None, enabled: bool=True, note: str='') -> 'MotionRecipeStep'
```

```python
@staticmethod
def from_dict(data: dict[str, Any]) -> 'MotionRecipeStep'
```

```python
def to_dict(self) -> dict[str, Any]
```

### `MotionRecipe`

```python
@dataclass(frozen=True)
class MotionRecipe:
```

Declared fields/defaults:

```python
name: str = 'Paint Development Recipe'
mock_only: bool = True
steps: tuple[MotionRecipeStep, ...] = field(default_factory=tuple)
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
@staticmethod
def default() -> 'MotionRecipe'
```

```python
@staticmethod
def from_dict(data: dict[str, Any]) -> 'MotionRecipe'
```

```python
def to_dict(self) -> dict[str, Any]
```

### `_normalize_pose`

```python
def _normalize_pose(value) -> Pose6D | None
```
