# Module reference: `tests/applications/robot_settings`

[Package guide](README.md) · [Complete source index](../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [test_movement_groups_tab.py](#test_movement_groups_tabpy)
- [test_robot_settings_application_service.py](#test_robot_settings_application_servicepy)
- [test_robot_settings_controller.py](#test_robot_settings_controllerpy)
- [test_robot_settings_factory.py](#test_robot_settings_factorypy)
- [test_robot_settings_mapper.py](#test_robot_settings_mapperpy)
- [test_robot_settings_model.py](#test_robot_settings_modelpy)
- [test_targeting_definitions_tab.py](#test_targeting_definitions_tabpy)

## `__init__.py`

Source: [tests/applications/robot_settings/__init__.py](../../../../tests/applications/robot_settings/__init__.py).

No top-level functions, classes or public value declarations; inspect the source for imports or entry-point statements.

## `test_movement_groups_tab.py`

Source: [tests/applications/robot_settings/test_movement_groups_tab.py](../../../../tests/applications/robot_settings/test_movement_groups_tab.py).

Imports (including optional/function-local imports; not a startup dependency list): `PyQt6.QtWidgets`, `src.applications.robot_settings.view.movement_groups_tab`, `src.engine.robot.configuration`, `src.shared_contracts.declarations`, `sys`, `unittest`, `unittest.mock`.

### `TestPositionEditorDialogParse`

```python
class TestPositionEditorDialogParse(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_valid_six_floats(self)
```

```python
def test_empty_string_returns_zeros(self)
```

```python
def test_invalid_string_returns_zeros(self)
```

```python
def test_too_few_values_returns_zeros(self)
```

```python
def test_too_many_values_returns_zeros(self)
```

```python
def test_integer_values_parsed_as_float(self)
```

### `TestMovementGroupsTabInferDef`

```python
class TestMovementGroupsTabInferDef(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_pickup_in_name_gives_multi_position(self)
```

```python
def test_dropoff_in_name_gives_multi_position(self)
```

```python
def test_group_with_position_gives_single_position(self)
```

```python
def test_group_with_points_gives_multi_position(self)
```

```python
def test_group_with_nothing_gives_velocity_only(self)
```

```python
def test_name_preserved(self)
```

### `TestMovementGroupWidgetLoad`

```python
class TestMovementGroupWidgetLoad(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
@classmethod
def setUpClass(cls)
```

```python
def test_load_sets_velocity(self)
```

```python
def test_load_sets_acceleration(self)
```

```python
def test_load_sets_motion_type(self)
```

```python
def test_load_sets_fast_lin_motion_type(self)
```

```python
def test_load_sets_position_display_for_single(self)
```

```python
def test_load_no_position_display_for_multi(self)
```

```python
def test_load_populates_points_list(self)
```

```python
def test_load_clears_previous_points(self)
```

```python
def test_load_sets_iterations(self)
```

```python
def test_load_does_not_emit_signals(self)
```

### `TestMovementGroupWidgetGetValues`

```python
class TestMovementGroupWidgetGetValues(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
@classmethod
def setUpClass(cls)
```

```python
def test_get_values_velocity(self)
```

```python
def test_get_values_acceleration(self)
```

```python
def test_get_values_motion_type(self)
```

```python
def test_get_values_position(self)
```

```python
def test_get_values_points(self)
```

```python
def test_get_values_velocity_only_has_no_position(self)
```

```python
def test_get_values_reflects_has_iterations_flag(self)
```

### `TestMovementGroupWidgetPublicAPI`

```python
class TestMovementGroupWidgetPublicAPI(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
@classmethod
def setUpClass(cls)
```

```python
def test_set_position_updates_display(self)
```

```python
def test_set_position_emits_position_changed(self)
```

```python
def test_add_point_appends_to_list(self)
```

```python
def test_add_point_multiple_appends(self)
```

```python
def test_add_point_emits_points_changed(self)
```

```python
def test_set_position_noop_for_multi(self)
```

```python
def test_add_point_noop_for_single(self)
```

### `TestMovementGroupsTab`

```python
class TestMovementGroupsTab(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
@classmethod
def setUpClass(cls)
```

```python
def test_load_creates_widget_for_each_group(self)
```

```python
def test_get_widget_returns_none_for_unknown(self)
```

```python
def test_get_values_returns_all_groups(self)
```

```python
def test_load_uses_known_definition(self)
```

```python
def test_load_does_not_duplicate_widget(self)
```

```python
def test_add_group_creates_widget(self)
```

```python
def test_add_group_does_not_duplicate(self)
```

```python
def test_remove_group_deletes_widget(self)
```

```python
def test_remove_nonexistent_group_preserves_empty_widget_map(self)
```

```python
def test_set_current_forwarded_from_widget(self)
```

```python
def test_load_with_extra_defs_uses_provided_definition(self)
```

## `test_robot_settings_application_service.py`

Source: [tests/applications/robot_settings/test_robot_settings_application_service.py](../../../../tests/applications/robot_settings/test_robot_settings_application_service.py).

Imports (including optional/function-local imports; not a startup dependency list): `src.applications.robot_settings.service.robot_settings_application_service`, `src.engine.common_settings_ids`, `types`, `unittest`, `unittest.mock`.

### `_make_svc`

```python
def _make_svc(robot=None, nav=None, tool_key=None, tool_settings=None)
```

### `TestGetCurrentPosition`

```python
class TestGetCurrentPosition(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_returns_none_when_no_robot(self)
```

```python
def test_area_tcp_mode_change_preserves_newer_global_calibration(self)
```

```python
def test_delegates_to_robot(self)
```

```python
def test_returns_none_on_robot_exception(self)
```

### `TestGetSlotInfo`

```python
class TestGetSlotInfo(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_returns_empty_when_no_tool_settings_key(self)
```

```python
def test_returns_empty_when_settings_returns_none(self)
```

```python
def test_returns_slot_with_assigned_tool_name(self)
```

```python
def test_returns_none_tool_name_for_unassigned_slot(self)
```

```python
def test_multiple_slots_mixed_assignment(self)
```

```python
def test_returns_empty_on_exception(self)
```

### `TestMoveToGroup`

```python
class TestMoveToGroup(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_returns_false_without_navigation(self)
```

```python
def test_delegates_to_navigation_and_returns_true(self)
```

```python
def test_delegates_to_navigation_and_returns_false(self)
```

```python
def test_returns_false_on_exception(self)
```

### `TestExecuteGroup`

```python
class TestExecuteGroup(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_returns_false_without_navigation(self)
```

```python
def test_calls_move_linear_group_on_navigation(self)
```

```python
def test_returns_false_on_exception(self)
```

### `TestMoveToPoint`

```python
class TestMoveToPoint(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_returns_false_without_navigation(self)
```

```python
def test_parses_and_delegates_six_values(self)
```

```python
def test_returns_false_for_wrong_arg_count(self)
```

```python
def test_returns_false_for_invalid_format(self)
```

```python
def test_returns_false_on_navigation_exception(self)
```

## `test_robot_settings_controller.py`

Source: [tests/applications/robot_settings/test_robot_settings_controller.py](../../../../tests/applications/robot_settings/test_robot_settings_controller.py).

Imports (including optional/function-local imports; not a startup dependency list): `src.applications.robot_settings.controller.robot_settings_controller`, `src.applications.robot_settings.model.mapper`, `src.applications.robot_settings.model.robot_settings_model`, `src.engine.robot.configuration`, `src.shared_contracts.declarations`, `unittest`, `unittest.mock`.

### `_make_view`

```python
def _make_view()
```

### `_make_model`

```python
def _make_model(config=None, calibration=None)
```

### `_make_messaging`

```python
def _make_messaging()
```

### `_make_jog`

```python
def _make_jog()
```

### `_make_ctrl`

```python
def _make_ctrl(model=None, view=None)
```

### `TestRobotSettingsControllerInit`

```python
class TestRobotSettingsControllerInit(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_wires_save_requested_signal(self)
```

```python
def test_wires_destroyed_signal(self)
```

### `TestRobotSettingsControllerLoad`

```python
class TestRobotSettingsControllerLoad(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_load_calls_model_load(self)
```

```python
def test_load_pushes_config_to_view(self)
```

```python
def test_load_pushes_movement_groups_to_view(self)
```

### `TestRobotSettingsControllerSave`

```python
class TestRobotSettingsControllerSave(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_on_save_calls_model_save(self)
```

```python
def test_on_save_passes_flat_dict_from_view(self)
```

```python
def test_on_save_passes_movement_groups_from_view(self)
```

```python
def test_stop_disconnects_motion_bridge_handlers(self)
```

### `TestRobotSettingsControllerInitSignals`

```python
class TestRobotSettingsControllerInitSignals(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_wires_remove_group_requested(self)
```

```python
def test_wires_set_current_requested(self)
```

```python
def test_wires_move_to_requested(self)
```

```python
def test_wires_execute_requested(self)
```

### `TestRobotSettingsControllerAutoSave`

```python
class TestRobotSettingsControllerAutoSave(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_auto_save_calls_model_save(self)
```

```python
def test_auto_save_passes_values_from_view(self)
```

```python
def test_auto_save_passes_movement_groups_from_view(self)
```

```python
def test_auto_save_swallows_exception(self)
```

### `TestRobotSettingsControllerSetCurrent`

```python
class TestRobotSettingsControllerSetCurrent(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
@patch('src.applications.robot_settings.controller.robot_settings_controller.show_warning')
def test_shows_warning_when_position_is_none(self, mock_warn)
```

```python
def test_does_nothing_when_widget_not_found(self)
```

```python
def test_calls_set_position_for_single_position_group(self)
```

```python
def test_calls_add_point_for_multi_position_group(self)
```

### `TestRobotSettingsControllerMotionDone`

```python
class TestRobotSettingsControllerMotionDone(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
@patch('src.applications.robot_settings.controller.robot_settings_controller.show_warning')
def test_shows_warning_on_failure(self, mock_warn)
```

```python
@patch('src.applications.robot_settings.controller.robot_settings_controller.show_warning')
def test_no_warning_on_success(self, mock_warn)
```

### `TestRobotSettingsControllerRemoveGroup`

```python
class TestRobotSettingsControllerRemoveGroup(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
@patch('src.applications.robot_settings.controller.robot_settings_controller.ask_yes_no')
def test_calls_remove_on_confirm(self, mock_ask)
```

```python
@patch('src.applications.robot_settings.controller.robot_settings_controller.ask_yes_no')
def test_does_nothing_on_cancel(self, mock_ask)
```

### `TestRobotSettingsControllerMoveTo`

```python
class TestRobotSettingsControllerMoveTo(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_move_to_calls_auto_save(self)
```

```python
def test_move_to_single_pos_calls_run_blocking(self)
```

```python
@patch('src.applications.robot_settings.controller.robot_settings_controller.show_warning')
def test_move_to_multi_pos_no_point_shows_warning(self, mock_warn)
```

```python
def test_move_to_explicit_point_calls_run_blocking(self)
```

```python
def test_move_to_single_pos_fn_delegates_to_move_to_group(self)
```

```python
def test_move_to_explicit_point_fn_delegates_to_move_to_point(self)
```

### `TestRobotSettingsControllerExecute`

```python
class TestRobotSettingsControllerExecute(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_execute_calls_auto_save(self)
```

```python
def test_execute_calls_run_blocking(self)
```

```python
def test_execute_fn_delegates_to_execute_group(self)
```

## `test_robot_settings_factory.py`

Source: [tests/applications/robot_settings/test_robot_settings_factory.py](../../../../tests/applications/robot_settings/test_robot_settings_factory.py).

Imports (including optional/function-local imports; not a startup dependency list): `PyQt6.QtWidgets`, `src.applications.robot_settings.controller.robot_settings_controller`, `src.applications.robot_settings.robot_settings_factory`, `src.applications.robot_settings.service.i_robot_settings_service`, `src.applications.robot_settings.view.robot_settings_view`, `src.engine.robot.configuration`, `sys`, `unittest`, `unittest.mock`.

### `_make_service`

```python
def _make_service()
```

### `TestRobotSettingsFactory`

```python
class TestRobotSettingsFactory(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
@classmethod
def setUpClass(cls)
```

```python
def test_build_returns_robot_settings_view(self)
```

```python
def test_build_attaches_controller_to_view(self)
```

```python
def test_build_calls_load_config_on_service(self)
```

```python
def test_build_calls_load_calibration_on_service(self)
```

```python
def test_two_builds_produce_independent_views(self)
```

## `test_robot_settings_mapper.py`

Source: [tests/applications/robot_settings/test_robot_settings_mapper.py](../../../../tests/applications/robot_settings/test_robot_settings_mapper.py).

Imports (including optional/function-local imports; not a startup dependency list): `copy`, `src.applications.robot_settings.model.mapper`, `src.engine.robot.configuration`, `unittest`.

### `TestRobotSettingsMapperToFlatDict`

```python
class TestRobotSettingsMapperToFlatDict(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def setUp(self)
```

```python
def test_robot_ip_present(self)
```

```python
def test_robot_tool_present(self)
```

```python
def test_tcp_offsets_present(self)
```

```python
def test_global_motion_present(self)
```

```python
def test_safety_limits_present(self)
```

```python
def test_offset_direction_as_strings(self)
```

```python
def test_all_expected_keys_present(self)
```

### `TestRobotSettingsMapperFromFlatDict`

```python
class TestRobotSettingsMapperFromFlatDict(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def setUp(self)
```

```python
def test_roundtrip_robot_ip(self)
```

```python
def test_roundtrip_robot_tool(self)
```

```python
def test_can_disable_automatic_camera_to_tcp_offset(self)
```

```python
def test_roundtrip_safety_limits(self)
```

```python
def test_roundtrip_global_motion(self)
```

```python
def test_offset_direction_true_string(self)
```

```python
def test_offset_direction_false_string(self)
```

```python
def test_missing_keys_fall_back_to_base(self)
```

```python
def test_does_not_mutate_base(self)
```

```python
def test_full_roundtrip(self)
```

### `TestRobotCalibrationMapperToFlatDict`

```python
class TestRobotCalibrationMapperToFlatDict(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def setUp(self)
```

```python
def test_all_expected_keys_present(self)
```

```python
def test_defaults_correct(self)
```

### `TestRobotCalibrationMapperFromFlatDict`

```python
class TestRobotCalibrationMapperFromFlatDict(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def setUp(self)
```

```python
def test_roundtrip_z_target(self)
```

```python
def test_roundtrip_adaptive_movement(self)
```

```python
def test_roundtrip_camera_tcp_calibration_config(self)
```

```python
def test_missing_keys_fall_back_to_base(self)
```

```python
def test_does_not_mutate_base(self)
```

```python
def test_full_roundtrip(self)
```

## `test_robot_settings_model.py`

Source: [tests/applications/robot_settings/test_robot_settings_model.py](../../../../tests/applications/robot_settings/test_robot_settings_model.py).

Imports (including optional/function-local imports; not a startup dependency list): `src.applications.robot_settings.model.mapper`, `src.applications.robot_settings.model.robot_settings_model`, `src.applications.robot_settings.service.robot_settings_application_service`, `src.engine.common_settings_ids`, `src.engine.robot.configuration`, `src.shared_contracts.declarations`, `unittest`, `unittest.mock`.

### `_make_service`

```python
def _make_service(config=None, calibration=None)
```

### `TestRobotSettingsModelLoad`

```python
class TestRobotSettingsModelLoad(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_load_calls_service(self)
```

```python
def test_load_returns_config_and_calibration(self)
```

```python
def test_config_accessible_after_load(self)
```

### `TestRobotSettingsModelSave`

```python
class TestRobotSettingsModelSave(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_save_calls_save_config(self)
```

```python
def test_save_calls_save_calibration(self)
```

```python
def test_save_updates_robot_ip(self)
```

```python
def test_save_persists_movement_groups(self)
```

```python
def test_save_updates_internal_config(self)
```

```python
def test_save_updates_calibration_z_target(self)
```

```python
def test_save_without_load_raises(self)
```

### `TestRobotSettingsApplicationService`

```python
class TestRobotSettingsApplicationService(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_load_config_delegates_to_settings_service(self)
```

```python
def test_load_calibration_delegates_to_settings_service(self)
```

```python
def test_save_config_delegates_to_settings_service(self)
```

```python
def test_save_calibration_delegates_to_settings_service(self)
```

### `TestRobotSettingsModelMotionDelegation`

```python
class TestRobotSettingsModelMotionDelegation(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_get_current_position_delegates(self)
```

```python
def test_get_slot_info_delegates(self)
```

```python
def test_move_to_group_delegates(self)
```

```python
def test_execute_group_delegates(self)
```

```python
def test_move_to_point_delegates(self)
```

### `TestRobotSettingsModelExpectedMovementGroups`

```python
class TestRobotSettingsModelExpectedMovementGroups(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_returns_existing_groups(self)
```

```python
def test_adds_groups_from_definitions(self)
```

```python
def test_does_not_overwrite_existing_group_from_definitions(self)
```

## `test_targeting_definitions_tab.py`

Source: [tests/applications/robot_settings/test_targeting_definitions_tab.py](../../../../tests/applications/robot_settings/test_targeting_definitions_tab.py).

Imports (including optional/function-local imports; not a startup dependency list): `PyQt6.QtWidgets`, `src.applications.robot_settings.view.targeting_definitions_tab`, `sys`, `unittest`.

### `TestTargetingDefinitionsTab`

```python
class TestTargetingDefinitionsTab(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
@classmethod
def setUpClass(cls)
```

```python
def test_calibration_profile_fields_round_trip_with_frame(self)
```

```python
def test_loading_mode_does_not_emit_user_change(self)
```

```python
def test_per_area_points_and_tcp_can_reuse_global_independently(self)
```

```python
def test_local_choice_derives_internal_profile_values(self)
```

```python
def test_global_and_not_configured_choices_clear_internal_local_values(self)
```
