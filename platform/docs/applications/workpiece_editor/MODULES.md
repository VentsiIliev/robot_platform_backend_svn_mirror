# Module reference: `src/applications/workpiece_editor`

[Package guide](README.md) · [Complete source index](../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [example_usage.py](#example_usagepy)
- [i_workpiece_matcher.py](#i_workpiece_matcherpy)
- [workpiece_editor_factory.py](#workpiece_editor_factorypy)

## `__init__.py`

Source: [src/applications/workpiece_editor/__init__.py](../../../src/applications/workpiece_editor/__init__.py).

No top-level functions, classes or public value declarations; inspect the source for imports or entry-point statements.

## `example_usage.py`

Source: [src/applications/workpiece_editor/example_usage.py](../../../src/applications/workpiece_editor/example_usage.py).

Imports (including optional/function-local imports; not a startup dependency list): `PyQt6.QtWidgets`, `logging`, `os`, `src.applications.workpiece_editor.editor_core.config.segment_editor_config`, `src.applications.workpiece_editor.editor_core.config.segment_settings_schema`, `src.applications.workpiece_editor.editor_core.config.workpiece_form_schema`, `src.applications.workpiece_editor.service.stub_workpiece_editor_service`, `src.applications.workpiece_editor.workpiece_editor_factory`, `src.engine.core.messaging_service`, `sys`.

Module declarations (expressions are shown without evaluating them):

```python
ID_ICON = 'fa5s.barcode'
NAME_ICON = 'fa5s.tag'
DESCRIPTION_ICON = 'fa5s.align-left'
HEIGHT_ICON = 'fa5s.ruler-vertical'
PART_TYPE_ICON = 'fa5s.layer-group'
ICON_COLOR = '#444444'
```

### `run_standalone`

```python
def run_standalone()
```

## `i_workpiece_matcher.py`

Source: [src/applications/workpiece_editor/i_workpiece_matcher.py](../../../src/applications/workpiece_editor/i_workpiece_matcher.py).

Imports (including optional/function-local imports; not a startup dependency list): `abc`.

### `IWorkpieceMatcher`

```python
class IWorkpieceMatcher(ABC):
```

Matching capability consumed by the reusable workpiece editor.

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
@abstractmethod
def can_match_saved_workpieces(self) -> bool
```

```python
@abstractmethod
def match_saved_workpieces(self, contour) -> tuple[bool, dict | None, str]
```

## `workpiece_editor_factory.py`

Source: [src/applications/workpiece_editor/workpiece_editor_factory.py](../../../src/applications/workpiece_editor/workpiece_editor_factory.py).

Imports (including optional/function-local imports; not a startup dependency list): `src.applications.base.application_factory`, `src.applications.base.i_application_controller`, `src.applications.base.i_application_model`, `src.applications.base.i_application_view`, `src.applications.workpiece_editor.controller.workpiece_editor_controller`, `src.applications.workpiece_editor.model`, `src.applications.workpiece_editor.service`, `src.applications.workpiece_editor.view.workpiece_editor_view`.

### `WorkpieceEditorFactory`

```python
class WorkpieceEditorFactory(ApplicationFactory):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self)
```

```python
def build(self, service: IWorkpieceEditorService, messaging=None, jog_service=None, ui_config=None, custom_action_handler=None)
```
