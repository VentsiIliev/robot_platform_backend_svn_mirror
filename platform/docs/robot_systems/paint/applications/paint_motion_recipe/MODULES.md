# Module reference: `src/robot_systems/paint/applications/paint_motion_recipe`

[Package guide](README.md) · [Complete source index](../../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [paint_motion_recipe_factory.py](#paint_motion_recipe_factorypy)

## `__init__.py`

Source: [src/robot_systems/paint/applications/paint_motion_recipe/__init__.py](../../../../../src/robot_systems/paint/applications/paint_motion_recipe/__init__.py).

Imports (including optional/function-local imports; not a startup dependency list): `src.robot_systems.paint.applications.paint_motion_recipe.paint_motion_recipe_factory`.

Package-level import/export surface:

```python
from src.robot_systems.paint.applications.paint_motion_recipe.paint_motion_recipe_factory import PaintMotionRecipeFactory
```

Module declarations (expressions are shown without evaluating them):

```python
__all__ = ['PaintMotionRecipeFactory']
```

## `paint_motion_recipe_factory.py`

Source: [src/robot_systems/paint/applications/paint_motion_recipe/paint_motion_recipe_factory.py](../../../../../src/robot_systems/paint/applications/paint_motion_recipe/paint_motion_recipe_factory.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `src.applications.base.application_factory`, `src.robot_systems.paint.applications.paint_motion_recipe.controller.paint_motion_recipe_controller`, `src.robot_systems.paint.applications.paint_motion_recipe.model.paint_motion_recipe_model`, `src.robot_systems.paint.applications.paint_motion_recipe.service.i_paint_motion_recipe_service`, `src.robot_systems.paint.applications.paint_motion_recipe.view.paint_motion_recipe_view`.

### `PaintMotionRecipeFactory`

```python
class PaintMotionRecipeFactory(ApplicationFactory):
```
