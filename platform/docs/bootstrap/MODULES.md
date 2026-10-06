# Module reference: `src/bootstrap`

[Package guide](README.md) · [Complete source index](../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [application_loader.py](#application_loaderpy)
- [build_engine.py](#build_enginepy)
- [logging_config.py](#logging_configpy)
- [ros_backend_launcher.py](#ros_backend_launcherpy)
- [run_main.py](#run_mainpy)
- [shell_configurator.py](#shell_configuratorpy)
- [shell_remote_support_controller.py](#shell_remote_support_controllerpy)
- [shell_session_controller.py](#shell_session_controllerpy)
- [startup_config.py](#startup_configpy)
- [startup_error.py](#startup_errorpy)
- [startup_splash_runtime.py](#startup_splash_runtimepy)

## `application_loader.py`

Source: [src/bootstrap/application_loader.py](../../src/bootstrap/application_loader.py).

Imports (including optional/function-local imports; not a startup dependency list): `logging`, `pl_gui.shell.app_descriptor`, `pl_gui.shell.app_registry`, `pl_gui.shell.base_app_widget.AppWidget`, `src.engine.core.i_messaging_service`, `src.shared_contracts.declarations.system_specs`, `typing`.

### `_ApplicationManager`

```python
class _ApplicationManager:
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self)
```

```python
def register_lazy(self, spec: ApplicationSpec, builder: Callable[[], Any]) -> None
```

```python
def get_loaded_application_names(self) -> List[str]
```

```python
def get_descriptors(self) -> List[AppDescriptor]
```

```python
def get_application(self, name: str) -> Any
```

```python
def get_or_create_application(self, name: str) -> Any
```

### `_WidgetFactory`

```python
class _WidgetFactory:
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, manager: _ApplicationManager, messaging_service: IMessagingService)
```

```python
def create_widget(self, app_name: str)
```

### `ApplicationLoader`

```python
class ApplicationLoader:
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, messaging_service: IMessagingService)
```

```python
def register_spec(self, spec: ApplicationSpec, builder: Callable[[], Any]) -> 'ApplicationLoader'
```

```python
def build_registry(self)
```

## `build_engine.py`

Source: [src/bootstrap/build_engine.py](../../src/bootstrap/build_engine.py).

Imports (including optional/function-local imports; not a startup dependency list): `src.engine.core.i_messaging_service`, `src.engine.core.messaging_service`.

### `EngineContext`

```python
class EngineContext:
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self)
```

```python
@classmethod
def build(cls) -> 'EngineContext'
```

## `logging_config.py`

Source: [src/bootstrap/logging_config.py](../../src/bootstrap/logging_config.py).

Imports (including optional/function-local imports; not a startup dependency list): `logging`, `os`.

### `_ColorFormatter`

```python
class _ColorFormatter(logging.Formatter):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def format(self, record: logging.LogRecord) -> str
```

### `setup_logging`

```python
def setup_logging() -> None
```

## `ros_backend_launcher.py`

Source: [src/bootstrap/ros_backend_launcher.py](../../src/bootstrap/ros_backend_launcher.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `dataclasses`, `json`, `logging`, `os`, `pathlib`, `src.bootstrap.startup_config`, `subprocess`, `sys`, `time`, `urllib.error`, `urllib.request`.

### `RosBackendLauncher`

```python
class RosBackendLauncher:
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, launch_script: str | os.PathLike | None=None, stop_script: str | os.PathLike | None=None, startup_delay_s: float=1.0, log_file: str | os.PathLike='/tmp/robot_app_zeroerr_backend.log', status_urls: tuple[str, ...]=('http://localhost:5000/startup/status', 'http://localhost:5000/health'), status_timeout_s: float=0.3, auto_launch: bool=True, auto_stop: bool=True, robot_target: str | None=None, backend_profile: str | None=None) -> None
```

```python
def start(self) -> None
```

```python
def stop(self) -> None
```

### `build_ros_backend_launcher_from_env`

```python
def build_ros_backend_launcher_from_env(config: RosBackendConfig | None=None, robot_target: str | None=None) -> RosBackendLauncher
```

### `_default_launch_script`

```python
def _default_launch_script() -> Path
```

### `_default_stop_script`

```python
def _default_stop_script() -> Path
```

### `_expand_path`

```python
def _expand_path(path: str | os.PathLike) -> Path
```

### `_value_from_env_or_config`

```python
def _value_from_env_or_config(name: str, config_value: object, default: str) -> str
```

### `_env_enabled`

```python
def _env_enabled(name: str, *, default: bool) -> bool
```

### `_status_urls_from_env`

```python
def _status_urls_from_env(config_urls: tuple[str, ...] | None=None) -> tuple[str, ...]
```

### `_default_status_urls`

```python
def _default_status_urls() -> tuple[str, ...]
```

### `_clean_ros_process_env`

```python
def _clean_ros_process_env() -> dict[str, str]
```

### `_clean_path`

```python
def _clean_path(path_value: str) -> str
```

## `run_main.py`

Source: [src/bootstrap/run_main.py](../../src/bootstrap/run_main.py).

Imports (including optional/function-local imports; not a startup dependency list): `PyQt6.QtCore`, `PyQt6.QtGui`, `PyQt6.QtWidgets`, `logging`, `os`, `pathlib`, `pl_gui.shell.AppShell`, `pl_gui.shell.startup_splash_view`, `setproctitle`, `signal`, `src.applications.base.notification_presenter`, `src.applications.base.robot_connection_notifier`, `src.applications.broker_debug.broker_debug_factory`, `src.applications.broker_debug.service.broker_debug_application_service`, `src.applications.login.stub_login_application_service`, `src.bootstrap.application_loader`, `src.bootstrap.build_engine`, `src.bootstrap.logging_config`, `src.bootstrap.ros_backend_launcher`, `src.bootstrap.shell_configurator`, `src.bootstrap.shell_remote_support_controller`, `src.bootstrap.shell_session_controller`, `src.bootstrap.startup_config`, `src.bootstrap.startup_splash_runtime`, `src.engine.auth.user_session`, `src.engine.localization.localization_service`, `src.engine.remote_support.client`, `src.engine.remote_support.session_client`, `src.engine.updates.paths`, `src.robot_systems.system_builder`, `src.shared_contracts.events.shell_events`, `sys`.

### `_FramelessHeaderDrag`

```python
class _FramelessHeaderDrag(QObject):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, window: QWidget, drag_widget: QWidget)
```

```python
def eventFilter(self, watched: QObject, event: QEvent) -> bool
```

### `_install_terminal_signal_handlers`

```python
def _install_terminal_signal_handlers(qt_app: QApplication) -> None
```

Route terminal shutdown signals through Qt so normal cleanup runs.

### `main`

```python
def main() -> None
```

### `_load_apps_into_shell`

```python
def _load_apps_into_shell(shell, session, robot_app, ctx, bootstrap_provider)
```

Load role-filtered apps and reload the shell's folder page.

### `_build_localization_service`

```python
def _build_localization_service(robot_app, messaging_service) -> LocalizationService
```

### `_build_broker_debug_window`

```python
def _build_broker_debug_window(messaging_service)
```

## `shell_configurator.py`

Source: [src/bootstrap/shell_configurator.py](../../src/bootstrap/shell_configurator.py).

Imports (including optional/function-local imports; not a startup dependency list): `logging`, `pl_gui.shell.shell_config`, `src.robot_systems.base_robot_system`, `typing`.

### `ShellConfigurator`

```python
class ShellConfigurator:
```

Reads ShellSetup metadata from a BaseRobotSystem and configures the pl_gui ShellConfig. Called once at bootstrap before AppShell is created.

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
@staticmethod
def configure(app_class: Type[BaseRobotSystem]) -> None
```

## `shell_remote_support_controller.py`

Source: [src/bootstrap/shell_remote_support_controller.py](../../src/bootstrap/shell_remote_support_controller.py).

Lifetime-scoped background remote-support monitoring for the shell.

Imports (including optional/function-local imports; not a startup dependency list): `PyQt6.QtCore`, `threading`.

### `_Worker`

```python
class _Worker(QObject):
```

Declared fields/defaults:

```python
status_updated = pyqtSignal(str)
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, support_client, session_client, interval: float) -> None
```

```python
def run(self) -> None
```

### `ShellRemoteSupportController`

```python
class ShellRemoteSupportController(QObject):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, header, support_client, session_client, interval: float=2) -> None
```

```python
def start(self) -> None
```

```python
def stop(self) -> None
```

## `shell_session_controller.py`

Source: [src/bootstrap/shell_session_controller.py](../../src/bootstrap/shell_session_controller.py).

Imports (including optional/function-local imports; not a startup dependency list): `PyQt6.QtCore`, `PyQt6.QtWidgets`, `__future__`, `collections.abc`, `logging`, `pl_gui.shell.AppShell`, `pl_gui.shell.session_drawer_view`, `src.engine.auth.i_authenticated_user`, `src.engine.auth.i_session_service`.

### `ShellSessionController`

```python
class ShellSessionController:
```

Owns shell account-button, session drawer, and logout wiring.

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, *, shell: AppShell, session: ISessionService, dev_skip_login: bool, show_account_button_when_dev_skip_login: bool, show_login_view: Callable[[], None], can_close_running_apps: Callable[[], bool]) -> None
```

```python
def start(self) -> None
```

```python
def login(self, user: IAuthenticatedUser) -> None
```

```python
def refresh_account_button(self) -> None
```

```python
def retranslateUi(self, *_) -> None
```

## `startup_config.py`

Source: [src/bootstrap/startup_config.py](../../src/bootstrap/startup_config.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `dataclasses`, `importlib`, `json`, `pathlib`, `re`, `src.engine.robot.drivers.ros2_robot`, `src.robot_systems.robot_system_bootstrap_provider`.

Module declarations (expressions are shown without evaluating them):

```python
DEFAULT_CONFIG_PATH = Path(__file__).resolve().parents[2] / 'config' / 'platform.json'
```

### `RosBackendConfig`

```python
@dataclass(frozen=True)
class RosBackendConfig:
```

Declared fields/defaults:

```python
auto_launch: bool = True
auto_stop: bool = True
launch_script: str | None = None
stop_script: str | None = None
startup_delay_s: float | None = None
log_file: str | None = None
status_urls: tuple[str, ...] | None = None
status_timeout_s: float | None = None
```

### `UiStartupConfig`

```python
@dataclass(frozen=True)
class UiStartupConfig:
```

Declared fields/defaults:

```python
dev_skip_login: bool = False
skip_splash: bool = False
show_account_button_when_dev_skip_login: bool = False
show_power_off_button: bool = False
custom_virtual_keyboard_enabled: bool = True
fullscreen: bool = True
window_width: int = 1280
window_height: int = 1024
```

### `StartupConfig`

```python
@dataclass(frozen=True)
class StartupConfig:
```

Declared fields/defaults:

```python
robot_system: str
supported_robot_systems: tuple[str, ...]
ros_backend: RosBackendConfig = field(default_factory=RosBackendConfig)
ui: UiStartupConfig = field(default_factory=UiStartupConfig)
system_config: dict = field(default_factory=dict)
```

### `load_startup_config`

```python
def load_startup_config(config_path: Path=DEFAULT_CONFIG_PATH) -> StartupConfig
```

### `load_robot_system_config`

```python
def load_robot_system_config(payload: dict, robot_system: str) -> dict
```

Require an explicit, complete configuration for the selected system.

### `_load_ros_backend_config`

```python
def _load_ros_backend_config(raw_config: object) -> RosBackendConfig
```

### `_load_ui_startup_config`

```python
def _load_ui_startup_config(raw_config: object) -> UiStartupConfig
```

### `_read_bool`

```python
def _read_bool(payload: dict, field_name: str, *, default: bool, prefix: str='ros_backend') -> bool
```

### `_read_positive_int`

```python
def _read_positive_int(payload: dict, field_name: str, *, default: int, prefix: str) -> int
```

### `_read_optional_str`

```python
def _read_optional_str(payload: dict, field_name: str, *, prefix: str='ros_backend') -> str | None
```

### `_read_optional_float`

```python
def _read_optional_float(payload: dict, field_name: str, *, prefix: str='ros_backend', minimum: float) -> float | None
```

### `_read_optional_str_tuple`

```python
def _read_optional_str_tuple(payload: dict, field_name: str, *, prefix: str='ros_backend') -> tuple[str, ...] | None
```

### `_validate_system_name`

```python
def _validate_system_name(value: object, field_name: str) -> str
```

### `load_bootstrap_provider`

```python
def load_bootstrap_provider(config: StartupConfig) -> RobotSystemBootstrapProvider
```

### `build_configured_robot`

```python
def build_configured_robot(config: StartupConfig)
```

Both supported ROS backends expose the same platform bridge contract.

## `startup_error.py`

Source: [src/bootstrap/startup_error.py](../../src/bootstrap/startup_error.py).

Report fatal startup failures to desktop users as well as the terminal.

Imports (including optional/function-local imports; not a startup dependency list): `PyQt6.QtCore`, `PyQt6.QtWidgets`, `os`, `pathlib`, `sys`, `traceback`.

### `report_startup_error`

```python
def report_startup_error(error: Exception, log_directory: Path) -> None
```

Persist the traceback and show a modal dialog; never start robot services.

### `_show_error_dialog`

```python
def _show_error_dialog(error_text: str, details: str) -> None
```

## `startup_splash_runtime.py`

Source: [src/bootstrap/startup_splash_runtime.py](../../src/bootstrap/startup_splash_runtime.py).

Imports (including optional/function-local imports; not a startup dependency list): `PyQt6.QtCore`, `__future__`, `pl_gui.shell.AppShell`, `pl_gui.shell.startup_splash_view`, `src.shared_contracts.events.robot_events`.

### `_StartupSplashBridge`

```python
class _StartupSplashBridge(QObject):
```

Declared fields/defaults:

```python
state_ready = pyqtSignal(object)
```

### `startup_splash_stage_text`

```python
def startup_splash_stage_text(snapshot) -> str
```

### `StartupSplashCoordinator`

```python
class StartupSplashCoordinator:
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, shell: AppShell, splash: StartupSplashView, messaging_service) -> None
```

```python
def start(self) -> None
```

```python
def stop(self) -> None
```
