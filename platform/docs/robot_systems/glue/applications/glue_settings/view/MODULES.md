# Module reference: `src/robot_systems/glue/applications/glue_settings/view`

[Package guide](README.md) · [Complete source index](../../../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [glue_settings_schema.py](#glue_settings_schemapy)
- [glue_settings_view.py](#glue_settings_viewpy)
- [glue_type_tab.py](#glue_type_tabpy)

## `__init__.py`

Source: [src/robot_systems/glue/applications/glue_settings/view/__init__.py](../../../../../../src/robot_systems/glue/applications/glue_settings/view/__init__.py).

No top-level functions, classes or public value declarations; inspect the source for imports or entry-point statements.

## `glue_settings_schema.py`

Source: [src/robot_systems/glue/applications/glue_settings/view/glue_settings_schema.py](../../../../../../src/robot_systems/glue/applications/glue_settings/view/glue_settings_schema.py).

Imports (including optional/function-local imports; not a startup dependency list): `pl_gui.settings.settings_view.schema`.

Module declarations (expressions are shown without evaluating them):

```python
SPRAY_GROUP = SettingGroup('Spray Settings', [SettingField('spray_width', 'Spray Width', 'double_spinbox', default=5.0, min_val=0, max_val=100, decimals=1, suffix=' mm', step=0.1, step_options=[0.1, 1, 5]), SettingField('spraying_height', 'Spraying Height', 'double_spinbox', default=10.0, min_val=0, max_val=100, decimals=1, suffix=' mm', step=0.1, step_options=[0.1, 1, 5]), SettingField('fan_speed', 'Fan Speed', 'double_spinbox', default=50.0, min_val=0, max_val=100, decimals=1, suffix=' %', step=1, step_options=[1, 5, 10]), SettingField('rz_angle', 'RZ Angle', 'double_spinbox', default=0.0, min_val=-180, max_val=180, decimals=1, suffix=' °', step=1, step_options=[1, 5, 10]), SettingField('spray_on', 'Spray On', 'toggle', default=True)])
PUMP_GROUP = SettingGroup('Pump Settings', [SettingField('motor_speed', 'Motor Speed', 'double_spinbox', default=10000.0, min_val=0, max_val=20000, decimals=1, suffix=' rpm', step=100, step_options=[100, 500, 1000]), SettingField('reverse_duration', 'Reverse Duration', 'double_spinbox', default=1.0, min_val=0, max_val=60, decimals=1, suffix=' s', step=0.1, step_options=[0.1, 1, 5]), SettingField('speed_reverse', 'Speed Reverse', 'double_spinbox', default=1000.0, min_val=0, max_val=20000, decimals=1, suffix=' rpm', step=100, step_options=[100, 500, 1000])])
GENERATOR_GROUP = SettingGroup('Generator Settings', [SettingField('time_between_generator_and_glue', 'Generator-Glue Delay', 'double_spinbox', default=1.0, min_val=0, max_val=60, decimals=1, suffix=' s', step=0.1, step_options=[0.1, 1, 5]), SettingField('generator_timeout', 'Generator Timeout', 'double_spinbox', default=5.0, min_val=0, max_val=60, decimals=1, suffix=' s', step=0.1, step_options=[0.1, 1, 5]), SettingField('glue_type', 'Glue Type', 'combo', default='Type A', choices=['Type A', 'Type B', 'Type C'])])
TIMING_GROUP = SettingGroup('Timing Settings', [SettingField('time_before_motion', 'Time Before Motion', 'double_spinbox', default=1.0, min_val=0, max_val=60, decimals=1, suffix=' s', step=0.1, step_options=[0.1, 1, 5]), SettingField('time_before_stop', 'Time Before Stop', 'double_spinbox', default=1.0, min_val=0, max_val=100, decimals=1, suffix=' s', step=0.1, step_options=[0.1, 1, 5]), SettingField('reach_start_threshold', 'Reach Start Threshold', 'double_spinbox', default=1.0, min_val=0, max_val=100, decimals=1, step=0.1, step_options=[0.1, 1, 5]), SettingField('reach_end_threshold', 'Reach End Threshold', 'double_spinbox', default=1.0, min_val=0, max_val=100, decimals=1, step=0.1, step_options=[0.1, 1, 5])])
RAMP_GROUP = SettingGroup('Ramp Settings', [SettingField('initial_ramp_speed', 'Initial Ramp Speed', 'double_spinbox', default=5000.0, min_val=0, max_val=20000, decimals=1, suffix=' rpm', step=100, step_options=[100, 500, 1000]), SettingField('forward_ramp_steps', 'Forward Ramp Steps', 'spinbox', default=1, min_val=0, max_val=100, step=1, step_options=[1, 5, 10]), SettingField('reverse_ramp_steps', 'Reverse Ramp Steps', 'spinbox', default=1, min_val=0, max_val=100, step=1, step_options=[1, 5, 10]), SettingField('initial_ramp_speed_duration', 'Ramp Speed Duration', 'double_spinbox', default=1.0, min_val=0, max_val=100, decimals=1, suffix=' ms', step=1, step_options=[1, 5, 10])])
```

## `glue_settings_view.py`

Source: [src/robot_systems/glue/applications/glue_settings/view/glue_settings_view.py](../../../../../../src/robot_systems/glue/applications/glue_settings/view/glue_settings_view.py).

Imports (including optional/function-local imports; not a startup dependency list): `PyQt6.QtCore`, `PyQt6.QtWidgets`, `src.applications.base.i_application_view`, `src.applications.base.keyboard_settings_view`, `src.robot_systems.glue.applications.glue_settings.model.mapper`, `src.robot_systems.glue.applications.glue_settings.view.glue_settings_schema`, `src.robot_systems.glue.applications.glue_settings.view.glue_type_tab`.

### `GlueSettingsView`

```python
class GlueSettingsView(IApplicationView):
```

View — pure Qt widget. No services, no model, no business logic.

Declared fields/defaults:

```python
SHOW_JOG_WIDGET = True
JOG_FRAME_SELECTOR_ENABLED = True
save_requested = pyqtSignal(dict)
spray_on_changed = pyqtSignal(bool)
add_type_requested = pyqtSignal(str, str)
update_type_requested = pyqtSignal(str, str, str)
remove_type_requested = pyqtSignal(str)
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, parent=None)
```

```python
def setup_ui(self) -> None
```

```python
def load_settings(self, settings) -> None
```

```python
def load_glue_types(self, types: list) -> None
```

```python
def get_values(self) -> dict
```

```python
def clean_up(self) -> None
```

## `glue_type_tab.py`

Source: [src/robot_systems/glue/applications/glue_settings/view/glue_type_tab.py](../../../../../../src/robot_systems/glue/applications/glue_settings/view/glue_type_tab.py).

Pure UI tab for managing custom glue types. Built-in types (Type A–D) are always shown, read-only, italic. Custom types are loaded via load_types() and can be added / edited / removed. Signals (connect to your repo calls from the controller): add_requested(name, description) update_requested(id, name, description) remove_requested(id)

Imports (including optional/function-local imports; not a startup dependency list): `PyQt6.QtCore`, `PyQt6.QtWidgets`, `__future__`, `pl_gui.settings.settings_view.styles`, `src.applications.base.widgets.custom_virtual_keyboard`, `src.robot_systems.glue.settings.glue_types`, `typing`.

### `GlueTypeTab`

```python
class GlueTypeTab(QWidget):
```

Tab widget for managing custom glue types. Built-in types are fixed and shown in italic. Custom types support Add / Edit / Remove via an inline form (no dialog).

Declared fields/defaults:

```python
add_requested = pyqtSignal(str, str)
update_requested = pyqtSignal(str, str, str)
remove_requested = pyqtSignal(str)
BUILTIN_TYPES = ['Type A', 'Type B', 'Type C', 'Type D']
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, parent=None)
```

```python
def load_types(self, types: List[GlueType]) -> None
```

Replace the current custom type list and refresh the table.
