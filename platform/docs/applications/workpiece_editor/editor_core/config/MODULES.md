# Module reference: `src/applications/workpiece_editor/editor_core/config`

[Package guide](README.md) · [Complete source index](../../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [segment_editor_config.py](#segment_editor_configpy)
- [segment_settings_provider_adapter.py](#segment_settings_provider_adapterpy)
- [segment_settings_schema.py](#segment_settings_schemapy)
- [virtual_keyboard_config.py](#virtual_keyboard_configpy)
- [virtual_keyboard_widget_factory.py](#virtual_keyboard_widget_factorypy)
- [workpiece_form_config.py](#workpiece_form_configpy)
- [workpiece_form_factory.py](#workpiece_form_factorypy)
- [workpiece_form_schema.py](#workpiece_form_schemapy)

## `__init__.py`

Source: [src/applications/workpiece_editor/editor_core/config/__init__.py](../../../../../src/applications/workpiece_editor/editor_core/config/__init__.py).

Imports (including optional/function-local imports; not a startup dependency list): `.segment_editor_config`, `.segment_settings_provider_adapter`, `.segment_settings_schema`, `.workpiece_form_factory`, `.workpiece_form_schema`.

Package-level import/export surface:

```python
from .segment_settings_schema import SegmentSettingsSchema, SegmentSettingSpec
from .segment_settings_provider_adapter import SegmentSettingsProviderAdapter
from .segment_editor_config import SegmentEditorConfig
from .workpiece_form_factory import WorkpieceFormFactory
from .workpiece_form_schema import WorkpieceFormSchema, WorkpieceFormFieldSpec, FieldIcon
```

No top-level functions, classes or public value declarations; inspect the source for imports or entry-point statements.

## `segment_editor_config.py`

Source: [src/applications/workpiece_editor/editor_core/config/segment_editor_config.py](../../../../../src/applications/workpiece_editor/editor_core/config/segment_editor_config.py).

Imports (including optional/function-local imports; not a startup dependency list): `contour_editor`, `dataclasses`, `src.applications.workpiece_editor.editor_core.config.segment_settings_provider_adapter`, `src.applications.workpiece_editor.editor_core.config.segment_settings_schema`.

### `SegmentEditorConfig`

```python
@dataclass
class SegmentEditorConfig:
```

Declared fields/defaults:

```python
schema: SegmentSettingsSchema
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
@property
def settings_provider(self) -> ISettingsProvider
```

```python
@property
def settings_config(self) -> SettingsConfig
```

## `segment_settings_provider_adapter.py`

Source: [src/applications/workpiece_editor/editor_core/config/segment_settings_provider_adapter.py](../../../../../src/applications/workpiece_editor/editor_core/config/segment_settings_provider_adapter.py).

Imports (including optional/function-local imports; not a startup dependency list): `contour_editor`, `src.applications.workpiece_editor.editor_core.config.segment_settings_schema`.

### `SegmentSettingsProviderAdapter`

```python
class SegmentSettingsProviderAdapter(ISettingsProvider):
```

Adapts SegmentSettingsSchema to the contour_editor.ISettingsProvider interface. Method names (get_material_type_key etc.) are fixed by the external contract and do not imply any domain knowledge — they map to combo_key / combo_options.

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, schema: SegmentSettingsSchema)
```

```python
def get_all_setting_keys(self)
```

```python
def get_default_values(self)
```

```python
def get_material_type_key(self)
```

```python
def get_available_material_types(self)
```

```python
def get_default_material_type(self)
```

```python
def get_setting_label(self, key: str)
```

```python
def get_setting_value(self, key: str)
```

```python
def validate_setting(self, key: str, value: str) -> bool
```

```python
def validate_setting_value(self, key: str, value: str) -> bool
```

```python
def get_settings_tabs_config(self)
```

## `segment_settings_schema.py`

Source: [src/applications/workpiece_editor/editor_core/config/segment_settings_schema.py](../../../../../src/applications/workpiece_editor/editor_core/config/segment_settings_schema.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `dataclasses`, `typing`.

### `SegmentSettingSpec`

```python
@dataclass
class SegmentSettingSpec:
```

Declared fields/defaults:

```python
key: str
label: str
default: str
group: str
validator: str = 'numeric'
```

### `SegmentSettingsSchema`

```python
@dataclass
class SegmentSettingsSchema:
```

Declared fields/defaults:

```python
fields: List[SegmentSettingSpec]
combo_key: str
combo_options: List[str]
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def get_defaults(self) -> Dict[str, str]
```

```python
def get_groups(self) -> Dict[str, List[str]]
```

```python
def get_label(self, key: str) -> str
```

```python
def validate(self, key: str, value: str) -> bool
```

## `virtual_keyboard_config.py`

Source: [src/applications/workpiece_editor/editor_core/config/virtual_keyboard_config.py](../../../../../src/applications/workpiece_editor/editor_core/config/virtual_keyboard_config.py).

Imports (including optional/function-local imports; not a startup dependency list): `src.applications.base.config.virtual_keyboard_config`.

Module declarations (expressions are shown without evaluating them):

```python
__all__ = ['ENABLE_CUSTOM_VIRTUAL_KEYBOARD']
```

## `virtual_keyboard_widget_factory.py`

Source: [src/applications/workpiece_editor/editor_core/config/virtual_keyboard_widget_factory.py](../../../../../src/applications/workpiece_editor/editor_core/config/virtual_keyboard_widget_factory.py).

Imports (including optional/function-local imports; not a startup dependency list): `src.applications.base.widgets.virtual_keyboard_widget_factory`.

Module declarations (expressions are shown without evaluating them):

```python
__all__ = ['VirtualKeyboardWidgetFactory']
```

## `workpiece_form_config.py`

Source: [src/applications/workpiece_editor/editor_core/config/workpiece_form_config.py](../../../../../src/applications/workpiece_editor/editor_core/config/workpiece_form_config.py).

Imports (including optional/function-local imports; not a startup dependency list): `os`, `src.applications.workpiece_editor.editor_core.config.workpiece_form_schema`, `src.applications.workpiece_editor.editor_core.ui.CreateWorkpieceForm`.

### `get_icon_path`

```python
def get_icon_path(icon_name)
```

### `get_contour_icon_path`

```python
def get_contour_icon_path(icon_name)
```

### `create_workpiece_form_config`

```python
def create_workpiece_form_config(schema: WorkpieceFormSchema) -> GenericFormConfig
```

## `workpiece_form_factory.py`

Source: [src/applications/workpiece_editor/editor_core/config/workpiece_form_factory.py](../../../../../src/applications/workpiece_editor/editor_core/config/workpiece_form_factory.py).

Imports (including optional/function-local imports; not a startup dependency list): `..ui.CreateWorkpieceForm`, `.workpiece_form_config`, `.workpiece_form_schema`.

### `WorkpieceFormFactory`

```python
class WorkpieceFormFactory:
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, schema: WorkpieceFormSchema)
```

```python
def create_form(self, parent=None)
```

## `workpiece_form_schema.py`

Source: [src/applications/workpiece_editor/editor_core/config/workpiece_form_schema.py](../../../../../src/applications/workpiece_editor/editor_core/config/workpiece_form_schema.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `dataclasses`, `typing`.

### `FieldIcon`

```python
@dataclass
class FieldIcon:
```

Declarative icon descriptor — resolved to a QPixmap/QIcon at render time. Use the factory methods; never construct directly.

Declared fields/defaults:

```python
kind: str
value: str = ''
color: str = '#ffffff'
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
@staticmethod
def none() -> 'FieldIcon'
```

```python
@staticmethod
def from_path(path: str) -> 'FieldIcon'
```

```python
@staticmethod
def from_qta(icon_id: str, color: str='#333333') -> 'FieldIcon'
```

### `WorkpieceFormFieldSpec`

```python
@dataclass
class WorkpieceFormFieldSpec:
```

Declared fields/defaults:

```python
key: str
label: str
field_type: str
mandatory: bool = False
options: Optional[List[Any]] = None
icon: FieldIcon = field(default_factory=FieldIcon.none)
placeholder: str = ''
default_value: Any = None
visible: bool = True
```

### `WorkpieceFormSchema`

```python
@dataclass
class WorkpieceFormSchema:
```

Declared fields/defaults:

```python
fields: List[WorkpieceFormFieldSpec]
id_key: str = 'workpieceId'
combo_key: str = ''
contour_key: str = 'contour'
spray_pattern_key: str = 'sprayPattern'
editor_layer_config: Any = None
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def get_required_keys(self) -> List[str]
```

```python
def get_field(self, key: str) -> Optional[WorkpieceFormFieldSpec]
```

```python
def get_options(self, key: str) -> List[Any]
```
