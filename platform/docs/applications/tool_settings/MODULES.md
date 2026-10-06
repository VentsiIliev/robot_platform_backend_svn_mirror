# Module reference: `src/applications/tool_settings`

[Package guide](README.md) · [Complete source index](../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [tool_settings_factory.py](#tool_settings_factorypy)

## `__init__.py`

Source: [src/applications/tool_settings/__init__.py](../../../src/applications/tool_settings/__init__.py).

Imports (including optional/function-local imports; not a startup dependency list): `.service.i_tool_settings_service`, `.service.tool_settings_application_service`, `.tool_settings_factory`.

Package-level import/export surface:

```python
from .tool_settings_factory import ToolSettingsFactory
from .service.i_tool_settings_service import IToolSettingsService
from .service.tool_settings_application_service import ToolSettingsApplicationService
```

No top-level functions, classes or public value declarations; inspect the source for imports or entry-point statements.

## `tool_settings_factory.py`

Source: [src/applications/tool_settings/tool_settings_factory.py](../../../src/applications/tool_settings/tool_settings_factory.py).

Imports (including optional/function-local imports; not a startup dependency list): `.controller.tool_settings_controller`, `.model.tool_settings_model`, `.service.i_tool_settings_service`, `.view.tool_settings_view`, `src.applications.base.application_factory`, `src.applications.base.i_application_controller`, `src.applications.base.i_application_model`, `src.applications.base.i_application_view`.

### `ToolSettingsFactory`

```python
class ToolSettingsFactory(ApplicationFactory):
```
