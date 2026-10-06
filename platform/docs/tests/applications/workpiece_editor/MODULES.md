# Module reference: `tests/applications/workpiece_editor`

[Package guide](README.md) · [Complete source index](../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [test_workpiece_editor_controller_matching.py](#test_workpiece_editor_controller_matchingpy)
- [test_workpiece_editor_factory.py](#test_workpiece_editor_factorypy)
- [test_workpiece_editor_model.py](#test_workpiece_editor_modelpy)
- [test_workpiece_editor_service.py](#test_workpiece_editor_servicepy)
- [test_workpiece_editor_view.py](#test_workpiece_editor_viewpy)
- [test_workpiece_matcher_contract.py](#test_workpiece_matcher_contractpy)

## `__init__.py`

Source: [tests/applications/workpiece_editor/__init__.py](../../../../tests/applications/workpiece_editor/__init__.py).

No top-level functions, classes or public value declarations; inspect the source for imports or entry-point statements.

## `test_workpiece_editor_controller_matching.py`

Source: [tests/applications/workpiece_editor/test_workpiece_editor_controller_matching.py](../../../../tests/applications/workpiece_editor/test_workpiece_editor_controller_matching.py).

Imports (including optional/function-local imports; not a startup dependency list): `logging`, `numpy`, `src.applications.workpiece_editor.controller.workpiece_editor_controller`, `unittest`, `unittest.mock`.

### `TestWorkpieceEditorCaptureMatching`

```python
class TestWorkpieceEditorCaptureMatching(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def setUp(self) -> None
```

```python
def test_success_returns_aligned_saved_workpiece_and_payload(self) -> None
```

```python
def test_failure_returns_matcher_diagnostic_for_capture_message(self) -> None
```

```python
def test_form_context_preserves_exact_camera_contour_for_matching(self) -> None
```

## `test_workpiece_editor_factory.py`

Source: [tests/applications/workpiece_editor/test_workpiece_editor_factory.py](../../../../tests/applications/workpiece_editor/test_workpiece_editor_factory.py).

Imports (including optional/function-local imports; not a startup dependency list): `PyQt6.QtWidgets`, `src.applications.workpiece_editor.controller.workpiece_editor_controller`, `src.applications.workpiece_editor.editor_core.config.workpiece_form_schema`, `src.applications.workpiece_editor.service.i_workpiece_editor_service`, `src.applications.workpiece_editor.view.workpiece_editor_view`, `src.applications.workpiece_editor.workpiece_editor_factory`, `src.engine.core.i_messaging_service`, `sys`, `unittest`, `unittest.mock`.

### `_make_service`

```python
def _make_service()
```

### `_make_factory`

```python
def _make_factory()
```

### `TestWorkpieceEditorFactory`

```python
class TestWorkpieceEditorFactory(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
@classmethod
def setUpClass(cls)
```

```python
def test_create_view_raises_not_implemented(self)
```

```python
def test_build_returns_workpiece_editor_view(self)
```

```python
def test_build_attaches_controller_to_view(self)
```

```python
def test_build_calls_get_form_schema(self)
```

```python
def test_build_calls_get_segment_config(self)
```

```python
def test_controller_uses_messaging_from_build(self)
```

```python
def test_two_builds_produce_independent_views(self)
```

## `test_workpiece_editor_model.py`

Source: [tests/applications/workpiece_editor/test_workpiece_editor_model.py](../../../../tests/applications/workpiece_editor/test_workpiece_editor_model.py).

Imports (including optional/function-local imports; not a startup dependency list): `src.applications.workpiece_editor.model`, `src.applications.workpiece_editor.service`, `unittest`, `unittest.mock`.

### `_make_service`

```python
def _make_service()
```

### `TestWorkpieceEditorModelNoOps`

```python
class TestWorkpieceEditorModelNoOps(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_load_returns_none_and_does_not_touch_service(self)
```

```python
def test_save_no_args_returns_none_and_does_not_touch_service(self)
```

```python
def test_save_with_args_returns_none_and_does_not_touch_service(self)
```

### `TestWorkpieceEditorModelDelegation`

```python
class TestWorkpieceEditorModelDelegation(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def setUp(self)
```

```python
def test_get_contours_delegates_and_returns(self)
```

```python
def test_save_workpiece_delegates_with_data(self)
```

```python
def test_save_workpiece_returns_service_result(self)
```

```python
def test_execute_workpiece_delegates_with_data(self)
```

```python
def test_execute_workpiece_returns_service_result(self)
```

```python
def test_set_editing_delegates_with_id(self)
```

```python
def test_set_editing_delegates_with_none(self)
```

## `test_workpiece_editor_service.py`

Source: [tests/applications/workpiece_editor/test_workpiece_editor_service.py](../../../../tests/applications/workpiece_editor/test_workpiece_editor_service.py).

Imports (including optional/function-local imports; not a startup dependency list): `numpy`, `src.applications.workpiece_editor.editor_core.config.workpiece_form_schema`, `src.applications.workpiece_editor.editor_core.handlers.SaveWorkpieceHandler`, `src.applications.workpiece_editor.service.workpiece_editor_service`, `src.engine.robot.path_preparation.default_workpiece_path_preparation_service`, `src.engine.robot.path_preparation.geometry`, `unittest`, `unittest.mock`.

### `_schema`

```python
def _schema(*required_keys)
```

### `_make_svc`

```python
def _make_svc(vision=None, save_fn=None, update_fn=None, schema=None, id_exists_fn=None)
```

### `TestHasValidContour`

```python
class TestHasValidContour(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_none_returns_false(self)
```

```python
def test_numpy_one_point_returns_false(self)
```

```python
def test_numpy_three_points_returns_true(self)
```

```python
def test_list_two_elements_returns_false(self)
```

```python
def test_list_three_elements_returns_true(self)
```

```python
def test_other_type_returns_false(self)
```

### `TestSaveWorkpieceHandlerValidate`

```python
class TestSaveWorkpieceHandlerValidate(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_all_keys_present_returns_true(self)
```

```python
def test_missing_key_returns_false(self)
```

```python
def test_empty_value_treated_as_missing(self)
```

```python
def test_no_required_keys_always_valid(self)
```

```python
def test_multiple_missing_keys_reported(self)
```

### `TestWorkpieceEditorServiceGetters`

```python
class TestWorkpieceEditorServiceGetters(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_get_form_schema_direct_instance(self)
```

```python
def test_get_form_schema_callable_is_called(self)
```

```python
def test_get_segment_config_returns_stored_config(self)
```

```python
def test_set_editing_stores_id(self)
```

```python
def test_set_editing_none_clears_id(self)
```

### `TestWorkpieceEditorServiceGetContours`

```python
class TestWorkpieceEditorServiceGetContours(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_no_vision_returns_empty_list(self)
```

```python
def test_with_vision_delegates_and_returns(self)
```

```python
def test_vision_exception_returns_empty_list(self)
```

### `TestWorkpieceEditorServiceSave`

```python
class TestWorkpieceEditorServiceSave(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_missing_required_field_returns_false(self)
```

```python
def test_missing_contour_returns_false(self)
```

```python
def test_valid_data_calls_save_fn(self)
```

```python
def test_save_fn_result_is_returned(self)
```

```python
def test_editing_id_set_calls_update_fn(self)
```

```python
def test_editing_id_cleared_after_successful_update(self)
```

```python
def test_duplicate_workpiece_id_returns_false(self)
```

```python
def test_id_check_skipped_when_form_has_no_id(self)
```

```python
def test_save_fn_exception_returns_false(self)
```

```python
def test_non_contour_editor_data_falls_back_to_form_data(self)
```

### `TestWorkpieceEditorServiceExecute`

```python
class TestWorkpieceEditorServiceExecute(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_projection_source_preview_uses_exact_job_pivot_source_path(self)
```

```python
def test_returns_true_with_success_message(self)
```

## `test_workpiece_editor_view.py`

Source: [tests/applications/workpiece_editor/test_workpiece_editor_view.py](../../../../tests/applications/workpiece_editor/test_workpiece_editor_view.py).

Imports (including optional/function-local imports; not a startup dependency list): `PyQt6.QtWidgets`, `src.applications.workpiece_editor.editor_core.config.workpiece_form_schema`, `src.applications.workpiece_editor.view.workpiece_editor_view`, `sys`, `unittest`, `unittest.mock`.

### `_make_view`

```python
def _make_view()
```

### `TestWorkpieceEditorViewConstruction`

```python
class TestWorkpieceEditorViewConstruction(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
@classmethod
def setUpClass(cls)
```

```python
def test_can_be_constructed_without_raising(self)
```

```python
def test_editor_attribute_exists_after_construction(self)
```

### `TestWorkpieceEditorViewSignals`

```python
class TestWorkpieceEditorViewSignals(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
@classmethod
def setUpClass(cls)
```

```python
def setUp(self)
```

```python
def test_on_save_cb_emits_save_requested(self)
```

```python
def test_on_execute_cb_emits_execute_requested(self)
```

```python
def test_on_custom_action_cb_emits_action_id(self)
```

```python
def test_on_camera_feed_cb_returns_none(self)
```

### `TestWorkpieceEditorViewCaptureHandler`

```python
class TestWorkpieceEditorViewCaptureHandler(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
@classmethod
def setUpClass(cls)
```

```python
def setUp(self)
```

```python
def test_capture_cb_returns_empty_without_handler(self)
```

```python
def test_set_capture_handler_is_called_on_capture(self)
```

```python
def test_handler_returning_none_yields_empty_list(self)
```

```python
def test_handler_exception_returns_empty_list(self)
```

### `TestWorkpieceEditorViewPublicApi`

```python
class TestWorkpieceEditorViewPublicApi(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
@classmethod
def setUpClass(cls)
```

```python
def setUp(self)
```

```python
def test_update_camera_feed_none_image_is_noop(self)
```

```python
def test_update_camera_feed_no_editor_is_noop(self)
```

```python
def test_update_camera_feed_calls_set_image_when_editor_present(self)
```

```python
def test_update_camera_feed_editor_without_set_image_is_noop(self)
```

```python
def test_update_contours_no_editor_is_noop(self)
```

```python
def test_update_contours_calls_set_contours_on_inner_editor(self)
```

```python
def test_update_contours_attribute_error_is_silenced(self)
```

```python
def test_clean_up_with_no_editor_is_noop(self)
```

```python
def test_clean_up_with_mock_editor_sets_editor_to_none(self)
```

```python
def test_clean_up_disconnects_event_bus_signals(self)
```

## `test_workpiece_matcher_contract.py`

Source: [tests/applications/workpiece_editor/test_workpiece_matcher_contract.py](../../../../tests/applications/workpiece_editor/test_workpiece_matcher_contract.py).

Imports (including optional/function-local imports; not a startup dependency list): `src.applications.workpiece_editor.i_workpiece_matcher`, `src.robot_systems.glue.domain.matching.i_matching_service`, `src.robot_systems.paint.processes.paint.match.workpiece_matching_service`, `unittest`.

### `TestWorkpieceMatcherContract`

```python
class TestWorkpieceMatcherContract(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_glue_matching_contract_preserves_editor_capabilities(self)
```

```python
def test_paint_matching_service_implements_editor_contract(self)
```
