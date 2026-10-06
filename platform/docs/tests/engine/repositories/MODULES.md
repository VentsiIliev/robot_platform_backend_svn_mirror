# Module reference: `tests/engine/repositories`

[Package guide](README.md) · [Complete source index](../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [fixtures.py](#fixturespy)
- [test_base_json_settings_repository.py](#test_base_json_settings_repositorypy)
- [test_settings_service.py](#test_settings_servicepy)
- [test_settings_service_factory.py](#test_settings_service_factorypy)

## `__init__.py`

Source: [tests/engine/repositories/__init__.py](../../../../tests/engine/repositories/__init__.py).

No top-level functions, classes or public value declarations; inspect the source for imports or entry-point statements.

## `fixtures.py`

Source: [tests/engine/repositories/fixtures.py](../../../../tests/engine/repositories/fixtures.py).

Imports (including optional/function-local imports; not a startup dependency list): `enum`.

### `SettingsIDTestEnum`

```python
class SettingsIDTestEnum(str, Enum):
```

Declared fields/defaults:

```python
A = 'a'
B = 'b'
C = 'c'
```

## `test_base_json_settings_repository.py`

Source: [tests/engine/repositories/test_base_json_settings_repository.py](../../../../tests/engine/repositories/test_base_json_settings_repository.py).

Unit tests for BaseJsonSettingsRepository. Covered: - No file_path → returns serializer default (no disk access) - Missing file → creates file with defaults and returns them - Existing valid JSON → deserializes via serializer.from_dict - Corrupt JSON (JSONDecodeError) → returns default, does NOT raise - Empty file → treated as corrupt, returns default, does NOT raise - save() writes serialized JSON to disk - save() creates intermediate directories - save() raises SettingsSaveError when no file_path is set - exists() returns False when no path, file missing, or file present

Imports (including optional/function-local imports; not a startup dependency list): `dataclasses`, `json`, `os`, `src.engine.repositories.interfaces`, `src.engine.repositories.json.base_json_settings_repository`, `tempfile`, `typing`, `unittest`.

### `_Config`

```python
@dataclass
class _Config:
```

Declared fields/defaults:

```python
name: str = 'default'
count: int = 0
```

### `_Serializer`

```python
class _Serializer(ISettingsSerializer[_Config]):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
@property
def settings_type(self) -> str
```

```python
def get_default(self) -> _Config
```

```python
def to_dict(self, settings: _Config) -> Dict[str, Any]
```

```python
def from_dict(self, data: Dict[str, Any]) -> _Config
```

### `TestLoadNoFilePath`

```python
class TestLoadNoFilePath(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_returns_default_when_no_file_path(self)
```

### `TestLoadMissingFile`

```python
class TestLoadMissingFile(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_creates_file_with_defaults_when_missing(self)
```

```python
def test_created_file_contains_valid_json(self)
```

### `TestLoadExistingFile`

```python
class TestLoadExistingFile(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_loads_and_deserializes_existing_file(self)
```

```python
def test_partial_json_uses_from_dict_defaults(self)
```

### `TestLoadCorruptFile`

```python
class TestLoadCorruptFile(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_corrupt_json_returns_default_without_raising(self)
```

```python
def test_empty_file_returns_default_without_raising(self)
```

### `TestSave`

```python
class TestSave(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_save_writes_json_to_disk(self)
```

```python
def test_save_roundtrip_via_load(self)
```

```python
def test_save_creates_intermediate_directories(self)
```

```python
def test_save_raises_settings_save_error_when_no_file_path(self)
```

### `TestExists`

```python
class TestExists(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_exists_false_when_no_file_path(self)
```

```python
def test_exists_false_when_file_not_on_disk(self)
```

```python
def test_exists_true_when_file_present(self)
```

## `test_settings_service.py`

Source: [tests/engine/repositories/test_settings_service.py](../../../../tests/engine/repositories/test_settings_service.py).

Unit tests for SettingsService. These are pure unit tests — all repositories are mocked, no disk I/O. Covered: - get() caches on the first load and returns cache on subsequent calls - reload() always calls repo.load() regardless of cache - save() persists via repo and updates the in-memory cache - Unknown key raises KeyError on get(), reload(), save(), and get_repo() - get_repo() returns the repository instance

Imports (including optional/function-local imports; not a startup dependency list): `src.engine.repositories.settings_service`, `tests.engine.repositories.test_settings_service_factory`, `unittest`, `unittest.mock`.

### `_make_repo`

```python
def _make_repo(load_value=None)
```

### `TestSettingsServiceCaching`

```python
class TestSettingsServiceCaching(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_get_calls_repo_load_on_first_access(self)
```

```python
def test_get_returns_cached_value_on_second_call(self)
```

```python
def test_reload_bypasses_cache_and_calls_repo(self)
```

```python
def test_reload_updates_cache(self)
```

### `TestSettingsServiceSave`

```python
class TestSettingsServiceSave(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_save_calls_repo_save(self)
```

```python
def test_save_updates_cache_so_get_skips_reload(self)
```

```python
def test_save_then_get_returns_saved_value(self)
```

### `TestSettingsServiceGetRepo`

```python
class TestSettingsServiceGetRepo(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_get_repo_returns_correct_repository(self)
```

## `test_settings_service_factory.py`

Source: [tests/engine/repositories/test_settings_service_factory.py](../../../../tests/engine/repositories/test_settings_service_factory.py).

Unit tests for settings_service_factory.build_from_specs() in isolation. Covered: - Returns a SettingsService instance - Lowercased class name used as storage subdirectory - One repository created per SettingsSpec - Multiple specs all accessible by name - Empty spec list produces a service that raises KeyError for any key - Absolute settings_root is used directly (no extra path resolution)

Imports (including optional/function-local imports; not a startup dependency list): `dataclasses`, `enum`, `os`, `src.engine.repositories.interfaces`, `src.engine.repositories.settings_service`, `src.engine.repositories.settings_service_factory`, `src.shared_contracts.declarations`, `tempfile`, `typing`, `unittest`.

### `SettingsIDTestEnum`

```python
class SettingsIDTestEnum(str, Enum):
```

Declared fields/defaults:

```python
A = 'a'
B = 'b'
C = 'c'
```

### `_Cfg`

```python
@dataclass
class _Cfg:
```

Declared fields/defaults:

```python
value: str = 'default'
```

### `_Ser`

```python
class _Ser(ISettingsSerializer[_Cfg]):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
@property
def settings_type(self) -> str
```

```python
def get_default(self) -> _Cfg
```

```python
def to_dict(self, s: _Cfg) -> Dict[str, Any]
```

```python
def from_dict(self, d: Dict[str, Any]) -> _Cfg
```

### `FakeSystem`

```python
class FakeSystem:
```

Dummy robot vision_service class — name resolves to 'fakesystem'.

### `AnotherSystem`

```python
class AnotherSystem:
```

A second vision_service class — name resolves to 'anothersystem'.

### `TestBuildFromSpecsReturnType`

```python
class TestBuildFromSpecsReturnType(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_returns_settings_service_instance(self)
```

### `TestBuildFromSpecsDirectoryNaming`

```python
class TestBuildFromSpecsDirectoryNaming(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_uses_lowercased_class_name_as_subdirectory(self)
```

```python
def test_different_system_classes_use_different_subdirs(self)
```

```python
def test_storage_key_used_as_relative_filename(self)
```

### `TestBuildFromSpecsMultipleSpecs`

```python
class TestBuildFromSpecsMultipleSpecs(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_all_specs_are_accessible_by_name(self)
```

```python
def test_each_spec_gets_its_own_file(self)
```
