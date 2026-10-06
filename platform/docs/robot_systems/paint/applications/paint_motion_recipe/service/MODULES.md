# Module reference: `src/robot_systems/paint/applications/paint_motion_recipe/service`

[Package guide](README.md) · [Complete source index](../../../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [i_paint_motion_recipe_service.py](#i_paint_motion_recipe_servicepy)
- [paint_motion_recipe_service.py](#paint_motion_recipe_servicepy)
- [stub_paint_motion_recipe_service.py](#stub_paint_motion_recipe_servicepy)

## `__init__.py`

Source: [src/robot_systems/paint/applications/paint_motion_recipe/service/__init__.py](../../../../../../src/robot_systems/paint/applications/paint_motion_recipe/service/__init__.py).

Imports (including optional/function-local imports; not a startup dependency list): `src.robot_systems.paint.applications.paint_motion_recipe.service.i_paint_motion_recipe_service`, `src.robot_systems.paint.applications.paint_motion_recipe.service.paint_motion_recipe_service`, `src.robot_systems.paint.applications.paint_motion_recipe.service.stub_paint_motion_recipe_service`.

Package-level import/export surface:

```python
from src.robot_systems.paint.applications.paint_motion_recipe.service.i_paint_motion_recipe_service import IPaintMotionRecipeService
from src.robot_systems.paint.applications.paint_motion_recipe.service.paint_motion_recipe_service import PaintMotionRecipeService
from src.robot_systems.paint.applications.paint_motion_recipe.service.stub_paint_motion_recipe_service import StubPaintMotionRecipeService
```

Module declarations (expressions are shown without evaluating them):

```python
__all__ = ['IPaintMotionRecipeService', 'PaintMotionRecipeService', 'StubPaintMotionRecipeService']
```

## `i_paint_motion_recipe_service.py`

Source: [src/robot_systems/paint/applications/paint_motion_recipe/service/i_paint_motion_recipe_service.py](../../../../../../src/robot_systems/paint/applications/paint_motion_recipe/service/i_paint_motion_recipe_service.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `abc`, `src.robot_systems.paint.applications.paint_motion_recipe.domain.recipe`.

### `IPaintMotionRecipeService`

```python
class IPaintMotionRecipeService(ABC):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
@abstractmethod
def load_recipe(self) -> MotionRecipe
```

```python
@abstractmethod
def save_recipe(self, recipe: MotionRecipe) -> None
```

```python
@abstractmethod
def get_group_ids(self) -> list[str]
```

```python
@abstractmethod
def get_group_pose(self, group_id: str) -> Pose6D | None
```

```python
@abstractmethod
def capture_current_pose(self) -> Pose6D
```

```python
@abstractmethod
def test_step(self, step: MotionRecipeStep) -> tuple[bool, str]
```

## `paint_motion_recipe_service.py`

Source: [src/robot_systems/paint/applications/paint_motion_recipe/service/paint_motion_recipe_service.py](../../../../../../src/robot_systems/paint/applications/paint_motion_recipe/service/paint_motion_recipe_service.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `json`, `logging`, `os`, `pathlib`, `src.robot_systems.paint.applications.paint_motion_recipe.domain.recipe`, `src.robot_systems.paint.applications.paint_motion_recipe.service.i_paint_motion_recipe_service`, `typing`.

### `PaintMotionRecipeService`

```python
class PaintMotionRecipeService(IPaintMotionRecipeService):
```

Developer-only recipe storage and mock motion tester.

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, *, recipe_path: str, group_ids: Iterable[str]=(), navigation_service=None, initial_mock_pose: Pose6D | None=None) -> None
```

```python
def load_recipe(self) -> MotionRecipe
```

```python
def save_recipe(self, recipe: MotionRecipe) -> None
```

```python
def get_group_ids(self) -> list[str]
```

```python
def get_group_pose(self, group_id: str) -> Pose6D | None
```

```python
def capture_current_pose(self) -> Pose6D
```

```python
def test_step(self, step: MotionRecipeStep) -> tuple[bool, str]
```

## `stub_paint_motion_recipe_service.py`

Source: [src/robot_systems/paint/applications/paint_motion_recipe/service/stub_paint_motion_recipe_service.py](../../../../../../src/robot_systems/paint/applications/paint_motion_recipe/service/stub_paint_motion_recipe_service.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `src.robot_systems.paint.applications.paint_motion_recipe.domain.recipe`, `src.robot_systems.paint.applications.paint_motion_recipe.service.i_paint_motion_recipe_service`.

### `StubPaintMotionRecipeService`

```python
class StubPaintMotionRecipeService(IPaintMotionRecipeService):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self) -> None
```

```python
def load_recipe(self) -> MotionRecipe
```

```python
def save_recipe(self, recipe: MotionRecipe) -> None
```

```python
def get_group_ids(self) -> list[str]
```

```python
def get_group_pose(self, group_id: str) -> Pose6D | None
```

```python
def capture_current_pose(self) -> Pose6D
```

```python
def test_step(self, step: MotionRecipeStep) -> tuple[bool, str]
```
