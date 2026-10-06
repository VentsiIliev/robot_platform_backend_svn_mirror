# Module reference: `tests/applications/workpiece_library`

[Package guide](README.md) · [Complete source index](../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [test_matching_selection.py](#test_matching_selectionpy)
- [test_workpiece_library_controller.py](#test_workpiece_library_controllerpy)
- [test_workpiece_library_model.py](#test_workpiece_library_modelpy)
- [test_workpiece_library_service.py](#test_workpiece_library_servicepy)
- [test_workpiece_thumbnail.py](#test_workpiece_thumbnailpy)

## `__init__.py`

Source: [tests/applications/workpiece_library/__init__.py](../../../../tests/applications/workpiece_library/__init__.py).

No top-level functions, classes or public value declarations; inspect the source for imports or entry-point statements.

## `test_matching_selection.py`

Source: [tests/applications/workpiece_library/test_matching_selection.py](../../../../tests/applications/workpiece_library/test_matching_selection.py).

Imports (including optional/function-local imports; not a startup dependency list): `PyQt6.QtCore`, `PyQt6.QtWidgets`, `os`, `pathlib`, `src.applications.workpiece_library.controller.workpiece_library_controller`, `src.applications.workpiece_library.domain.workpiece_schema`, `src.applications.workpiece_library.model.workpiece_library_model`, `src.applications.workpiece_library.service.stub_workpiece_library_service`, `src.applications.workpiece_library.view.workpiece_library_view`, `src.applications.workpiece_library.workpiece_thumbnail`, `src.robot_systems.paint.domain.workpieces.matching_selection`, `tempfile`, `unittest`, `unittest.mock`.

### `TestMatchingSelectionView`

```python
class TestMatchingSelectionView(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
@classmethod
def setUpClass(cls)
```

```python
def test_checked_workpieces_survive_search_and_save_automatically(self)
```

```python
def test_clear_checkbox_and_select_all_persist_without_apply(self)
```

## `test_workpiece_library_controller.py`

Source: [tests/applications/workpiece_library/test_workpiece_library_controller.py](../../../../tests/applications/workpiece_library/test_workpiece_library_controller.py).

Imports (including optional/function-local imports; not a startup dependency list): `src.applications.workpiece_library.controller.workpiece_library_controller`, `src.applications.workpiece_library.domain.workpiece_schema`, `unittest`, `unittest.mock`.

### `TestWorkpieceLibraryController`

```python
class TestWorkpieceLibraryController(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_selection_changes_save_without_apply_button(self)
```

```python
def test_show_selected_combines_with_search(self)
```

```python
@patch('src.applications.workpiece_library.controller.workpiece_library_controller.ask_yes_no', return_value=True)
def test_delete_refreshes_controller_cache_used_by_search(self, _ask_yes_no)
```

## `test_workpiece_library_model.py`

Source: [tests/applications/workpiece_library/test_workpiece_library_model.py](../../../../tests/applications/workpiece_library/test_workpiece_library_model.py).

Tests for src/applications/workpiece_library/model/workpiece_library_model.y_pixels

Imports (including optional/function-local imports; not a startup dependency list): `src.applications.workpiece_library.domain.workpiece_schema`, `src.applications.workpiece_library.model.workpiece_library_model`, `src.applications.workpiece_library.service.i_workpiece_library_service`, `unittest`, `unittest.mock`.

### `_make_schema`

```python
def _make_schema()
```

### `_record`

```python
def _record(wp_id: str)
```

### `_make_service`

```python
def _make_service(records=None)
```

### `TestWorkpieceLibraryModelDelegation`

```python
class TestWorkpieceLibraryModelDelegation(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_load_delegates_to_service_list_all(self)
```

```python
def test_load_returns_records(self)
```

```python
def test_get_all_returns_cached_records_after_load(self)
```

```python
def test_delete_delegates_to_service(self)
```

```python
def test_delete_success_refreshes_records(self)
```

```python
def test_delete_failure_does_not_refresh(self)
```

```python
def test_update_delegates_to_service(self)
```

```python
def test_get_thumbnail_delegates_to_service(self)
```

```python
def test_load_raw_delegates_to_service(self)
```

```python
def test_schema_provided_at_construction(self)
```

```python
def test_save_is_no_op(self)
```

## `test_workpiece_library_service.py`

Source: [tests/applications/workpiece_library/test_workpiece_library_service.py](../../../../tests/applications/workpiece_library/test_workpiece_library_service.py).

Tests for workpiece_library service layer. Covers: - StubWorkpieceLibraryService — interface compliance + in-memory CRUD behaviour

Imports (including optional/function-local imports; not a startup dependency list): `src.applications.workpiece_library.domain.workpiece_schema`, `src.applications.workpiece_library.service.stub_workpiece_library_service`, `unittest`.

### `TestStubWorkpieceLibraryServiceSchema`

```python
class TestStubWorkpieceLibraryServiceSchema(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_get_schema_exposes_expected_id_and_name_keys(self)
```

### `TestWorkpieceLibraryServiceListAll`

```python
class TestWorkpieceLibraryServiceListAll(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def setUp(self)
```

```python
def test_list_all_returns_list(self)
```

```python
def test_list_all_returns_workpiece_records(self)
```

```python
def test_list_all_returns_stub_records(self)
```

```python
def test_list_all_returns_copy(self)
```

### `TestWorkpieceLibraryServiceDelete`

```python
class TestWorkpieceLibraryServiceDelete(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def setUp(self)
```

```python
def test_delete_existing_returns_true(self)
```

```python
def test_delete_existing_removes_record(self)
```

```python
def test_delete_not_found_returns_false(self)
```

```python
def test_delete_not_found_does_not_change_list(self)
```

### `TestWorkpieceLibraryServiceUpdate`

```python
class TestWorkpieceLibraryServiceUpdate(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def setUp(self)
```

```python
def test_update_existing_returns_true(self)
```

```python
def test_update_not_found_returns_false(self)
```

### `TestWorkpieceLibraryServiceGetThumbnail`

```python
class TestWorkpieceLibraryServiceGetThumbnail(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_get_thumbnail_returns_none_for_stub(self)
```

```python
def test_get_thumbnail_unknown_id_returns_none(self)
```

### `TestWorkpieceLibraryServiceLoadRaw`

```python
class TestWorkpieceLibraryServiceLoadRaw(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_load_raw_returns_none_for_stub(self)
```

```python
def test_load_raw_unknown_id_returns_none(self)
```

## `test_workpiece_thumbnail.py`

Source: [tests/applications/workpiece_library/test_workpiece_thumbnail.py](../../../../tests/applications/workpiece_library/test_workpiece_thumbnail.py).

Imports (including optional/function-local imports; not a startup dependency list): `hashlib`, `src.applications.workpiece_library.workpiece_thumbnail`, `src.robot_systems.glue.domain.workpieces.workpiece_thumbnail`, `unittest`.

### `TestWorkpieceThumbnail`

```python
class TestWorkpieceThumbnail(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_rendering_matches_pre_extraction_golden_png(self)
```

```python
def test_legacy_glue_import_reexports_shared_renderer(self)
```

```python
def test_returns_none_when_fewer_than_two_points_are_available(self)
```
