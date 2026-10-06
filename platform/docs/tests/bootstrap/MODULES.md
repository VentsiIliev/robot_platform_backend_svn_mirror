# Module reference: `tests/bootstrap`

[Package guide](README.md) · [Complete source index](../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [test_application_loader.py](#test_application_loaderpy)
- [test_build_engine.py](#test_build_enginepy)
- [test_main.py](#test_mainpy)
- [test_ros_backend_launcher.py](#test_ros_backend_launcherpy)
- [test_shell_configurator.py](#test_shell_configuratorpy)
- [test_startup_config.py](#test_startup_configpy)
- [test_startup_error.py](#test_startup_errorpy)
- [test_startup_splash_lifecycle.py](#test_startup_splash_lifecyclepy)
- [test_startup_splash_status_text.py](#test_startup_splash_status_textpy)

## `__init__.py`

Source: [tests/bootstrap/__init__.py](../../../tests/bootstrap/__init__.py).

No top-level functions, classes or public value declarations; inspect the source for imports or entry-point statements.

## `test_application_loader.py`

Source: [tests/bootstrap/test_application_loader.py](../../../tests/bootstrap/test_application_loader.py).

Imports (including optional/function-local imports; not a startup dependency list): `PyQt6.QtWidgets`, `os`, `src.bootstrap.application_loader`, `src.engine.core.i_messaging_service`, `src.shared_contracts.declarations.system_specs`, `sys`, `unittest`, `unittest.mock`.

### `_make_ms`

```python
def _make_ms()
```

### `_make_application`

```python
def _make_application(name='MyApplication')
```

### `_make_spec`

```python
def _make_spec(name='MyApplication', folder_id=1, icon='fa5s.cog')
```

### `TestApplicationManager`

```python
class TestApplicationManager(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_register_lazy_exposes_descriptor_metadata(self)
```

```python
def test_get_loaded_application_names(self)
```

```python
def test_get_application_unknown_returns_none(self)
```

```python
def test_register_lazy_multiple_applications(self)
```

```python
def test_get_or_create_application_builds_and_caches(self)
```

### `TestWidgetFactory`

```python
class TestWidgetFactory(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
@classmethod
def setUpClass(cls)
```

```python
def test_create_widget_calls_application_create_widget(self)
```

```python
def test_create_widget_unknown_returns_fallback(self)
```

```python
def test_create_widget_application_without_create_widget_returns_fallback(self)
```

### `TestApplicationLoaderInit`

```python
class TestApplicationLoaderInit(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_init_stores_messaging_service(self)
```

```python
def test_init_creates_empty_manager(self)
```

### `TestApplicationLoaderRegisterSpec`

```python
class TestApplicationLoaderRegisterSpec(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
@classmethod
def setUpClass(cls)
```

```python
def test_register_spec_stores_descriptor_name(self)
```

```python
def test_register_spec_returns_self_for_chaining(self)
```

```python
def test_register_spec_multiple_applications(self)
```

```python
def test_register_spec_does_not_build_application_eagerly(self)
```

```python
def test_widget_factory_registers_application_on_first_widget_creation(self)
```

```python
def test_widget_factory_builder_failure_returns_fallback_widget(self)
```

```python
def test_widget_factory_create_widget_failure_returns_fallback_widget(self)
```

### `TestApplicationLoaderBuildRegistry`

```python
class TestApplicationLoaderBuildRegistry(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_build_registry_returns_tuple(self)
```

```python
def test_build_registry_descriptors_is_iterable(self)
```

```python
def test_build_registry_widget_factory_is_callable(self)
```

## `test_build_engine.py`

Source: [tests/bootstrap/test_build_engine.py](../../../tests/bootstrap/test_build_engine.py).

Imports (including optional/function-local imports; not a startup dependency list): `src.bootstrap.build_engine`, `src.engine.core.i_messaging_service`, `unittest`, `unittest.mock`.

### `TestEngineContextBuild`

```python
class TestEngineContextBuild(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_build_returns_engine_context(self)
```

```python
def test_build_each_call_returns_new_instance(self)
```

```python
def test_messaging_service_present(self)
```

```python
def test_messaging_service_implements_interface(self)
```

```python
def test_messaging_service_is_independent_per_context(self)
```

```python
def test_messaging_service_can_subscribe(self)
```

```python
def test_messaging_service_can_publish_without_subscribers(self)
```

```python
def test_init_creates_messaging_service(self)
```

## `test_main.py`

Source: [tests/bootstrap/test_main.py](../../../tests/bootstrap/test_main.py).

Smoke tests for src/bootstrap/main.y_pixels. The startup sequence calls Qt, hardware drivers, and the full robot system — all of which are mocked here. Tests verify import integrity and step ordering, not full execution.

Imports (including optional/function-local imports; not a startup dependency list): `pathlib`, `src.bootstrap.run_main`, `src.robot_systems.glue.glue_robot_system`, `sys`, `unittest`, `unittest.mock`.

### `TestMainImport`

```python
class TestMainImport(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_localization_service_uses_robot_system_storage_paths(self)
```

### `TestStartupSequenceOrder`

```python
class TestStartupSequenceOrder(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_startup_sequence_order(self)
```

Patches all six startup steps and verifies they are invoked in the documented order: 1. EngineContext.build() 2. SystemBuilder().with_robot(...).with_messaging_service(...).build(...) 3. ShellConfigurator.configure(...) 4. QApplication(sys.argv) 5. ApplicationLoader — spec.factory + loader.load + loader.build_registry 6. AppShell — show

### `TestStartupAbortOnFailure`

```python
class TestStartupAbortOnFailure(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_startup_aborts_cleanly_on_engine_build_failure(self)
```

If EngineContext.build() raises, main() must propagate (not swallow) the exception and must not attempt to build the Qt application.

## `test_ros_backend_launcher.py`

Source: [tests/bootstrap/test_ros_backend_launcher.py](../../../tests/bootstrap/test_ros_backend_launcher.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `io`, `os`, `pathlib`, `src.bootstrap.ros_backend_launcher`, `src.bootstrap.startup_config`, `subprocess`, `tempfile`, `unittest`, `unittest.mock`.

### `TestRosBackendLauncher`

```python
class TestRosBackendLauncher(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_start_launches_script_with_delay(self) -> None
```

```python
def test_stop_runs_stop_script_and_waits_for_launch_wrapper(self) -> None
```

```python
def test_start_skips_launch_when_backend_is_already_reachable(self) -> None
```

```python
def test_target_reuse_rejects_wrong_or_missing_identity(self)
```

```python
def test_target_reuse_accepts_matching_identity(self)
```

```python
def test_unmapped_target_cannot_autostart(self)
```

```python
def test_target_cannot_use_another_workspace(self)
```

```python
def test_clean_env_removes_python_virtualenv_contamination(self) -> None
```

```python
def test_start_can_be_disabled_by_env(self) -> None
```

```python
def test_start_can_be_disabled_by_config(self) -> None
```

```python
def test_stop_can_be_disabled_by_config(self) -> None
```

```python
def test_builder_uses_config_defaults(self) -> None
```

```python
def test_builder_defaults_to_current_users_ros_workspace(self) -> None
```

```python
def test_env_overrides_config_paths(self) -> None
```

## `test_shell_configurator.py`

Source: [tests/bootstrap/test_shell_configurator.py](../../../tests/bootstrap/test_shell_configurator.py).

Imports (including optional/function-local imports; not a startup dependency list): `pl_gui.shell.shell_config`, `src.bootstrap.shell_configurator`, `src.robot_systems.base_robot_system`, `src.robot_systems.glue.glue_robot_system`, `src.shared_contracts.declarations`, `unittest`, `unittest.mock`.

### `_AppWithFolders`

```python
class _AppWithFolders(BaseRobotSystem):
```

Declared fields/defaults:

```python
metadata = SystemMetadata(name='TestApp')
shell = ShellSetup(folders=[FolderSpec(folder_id=1, name='PROD', display_name='Production'), FolderSpec(folder_id=2, name='SERVICE', display_name='Service'), FolderSpec(folder_id=3, name='ADMIN', display_name='Administration')])
settings_specs = []
services = []
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def on_start(self) -> None
```

```python
def on_stop(self) -> None
```

### `_AppWithNoFolders`

```python
class _AppWithNoFolders(BaseRobotSystem):
```

Declared fields/defaults:

```python
metadata = SystemMetadata(name='EmptyApp')
shell = ShellSetup(folders=[])
settings_specs = []
services = []
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def on_start(self) -> None
```

```python
def on_stop(self) -> None
```

### `TestShellConfiguratorWithFolders`

```python
class TestShellConfiguratorWithFolders(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def setUp(self)
```

```python
def test_configure_clears_previous_folders(self)
```

```python
def test_configure_registers_correct_count(self)
```

```python
def test_configure_registers_correct_folder_ids(self)
```

```python
def test_configure_registers_correct_display_names(self)
```

```python
def test_configure_folder_names(self)
```

### `TestShellConfiguratorNoFolders`

```python
class TestShellConfiguratorNoFolders(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def setUp(self)
```

```python
def test_configure_no_folders_initializes_defaults(self)
```

### `TestShellConfiguratorGlueApp`

```python
class TestShellConfiguratorGlueApp(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def setUp(self)
```

```python
def test_glue_app_registers_three_folders(self)
```

```python
def test_glue_app_registers_production_folder(self)
```

```python
def test_glue_app_registers_service_folder(self)
```

```python
def test_glue_app_registers_admin_folder(self)
```

```python
def test_configure_is_idempotent(self)
```

## `test_startup_config.py`

Source: [tests/bootstrap/test_startup_config.py](../../../tests/bootstrap/test_startup_config.py).

Imports (including optional/function-local imports; not a startup dependency list): `json`, `pathlib`, `src.bootstrap.startup_config`, `src.robot_systems.robot_system_bootstrap_provider`, `sys`, `tempfile`, `types`, `unittest`, `unittest.mock`.

### `_TestProvider`

```python
class _TestProvider(RobotSystemBootstrapProvider):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
@property
def system_class(self)
```

```python
def build_robot(self)
```

```python
def build_login_view(self, robot_system, messaging_service)
```

```python
def build_authorization_service(self, robot_system)
```

### `TestStartupConfig`

```python
class TestStartupConfig(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
@staticmethod
def system_config()
```

```python
def test_robot_driver_mismatch_fails(self)
```

```python
def test_configured_robot_uses_bridge_without_provider_fallback(self)
```

```python
def test_missing_selected_system_fails(self)
```

```python
def test_incomplete_selected_system_fails(self)
```

```python
def test_loads_selected_robot_system(self)
```

```python
def test_loads_ros_backend_config(self)
```

```python
def test_loads_ui_startup_config(self)
```

```python
def test_rejects_invalid_ui_window_size(self)
```

```python
def test_rejects_invalid_ui_bool(self)
```

```python
def test_rejects_invalid_ros_backend_bool(self)
```

```python
def test_rejects_invalid_ros_backend_path(self)
```

```python
def test_rejects_dotted_module_path(self)
```

```python
def test_loads_provider_factory_by_convention(self)
```

```python
def test_loads_paint_auto_dry_as_a_robot_system(self)
```

```python
def test_reports_missing_robot_system(self)
```

```python
def test_rejects_selected_system_not_in_supported_list(self)
```

## `test_startup_error.py`

Source: [tests/bootstrap/test_startup_error.py](../../../tests/bootstrap/test_startup_error.py).

Imports (including optional/function-local imports; not a startup dependency list): `PyQt6.QtWidgets`, `contextlib`, `io`, `pathlib`, `src.bootstrap.startup_error`, `tempfile`, `unittest`, `unittest.mock`.

### `StartupErrorTests`

```python
class StartupErrorTests(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_error_is_saved_and_presented_without_a_terminal(self)
```

```python
def test_unwritable_log_does_not_prevent_the_dialog(self)
```

```python
def test_dialog_displays_plain_error_and_expandable_details(self)
```

## `test_startup_splash_lifecycle.py`

Source: [tests/bootstrap/test_startup_splash_lifecycle.py](../../../tests/bootstrap/test_startup_splash_lifecycle.py).

Imports (including optional/function-local imports; not a startup dependency list): `PyQt6.QtCore`, `PyQt6.QtWidgets`, `os`, `pl_gui.shell.startup_splash_view`, `src.bootstrap.startup_splash_runtime`, `types`, `unittest`, `unittest.mock`.

### `StartupSplashLifecycleTests`

```python
class StartupSplashLifecycleTests(unittest.TestCase):
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
def tearDown(self)
```

```python
def test_second_login_reuses_live_splash_and_completes(self)
```

```python
def test_queued_state_after_stop_does_not_update_splash(self)
```

```python
def test_stop_cancels_pending_hide(self)
```

## `test_startup_splash_status_text.py`

Source: [tests/bootstrap/test_startup_splash_status_text.py](../../../tests/bootstrap/test_startup_splash_status_text.py).

Imports (including optional/function-local imports; not a startup dependency list): `src.bootstrap.startup_splash_runtime`, `types`, `unittest`.

### `TestStartupSplashStatusText`

```python
class TestStartupSplashStatusText(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_disconnected_state_shows_connecting_stage(self)
```

```python
def test_disabled_drives_show_enabling_stage(self)
```

```python
def test_ethercat_drive_warning_shows_communication_stage(self)
```

```python
def test_tool_mismatch_shows_tool_configuration_stage(self)
```

```python
def test_unknown_state_uses_neutral_readiness_stage(self)
```
