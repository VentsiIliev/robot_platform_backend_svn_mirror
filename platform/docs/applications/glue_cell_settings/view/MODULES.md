# Module reference: `src/applications/glue_cell_settings/view`

[Package guide](README.md) · [Complete source index](../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [cell_monitor_widget.py](#cell_monitor_widgetpy)
- [cell_settings_tab.py](#cell_settings_tabpy)
- [glue_cell_schema.py](#glue_cell_schemapy)
- [glue_cell_settings_view.py](#glue_cell_settings_viewpy)

## `__init__.py`

Source: [src/applications/glue_cell_settings/view/__init__.py](../../../../src/applications/glue_cell_settings/view/__init__.py).

No top-level functions, classes or public value declarations; inspect the source for imports or entry-point statements.

## `cell_monitor_widget.py`

Source: [src/applications/glue_cell_settings/view/cell_monitor_widget.py](../../../../src/applications/glue_cell_settings/view/cell_monitor_widget.py).

Imports (including optional/function-local imports; not a startup dependency list): `PyQt6.QtCore`, `PyQt6.QtWidgets`, `pl_gui.settings.settings_view.styles`.

### `_MonitorBridge`

```python
class _MonitorBridge(QObject):
```

Declared fields/defaults:

```python
weight_updated = pyqtSignal(float)
state_updated = pyqtSignal(str)
```

### `CellMonitorWidget`

```python
class CellMonitorWidget(QWidget):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, parent=None)
```

```python
def set_weight(self, value: float) -> None
```

```python
def set_state(self, state: str) -> None
```

## `cell_settings_tab.py`

Source: [src/applications/glue_cell_settings/view/cell_settings_tab.py](../../../../src/applications/glue_cell_settings/view/cell_settings_tab.py).

Imports (including optional/function-local imports; not a startup dependency list): `PyQt6.QtCore`, `PyQt6.QtWidgets`, `__future__`, `pl_gui.settings.settings_view.styles`, `src.applications.base.keyboard_settings_view`, `src.applications.glue_cell_settings.view.cell_monitor_widget`, `src.applications.glue_cell_settings.view.glue_cell_schema`.

### `CellSettingsTab`

```python
class CellSettingsTab(QWidget):
```

Declared fields/defaults:

```python
save_requested = pyqtSignal(dict)
tare_requested = pyqtSignal()
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, cell_id: int, parent=None)
```

```python
def load(self, flat: dict) -> None
```

```python
def set_weight(self, value: float) -> None
```

```python
def set_state(self, state: str) -> None
```

## `glue_cell_schema.py`

Source: [src/applications/glue_cell_settings/view/glue_cell_schema.py](../../../../src/applications/glue_cell_settings/view/glue_cell_schema.py).

Imports (including optional/function-local imports; not a startup dependency list): `pl_gui.settings.settings_view.schema`.

Module declarations (expressions are shown without evaluating them):

```python
CONNECTION_GROUP = SettingGroup('Connection', [SettingField('url', 'URL', 'line_edit', default='http://192.168.1.100'), SettingField('type', 'Glue Type', 'line_edit', default='Type A'), SettingField('capacity', 'Capacity', 'double_spinbox', default=1000.0, min_val=0.0, max_val=100000.0, decimals=1, suffix=' g', step=100.0), SettingField('fetch_timeout_seconds', 'Fetch Timeout', 'double_spinbox', default=5.0, min_val=0.1, max_val=60.0, decimals=1, suffix=' s', step=0.5), SettingField('data_fetch_interval_ms', 'Fetch Interval', 'spinbox', default=500, min_val=50, max_val=10000, suffix=' ms', step=50), SettingField('motor_address', 'Motor Address', 'spinbox', default=0, min_val=0, max_val=255, step=1)])
CALIBRATION_GROUP = SettingGroup('Calibration', [SettingField('zero_offset', 'Zero Offset', 'double_spinbox', default=0.0, min_val=-10000.0, max_val=10000.0, decimals=4, step=0.0001), SettingField('scale_factor', 'Scale Factor', 'double_spinbox', default=1.0, min_val=-1000.0, max_val=1000.0, decimals=6, step=1e-06)])
MEASUREMENT_GROUP = SettingGroup('Measurement', [SettingField('sampling_rate', 'Sampling Rate', 'spinbox', default=10, min_val=1, max_val=1000, suffix=' Hz', step=1), SettingField('filter_cutoff', 'Filter Cutoff', 'double_spinbox', default=1.0, min_val=0.01, max_val=100.0, decimals=2, suffix=' Hz', step=0.1), SettingField('averaging_samples', 'Averaging Samples', 'spinbox', default=5, min_val=1, max_val=100, step=1), SettingField('min_weight_threshold', 'Min Weight Threshold', 'double_spinbox', default=0.0, min_val=0.0, max_val=100.0, decimals=2, suffix=' g', step=0.01), SettingField('max_weight_threshold', 'Max Weight Threshold', 'double_spinbox', default=1000.0, min_val=0.0, max_val=100000, decimals=1, suffix=' g', step=100.0)])
```

## `glue_cell_settings_view.py`

Source: [src/applications/glue_cell_settings/view/glue_cell_settings_view.py](../../../../src/applications/glue_cell_settings/view/glue_cell_settings_view.py).

Imports (including optional/function-local imports; not a startup dependency list): `PyQt6.QtCore`, `PyQt6.QtWidgets`, `__future__`, `pl_gui.settings.settings_view.styles`, `src.applications.base.i_application_view`, `src.applications.glue_cell_settings.view.cell_settings_tab`, `typing`.

### `GlueCellSettingsView`

```python
class GlueCellSettingsView(IApplicationView):
```

Declared fields/defaults:

```python
save_requested = pyqtSignal(int, dict)
tare_requested = pyqtSignal(int)
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, cell_ids: List[int], parent=None)
```

```python
def setup_ui(self) -> None
```

```python
def load_cell(self, cell_id: int, flat: dict) -> None
```

```python
def set_cell_weight(self, cell_id: int, value: float) -> None
```

```python
def set_cell_state(self, cell_id: int, state: str) -> None
```

```python
def clean_up(self) -> None
```
