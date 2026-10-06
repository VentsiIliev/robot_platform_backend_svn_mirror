# Module reference: `pl_gui/shell`

[Package guide](README.md) · [Complete source index](../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [AppShell.py](#appshellpy)
- [FolderLauncher.py](#folderlauncherpy)
- [__init__.py](#__init__py)
- [app_descriptor.py](#app_descriptorpy)
- [app_registry.py](#app_registrypy)
- [folder_controller.py](#folder_controllerpy)
- [interfaces.py](#interfacespy)
- [session_drawer_view.py](#session_drawer_viewpy)
- [shell_config.py](#shell_configpy)
- [startup_splash_view.py](#startup_splash_viewpy)

## `AppShell.py`

Source: [pl_gui/shell/AppShell.py](../../../pl_gui/shell/AppShell.py).

Imports (including optional/function-local imports; not a startup dependency list): `PyQt6.QtCore`, `PyQt6.QtWidgets`, `pl_gui.shell.FolderLauncher`, `pl_gui.shell.app_descriptor`, `pl_gui.shell.shell_config`, `pl_gui.shell.ui.Header`, `pl_gui.shell.ui.material`, `typing`.

### `AppShell`

```python
class AppShell(QWidget):
```

Pure Qt shell - knows nothing about plugins_example, applications, or business logic

Declared fields/defaults:

```python
start_requested = pyqtSignal()
stop_requested = pyqtSignal()
pause_requested = pyqtSignal()
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, app_descriptors: List[AppDescriptor], widget_factory: Callable[[str], QWidget], ui_factory=None, languages: list=None)
```

Args: app_descriptors: List of apps to display in folders widget_factory: Callable that creates widgets given an app name ui_factory: Optional UIFactory for swappable UI components (defaults to MaterialUIFactory) languages: Optional list of (code, display_name) tuples for language selector. Defaults to [("en", "English"), ("bg", "Bulgarian")].

```python
def on_folder_opened(self, opened_folder)
```

Handle when a folder is opened - gray out other folders

```python
def on_folder_closed(self)
```

Handle when a folder is closed - restore all folders

```python
def on_app_selected(self, app_name)
```

Handle when an app is selected from any folder

```python
def on_back_button_pressed(self)
```

Handle when the back button is pressed in the sidebar

```python
def create_app(self, app_name: str) -> QWidget
```

Create app widget using injected factory - ONE LINE!

```python
def show_app(self, app_name)
```

```python
def close_all_apps(self, *, force: bool=False)
```

Close all cached app widgets and restore the folder interface. Useful when logging out or shutting down.

```python
def close_current_app(self)
```

```python
def setup_ui(self)
```

```python
def create_folders_page(self)
```

Create and configure the folders page from AppDescriptors

```python
def retranslate(self)
```

Handle language change events - called automatically

```python
def center_on_screen(self)
```

Center the window on the screen

```python
def resizeEvent(self, event)
```

Handle window resize to maintain proper layout

```python
def sizeHint(self)
```

Provide a reasonable size hint for the window

```python
def keyPressEvent(self, event)
```

Handle key press events

```python
def changeEvent(self, event)
```

Handle Qt events - particularly LanguageChange

```python
def lock(self)
```

Lock the GUI to prevent interaction

```python
def unlock(self)
```

Unlock the GUI to allow interaction

```python
def cleanup(self)
```

Cleanup resources when main window is closed

```python
def closeEvent(self, event)
```

Handle window close event

## `FolderLauncher.py`

Source: [pl_gui/shell/FolderLauncher.py](../../../pl_gui/shell/FolderLauncher.py).

Imports (including optional/function-local imports; not a startup dependency list): `PyQt6.QtCore`, `PyQt6.QtWidgets`, `dataclasses`, `pl_gui.shell.folder_controller`, `typing`.

### `FolderConfig`

```python
@dataclass
class FolderConfig:
```

Declared fields/defaults:

```python
ID: int
name: str
apps: list
translate_fn: Callable = None
```

### `FolderLauncher`

```python
class FolderLauncher(QWidget):
```

Manages the main folders page layout using FolderController vision_service

Declared fields/defaults:

```python
folder_opened = pyqtSignal(object)
folder_closed = pyqtSignal()
app_selected = pyqtSignal(str)
close_current_app_requested = pyqtSignal()
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, parent=None, folder_config_list=None, main_window=None, ui_factory=None)
```

```python
def setup_ui(self)
```

Set up the main UI for the folders page

```python
def on_folder_opened(self, opened_folder_controller=None)
```

Handle when a folder is opened - gray out other folders

```python
def enable_folder_by_id(self, ID)
```

Enable a folder by its name

```python
def disable_folder_by_id(self, ID)
```

Disable a folder by its name

```python
def on_folder_closed(self)
```

Handle when a folder is closed - restore all folders

```python
def on_app_selected(self, app_name)
```

Handle when an app is selected from any folder

```python
def on_close_current_app_requested(self)
```

Handle when close current app is requested

```python
def get_folders(self)
```

Get the list of all folder controllers (updated for compatibility)

```python
def get_folder_controllers(self)
```

Get the list of all folder controllers

```python
def get_folder_widgets(self)
```

Get the list of all folder widgets

## `__init__.py`

Source: [pl_gui/shell/__init__.py](../../../pl_gui/shell/__init__.py).

No top-level functions, classes or public value declarations; inspect the source for imports or entry-point statements.

## `app_descriptor.py`

Source: [pl_gui/shell/app_descriptor.py](../../../pl_gui/shell/app_descriptor.py).

Imports (including optional/function-local imports; not a startup dependency list): `dataclasses`.

### `AppDescriptor`

```python
@dataclass
class AppDescriptor:
```

Declared fields/defaults:

```python
name: str
icon_str: str
folder_id: int
```

## `app_registry.py`

Source: [pl_gui/shell/app_registry.py](../../../pl_gui/shell/app_registry.py).

Imports (including optional/function-local imports; not a startup dependency list): `.app_descriptor`, `PyQt6.QtWidgets`, `pl_gui.shell.base_app_widget.AppWidget`, `typing`.

### `build_app_registry`

```python
def build_app_registry(plugin_manager, widget_factory_instance) -> Tuple[List[AppDescriptor], Callable[[str], QWidget]]
```

Build app descriptors and factory from loaded plugins_example. This is the integration point - it knows about plugins_example, but MainWindow doesn't. Args: plugin_manager: Object with get_loaded_application_names() and get_application(name) widget_factory_instance: Instance that can create widgets via create_widget(app_name) Returns: (app_descriptors, widget_factory_callable)

## `folder_controller.py`

Source: [pl_gui/shell/folder_controller.py](../../../pl_gui/shell/folder_controller.py).

Imports (including optional/function-local imports; not a startup dependency list): `PyQt6.QtCore`, `dataclasses`, `pl_gui.shell.ui.styles`, `traceback`, `typing`.

### `FolderState`

```python
@dataclass
class FolderState:
```

Simple folder state data

Declared fields/defaults:

```python
is_open: bool = False
is_grayed_out: bool = False
app_running: bool = False
current_app_name: Optional[str] = None
```

### `FolderController`

```python
class FolderController(QObject):
```

Handles all folder business logic and orchestration

Declared fields/defaults:

```python
folder_opened = pyqtSignal()
folder_closed = pyqtSignal()
app_selected = pyqtSignal(str)
close_current_app_signal = pyqtSignal()
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, folder_widget, main_window=None, ui_factory=None, parent=None)
```

```python
def set_main_window(self, main_window)
```

```python
def handle_folder_click(self)
```

```python
def open_folder(self)
```

```python
def handle_outside_click(self)
```

```python
def minimize_to_floating_icon(self)
```

```python
def restore_from_floating_icon(self)
```

```python
def close_folder(self)
```

```python
def handle_app_selected(self, app_name)
```

```python
def handle_close_app(self)
```

```python
def set_disabled(self, disabled)
```

## `interfaces.py`

Source: [pl_gui/shell/interfaces.py](../../../pl_gui/shell/interfaces.py).

Imports (including optional/function-local imports; not a startup dependency list): `typing`.

### `IMenuIcon`

```python
@runtime_checkable
class IMenuIcon(Protocol):
```

Declared fields/defaults:

```python
icon_label: str
icon_path: object
icon_text: str
callback: Optional[Callable]
```

### `IFolderWidget`

```python
@runtime_checkable
class IFolderWidget(Protocol):
```

Declared fields/defaults:

```python
ID: int
folder_name: str
buttons: list
translate_fn: Optional[Callable]
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def add_app(self, app_name: str, icon_path, callback=None) -> None
```

```python
def set_grayed_out(self, grayed_out: bool) -> None
```

```python
def update_title_label(self, message=None) -> None
```

```python
def update_folder_preview(self) -> None
```

### `IExpandedView`

```python
@runtime_checkable
class IExpandedView(Protocol):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def add_app_icon(self, widget, row: int, col: int) -> None
```

```python
def fade_in(self, center_pos) -> None
```

```python
def fade_out(self) -> None
```

```python
def show_close_app_button(self) -> None
```

```python
def hide_close_app_button(self) -> None
```

### `IOverlay`

```python
@runtime_checkable
class IOverlay(Protocol):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def fade_in(self) -> None
```

```python
def fade_out(self) -> None
```

```python
def setStyleSheet(self, style: str) -> None
```

```python
def resize(self, *args) -> None
```

### `IFloatingIcon`

```python
@runtime_checkable
class IFloatingIcon(Protocol):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def show_with_animation(self) -> None
```

```python
def hide_with_animation(self) -> None
```

```python
def move(self, x: int, y: int) -> None
```

### `IExpandedViewManager`

```python
@runtime_checkable
class IExpandedViewManager(Protocol):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def show_expanded_view(self, folder_name, overlay_parent, on_close, on_app_selected, on_minimize, on_close_app)
```

```python
def populate_apps(self, buttons: list) -> None
```

```python
def fade_in(self, center_pos) -> None
```

```python
def fade_out(self) -> None
```

```python
def show_close_button(self) -> None
```

```python
def hide_close_button(self) -> None
```

### `IFloatingIconManager`

```python
@runtime_checkable
class IFloatingIconManager(Protocol):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def show_floating_icon(self, folder_name: str, on_click_callback: Callable) -> None
```

```python
def hide_floating_icon(self) -> None
```

### `IOverlayManager`

```python
@runtime_checkable
class IOverlayManager(Protocol):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def show_overlay(self)
```

```python
def hide_overlay(self) -> None
```

```python
def set_style(self, style: str) -> None
```

### `IAppWidget`

```python
@runtime_checkable
class IAppWidget(Protocol):
```

Declared fields/defaults:

```python
app_name: str
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def close_app(self) -> None
```

```python
def on_language_changed(self) -> None
```

```python
def clean_up(self) -> None
```

### `UIFactory`

```python
@runtime_checkable
class UIFactory(Protocol):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def create_folder_widget(self, ID: int, folder_name: str) -> IFolderWidget
```

```python
def create_expanded_view_manager(self, folder_widget) -> IExpandedViewManager
```

```python
def create_floating_icon_manager(self, folder_widget) -> IFloatingIconManager
```

```python
def create_overlay_manager(self, folder_widget, overlay_parent, overlay_callback) -> IOverlayManager
```

## `session_drawer_view.py`

Source: [pl_gui/shell/session_drawer_view.py](../../../pl_gui/shell/session_drawer_view.py).

Imports (including optional/function-local imports; not a startup dependency list): `PyQt6.QtCore`, `PyQt6.QtWidgets`, `__future__`, `pl_gui.shell.ui.styles`, `pl_gui.utils.utils_widgets.Drawer`.

### `SessionDrawerView`

```python
class SessionDrawerView(Drawer):
```

Generic shell drawer for displaying session details.

Declared fields/defaults:

```python
logout_requested = pyqtSignal()
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, parent: QWidget) -> None
```

```python
def set_logged_out(self) -> None
```

```python
def set_session_info(self, *, name: str, user_id: str, role: str, email: str) -> None
```

```python
def set_logout_enabled(self, enabled: bool) -> None
```

```python
def position_below(self, anchor: QWidget) -> None
```

```python
def retranslateUi(self) -> None
```

```python
def changeEvent(self, event) -> None
```

## `shell_config.py`

Source: [pl_gui/shell/shell_config.py](../../../pl_gui/shell/shell_config.py).

Shell configuration module. Provides centralized folder structure definition and dynamic management API.

Imports (including optional/function-local imports; not a startup dependency list): `PyQt6.QtCore`, `dataclasses`, `typing`.

Module declarations (expressions are shown without evaluating them):

```python
FOLDER_WORK = 1
FOLDER_SERVICE = 2
FOLDER_ADMINISTRATION = 3
```

### `FolderDefinition`

```python
@dataclass
class FolderDefinition:
```

Definition of a folder in the shell launcher.

Declared fields/defaults:

```python
id: int
name: str
translation_key: str
display_name: str
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def get_translate_fn(self) -> Callable[[str], str]
```

Return a translate function for this folder.

### `ShellConfig`

```python
class ShellConfig:
```

Configuration for the App Shell launcher. Provides both static configuration and dynamic management API.

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
@classmethod
def initialize_defaults(cls)
```

Initialize with default folder structure.

```python
@classmethod
def add_folder(cls, folder: FolderDefinition, override_defaults: bool=False) -> None
```

Add a new folder definition. Args: folder: FolderDefinition to add override_defaults: If True, don't initialize defaults (for custom-only config). If False (default), initialize defaults first (add to defaults). Raises: ValueError: If folder ID already exists Example: >>> # Add to defaults >>> new_folder = FolderDefinition(id=4, name="MAINTENANCE", ...) >>> ShellConfig.add_folder(new_folder) >>> # Override defaults (custom-only) >>> ShellConfig.add_folder(custom_folder, override_defaults=True)

```python
@classmethod
def remove_folder(cls, folder_id: int) -> bool
```

Remove a folder definition by ID. Args: folder_id: ID of folder to remove Returns: True if folder was removed, False if not found Example: >>> ShellConfig.remove_folder(4) True

```python
@classmethod
def update_folder(cls, folder_id: int, **updates) -> bool
```

Update an existing folder definition. Args: folder_id: ID of folder to update **updates: Fields to update (name, translation_key, display_name) Returns: True if folder was updated, False if not found Example: >>> ShellConfig.update_folder(1, display_name="WORK AREA") True

```python
@classmethod
def clear_folders(cls) -> None
```

Clear all folder definitions. After calling this, use add_folder(folder, override_defaults=True) to build a custom-only configuration. Warning: Use with caution. Usually followed by add_folder() calls. Example: >>> ShellConfig.clear_folders() >>> # Add custom folders without defaults >>> ShellConfig.add_folder(custom_folder, override_defaults=True)

```python
@classmethod
def reset_to_defaults(cls) -> None
```

Reset to default folder configuration. Example: >>> ShellConfig.reset_to_defaults()

```python
@classmethod
def get_folders(cls) -> list[FolderDefinition]
```

Get all folder definitions. Returns: List of all FolderDefinition objects Example: >>> folders = ShellConfig.get_folders() >>> for folder in folders: ... print(f"{folder.id}: {folder.name}")

```python
@classmethod
def get_folder_by_id(cls, folder_id: int) -> Optional[FolderDefinition]
```

Get folder definition by ID. Args: folder_id: Folder ID to find Returns: FolderDefinition if found, None otherwise Example: >>> folder = ShellConfig.get_folder_by_id(1) >>> if folder: ... print(folder.name)

```python
@classmethod
def get_all_folder_ids(cls) -> list[int]
```

Get all defined folder IDs. Returns: List of folder IDs Example: >>> ids = ShellConfig.get_all_folder_ids() >>> print(ids) # [1, 2, 3]

```python
@classmethod
def folder_exists(cls, folder_id: int) -> bool
```

Check if folder ID exists in configuration. Args: folder_id: Folder ID to check Returns: True if folder exists, False otherwise Example: >>> if ShellConfig.folder_exists(4): ... print("Folder 4 exists")

```python
@classmethod
def get_folders_with_apps(cls, filtered_apps: dict[int, list]) -> list[FolderDefinition]
```

Get only folders that have apps assigned. Args: filtered_apps: Dictionary mapping folder_id to list of apps Returns: List of FolderDefinition objects that have apps Example: >>> app_map = {1: [app1, app2], 2: [app3]} >>> folders = ShellConfig.get_folders_with_apps(app_map)

### `create_custom_folder`

```python
def create_custom_folder(folder_id: int, name: str, display_name: Optional[str]=None, translation_key: Optional[str]=None) -> FolderDefinition
```

Helper to create a custom folder definition. Args: folder_id: Unique folder ID name: Internal folder name (uppercase recommended) display_name: Display name (defaults to name) translation_key: Translation key (defaults to folder.{name.lower()}) Returns: FolderDefinition ready to add via ShellConfig.add_folder() Example: >>> folder = create_custom_folder(4, "MAINTENANCE", "Maintenance") >>> ShellConfig.add_folder(folder)

## `startup_splash_view.py`

Source: [pl_gui/shell/startup_splash_view.py](../../../pl_gui/shell/startup_splash_view.py).

Imports (including optional/function-local imports; not a startup dependency list): `PyQt6.QtCore`, `PyQt6.QtGui`, `PyQt6.QtWidgets`, `__future__`, `pathlib`, `pl_gui.settings.settings_view.styles`.

### `StartupSplashView`

```python
class StartupSplashView(QWidget):
```

Reusable shell startup/loading view.

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, parent: QWidget | None=None, *, logo_path: str | Path | None=None) -> None
```

```python
def set_title(self, text: str) -> None
```

```python
def set_message(self, text: str) -> None
```

```python
def set_steps(self, steps: list[str]) -> None
```

```python
def set_active_step(self, index: int) -> None
```

```python
def mark_complete(self) -> None
```

```python
def set_error(self, message: str) -> None
```

```python
def set_busy(self, busy: bool) -> None
```

```python
def retranslateUi(self) -> None
```

```python
def changeEvent(self, event) -> None
```
