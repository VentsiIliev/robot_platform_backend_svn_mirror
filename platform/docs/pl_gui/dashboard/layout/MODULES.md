# Module reference: `pl_gui/dashboard/layout`

[Package guide](README.md) · [Complete source index](../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [layout_manager.py](#layout_managerpy)

## `__init__.py`

Source: [pl_gui/dashboard/layout/__init__.py](../../../../pl_gui/dashboard/layout/__init__.py).

No top-level functions, classes or public value declarations; inspect the source for imports or entry-point statements.

## `layout_manager.py`

Source: [pl_gui/dashboard/layout/layout_manager.py](../../../../pl_gui/dashboard/layout/layout_manager.py).

Imports (including optional/function-local imports; not a startup dependency list): `PyQt6.QtCore`, `PyQt6.QtWidgets`, `dashboard.styles`, `pl_gui.dashboard.resources.styles`, `pl_gui.utils.utils_widgets.MaterialButton`, `typing`.

### `DashboardLayoutManager`

```python
class DashboardLayoutManager:
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, parent_widget: QWidget, config)
```

```python
def setup_complete_layout(self, trajectory_widget, glue_cards: List[QWidget], control_buttons: QWidget, action_buttons: List[MaterialButton]) -> None
```
