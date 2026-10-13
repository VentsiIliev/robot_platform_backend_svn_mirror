# Module reference: `src/robot_systems/paint/applications/dashboard/onboarding`

[Package guide](README.md) · [Complete source index](../../../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [paint_dashboard_tour.py](#paint_dashboard_tourpy)

## `__init__.py`

Source: [src/robot_systems/paint/applications/dashboard/onboarding/__init__.py](../../../../../../src/robot_systems/paint/applications/dashboard/onboarding/__init__.py).

Imports (including optional/function-local imports; not a startup dependency list): `src.robot_systems.paint.applications.dashboard.onboarding.paint_dashboard_tour`.

Package-level import/export surface:

```python
from src.robot_systems.paint.applications.dashboard.onboarding.paint_dashboard_tour import build_paint_dashboard_tour
```

Module declarations (expressions are shown without evaluating them):

```python
__all__ = ['build_paint_dashboard_tour']
```

## `paint_dashboard_tour.py`

Source: [src/robot_systems/paint/applications/dashboard/onboarding/paint_dashboard_tour.py](../../../../../../src/robot_systems/paint/applications/dashboard/onboarding/paint_dashboard_tour.py).

Imports (including optional/function-local imports; not a startup dependency list): `PyQt6.QtCore`, `__future__`, `src.applications.base.onboarding`.

### `build_paint_dashboard_tour`

```python
def build_paint_dashboard_tour(view) -> OnboardingTour
```

Build the paint-owned tour on top of the reusable onboarding UI.

### `_translate`

```python
def _translate(source: str) -> str
```
