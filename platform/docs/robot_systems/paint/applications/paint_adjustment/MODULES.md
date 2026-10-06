# Module reference: `src/robot_systems/paint/applications/paint_adjustment`

[Package guide](README.md) · [Complete source index](../../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [dial_geometry.py](#dial_geometrypy)
- [paint_adjustment_factory.py](#paint_adjustment_factorypy)

## `__init__.py`

Source: [src/robot_systems/paint/applications/paint_adjustment/__init__.py](../../../../../src/robot_systems/paint/applications/paint_adjustment/__init__.py).

Paint-specific auxiliary camera adjustment screen.

Imports (including optional/function-local imports; not a startup dependency list): `.paint_adjustment_factory`, `.service.i_paint_adjustment_service`.

Package-level import/export surface:

```python
from .paint_adjustment_factory import PaintAdjustmentFactory
from .service.i_paint_adjustment_service import IPaintAdjustmentService
```

Module declarations (expressions are shown without evaluating them):

```python
__all__ = ['PaintAdjustmentFactory', 'IPaintAdjustmentService']
```

## `dial_geometry.py`

Source: [src/robot_systems/paint/applications/paint_adjustment/dial_geometry.py](../../../../../src/robot_systems/paint/applications/paint_adjustment/dial_geometry.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`.

### `dial_angle_for_value`

```python
def dial_angle_for_value(value: int, minimum: int, spacing: int, count: int) -> float | None
```

Map a register value to a clockwise dial angle; setting 1 is at top.

### `dial_value_for_angle`

```python
def dial_value_for_angle(angle: float, minimum: int, spacing: int, count: int) -> int
```

Map a pointer angle to a register value, clamping the gap after the last setting.

### `dial_setting_for_value`

```python
def dial_setting_for_value(value: int, minimum: int, spacing: int, count: int) -> float | None
```

Express a register value on the numbered setting scale.

## `paint_adjustment_factory.py`

Source: [src/robot_systems/paint/applications/paint_adjustment/paint_adjustment_factory.py](../../../../../src/robot_systems/paint/applications/paint_adjustment/paint_adjustment_factory.py).

Imports (including optional/function-local imports; not a startup dependency list): `.controller.paint_adjustment_controller`, `.model.paint_adjustment_model`, `.view.paint_adjustment_view`, `src.applications.base.application_factory`.

### `PaintAdjustmentFactory`

```python
class PaintAdjustmentFactory(ApplicationFactory):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self) -> None
```

```python
def build(self, service, messaging=None, jog_service=None)
```
