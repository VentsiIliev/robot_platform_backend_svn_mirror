# Module reference: `tests/applications/tool_settings`

[Package guide](README.md) · [Complete source index](../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [test_stub_tool_settings_service.py](#test_stub_tool_settings_servicepy)
- [test_tool_settings_application_service.py](#test_tool_settings_application_servicepy)
- [test_tool_settings_controller.py](#test_tool_settings_controllerpy)
- [test_tool_settings_factory.py](#test_tool_settings_factorypy)
- [test_tool_settings_model.py](#test_tool_settings_modelpy)
- [test_tool_settings_view.py](#test_tool_settings_viewpy)

## `__init__.py`

Source: [tests/applications/tool_settings/__init__.py](../../../../tests/applications/tool_settings/__init__.py).

No top-level functions, classes or public value declarations; inspect the source for imports or entry-point statements.

## `test_stub_tool_settings_service.py`

Source: [tests/applications/tool_settings/test_stub_tool_settings_service.py](../../../../tests/applications/tool_settings/test_stub_tool_settings_service.py).

Imports (including optional/function-local imports; not a startup dependency list): `src.applications.tool_settings.service.stub_tool_settings_service`, `unittest`.

### `TestStubToolSettingsServiceTools`

```python
class TestStubToolSettingsServiceTools(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def setUp(self)
```

```python
def test_get_tools_returns_initial_tools(self)
```

```python
def test_add_tool_returns_true_and_message(self)
```

```python
def test_add_tool_appends_to_list(self)
```

```python
def test_update_tool_existing_returns_true(self)
```

```python
def test_update_tool_updates_name(self)
```

```python
def test_update_tool_not_found_returns_false(self)
```

```python
def test_remove_tool_existing_returns_true(self)
```

```python
def test_remove_tool_removes_from_list(self)
```

```python
def test_remove_tool_not_found_returns_false(self)
```

### `TestStubToolSettingsServiceSlots`

```python
class TestStubToolSettingsServiceSlots(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def setUp(self)
```

```python
def test_get_slots_returns_initial_slots(self)
```

```python
def test_update_slot_existing_returns_true(self)
```

```python
def test_update_slot_updates_tool_id(self)
```

```python
def test_update_slot_not_found_returns_false(self)
```

```python
def test_add_slot_returns_true(self)
```

```python
def test_add_slot_appends_to_list(self)
```

```python
def test_remove_slot_existing_returns_true(self)
```

```python
def test_remove_slot_removes_from_list(self)
```

```python
def test_remove_slot_not_found_returns_false(self)
```

## `test_tool_settings_application_service.py`

Source: [tests/applications/tool_settings/test_tool_settings_application_service.py](../../../../tests/applications/tool_settings/test_tool_settings_application_service.py).

Imports (including optional/function-local imports; not a startup dependency list): `src.applications.tool_settings.service.tool_settings_application_service`, `src.engine.common_settings_ids`, `src.engine.robot.configuration`, `src.engine.robot.interfaces.tool_definition`, `src.engine.robot.tool_changer`, `unittest`, `unittest.mock`.

### `_make_tc`

```python
def _make_tc(tools=None, slots=None)
```

### `_make_svc`

```python
def _make_svc(tc=None)
```

### `TestToolSettingsApplicationServiceTools`

```python
class TestToolSettingsApplicationServiceTools(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_get_tools_delegates_to_settings(self)
```

```python
def test_add_tool_duplicate_id_returns_false_no_save(self)
```

```python
def test_add_tool_new_id_returns_true_and_saves(self)
```

```python
def test_add_tool_saves_with_correct_key(self)
```

```python
def test_update_tool_existing_returns_true_and_saves(self)
```

```python
def test_update_tool_not_found_returns_false_no_save(self)
```

```python
def test_remove_tool_assigned_to_slot_returns_false(self)
```

```python
def test_remove_tool_not_found_returns_false(self)
```

```python
def test_remove_tool_success_returns_true_and_saves(self)
```

### `TestToolSettingsApplicationServiceSlots`

```python
class TestToolSettingsApplicationServiceSlots(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_get_slots_delegates_to_settings(self)
```

```python
def test_update_slot_unknown_tool_id_returns_false(self)
```

```python
def test_update_slot_unknown_slot_id_returns_false(self)
```

```python
def test_update_slot_success_saves(self)
```

```python
def test_update_slot_none_unassigns(self)
```

```python
def test_add_slot_duplicate_id_returns_false(self)
```

```python
def test_add_slot_unknown_tool_id_returns_false(self)
```

```python
def test_add_slot_with_valid_tool_saves(self)
```

```python
def test_add_slot_with_none_tool_saves(self)
```

```python
def test_remove_slot_not_found_returns_false(self)
```

```python
def test_remove_slot_success_returns_true_and_saves(self)
```

```python
def test_update_slot_sequences_persists_typed_steps(self)
```

### `TestToolSettingsApplicationServiceCalibration`

```python
class TestToolSettingsApplicationServiceCalibration(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_update_tool_geometry_persists_relative_transform(self)
```

## `test_tool_settings_controller.py`

Source: [tests/applications/tool_settings/test_tool_settings_controller.py](../../../../tests/applications/tool_settings/test_tool_settings_controller.py).

Imports (including optional/function-local imports; not a startup dependency list): `PyQt6.QtWidgets`, `src.applications.tool_settings.controller.tool_settings_controller`, `src.applications.tool_settings.model.tool_settings_model`, `src.applications.tool_settings.view.tool_settings_view`, `src.engine.robot.interfaces.tool_definition`, `src.engine.robot.tool_changer`, `sys`, `unittest`, `unittest.mock`.

### `_make_model`

```python
def _make_model(tools=None, slots=None)
```

### `_make_view`

```python
def _make_view()
```

### `_make_ctrl`

```python
def _make_ctrl(tools=None, slots=None)
```

### `TestToolSettingsControllerLoad`

```python
class TestToolSettingsControllerLoad(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
@classmethod
def setUpClass(cls)
```

```python
def test_load_connects_all_view_signals(self)
```

```python
def test_load_triggers_refresh(self)
```

```python
def test_successful_reference_capture_resets_samples_and_updates_progress(self)
```

```python
def test_successful_candidate_capture_increments_progress(self)
```

```python
def test_start_over_resets_guided_progress(self)
```

### `TestToolSettingsControllerRefresh`

```python
class TestToolSettingsControllerRefresh(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_refresh_passes_tools_to_view(self)
```

```python
def test_refresh_passes_slots_and_tools_to_view(self)
```

```python
def test_refresh_status_contains_tool_and_slot_counts(self)
```

### `TestToolSettingsControllerOnAdd`

```python
class TestToolSettingsControllerOnAdd(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
@classmethod
def setUpClass(cls)
```

```python
@patch(f'{_CTRL_MOD}._ToolDialog')
def test_rejected_dialog_does_not_call_model(self, MockDialog)
```

```python
@patch(f'{_CTRL_MOD}._ToolDialog')
def test_accepted_dialog_calls_add_tool(self, MockDialog)
```

```python
@patch(f'{_CTRL_MOD}._ToolDialog')
def test_success_triggers_refresh(self, MockDialog)
```

```python
@patch(f'{_CTRL_MOD}.show_warning')
@patch(f'{_CTRL_MOD}._ToolDialog')
def test_failure_shows_warning_no_refresh(self, MockDialog, mock_warn)
```

### `TestToolSettingsControllerOnEdit`

```python
class TestToolSettingsControllerOnEdit(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
@classmethod
def setUpClass(cls)
```

```python
@patch(f'{_CTRL_MOD}._ToolDialog')
def test_rejected_dialog_does_not_call_model(self, MockDialog)
```

```python
@patch(f'{_CTRL_MOD}._ToolDialog')
def test_accepted_calls_update_tool_with_new_name(self, MockDialog)
```

```python
@patch(f'{_CTRL_MOD}.show_warning')
@patch(f'{_CTRL_MOD}._ToolDialog')
def test_failure_shows_warning(self, MockDialog, mock_warn)
```

### `TestToolSettingsControllerOnRemove`

```python
class TestToolSettingsControllerOnRemove(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
@classmethod
def setUpClass(cls)
```

```python
@patch(f'{_CTRL_MOD}.ask_yes_no')
def test_cancelled_does_not_call_model(self, mock_ask)
```

```python
@patch(f'{_CTRL_MOD}.ask_yes_no')
def test_confirmed_calls_remove_tool(self, mock_ask)
```

```python
@patch(f'{_CTRL_MOD}.show_warning')
@patch(f'{_CTRL_MOD}.ask_yes_no')
def test_failure_shows_warning(self, mock_ask, mock_warn)
```

### `TestToolSettingsControllerOnAddSlot`

```python
class TestToolSettingsControllerOnAddSlot(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
@classmethod
def setUpClass(cls)
```

```python
@patch(f'{_CTRL_MOD}.show_warning')
def test_no_tools_shows_warning_and_aborts(self, mock_warn)
```

```python
@patch(f'{_CTRL_MOD}._SlotDialog')
def test_rejected_dialog_does_not_call_model(self, MockDialog)
```

```python
@patch(f'{_CTRL_MOD}._SlotDialog')
def test_accepted_calls_add_slot(self, MockDialog)
```

```python
@patch(f'{_CTRL_MOD}.show_warning')
@patch(f'{_CTRL_MOD}._SlotDialog')
def test_failure_shows_warning(self, MockDialog, mock_warn)
```

### `TestToolSettingsControllerOnRemoveSlot`

```python
class TestToolSettingsControllerOnRemoveSlot(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
@classmethod
def setUpClass(cls)
```

```python
@patch(f'{_CTRL_MOD}.ask_yes_no')
def test_cancelled_does_not_call_model(self, mock_ask)
```

```python
@patch(f'{_CTRL_MOD}.ask_yes_no')
def test_confirmed_calls_remove_slot(self, mock_ask)
```

```python
@patch(f'{_CTRL_MOD}.show_warning')
@patch(f'{_CTRL_MOD}.ask_yes_no')
def test_failure_shows_warning(self, mock_ask, mock_warn)
```

### `TestToolSettingsControllerOnSaveSlots`

```python
class TestToolSettingsControllerOnSaveSlots(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
@classmethod
def setUpClass(cls)
```

```python
def test_calls_update_slot_for_each_assignment(self)
```

```python
def test_all_success_sets_saved_status(self)
```

```python
def test_empty_list_sets_saved_status(self)
```

```python
@patch(f'{_CTRL_MOD}.show_warning')
def test_partial_failure_shows_warning(self, mock_warn)
```

```python
@patch(f'{_CTRL_MOD}.show_warning')
def test_all_failure_shows_warning_no_refresh(self, mock_warn)
```

### `TestToolSettingsControllerOnEditSlot`

```python
class TestToolSettingsControllerOnEditSlot(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
@classmethod
def setUpClass(cls)
```

```python
@patch(f'{_CTRL_MOD}.show_warning')
def test_no_tools_shows_warning_and_aborts(self, mock_warn)
```

```python
@patch(f'{_CTRL_MOD}._SlotDialog')
def test_rejected_dialog_does_not_call_model(self, MockDialog)
```

```python
@patch(f'{_CTRL_MOD}._SlotDialog')
def test_accepted_calls_update_slot(self, MockDialog)
```

```python
@patch(f'{_CTRL_MOD}.show_warning')
@patch(f'{_CTRL_MOD}._SlotDialog')
def test_failure_shows_warning(self, MockDialog, mock_warn)
```

## `test_tool_settings_factory.py`

Source: [tests/applications/tool_settings/test_tool_settings_factory.py](../../../../tests/applications/tool_settings/test_tool_settings_factory.py).

Imports (including optional/function-local imports; not a startup dependency list): `PyQt6.QtWidgets`, `src.applications.tool_settings.controller.tool_settings_controller`, `src.applications.tool_settings.service.i_tool_settings_service`, `src.applications.tool_settings.tool_settings_factory`, `src.applications.tool_settings.view.tool_settings_view`, `src.engine.robot.interfaces.tool_definition`, `src.engine.robot.tool_changer`, `sys`, `unittest`, `unittest.mock`.

### `_make_service`

```python
def _make_service()
```

### `TestToolSettingsFactory`

```python
class TestToolSettingsFactory(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_view_enables_shared_jog_widget(self)
```

```python
@classmethod
def setUpClass(cls)
```

```python
def test_build_returns_tool_settings_view(self)
```

```python
def test_build_attaches_controller_to_view(self)
```

```python
def test_build_calls_get_tools_via_load(self)
```

```python
def test_build_calls_get_slots_via_load(self)
```

```python
def test_two_builds_produce_independent_views(self)
```

## `test_tool_settings_model.py`

Source: [tests/applications/tool_settings/test_tool_settings_model.py](../../../../tests/applications/tool_settings/test_tool_settings_model.py).

Imports (including optional/function-local imports; not a startup dependency list): `src.applications.tool_settings.model.tool_settings_model`, `src.applications.tool_settings.service.i_tool_settings_service`, `src.engine.robot.interfaces.tool_definition`, `src.engine.robot.tool_changer`, `unittest`, `unittest.mock`.

### `_make_service`

```python
def _make_service()
```

### `TestToolSettingsModelLoad`

```python
class TestToolSettingsModelLoad(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_load_returns_tools_list(self)
```

```python
def test_load_calls_get_tools(self)
```

### `TestToolSettingsModelSave`

```python
class TestToolSettingsModelSave(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_save_with_no_args_returns_none(self)
```

```python
def test_save_with_arbitrary_args_returns_none(self)
```

### `TestToolSettingsModelDelegation`

```python
class TestToolSettingsModelDelegation(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def setUp(self)
```

```python
def test_get_tools_delegates_and_returns(self)
```

```python
def test_get_slots_delegates_and_returns(self)
```

```python
def test_add_tool_delegates_with_args(self)
```

```python
def test_update_tool_delegates_with_args(self)
```

```python
def test_remove_tool_delegates_with_args(self)
```

```python
def test_update_slot_delegates_with_args(self)
```

```python
def test_add_slot_delegates_with_args(self)
```

```python
def test_remove_slot_delegates_with_args(self)
```

## `test_tool_settings_view.py`

Source: [tests/applications/tool_settings/test_tool_settings_view.py](../../../../tests/applications/tool_settings/test_tool_settings_view.py).

Imports (including optional/function-local imports; not a startup dependency list): `PyQt6.QtWidgets`, `src.applications.base.widgets.keyboard_number_field`, `src.applications.tool_settings.controller.tool_settings_controller`, `src.applications.tool_settings.view.tool_settings_view`, `src.engine.robot.interfaces.tool_definition`, `src.engine.robot.tool_changer`, `sys`, `unittest`.

### `TestToolSettingsViewSetTools`

```python
class TestToolSettingsViewSetTools(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
@classmethod
def setUpClass(cls)
```

```python
def test_set_tools_populates_rows(self)
```

```python
def test_set_tools_replaces_previous_rows(self)
```

```python
def test_set_tools_empty_clears_table(self)
```

```python
def test_set_tools_displays_id_in_column_0(self)
```

```python
def test_set_tools_displays_name_in_column_1(self)
```

### `TestToolSettingsViewSetSlots`

```python
class TestToolSettingsViewSetSlots(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
@classmethod
def setUpClass(cls)
```

```python
def test_set_slots_populates_rows(self)
```

```python
def test_set_slots_replaces_previous_rows(self)
```

```python
def test_set_slots_displays_slot_id_in_column_0(self)
```

### `TestToolSettingsViewSetStatus`

```python
class TestToolSettingsViewSetStatus(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
@classmethod
def setUpClass(cls)
```

```python
def test_set_status_updates_label(self)
```

```python
def test_set_status_empty_string(self)
```

```python
def test_calibration_progress_guides_user_to_next_step(self)
```

```python
def test_solve_is_enabled_after_three_samples_and_tool_selection(self)
```

### `TestToolSettingsViewSelectedTool`

```python
class TestToolSettingsViewSelectedTool(unittest.TestCase):
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
def test_no_selection_returns_none_none(self)
```

```python
def test_selected_row_returns_id_and_name(self)
```

### `TestToolSettingsViewButtonStates`

```python
class TestToolSettingsViewButtonStates(unittest.TestCase):
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
def test_edit_and_remove_tool_buttons_disabled_initially(self)
```

```python
def test_edit_and_remove_tool_buttons_enabled_after_selection(self)
```

```python
def test_edit_and_remove_slot_buttons_disabled_initially(self)
```

```python
def test_edit_and_remove_slot_buttons_enabled_after_selection(self)
```

### `TestToolSettingsViewSignals`

```python
class TestToolSettingsViewSignals(unittest.TestCase):
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
def test_add_tool_button_emits_add_tool_requested(self)
```

```python
def test_add_slot_button_emits_add_slot_requested(self)
```

```python
def test_remove_tool_button_emits_with_selected_id(self)
```

```python
def test_edit_tool_button_emits_with_id_and_name(self)
```

```python
def test_remove_slot_button_emits_with_selected_slot_id(self)
```

```python
def test_edit_slot_button_emits_with_slot_and_tool_id(self)
```

```python
def test_save_button_emits_save_slots_requested_with_assignments(self)
```

```python
def test_clean_up_returns_none(self)
```

```python
def test_tabs_separate_tools_slots_and_calibration(self)
```

```python
def test_discard_restores_loaded_slot_assignment(self)
```

```python
def test_calibration_selector_controls_solve_target(self)
```

```python
def test_edit_dialogs_use_shared_touch_number_fields(self)
```
