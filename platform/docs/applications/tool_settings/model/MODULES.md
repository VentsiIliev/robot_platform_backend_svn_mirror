# Module reference: `src/applications/tool_settings/model`

[Package guide](README.md) · [Complete source index](../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [tool_settings_model.py](#tool_settings_modelpy)

## `__init__.py`

Source: [src/applications/tool_settings/model/__init__.py](../../../../src/applications/tool_settings/model/__init__.py).

No top-level functions, classes or public value declarations; inspect the source for imports or entry-point statements.

## `tool_settings_model.py`

Source: [src/applications/tool_settings/model/tool_settings_model.py](../../../../src/applications/tool_settings/model/tool_settings_model.py).

Imports (including optional/function-local imports; not a startup dependency list): `..service.i_tool_settings_service`, `src.applications.base.i_application_model`.

### `ToolSettingsModel`

```python
class ToolSettingsModel(IApplicationModel):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, service: IToolSettingsService)
```

```python
def load(self)
```

```python
def save(self, *_, **__)
```

```python
def get_tools(self)
```

```python
def get_slots(self)
```

```python
def add_tool(self, tool_id, name)
```

```python
def update_tool(self, tool_id, name)
```

```python
def remove_tool(self, tool_id)
```

```python
def update_slot(self, slot_id, tool_id)
```

```python
def add_slot(self, slot_id, tool_id)
```

```python
def remove_slot(self, slot_id)
```

```python
def update_tool_geometry(self, tool_id, transform, collision_profile='')
```

```python
def update_slot_sequences(self, slot_id, pickup, dropoff)
```

```python
def capture_reference_contact(self)
```

```python
def capture_tool_contact(self)
```

```python
def solve_tool_calibration(self, tool_id)
```

```python
def activate_tool(self, tool_id)
```

```python
def get_current_motion_pose(self)
```
