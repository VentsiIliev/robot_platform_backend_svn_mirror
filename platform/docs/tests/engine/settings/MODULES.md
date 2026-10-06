# Module reference: `tests/engine/settings`

[Package guide](README.md) · [Complete source index](../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [test_settings_loading.py](#test_settings_loadingpy)
- [test_tool_changer_settings.py](#test_tool_changer_settingspy)

## `__init__.py`

Source: [tests/engine/settings/__init__.py](../../../../tests/engine/settings/__init__.py).

No top-level functions, classes or public value declarations; inspect the source for imports or entry-point statements.

## `test_settings_loading.py`

Source: [tests/engine/settings/test_settings_loading.py](../../../../tests/engine/settings/test_settings_loading.py).

Imports (including optional/function-local imports; not a startup dependency list): `inspect`, `json`, `os`, `src.engine.common_settings_ids`, `src.engine.repositories.settings_service_factory`, `src.engine.robot.configuration`, `src.robot_systems.glue.glue_robot_system`, `src.shared_contracts.declarations`, `tempfile`, `unittest`.

Module declarations (expressions are shown without evaluating them):

```python
APP_NAME = GlueRobotSystem.__name__.lower()
```

### `_get_settings_path`

```python
def _get_settings_path(app_class, settings_root: str, storage_key: str) -> str
```

Mirror exactly what build_from_specs does.

### `TestRobotSettingsSerialiser`

```python
class TestRobotSettingsSerialiser(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_default_values(self)
```

```python
def test_round_trip(self)
```

```python
def test_movement_groups_round_trip(self)
```

```python
def test_safety_limits_round_trip(self)
```

```python
def test_from_dict_missing_keys_uses_defaults(self)
```

### `TestRobotSettingsSerializer`

```python
class TestRobotSettingsSerializer(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def setUp(self)
```

```python
def test_settings_type(self)
```

```python
def test_get_default_returns_robot_settings(self)
```

```python
def test_to_dict_from_dict_round_trip(self)
```

### `TestSettingsServiceIntegration`

```python
class TestSettingsServiceIntegration(unittest.TestCase):
```

Full integration: build_from_specs → file on disk → load → typed object.

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_creates_default_file_and_loads_on_first_run(self)
```

```python
def test_loads_existing_file(self)
```

```python
def test_get_returns_cached_instance(self)
```

```python
def test_reload_returns_fresh_instance(self)
```

```python
def test_save_persists_to_file(self)
```

```python
def test_not_enum_key_raises(self)
```

## `test_tool_changer_settings.py`

Source: [tests/engine/settings/test_tool_changer_settings.py](../../../../tests/engine/settings/test_tool_changer_settings.py).

Imports (including optional/function-local imports; not a startup dependency list): `src.engine.robot.configuration.tool_changer_settings`, `src.engine.robot.interfaces.tool_definition`, `src.engine.robot.tool_changer`, `unittest`.

### `ToolChangerSettingsSerializerTests`

```python
class ToolChangerSettingsSerializerTests(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_round_trip_preserves_geometry_and_sequences(self)
```

```python
def test_old_shape_remains_loadable(self)
```
