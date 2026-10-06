# Module reference: `src/applications/base`

[Package guide](README.md) · [Complete source index](../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [app_dialog.py](#app_dialogpy)
- [app_styles.py](#app_stylespy)
- [application_factory.py](#application_factorypy)
- [application_interface.py](#application_interfacepy)
- [background_worker.py](#background_workerpy)
- [broker_subscription_mixin.py](#broker_subscription_mixinpy)
- [collapsible_settings_view.py](#collapsible_settings_viewpy)
- [dashboard_camera_feed_mixin.py](#dashboard_camera_feed_mixinpy)
- [dashboard_process_state_mixin.py](#dashboard_process_state_mixinpy)
- [drawer_toggle.py](#drawer_togglepy)
- [i_application_controller.py](#i_application_controllerpy)
- [i_application_model.py](#i_application_modelpy)
- [i_application_view.py](#i_application_viewpy)
- [jog_controller.py](#jog_controllerpy)
- [keyboard_settings_view.py](#keyboard_settings_viewpy)
- [notification_presenter.py](#notification_presenterpy)
- [robot_connection_notifier.py](#robot_connection_notifierpy)
- [robot_jog_service.py](#robot_jog_servicepy)
- [robot_jog_service_builder.py](#robot_jog_service_builderpy)
- [robot_jog_widget.py](#robot_jog_widgetpy)
- [settings_keyboard_test.py](#settings_keyboard_testpy)
- [styled_message_box.py](#styled_message_boxpy)
- [widget_application.py](#widget_applicationpy)

## `__init__.py`

Source: [src/applications/base/__init__.py](../../../src/applications/base/__init__.py).

Imports (including optional/function-local imports; not a startup dependency list): `src.applications.base.keyboard_settings_view`.

Package-level import/export surface:

```python
from src.applications.base.keyboard_settings_view import KeyboardSettingsView
```

Module declarations (expressions are shown without evaluating them):

```python
__all__ = ['KeyboardSettingsView']
```

## `app_dialog.py`

Source: [src/applications/base/app_dialog.py](../../../src/applications/base/app_dialog.py).

Imports (including optional/function-local imports; not a startup dependency list): `PyQt6.QtCore`, `PyQt6.QtWidgets`, `pl_gui.settings.settings_view.styles`.

Module declarations (expressions are shown without evaluating them):

```python
DIALOG_INPUT_STYLE = f'\nQLineEdit, QSpinBox, QDoubleSpinBox {{\n    background: white;\n    color: {TEXT_COLOR};\n    border: 2px solid {BORDER};\n    border-radius: 8px;\n    padding: 8px 12px;\n    font-size: 11pt;\n    min-height: 40px;\n}}\nQLineEdit:focus, QSpinBox:focus {{ border-color: {PRIMARY}; }}\n'
DIALOG_COMBO_STYLE = f'\nQComboBox {{\n    background: white;\n    color: {TEXT_COLOR};\n    border: 2px solid {BORDER};\n    border-radius: 8px;\n    padding: 8px 12px;\n    font-size: 11pt;\n    min-height: 40px;\n}}\nQComboBox:focus {{ border-color: {PRIMARY}; }}\nQComboBox::drop-down {{ border: none; padding-right: 8px; }}\nQComboBox QAbstractItemView {{\n    background: white;\n    border: 2px solid {BORDER};\n    border-radius: 8px;\n    selection-background-color: {PRIMARY};\n    selection-color: white;\n    font-size: 11pt;\n    padding: 4px;\n}}\n'
DIALOG_CHECKBOX_STYLE = f'\nQCheckBox {{\n    color: {TEXT_COLOR};\n    font-size: 11pt;\n    spacing: 10px;\n}}\nQCheckBox::indicator {{\n    width: 22px; height: 22px;\n    border: 2px solid {BORDER};\n    border-radius: 4px;\n    background: white;\n}}\nQCheckBox::indicator:checked {{\n    background: {PRIMARY};\n    border-color: {PRIMARY};\n}}\nQCheckBox::indicator:hover {{ border-color: {PRIMARY}; }}\n'
```

### `AppDialog`

```python
class AppDialog(QDialog):
```

Base for all app dialogs — consistent styling + standard button row.

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, title: str, min_width: int=400, parent=None)
```

## `app_styles.py`

Source: [src/applications/base/app_styles.py](../../../src/applications/base/app_styles.py).

Imports (including optional/function-local imports; not a startup dependency list): `PyQt6.QtWidgets`, `__future__`, `pl_gui.settings.settings_view.styles`.

Module declarations (expressions are shown without evaluating them):

```python
APP_BG = BG_COLOR
APP_PANEL_BG = '#FFFFFF'
APP_CARD_STYLE = f'background: {APP_PANEL_BG}; border: 1px solid {BORDER}; border-radius: 10px;'
APP_SECTION_LABEL_STYLE = 'color: #1A1A2E; font-size: 9pt; font-weight: bold; background: transparent; padding: 4px 0;'
APP_SECTION_HINT_STYLE = 'color: #666688; font-size: 8.5pt; background: transparent; padding: 0 0 4px 0;'
APP_CAPTION_STYLE = 'color: #888899; font-size: 8pt; background: transparent; padding: 2px 6px;'
APP_LOG_STYLE = f'\nQTextEdit {{\n    background: #F3F4F8;\n    color: #1A1A2E;\n    border: 1px solid {BORDER};\n    border-radius: 6px;\n    font-family: monospace;\n    font-size: 9pt;\n    padding: 6px;\n}}\n'
APP_PANEL_SPLIT_STYLE = f'background: {APP_PANEL_BG}; border-left: 1px solid {BORDER};'
APP_PRIMARY_BUTTON_STYLE = ACTION_BTN_STYLE
APP_SECONDARY_BUTTON_STYLE = GHOST_BTN_STYLE
APP_SEQUENCE_BUTTON_STYLE = '\nMaterialButton {\n    background: #EDE7F6;\n    color: #5B3ED6;\n    border: 1.5px solid #5B3ED6;\n    border-radius: 8px;\n    font-weight: bold;\n    min-height: 44px;\n}\nMaterialButton:hover   { background: #E0D6F0; }\nMaterialButton:pressed { background: #D4CAE4; }\n'
APP_DANGER_BUTTON_STYLE = '\nMaterialButton {\n    background: #D32F2F;\n    color: white;\n    border-radius: 8px;\n    font-weight: bold;\n    min-height: 44px;\n}\nMaterialButton:hover   { background: #B71C1C; }\nMaterialButton:pressed { background: #9A0007; }\nMaterialButton:disabled {\n    background: #EEEEEE;\n    color: #BDBDBD;\n    border: 1.5px solid #E0E0E0;\n}\n'
APP_SUCCESS_BUTTON_STYLE = '\nMaterialButton {\n    background: #E8F5E9;\n    color: #2E7D32;\n    border: 1.5px solid #4CAF50;\n    border-radius: 8px;\n    font-weight: bold;\n    min-height: 44px;\n}\nMaterialButton:hover   { background: #DCEDC8; }\nMaterialButton:pressed { background: #C8E6C9; }\nMaterialButton:disabled {\n    background: #EEEEEE;\n    color: #BDBDBD;\n    border: 1.5px solid #E0E0E0;\n}\n'
APP_TOGGLE_OFF_BUTTON_STYLE = '\nMaterialButton {\n    background: transparent;\n    color: #888;\n    border: 1.5px solid #CCCCCC;\n    border-radius: 8px;\n    font-weight: bold;\n    min-height: 36px;\n}\nMaterialButton:hover { background: rgba(0,0,0,0.04); }\n'
APP_TOGGLE_ON_BUTTON_STYLE = '\nMaterialButton {\n    background: #E8F5E9;\n    color: #2E7D32;\n    border: 1.5px solid #4CAF50;\n    border-radius: 8px;\n    font-weight: bold;\n    min-height: 36px;\n}\nMaterialButton:hover { background: #DCEDC8; }\n'
```

### `panel_style`

```python
def panel_style(*, radius: int=6, bg: str=APP_PANEL_BG, border_color: str=BORDER) -> str
```

### `split_panel_style`

```python
def split_panel_style(*, bg: str=APP_PANEL_BG, border_color: str=BORDER) -> str
```

### `muted_text_style`

```python
def muted_text_style(*, color: str='#666688', size_pt: float=9.0, extra: str='') -> str
```

### `emphasis_text_style`

```python
def emphasis_text_style(*, color: str, size_pt: float=9.0, bold: bool=True, extra: str='') -> str
```

### `monospace_log_style`

```python
def monospace_log_style(*, dark: bool=False, font_size_pt: float=9.0) -> str
```

### `table_style`

```python
def table_style(*, header_font_pt: float=9.0, body_font_pt: float=9.0, radius: int=6) -> str
```

### `list_style`

```python
def list_style(*, radius: int=4, font_px: int=12, text_color: str=TEXT_COLOR) -> str
```

### `input_style`

```python
def input_style(*, selector: str='QLineEdit', radius: int=6, font_pt: float=9.0) -> str
```

### `compact_button_style`

```python
def compact_button_style(*, variant: str='primary', selector: str='QPushButton', min_height: int=34, radius: int=6) -> str
```

### `toggle_button_style`

```python
def toggle_button_style(*, selector: str='QPushButton', radius: int=4, font_pt: float=9.0, checked_bg: str='#E8F5E9', checked_border: str='#2E7D32', checked_fg: str='#1E4620') -> str
```

### `semantic_button_style`

```python
def semantic_button_style(*, selector: str='QPushButton', bg: str, hover_bg: str, fg: str='white', disabled_bg: str='#9E9E9E', disabled_fg: str='white', radius: int=8, min_height: int=44) -> str
```

### `indicator_dot_style`

```python
def indicator_dot_style(*, color: str, font_pt: int=18) -> str
```

### `app_state_label_style`

```python
def app_state_label_style(*, fg: str, bg: str) -> str
```

### `outlined_role_button_style`

```python
def outlined_role_button_style(*, checked_bg: str=PRIMARY, checked_fg: str='white') -> str
```

### `divider`

```python
def divider() -> QWidget
```

### `section_label`

```python
def section_label(text: str) -> QLabel
```

### `section_hint`

```python
def section_hint(text: str) -> QLabel
```

## `application_factory.py`

Source: [src/applications/base/application_factory.py](../../../src/applications/base/application_factory.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `abc`, `logging`, `pl_gui.shell.base_app_widget.AppWidget`, `src.applications.base.i_application_controller`, `src.applications.base.i_application_model`, `src.applications.base.i_application_view`, `src.applications.base.jog_controller`.

### `finalize_application_build`

```python
def finalize_application_build(*, logger: logging.Logger, factory_name: str, model: IApplicationModel, view: IApplicationView, controller: IApplicationController, messaging=None, jog_service=None) -> AppWidget
```

### `ApplicationFactory`

```python
class ApplicationFactory(ABC):
```

Template-method factory for all MVC applications. Subclasses implement the three abstract factory methods. This base class owns: - the wiring order (model → view → controller) - the GC fix (view._controller = controller) - the load call (controller.load()) - the teardown wiring (view.clean_up → controller.stop()) Usage: class MyApplicationFactory(ApplicationFactory): def _create_model(self, service): return MyModel(service) def _create_view(self): return MyView() def _create_controller(self, model, view): return MyController(model, view) widget = MyApplicationFactory().build(service)

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def build(self, service, messaging=None, jog_service=None) -> AppWidget
```

## `application_interface.py`

Source: [src/applications/base/application_interface.py](../../../src/applications/base/application_interface.py).

Imports (including optional/function-local imports; not a startup dependency list): `PyQt6.QtWidgets`, `abc`, `src.engine.core.i_messaging_service`.

### `IApplication`

```python
class IApplication(ABC):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
@abstractmethod
def register(self, messaging_service: IMessagingService) -> None
```

```python
@abstractmethod
def create_widget(self) -> QWidget
```

## `background_worker.py`

Source: [src/applications/base/background_worker.py](../../../src/applications/base/background_worker.py).

BackgroundWorker — mixin that provides a thread-safe _run_in_thread() helper. Eliminates the private ``_Worker`` class + worker-list + ``_run_in_thread`` boilerplate that was duplicated across modbus_settings, robot_settings, height_measuring, and device_control controllers. Usage:: class MyController(IApplicationController, BackgroundWorker): def __init__(self, ...): BackgroundWorker.__init__(self) ... def _do_something(self) -> None: self._run_in_thread( fn = self._model.slow_operation, on_done = self._on_done, # called on GUI thread on_error = self._on_error, # optional ) def stop(self) -> None: self._stop_threads() ... Notes ----- - ``BackgroundWorker`` is NOT a ``QObject`` subclass — it does not interfere with Qt's meta-object system. Always put Qt base classes first in the MRO. - A strong reference to every ``(QThread, _Worker)`` pair is kept in ``self._active_workers`` so Python's GC cannot destroy the worker while its thread is still running. - The attribute is deliberately named ``_active_workers``, NOT ``_active``: controller classes in this codebase widely use ``self._active`` as a boolean "controller is live" flag, and a subclass assignment would otherwise silently shadow the worker list (``bool`` has no ``append``). - ``_on_thread_finished`` is connected to ``thread.finished``; it prunes completed pairs automatically, so ``_active_workers`` stays lean.

Imports (including optional/function-local imports; not a startup dependency list): `PyQt6.QtCore`, `__future__`, `logging`, `typing`.

### `_Worker`

```python
class _Worker(QObject):
```

Runs *fn* off the GUI thread; emits ``finished`` or ``failed``.

Declared fields/defaults:

```python
finished = pyqtSignal(object)
failed = pyqtSignal(str)
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, fn: Callable) -> None
```

```python
def run(self) -> None
```

### `_UiRelay`

```python
class _UiRelay(QObject):
```

Ensures result/error callbacks run on the GUI thread.

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, on_done: Callable, on_error: Optional[Callable]=None, on_thread_finished: Optional[Callable]=None) -> None
```

```python
@pyqtSlot(object)
def handle_finished(self, result) -> None
```

```python
@pyqtSlot(str)
def handle_failed(self, message: str) -> None
```

```python
@pyqtSlot()
def handle_thread_finished(self) -> None
```

### `BackgroundWorker`

```python
class BackgroundWorker:
```

Mixin that provides ``_run_in_thread()`` for controller classes. Mix in after ``IApplicationController`` (or any QObject base):: class MyController(IApplicationController, BackgroundWorker): ...

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self) -> None
```

## `broker_subscription_mixin.py`

Source: [src/applications/base/broker_subscription_mixin.py](../../../src/applications/base/broker_subscription_mixin.py).

BrokerSubscriptionMixin — manages broker topic subscriptions in controllers. Eliminates the ``_subs: List[Tuple[str, Callable]]`` list + ``_sub()`` helper + manual unsubscribe loop that was duplicated across glue_cell_settings and camera_settings controllers (and any future broker-subscribing controller). Usage:: class MyController(IApplicationController, BrokerSubscriptionMixin): def __init__(self, ..., messaging: IMessagingService): BrokerSubscriptionMixin.__init__(self) self._broker = messaging ... def load(self) -> None: self._subscribe(SomeTopic.EVENT, self._bridge.event_signal.emit) def stop(self) -> None: self._unsubscribe_all() ---- SignalBridge ------------ A base class for cross-thread signal relay objects. Subclass it and declare ``pyqtSignal`` attributes for each piece of data that needs to travel from a broker callback thread to the Qt main thread:: class _Bridge(SignalBridge): frame_ready = pyqtSignal(object) state_changed = pyqtSignal(str) # In controller.__init__: self._bridge = _Bridge() self._bridge.frame_ready.connect(self._view.set_frame) # In load() — broker callback fires on background thread, signal delivers # to main thread automatically: self._subscribe(VisionTopics.LATEST_IMAGE, lambda msg: self._bridge.frame_ready.emit(msg))

Imports (including optional/function-local imports; not a startup dependency list): `PyQt6.QtCore`, `__future__`, `typing`.

### `SignalBridge`

```python
class SignalBridge(QObject):
```

Base class for cross-thread signal relay objects. Subclass and add ``pyqtSignal`` fields — no other implementation needed. The name makes the intent obvious in controller code.

### `BrokerSubscriptionMixin`

```python
class BrokerSubscriptionMixin:
```

Mixin that manages broker topic subscriptions for controller classes. Requires ``self._broker`` (an ``IMessagingService``) to be set before any ``_subscribe`` call — typically assigned in ``__init__``.

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self) -> None
```

## `collapsible_settings_view.py`

Source: [src/applications/base/collapsible_settings_view.py](../../../src/applications/base/collapsible_settings_view.py).

Imports (including optional/function-local imports; not a startup dependency list): `PyQt6.QtCore`, `PyQt6.QtWidgets`, `pl_gui.settings.settings_view.group_widget`, `pl_gui.settings.settings_view.schema`, `pl_gui.settings.settings_view.settings_view`, `pl_gui.settings.settings_view.styles`, `typing`.

### `CollapsibleGroup`

```python
class CollapsibleGroup(QWidget):
```

Declared fields/defaults:

```python
value_changed = pyqtSignal(str, object)
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, schema: SettingGroup, parent=None)
```

```python
def set_values(self, flat: dict) -> None
```

```python
def get_values(self) -> dict
```

### `CollapsibleSettingsView`

```python
class CollapsibleSettingsView(SettingsView):
```

## `dashboard_camera_feed_mixin.py`

Source: [src/applications/base/dashboard_camera_feed_mixin.py](../../../src/applications/base/dashboard_camera_feed_mixin.py).

Imports (including optional/function-local imports; not a startup dependency list): `PyQt6.QtCore`, `__future__`, `src.applications.base.broker_subscription_mixin`, `src.shared_contracts.events.vision_events`.

### `_DashboardCameraBridge`

```python
class _DashboardCameraBridge(SignalBridge):
```

Declared fields/defaults:

```python
frame_ready = pyqtSignal(object)
```

### `DashboardCameraFeedMixin`

```python
class DashboardCameraFeedMixin:
```

Shared dashboard camera-feed wiring. Assumptions: - controller has `_view` - controller has either `_sub(topic, callback)` or `_subscribe(topic, callback)` - view exposes `set_trajectory_image(image)`

## `dashboard_process_state_mixin.py`

Source: [src/applications/base/dashboard_process_state_mixin.py](../../../src/applications/base/dashboard_process_state_mixin.py).

Imports (including optional/function-local imports; not a startup dependency list): `PyQt6.QtCore`, `__future__`, `src.applications.base.broker_subscription_mixin`, `src.shared_contracts.events.process_events`.

### `_DashboardProcessBridge`

```python
class _DashboardProcessBridge(SignalBridge):
```

Declared fields/defaults:

```python
state_ready = pyqtSignal(object)
warning_ready = pyqtSignal(str, str)
```

### `DashboardProcessStateMixin`

```python
class DashboardProcessStateMixin:
```

Shared dashboard process-state wiring. Assumptions: - controller has `_model` with `_service` - dashboard service exposes `get_process_id()` - controller has either `_sub(topic, callback)` or `_subscribe(topic, callback)` - model exposes `load()` - view exposes `apply_dashboard_state(state)`

## `drawer_toggle.py`

Source: [src/applications/base/drawer_toggle.py](../../../src/applications/base/drawer_toggle.py).

Imports (including optional/function-local imports; not a startup dependency list): `PyQt6.QtCore`, `PyQt6.QtWidgets`, `pl_gui.settings.settings_view.styles`.

### `DrawerToggle`

```python
class DrawerToggle(QObject):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, parent_widget, side='right', width=300, height_offset=0)
```

```python
def add_widget(self, widget, *, fill_height: bool=False)
```

```python
def set_visible(self, visible: bool) -> None
```

```python
def eventFilter(self, obj, event)
```

## `i_application_controller.py`

Source: [src/applications/base/i_application_controller.py](../../../src/applications/base/i_application_controller.py).

Imports (including optional/function-local imports; not a startup dependency list): `abc`.

### `IApplicationController`

```python
class IApplicationController(ABC):
```

Base interface for all application controllers. The only layer allowed touching both model and view. Enforces the lifecycle contract: - load(): called once by the factory — populates view from model - stop(): called on view destruction — unsubscribes broker topics, stops threads

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
@abstractmethod
def load(self) -> None
```

```python
@abstractmethod
def stop(self) -> None
```

## `i_application_model.py`

Source: [src/applications/base/i_application_model.py](../../../src/applications/base/i_application_model.py).

Imports (including optional/function-local imports; not a startup dependency list): `abc`.

### `IApplicationModel`

```python
class IApplicationModel(ABC):
```

Base interface for all application models. Responsible for in-memory state and I/O delegation to the service. Has NO knowledge of Qt, views, or controllers.

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
@abstractmethod
def load(self)
```

```python
@abstractmethod
def save(self, *args, **kwargs) -> None
```

## `i_application_view.py`

Source: [src/applications/base/i_application_view.py](../../../src/applications/base/i_application_view.py).

Imports (including optional/function-local imports; not a startup dependency list): `PyQt6.QtCore`, `abc`, `pl_gui.shell.base_app_widget.AppWidget`, `src.applications.base.drawer_toggle`, `src.applications.base.robot_jog_widget`, `typing`.

### `IApplicationView`

```python
class IApplicationView(AppWidget):
```

Base class for all application views. Extends AppWidget — required by the shell (provides app_closed signal). Enforces the two rules of the view layer: - setup_ui() : build widgets, wire internal signals to outbound pyqtSignals - clean_up() : stop timers, threads, subscriptions on widget destruction

Declared fields/defaults:

```python
SHOW_JOG_WIDGET = False
JOG_LIVE_POSITION_ENABLED = True
JOG_FRAME_SELECTOR_ENABLED = False
JOG_DRAWER_SIDE = 'right'
JOG_DRAWER_WIDTH = 320
jog_requested = pyqtSignal(str, str, str, float)
joint_jog_requested = pyqtSignal(str, str, str, float)
jog_started = pyqtSignal(str)
jog_stopped = pyqtSignal(str)
recovery_mode_changed = pyqtSignal(bool)
language_changed = pyqtSignal()
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, title: str, parent=None)
```

```python
def enable_jog_widget(self, enabled: bool) -> None
```

```python
def set_jog_position(self, pos: list) -> None
```

```python
def set_joint_position(self, joints: list) -> None
```

```python
def set_jog_frame_options(self, names: list[str], default: str | None=None) -> None
```

```python
def set_jog_frame(self, name: str) -> None
```

```python
def get_jog_frame(self) -> str
```

```python
def retranslateUi(self) -> None
```

Override in subclasses to refresh widget-owned text.

```python
def on_language_changed(self) -> None
```

Default localization hook for all application views.

```python
@abstractmethod
def setup_ui(self) -> None
```

```python
@abstractmethod
def clean_up(self) -> None
```

## `jog_controller.py`

Source: [src/applications/base/jog_controller.py](../../../src/applications/base/jog_controller.py).

Imports (including optional/function-local imports; not a startup dependency list): `PyQt6.QtCore`, `functools`, `logging`, `src.applications.base.robot_jog_service`, `src.engine.core.i_messaging_service`, `src.shared_contracts.events.robot_events`, `threading`, `typing`.

### `_coerce_joint_degrees`

```python
def _coerce_joint_degrees(value: Any) -> list[float]
```

### `_Bridge`

```python
class _Bridge(QObject):
```

Declared fields/defaults:

```python
frame_options_received = pyqtSignal(object, str)
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, view, apply_frame_options)
```

```python
def ingest_position(self, pos: list) -> None
```

```python
def ingest_joints(self, joints: list) -> None
```

```python
@pyqtSlot()
def flush_position(self) -> None
```

```python
@pyqtSlot(object, str)
def handle_frame_options(self, names_obj, default: str) -> None
```

```python
@pyqtSlot()
def handle_view_destroyed(self) -> None
```

```python
def stop(self) -> None
```

### `_FireAndForget`

```python
class _FireAndForget(QRunnable):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, fn)
```

```python
def run(self)
```

### `JogController`

```python
class JogController:
```

Reusable controller fragment — wires a jog-capable view to robot jog + live position display. The host view must expose: - jog_requested pyqtSignal(str, str, str, float) # command, axis, direction, step - jog_stopped pyqtSignal(str) # key - set_jog_position(pos: list) -> None Usage inside a host application controller:: class MyController(IApplicationController): def __init__(self, model, view, messaging, jog_service): ... self._jog = JogController(view, jog_service, messaging) def load(self): ... self._jog.start() def stop(self): self._jog.stop() ...

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, view, jog_service: RobotJogService, messaging: IMessagingService)
```

```python
def start(self) -> None
```

```python
def stop(self) -> None
```

## `keyboard_settings_view.py`

Source: [src/applications/base/keyboard_settings_view.py](../../../src/applications/base/keyboard_settings_view.py).

Imports (including optional/function-local imports; not a startup dependency list): `pl_gui.settings.settings_view`, `pl_gui.settings.settings_view.schema`, `pl_gui.settings.settings_view.styles`, `pl_gui.settings.settings_view.widget_factory`, `src.applications.base.collapsible_settings_view`, `src.applications.base.widgets.card_checkbox`, `src.applications.base.widgets.custom_virtual_keyboard`, `src.applications.base.widgets.keyboard_number_field`, `typing`.

### `_make_keyboard_line_edit`

```python
def _make_keyboard_line_edit(field: SettingField, emit: Callable[[Any], None]) -> KeyboardLineEdit
```

### `_make_keyboard_spinbox`

```python
def _make_keyboard_spinbox(field: SettingField, emit: Callable[[Any], None]) -> KeyboardNumberField
```

### `_make_keyboard_double_spinbox`

```python
def _make_keyboard_double_spinbox(field: SettingField, emit: Callable[[Any], None]) -> KeyboardNumberField
```

### `_keyboard_setting_handlers`

```python
def _keyboard_setting_handlers() -> dict[str, WidgetHandler]
```

### `install_keyboard_setting_handlers`

```python
def install_keyboard_setting_handlers() -> dict[str, WidgetHandler]
```

### `restore_setting_handlers`

```python
def restore_setting_handlers(handlers: dict[str, WidgetHandler]) -> None
```

### `build_with_keyboard_setting_handlers`

```python
def build_with_keyboard_setting_handlers(fn: Callable[[], Any]) -> Any
```

### `build_with_keyboard_card_handlers`

```python
def build_with_keyboard_card_handlers(fn: Callable[[], Any]) -> Any
```

Use compact keyboard fields and plus/minus controls for a card form.

### `install_keyboard_setting_handlers_permanently`

```python
def install_keyboard_setting_handlers_permanently() -> None
```

### `KeyboardSettingsView`

```python
class KeyboardSettingsView(CollapsibleSettingsView):
```

Collapsible settings view whose editable fields use the shared virtual keyboard.

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, component_name: str='KeyboardSettingsView', mapper=None, parent=None)
```

```python
def add_tab(self, title: str, groups: List[SettingGroup]) -> None
```

```python
def add_plain_tab(self, title: str, groups: List[SettingGroup]) -> None
```

## `notification_presenter.py`

Source: [src/applications/base/notification_presenter.py](../../../src/applications/base/notification_presenter.py).

Imports (including optional/function-local imports; not a startup dependency list): `PyQt6.QtCore`, `PyQt6.QtWidgets`, `__future__`, `logging`, `src.applications.base.styled_message_box`, `src.engine.core.i_messaging_service`, `src.shared_contracts.events.notification_events`, `typing`.

### `_NotificationBridge`

```python
class _NotificationBridge(QObject):
```

Declared fields/defaults:

```python
notification = pyqtSignal(object)
dismiss = pyqtSignal(object)
```

### `NotificationTextResolver`

```python
class NotificationTextResolver:
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, translate: Callable[[str], str] | None=None) -> None
```

```python
def resolve_text(self, key: str, fallback: str, params: Mapping[str, object]) -> str
```

### `UserNotificationPresenter`

```python
class UserNotificationPresenter:
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, parent: QWidget, messaging_service: IMessagingService, translate: Callable[[str], str] | None=None) -> None
```

```python
def start(self) -> None
```

```python
def stop(self) -> None
```

```python
def present(self, event: UserNotificationEvent) -> None
```

## `robot_connection_notifier.py`

Source: [src/applications/base/robot_connection_notifier.py](../../../src/applications/base/robot_connection_notifier.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `logging`, `src.engine.core.i_messaging_service`, `src.engine.robot.services.robot_state_snapshot`, `src.shared_contracts.events.notification_events`, `src.shared_contracts.events.robot_events`.

### `RobotConnectionNotifier`

```python
class RobotConnectionNotifier:
```

Converts robot availability changes into user-facing notifications.

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, messaging_service: IMessagingService, *, suppress_until_ready: bool=False) -> None
```

```python
def start(self) -> None
```

```python
def stop(self) -> None
```

## `robot_jog_service.py`

Source: [src/applications/base/robot_jog_service.py](../../../src/applications/base/robot_jog_service.py).

Imports (including optional/function-local imports; not a startup dependency list): `logging`, `src.engine.robot.enums.axis`, `threading`, `typing`.

### `RobotJogService`

```python
class RobotJogService:
```

Application-layer adapter: converts string axis/direction to engine enums and delegates to IRobotService. Accepts None robot (robot not connected) — all calls become no-ops.

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, robot_service=None, pose_resolver=None, pose_resolver_getter=None, frame_options_getter=None, default_frame_getter=None, tool_getter=None, user_getter=None, move_velocity: float=10.0, move_acceleration: float=10.0, move_velocity_getter: Callable[[], float | None] | None=None, move_acceleration_getter: Callable[[], float | None] | None=None, servo_linear_speed_mm_s: float=250.0, servo_angular_speed_deg_s: float=3.0, servo_linear_speed_getter: Callable[[], float | None] | None=None, servo_angular_speed_getter: Callable[[], float | None] | None=None, recovery_servo_linear_speed_getter: Callable[[], float | None] | None=None, recovery_servo_angular_speed_getter: Callable[[], float | None] | None=None)
```

```python
def set_recovery_mode(self, enabled: bool) -> None
```

```python
def recovery_mode_enabled(self) -> bool
```

```python
def set_frame(self, frame_name: str) -> None
```

```python
def get_available_frames(self) -> list[str]
```

```python
def get_default_frame(self) -> str
```

```python
def jog(self, command: str, axis: str | None=None, direction: str | None=None, step: float | None=None) -> None
```

```python
def joint_jog(self, command: str, joint: str | None=None, direction: str | None=None, step: float | None=None) -> None
```

```python
def stop_jog(self) -> None
```

## `robot_jog_service_builder.py`

Source: [src/applications/base/robot_jog_service_builder.py](../../../src/applications/base/robot_jog_service_builder.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `src.applications.base.robot_jog_service`, `src.engine.common_settings_ids`.

### `build_robot_system_jog_service`

```python
def build_robot_system_jog_service(robot_system, reference_rz_provider=None) -> RobotJogService
```

## `robot_jog_widget.py`

Source: [src/applications/base/robot_jog_widget.py](../../../src/applications/base/robot_jog_widget.py).

Imports (including optional/function-local imports; not a startup dependency list): `PyQt6.QtCore`, `PyQt6.QtWidgets`, `functools`, `pl_gui.settings.settings_view.styles`, `sys`, `typing`.

### `RobotJogWidget`

```python
class RobotJogWidget(QFrame):
```

Declared fields/defaults:

```python
jog_requested = pyqtSignal(str, str, str, float)
jog_started = pyqtSignal(str)
jog_stopped = pyqtSignal(str)
frame_changed = pyqtSignal(str)
joint_jog_requested = pyqtSignal(str, str, str, float)
joint_jog_started = pyqtSignal(str)
joint_jog_stopped = pyqtSignal(str)
recovery_mode_changed = pyqtSignal(bool)
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, parent=None)
```

```python
def set_position(self, pos: list) -> None
```

```python
def set_joint_position(self, joints: list) -> None
```

```python
def set_frame_options(self, names: Sequence[object], default: Optional[str]=None) -> None
```

Populate the frame selector combo box.

```python
def enable_frame_selector(self, enabled: bool) -> None
```

Show or hide the optional frame selector.

```python
def set_frame(self, name: str) -> None
```

Programmatically select a frame without emitting frame_changed.

```python
def get_frame(self) -> str
```

Return the currently selected frame name, or empty string if none.

```python
def retranslateUi(self) -> None
```

```python
def changeEvent(self, event) -> None
```

## `settings_keyboard_test.py`

Source: [src/applications/base/settings_keyboard_test.py](../../../src/applications/base/settings_keyboard_test.py).

Imports (including optional/function-local imports; not a startup dependency list): `PyQt6.QtWidgets`, `pl_gui.settings.settings_view.schema`, `src.applications.base.keyboard_settings_view`, `sys`.

### `build_keyboard_settings_view`

```python
def build_keyboard_settings_view() -> KeyboardSettingsView
```

### `SettingsKeyboardWindow`

```python
class SettingsKeyboardWindow(QMainWindow):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self)
```

### `main`

```python
def main() -> None
```

## `styled_message_box.py`

Source: [src/applications/base/styled_message_box.py](../../../src/applications/base/styled_message_box.py).

Imports (including optional/function-local imports; not a startup dependency list): `PyQt6.QtCore`, `PyQt6.QtWidgets`, `dataclasses`, `pl_gui.settings.settings_view.styles`, `typing`.

### `_make`

```python
def _make(icon, title: str, text: str, parent: QWidget) -> QMessageBox
```

### `make_warning`

```python
def make_warning(parent: QWidget, title: str, text: str) -> QMessageBox
```

### `make_info`

```python
def make_info(parent: QWidget, title: str, text: str) -> QMessageBox
```

### `make_critical`

```python
def make_critical(parent: QWidget, title: str, text: str) -> QMessageBox
```

### `DialogAction`

```python
@dataclass(frozen=True)
class DialogAction:
```

Declared fields/defaults:

```python
key: str
text: str
primary: bool = False
full_width: bool = False
```

### `ActionWarningDialog`

```python
class ActionWarningDialog(QDialog):
```

Optional action layout for warnings that need a clear next step.

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, parent: QWidget, title: str, text: str, *, heading: str, guidance: str='', status: str='', actions: Sequence[DialogAction]) -> None
```

### `show_warning`

```python
def show_warning(parent: QWidget, title: str, text: str, *, heading: str='', guidance: str='', status: str='', actions: Sequence[DialogAction] | None=None) -> str | None
```

### `show_info`

```python
def show_info(parent: QWidget, title: str, text: str) -> None
```

### `show_critical`

```python
def show_critical(parent: QWidget, title: str, text: str) -> None
```

### `ask_yes_no`

```python
def ask_yes_no(parent: QWidget, title: str, text: str, default_no: bool=True) -> bool
```

## `widget_application.py`

Source: [src/applications/base/widget_application.py](../../../src/applications/base/widget_application.py).

Imports (including optional/function-local imports; not a startup dependency list): `PyQt6.QtWidgets`, `logging`, `src.applications.base.application_interface`, `src.engine.core.i_messaging_service`, `typing`.

### `WidgetApplication`

```python
class WidgetApplication(IApplication):
```

Generic IApplication adapter that wraps any widget_factory callable. The widget_factory receives IMessagingService so it can subscribe to live topics if needed.

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, widget_factory: Callable[[IMessagingService], QWidget])
```

```python
def register(self, messaging_service: IMessagingService) -> None
```

```python
def create_widget(self) -> QWidget
```
