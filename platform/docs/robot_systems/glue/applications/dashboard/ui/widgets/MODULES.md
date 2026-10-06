# Module reference: `src/robot_systems/glue/applications/dashboard/ui/widgets`

[Package guide](README.md) · [Complete source index](../../../../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [GlueMeterCard.py](#gluemetercardpy)
- [GlueMeterWidget.py](#gluemeterwidgetpy)
- [__init__.py](#__init__py)

## `GlueMeterCard.py`

Source: [src/robot_systems/glue/applications/dashboard/ui/widgets/GlueMeterCard.py](../../../../../../../src/robot_systems/glue/applications/dashboard/ui/widgets/GlueMeterCard.py).

Imports (including optional/function-local imports; not a startup dependency list): `..widgets.GlueMeterWidget`, `PyQt6.QtCore`, `PyQt6.QtWidgets`, `pl_gui.dashboard.resources.styles`, `pl_gui.utils.utils_widgets.MaterialButton`, `typing`.

### `GlueMeterCard`

```python
class GlueMeterCard(QFrame):
```

Declared fields/defaults:

```python
change_glue_requested = pyqtSignal(int)
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, label_text: str, index: int, capacity_grams: float=5000.0)
```

```python
def set_weight(self, grams: float) -> None
```

```python
def set_state(self, state_str: str) -> None
```

```python
def set_glue_type(self, glue_type: Optional[str]) -> None
```

```python
def initialize_display(self, initial_state: Optional[dict], glue_type: Optional[str]) -> None
```

```python
def retranslateUi(self) -> None
```

```python
def changeEvent(self, event) -> None
```

## `GlueMeterWidget.py`

Source: [src/robot_systems/glue/applications/dashboard/ui/widgets/GlueMeterWidget.py](../../../../../../../src/robot_systems/glue/applications/dashboard/ui/widgets/GlueMeterWidget.py).

Imports (including optional/function-local imports; not a startup dependency list): `PyQt6.QtCore`, `PyQt6.QtGui`, `PyQt6.QtWidgets`, `dashboard.styles`, `logging`, `src.dashboard.resources.styles`.

### `GlueMeterWidget`

```python
class GlueMeterWidget(QWidget):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, id: int, parent: QWidget=None, capacity_grams: float=5000.0)
```

```python
def set_weight(self, grams: float) -> None
```

```python
def set_state(self, state: str) -> None
```

```python
def updateWidgets(self, message) -> None
```

```python
def updateState(self, message) -> None
```

```python
def setGluePercent(self, percent, grams=None) -> None
```

```python
def get_shade(self) -> QColor
```

```python
def paintEvent(self, event) -> None
```

```python
def resizeEvent(self, event) -> None
```

```python
def showEvent(self, event) -> None
```

```python
def custom_paint_event(self, event) -> None
```

## `__init__.py`

Source: [src/robot_systems/glue/applications/dashboard/ui/widgets/__init__.py](../../../../../../../src/robot_systems/glue/applications/dashboard/ui/widgets/__init__.py).

No top-level functions, classes or public value declarations; inspect the source for imports or entry-point statements.
