# Module reference: `src/applications/broker_debug/view`

[Package guide](README.md) · [Complete source index](../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [broker_debug_view.py](#broker_debug_viewpy)
- [graph_widget.py](#graph_widgetpy)

## `__init__.py`

Source: [src/applications/broker_debug/view/__init__.py](../../../../src/applications/broker_debug/view/__init__.py).

No top-level functions, classes or public value declarations; inspect the source for imports or entry-point statements.

## `broker_debug_view.py`

Source: [src/applications/broker_debug/view/broker_debug_view.py](../../../../src/applications/broker_debug/view/broker_debug_view.py).

Imports (including optional/function-local imports; not a startup dependency list): `PyQt6.QtCore`, `PyQt6.QtGui`, `PyQt6.QtWidgets`, `datetime`, `pl_gui.utils.utils_widgets.MaterialButton`, `pl_gui.utils.utils_widgets.table_helpers`, `src.applications.base.app_styles`, `src.applications.base.i_application_view`, `src.applications.broker_debug.view.graph_widget`, `typing`.

### `BrokerDebugView`

```python
class BrokerDebugView(IApplicationView):
```

Declared fields/defaults:

```python
refresh_requested = pyqtSignal()
publish_requested = pyqtSignal(str, str)
spy_requested = pyqtSignal(str)
unspy_requested = pyqtSignal(str)
clear_topic_requested = pyqtSignal(str)
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, parent=None)
```

```python
def setup_ui(self) -> None
```

```python
def clean_up(self) -> None
```

```python
def set_topic_map(self, topic_map: Dict[str, int]) -> None
```

```python
def append_log(self, message: str) -> None
```

```python
def set_spy_topic(self, topic: str) -> None
```

## `graph_widget.py`

Source: [src/applications/broker_debug/view/graph_widget.py](../../../../src/applications/broker_debug/view/graph_widget.py).

Imports (including optional/function-local imports; not a startup dependency list): `PyQt6.QtCore`, `PyQt6.QtGui`, `PyQt6.QtWidgets`, `math`, `typing`.

### `GraphWidget`

```python
class GraphWidget(QWidget):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, parent=None)
```

```python
def set_topic_map(self, topic_map: Dict[str, int]) -> None
```

```python
def paintEvent(self, event) -> None
```
