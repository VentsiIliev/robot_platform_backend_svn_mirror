# Module reference: `src/applications/workpiece_editor/editor_core/ui`

[Package guide](README.md) · [Complete source index](../../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [CreateWorkpieceForm.py](#createworkpieceformpy)
- [CreateWorkpieceStyles.py](#createworkpiecestylespy)
- [Drawer.py](#drawerpy)
- [__init__.py](#__init__py)
- [custom_virtual_keyboard.py](#custom_virtual_keyboardpy)

## `CreateWorkpieceForm.py`

Source: [src/applications/workpiece_editor/editor_core/ui/CreateWorkpieceForm.py](../../../../../src/applications/workpiece_editor/editor_core/ui/CreateWorkpieceForm.py).

Generic Form Component Usage Example: ------------- from enum import Enum from editor_core.ui.CreateWorkpieceForm import ( CreateWorkpieceForm, FormFieldConfig, GenericFormConfig ) # Define any enums you need class Priority(Enum): LOW = "low" MEDIUM = "medium" HIGH = "high" # Create field configurations fields = [ FormFieldConfig( field_id="name", field_type="text", label="Name", icon_path="/path/to/name_icon.png", placeholder="Enter name", mandatory=True ), FormFieldConfig( field_id="priority", field_type="dropdown", label="Priority", icon_path="/path/to/priority_icon.png", options=list(Priority), default_value=Priority.MEDIUM.name ), ] # Create form configuration form_config = GenericFormConfig( form_title="Create Item", fields=fields, accept_button_icon="/path/to/accept_icon.png", cancel_button_icon="/path/to/cancel_icon.png", config_file="settings/my_form_config.json", data_factory=lambda data: {"item": data} # Optional transform function ) # Create and use the form form = CreateWorkpieceForm( parent=parent_widget, form_config=form_config, showButtons=True ) form.data_submitted.connect(handle_data) form.show()

Imports (including optional/function-local imports; not a startup dependency list): `.CreateWorkpieceStyles`, `.Drawer`, `PyQt6.QtCore`, `PyQt6.QtGui`, `PyQt6.QtWidgets`, `contour_editor.models.interfaces`, `contour_editor.persistence.providers.widget_provider`, `dataclasses`, `enum`, `json`, `logging`, `os`, `pl_gui.settings.settings_view.styles`, `qtawesome`, `src.applications.workpiece_editor.editor_core.config.workpiece_form_schema`, `sys`, `typing`.

### `FormFieldConfig`

```python
@dataclass
class FormFieldConfig:
```

Declared fields/defaults:

```python
field_id: str
field_type: str
label: str
icon: Any = ''
visible: bool = True
mandatory: bool = False
placeholder: str = ''
options: List[Any] = field(default_factory=list)
default_value: Any = None
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def to_dict(self) -> Dict[str, Any]
```

```python
@classmethod
def from_dict(cls, data: Dict[str, Any]) -> 'FormFieldConfig'
```

### `GenericFormConfig`

```python
@dataclass
class GenericFormConfig:
```

Declared fields/defaults:

```python
form_title: str
fields: List[FormFieldConfig]
accept_button_icon: str = ''
cancel_button_icon: str = ''
config_file: str = 'settings/form_config.json'
data_factory: Optional[Callable] = None
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def get_field(self, field_id: str) -> Optional[FormFieldConfig]
```

```python
def get_visible_fields(self) -> List[FormFieldConfig]
```

### `FormConfigManager`

```python
class FormConfigManager:
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, form_config: GenericFormConfig)
```

```python
def load_config(self)
```

```python
def save_config(self, config)
```

```python
def get_config(self)
```

```python
def is_field_visible(self, field_id)
```

```python
def is_field_mandatory(self, field_id)
```

### `FieldConfigWidget`

```python
class FieldConfigWidget(QWidget):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, field: FormFieldConfig, field_config, parent=None)
```

```python
def init_ui(self, field_config)
```

```python
def get_config(self)
```

### `FormConfigDialog`

```python
class FormConfigDialog(QDialog):
```

Declared fields/defaults:

```python
config_changed = pyqtSignal(dict)
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, config_manager, parent=None)
```

```python
def init_ui(self)
```

```python
def reset_to_defaults(self)
```

```python
def save_config(self)
```

### `CreateWorkpieceForm`

```python
class CreateWorkpieceForm(Drawer, QFrame):
```

Declared fields/defaults:

```python
data_submitted = pyqtSignal(dict)
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, parent=None, form_config: GenericFormConfig=None, showButtons=False, callBack=None)
```

```python
def prefill_form(self, data)
```

```python
def apply_stylesheet(self)
```

```python
def add_config_button(self)
```

Add configuration button to the form

```python
def show_config_dialog(self)
```

```python
def refresh_form(self, new_config)
```

```python
def build_form(self)
```

```python
def add_input_field(self, field_config: FormFieldConfig)
```

```python
def add_dropdown_field(self, field_config: FormFieldConfig)
```

```python
def add_button(self, button_type, icon_path, layout)
```

Helper method to add a button with an icon and click functionality

```python
def validate_mandatory_fields(self)
```

```python
def get_data(self) -> Dict[str, Any]
```

```python
def validate(self) -> Tuple[bool, str]
```

```python
def clear(self) -> None
```

```python
def onSubmit(self) -> bool
```

```python
def onCancel(self)
```

```python
def create_icon_label(self, icon, size=28)
```

```python
def resizeEvent(self, event)
```

```python
def set_field_value(self, field_id: str, value: Any)
```

```python
def clear_form(self)
```

## `CreateWorkpieceStyles.py`

Source: [src/applications/workpiece_editor/editor_core/ui/CreateWorkpieceStyles.py](../../../../../src/applications/workpiece_editor/editor_core/ui/CreateWorkpieceStyles.py).

Imports (including optional/function-local imports; not a startup dependency list): `pl_gui.settings.settings_view.styles`.

### `getStyles`

```python
def getStyles()
```

### `get_input_field_styles`

```python
def get_input_field_styles()
```

### `get_popup_view_styles`

```python
def get_popup_view_styles()
```

## `Drawer.py`

Source: [src/applications/workpiece_editor/editor_core/ui/Drawer.py](../../../../../src/applications/workpiece_editor/editor_core/ui/Drawer.py).

Imports (including optional/function-local imports; not a startup dependency list): `PyQt6.QtCore`, `PyQt6.QtWidgets`.

### `Drawer`

```python
class Drawer(QWidget):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, parent=None, animation_duration=300, side='right')
```

```python
def toggle(self)
```

Animate drawer open/close from left or right, respecting heightOffset

```python
def resize_to_parent_height(self)
```

Adjust height and position based on parent size and drawer side, respecting heightOffset

## `__init__.py`

Source: [src/applications/workpiece_editor/editor_core/ui/__init__.py](../../../../../src/applications/workpiece_editor/editor_core/ui/__init__.py).

Imports (including optional/function-local imports; not a startup dependency list): `.CreateWorkpieceForm`, `.Drawer`.

Package-level import/export surface:

```python
from .CreateWorkpieceForm import CreateWorkpieceForm
from .Drawer import Drawer
```

Module declarations (expressions are shown without evaluating them):

```python
__all__ = ['CreateWorkpieceForm', 'Drawer']
```

## `custom_virtual_keyboard.py`

Source: [src/applications/workpiece_editor/editor_core/ui/custom_virtual_keyboard.py](../../../../../src/applications/workpiece_editor/editor_core/ui/custom_virtual_keyboard.py).

Imports (including optional/function-local imports; not a startup dependency list): `src.applications.base.widgets.custom_virtual_keyboard`.

Module declarations (expressions are shown without evaluating them):

```python
__all__ = ['KeyboardLineEdit', 'KeyboardSpinBox', 'KeyboardDoubleSpinBox']
```
