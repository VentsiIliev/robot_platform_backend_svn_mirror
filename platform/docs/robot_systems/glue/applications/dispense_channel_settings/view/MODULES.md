# Module reference: `src/robot_systems/glue/applications/dispense_channel_settings/view`

[Package guide](README.md) · [Complete source index](../../../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [dispense_channel_schema.py](#dispense_channel_schemapy)
- [dispense_channel_settings_view.py](#dispense_channel_settings_viewpy)
- [dispense_channel_tab.py](#dispense_channel_tabpy)

## `dispense_channel_schema.py`

Source: [src/robot_systems/glue/applications/dispense_channel_settings/view/dispense_channel_schema.py](../../../../../../src/robot_systems/glue/applications/dispense_channel_settings/view/dispense_channel_schema.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `pl_gui.settings.settings_view.schema`.

Module declarations (expressions are shown without evaluating them):

```python
SCALE_GROUP = SettingGroup('Scale', [SettingField('url', 'URL', 'line_edit', default='http://192.168.1.100'), SettingField('capacity', 'Capacity', 'double_spinbox', default=1000.0, min_val=0.0, max_val=100000.0, decimals=1, suffix=' g', step=100.0), SettingField('fetch_timeout_seconds', 'Fetch Timeout', 'double_spinbox', default=5.0, min_val=0.1, max_val=60.0, decimals=1, suffix=' s', step=0.5), SettingField('data_fetch_interval_ms', 'Fetch Interval', 'spinbox', default=500, min_val=50, max_val=10000, suffix=' ms', step=50)])
CALIBRATION_GROUP = SettingGroup('Calibration', [SettingField('zero_offset', 'Zero Offset', 'double_spinbox', default=0.0, min_val=-10000.0, max_val=10000.0, decimals=4, step=0.0001), SettingField('scale_factor', 'Scale Factor', 'double_spinbox', default=1.0, min_val=-1000.0, max_val=1000.0, decimals=6, step=1e-06)])
MEASUREMENT_GROUP = SettingGroup('Measurement', [SettingField('sampling_rate', 'Sampling Rate', 'spinbox', default=10, min_val=1, max_val=1000, suffix=' Hz', step=1), SettingField('filter_cutoff', 'Filter Cutoff', 'double_spinbox', default=1.0, min_val=0.01, max_val=100.0, decimals=2, suffix=' Hz', step=0.1), SettingField('averaging_samples', 'Averaging Samples', 'spinbox', default=5, min_val=1, max_val=100, step=1), SettingField('min_weight_threshold', 'Min Weight Threshold', 'double_spinbox', default=0.0, min_val=0.0, max_val=100.0, decimals=2, suffix=' g', step=0.01), SettingField('max_weight_threshold', 'Max Weight Threshold', 'double_spinbox', default=1000.0, min_val=0.0, max_val=100000.0, decimals=1, suffix=' g', step=100.0)])
```

### `build_glue_group`

```python
def build_glue_group(glue_types: list[str]) -> SettingGroup
```

## `dispense_channel_settings_view.py`

Source: [src/robot_systems/glue/applications/dispense_channel_settings/view/dispense_channel_settings_view.py](../../../../../../src/robot_systems/glue/applications/dispense_channel_settings/view/dispense_channel_settings_view.py).

Imports (including optional/function-local imports; not a startup dependency list): `PyQt6.QtCore`, `PyQt6.QtWidgets`, `__future__`, `pl_gui.settings.settings_view.styles`, `src.applications.base.i_application_view`, `src.robot_systems.glue.applications.dispense_channel_settings.view.dispense_channel_tab`, `src.shared_contracts.declarations`, `typing`.

### `DispenseChannelSettingsView`

```python
class DispenseChannelSettingsView(IApplicationView):
```

Declared fields/defaults:

```python
save_requested = pyqtSignal(str, dict)
tare_requested = pyqtSignal(str)
pump_on_requested = pyqtSignal(str)
pump_off_requested = pyqtSignal(str)
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, channel_definitions: List[DispenseChannelDefinition], glue_types: list[str], parent=None)
```

```python
def setup_ui(self) -> None
```

```python
def load_channel(self, channel_id: str, flat: dict) -> None
```

```python
def set_channel_weight(self, channel_id: str, value: float) -> None
```

```python
def set_channel_state(self, channel_id: str, state: str) -> None
```

```python
def clean_up(self) -> None
```

## `dispense_channel_tab.py`

Source: [src/robot_systems/glue/applications/dispense_channel_settings/view/dispense_channel_tab.py](../../../../../../src/robot_systems/glue/applications/dispense_channel_settings/view/dispense_channel_tab.py).

Imports (including optional/function-local imports; not a startup dependency list): `PyQt6.QtCore`, `PyQt6.QtWidgets`, `__future__`, `pl_gui.settings.settings_view.styles`, `src.applications.base.keyboard_settings_view`, `src.applications.glue_cell_settings.view.cell_monitor_widget`, `src.robot_systems.glue.applications.dispense_channel_settings.view.dispense_channel_schema`, `src.shared_contracts.declarations`.

### `DispenseChannelTab`

```python
class DispenseChannelTab(QWidget):
```

Declared fields/defaults:

```python
save_requested = pyqtSignal(str, dict)
tare_requested = pyqtSignal(str)
pump_on_requested = pyqtSignal(str)
pump_off_requested = pyqtSignal(str)
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, definition: DispenseChannelDefinition, glue_types: list[str], parent=None)
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
