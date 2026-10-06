# Module reference: `tests/applications/base`

[Package guide](README.md) · [Complete source index](../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [test_application_factory.py](#test_application_factorypy)
- [test_dashboard_process_state_mixin.py](#test_dashboard_process_state_mixinpy)
- [test_jog_controller.py](#test_jog_controllerpy)
- [test_keyboard_number_field.py](#test_keyboard_number_fieldpy)
- [test_notification_presenter.py](#test_notification_presenterpy)
- [test_robot_connection_notifier.py](#test_robot_connection_notifierpy)
- [test_robot_jog_service.py](#test_robot_jog_servicepy)
- [test_styled_message_box.py](#test_styled_message_boxpy)
- [test_virtual_keyboard_cleanup.py](#test_virtual_keyboard_cleanuppy)
- [test_widget_application.py](#test_widget_applicationpy)

## `__init__.py`

Source: [tests/applications/base/__init__.py](../../../../tests/applications/base/__init__.py).

No top-level functions, classes or public value declarations; inspect the source for imports or entry-point statements.

## `test_application_factory.py`

Source: [tests/applications/base/test_application_factory.py](../../../../tests/applications/base/test_application_factory.py).

Unit tests for ApplicationFactory. These are pure unit tests — all MVC collaborators are mocked, no Qt needed. Covered: - build() returns the view - _create_model() receives the service argument - _create_controller() receives the model from _create_model and view from _create_view - controller.load() is called exactly once - GC fix: view._controller is assigned the controller after build() - GC fix ordering: load() is called BEFORE view._controller is assigned - Template method wiring order: create_model → create_view → create_controller → load

Imports (including optional/function-local imports; not a startup dependency list): `src.applications.base.application_factory`, `src.applications.base.i_application_controller`, `src.applications.base.i_application_model`, `src.applications.base.i_application_view`, `unittest`, `unittest.mock`.

### `_SimpleView`

```python
class _SimpleView:
```

Minimal stand-in for a view — plain object so attribute assignment is detectable.

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def clean_up(self)
```

### `_make_factory`

```python
def _make_factory(model=None, view=None, controller=None)
```

Return a concrete ApplicationFactory wired to the given (or fresh mock) collaborators.

### `TestBuildReturnValue`

```python
class TestBuildReturnValue(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_build_returns_the_view(self)
```

### `TestTemplateMethodDelegation`

```python
class TestTemplateMethodDelegation(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_create_model_receives_service_argument(self)
```

```python
def test_create_controller_receives_model_returned_by_create_model(self)
```

```python
def test_create_controller_receives_view_returned_by_create_view(self)
```

```python
def test_controller_load_called_exactly_once(self)
```

### `TestGcFix`

```python
class TestGcFix(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_view_controller_attribute_is_set_to_controller(self)
```

```python
def test_gc_fix_is_assigned_after_controller_load(self)
```

load() must be called before view._controller is set.

### `TestWiringOrder`

```python
class TestWiringOrder(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_template_methods_execute_in_correct_order(self)
```

## `test_dashboard_process_state_mixin.py`

Source: [tests/applications/base/test_dashboard_process_state_mixin.py](../../../../tests/applications/base/test_dashboard_process_state_mixin.py).

Imports (including optional/function-local imports; not a startup dependency list): `enum`, `src.applications.base.dashboard_process_state_mixin`, `types`, `unittest`, `unittest.mock`.

### `_ProcessID`

```python
class _ProcessID(str, Enum):
```

Declared fields/defaults:

```python
MAIN_PROCESS = 'main_process'
```

### `_Controller`

```python
class _Controller(DashboardProcessStateMixin):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self)
```

### `TestDashboardProcessStateMixin`

```python
class TestDashboardProcessStateMixin(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_error_event_message_is_shown_once(self)
```

```python
def test_no_workpiece_text_in_error_preserves_failure_message(self)
```

```python
def test_magazine_servo_failure_with_no_workpiece_text_is_not_downgraded(self)
```

```python
def test_no_workpiece_stopped_message_is_shown_as_operator_warning(self)
```

```python
def test_non_matching_process_event_is_ignored(self)
```

```python
def test_enum_process_id_event_matches_service_string_process_id(self)
```

## `test_jog_controller.py`

Source: [tests/applications/base/test_jog_controller.py](../../../../tests/applications/base/test_jog_controller.py).

Imports (including optional/function-local imports; not a startup dependency list): `PyQt6.QtCore`, `PyQt6.QtWidgets`, `os`, `src.applications.base.jog_controller`, `threading`, `unittest`, `unittest.mock`.

### `_JogView`

```python
class _JogView(QWidget):
```

Declared fields/defaults:

```python
jog_requested = pyqtSignal(str, str, str, float)
jog_stopped = pyqtSignal(str)
```

### `TestJogController`

```python
class TestJogController(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
@classmethod
def setUpClass(cls)
```

```python
def test_servo_stop_is_executed_after_queued_start(self)
```

## `test_keyboard_number_field.py`

Source: [tests/applications/base/test_keyboard_number_field.py](../../../../tests/applications/base/test_keyboard_number_field.py).

Imports (including optional/function-local imports; not a startup dependency list): `PyQt6.QtCore`, `PyQt6.QtTest`, `PyQt6.QtWidgets`, `pl_gui.settings.settings_view.group_widget`, `pl_gui.settings.settings_view.schema`, `src.applications.base.keyboard_settings_view`, `src.applications.base.widgets.keyboard_number_field`, `unittest`.

### `TestKeyboardNumberField`

```python
class TestKeyboardNumberField(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
@classmethod
def setUpClass(cls)
```

```python
def test_tap_steps_once_with_selected_step_and_respects_bounds(self)
```

```python
def test_hold_accelerates_and_release_stops_repeating(self)
```

```python
def test_decrease_hold_uses_selected_step(self)
```

```python
def test_schema_numeric_fields_use_the_shared_control(self)
```

```python
def test_special_value_and_bounds_update_touch_controls(self)
```

```python
def test_read_only_disables_touch_stepping(self)
```

## `test_notification_presenter.py`

Source: [tests/applications/base/test_notification_presenter.py](../../../../tests/applications/base/test_notification_presenter.py).

Imports (including optional/function-local imports; not a startup dependency list): `src.applications.base.notification_presenter`, `src.shared_contracts.events.notification_events`, `unittest`, `unittest.mock`.

### `TestNotificationTextResolver`

```python
class TestNotificationTextResolver(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_uses_fallback_when_translation_missing(self)
```

```python
def test_uses_translated_template_and_formats_params(self)
```

### `TestUserNotificationPresenter`

```python
class TestUserNotificationPresenter(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
@patch('src.applications.base.notification_presenter.show_critical')
def test_present_shows_critical_message(self, mock_show_critical)
```

```python
@patch('src.applications.base.notification_presenter.make_warning')
def test_dedupes_consecutive_notifications_with_same_key(self, mock_make_warning)
```

```python
@patch('src.applications.base.notification_presenter.make_warning')
def test_dismiss_closes_matching_keyed_notification(self, mock_make_warning)
```

```python
def test_start_and_stop_manage_broker_subscription(self)
```

## `test_robot_connection_notifier.py`

Source: [tests/applications/base/test_robot_connection_notifier.py](../../../../tests/applications/base/test_robot_connection_notifier.py).

Imports (including optional/function-local imports; not a startup dependency list): `src.applications.base.robot_connection_notifier`, `src.engine.robot.services.robot_state_snapshot`, `src.shared_contracts.events.notification_events`, `src.shared_contracts.events.robot_events`, `unittest`.

### `_Broker`

```python
class _Broker:
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self) -> None
```

```python
def subscribe(self, topic, callback) -> None
```

```python
def unsubscribe(self, topic, callback) -> None
```

```python
def publish(self, topic, message) -> None
```

### `TestRobotConnectionNotifier`

```python
class TestRobotConnectionNotifier(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_start_and_stop_manage_robot_state_subscription(self)
```

```python
def test_disconnected_state_publishes_user_warning(self)
```

```python
def test_repeated_disconnected_state_is_suppressed_until_recovered(self)
```

```python
def test_drive_not_ready_state_publishes_readiness_warning_until_idle(self)
```

```python
def test_startup_suppression_ignores_initial_not_ready_until_first_ready(self)
```

```python
def test_startup_configuration_failure_is_shown_immediately(self)
```

## `test_robot_jog_service.py`

Source: [tests/applications/base/test_robot_jog_service.py](../../../../tests/applications/base/test_robot_jog_service.py).

Imports (including optional/function-local imports; not a startup dependency list): `src.applications.base.robot_jog_service`, `src.applications.base.robot_jog_service_builder`, `src.engine.common_settings_ids`, `src.engine.robot.configuration.movement_group_settings`, `src.engine.robot.configuration.robot_settings`, `types`, `unittest`, `unittest.mock`.

### `TestRobotJogService`

```python
class TestRobotJogService(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_joint_jog_sends_j6_full_turn_as_one_command(self)
```

```python
def test_joint_jog_rejects_step_over_90_degrees_for_other_joints(self)
```

```python
def test_joint_jog_rejects_step_over_360_degrees_for_j6(self)
```

```python
def test_jog_moves_configured_tool_from_current_pose(self)
```

```python
def test_jog_uses_live_motion_settings_getters(self)
```

```python
def test_rotation_jog_uses_linear_pose_move(self)
```

```python
def test_builder_uses_ten_when_saved_jog_velocity_or_acceleration_is_zero(self)
```

```python
def test_builder_reads_current_tool_and_workobject_from_settings(self)
```

```python
def test_jog_activates_tool_before_reading_current_position(self)
```

```python
def test_jog_aborts_when_configured_tool_cannot_be_activated(self)
```

```python
def test_step_jog_applies_delta_in_configured_user_frame(self)
```

```python
def test_servo_jog_uses_same_tool_user_frame_and_direction_as_step(self)
```

```python
def test_recovery_mode_scopes_collision_override_to_servo_z_plus(self)
```

```python
def test_recovery_mode_disables_collision_for_operator_selected_servo_axis(self)
```

```python
def test_recovery_servo_uses_configured_recovery_speed_limit(self)
```

```python
def test_recovery_step_above_zero_requests_collision_recovery_without_floor_bypass(self)
```

```python
def test_servo_jog_caps_slider_speed_to_configured_maximum(self)
```

```python
def test_jog_aborts_when_configured_workobject_cannot_be_activated(self)
```

```python
def test_jog_ignores_frame_options_and_pose_resolver_offsets(self)
```

```python
def test_jog_does_not_use_native_incremental_jog_when_driver_prefers_it(self)
```

## `test_styled_message_box.py`

Source: [tests/applications/base/test_styled_message_box.py](../../../../tests/applications/base/test_styled_message_box.py).

Imports (including optional/function-local imports; not a startup dependency list): `PyQt6.QtCore`, `PyQt6.QtWidgets`, `os`, `src.applications.base.styled_message_box`, `unittest`.

### `TestStyledMessageBox`

```python
class TestStyledMessageBox(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
@classmethod
def setUpClass(cls) -> None
```

```python
def test_action_warning_returns_chosen_button_and_allows_optional_sections(self) -> None
```

```python
def test_plain_warning_keeps_message_box_api(self) -> None
```

## `test_virtual_keyboard_cleanup.py`

Source: [tests/applications/base/test_virtual_keyboard_cleanup.py](../../../../tests/applications/base/test_virtual_keyboard_cleanup.py).

Imports (including optional/function-local imports; not a startup dependency list): `PyQt6`, `PyQt6.QtWidgets`, `src.applications.base.widgets.custom_virtual_keyboard`, `unittest`.

### `VirtualKeyboardCleanupTests`

```python
class VirtualKeyboardCleanupTests(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
@classmethod
def setUpClass(cls)
```

```python
def test_pending_scroll_restore_survives_form_destruction(self)
```

## `test_widget_application.py`

Source: [tests/applications/base/test_widget_application.py](../../../../tests/applications/base/test_widget_application.py).

Unit tests for WidgetApplication. These are pure unit tests — widget_factory is always a mock, no Qt needed. Covered: - register() stores the messaging service for later use - register() called twice keeps the most recent service - create_widget() delegates to widget_factory with the stored messaging service - create_widget() returns exactly what widget_factory returns - create_widget() before register() passes None to the factory (safe default) - create_widget() can be called multiple times; factory is called each time

Imports (including optional/function-local imports; not a startup dependency list): `src.applications.base.widget_application`, `unittest`, `unittest.mock`.

### `TestRegister`

```python
class TestRegister(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_register_stores_messaging_service(self)
```

```python
def test_register_twice_keeps_most_recent_service(self)
```

```python
def test_messaging_service_is_none_before_register(self)
```

### `TestCreateWidget`

```python
class TestCreateWidget(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_create_widget_calls_factory_with_messaging_service(self)
```

```python
def test_create_widget_returns_factory_result(self)
```

```python
def test_create_widget_before_register_passes_none_to_factory(self)
```

```python
def test_create_widget_called_multiple_times_invokes_factory_each_time(self)
```

```python
def test_create_widget_passes_updated_service_after_second_register(self)
```
