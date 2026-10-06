# Module reference: `src/robot_systems/paint/applications/paint_motion_recipe/model`

[Package guide](README.md) · [Complete source index](../../../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [paint_motion_recipe_model.py](#paint_motion_recipe_modelpy)

## `__init__.py`

Source: [src/robot_systems/paint/applications/paint_motion_recipe/model/__init__.py](../../../../../../src/robot_systems/paint/applications/paint_motion_recipe/model/__init__.py).

Imports (including optional/function-local imports; not a startup dependency list): `src.robot_systems.paint.applications.paint_motion_recipe.model.paint_motion_recipe_model`.

Package-level import/export surface:

```python
from src.robot_systems.paint.applications.paint_motion_recipe.model.paint_motion_recipe_model import PaintMotionRecipeModel
```

Module declarations (expressions are shown without evaluating them):

```python
__all__ = ['PaintMotionRecipeModel']
```

## `paint_motion_recipe_model.py`

Source: [src/robot_systems/paint/applications/paint_motion_recipe/model/paint_motion_recipe_model.py](../../../../../../src/robot_systems/paint/applications/paint_motion_recipe/model/paint_motion_recipe_model.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `dataclasses`, `src.applications.base.i_application_model`, `src.robot_systems.paint.applications.paint_motion_recipe.domain.recipe`, `src.robot_systems.paint.applications.paint_motion_recipe.service.i_paint_motion_recipe_service`.

### `PaintMotionRecipeModel`

```python
class PaintMotionRecipeModel(IApplicationModel):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, service: IPaintMotionRecipeService) -> None
```

```python
def load(self) -> MotionRecipe
```

```python
def save(self, _data=None) -> None
```

```python
@property
def recipe(self) -> MotionRecipe
```

```python
@property
def group_ids(self) -> list[str]
```

```python
def add_group_step(self, *, label: str, action: str, group_id: str) -> MotionRecipe
```

```python
def add_captured_pose_step(self, *, label: str) -> MotionRecipe
```

```python
def remove_step(self, index: int) -> MotionRecipe
```

```python
def move_step(self, index: int, delta: int) -> MotionRecipe
```

```python
def toggle_step(self, index: int, enabled: bool) -> MotionRecipe
```

```python
def test_step(self, index: int) -> tuple[bool, str]
```
