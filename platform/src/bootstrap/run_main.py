from setproctitle import setproctitle

setproctitle("robot_app_platform")
# then continue with normal imports / startup
import logging
import os
import signal
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from PyQt6.QtCore import QObject, QEvent, QPoint, Qt, QTimer
from PyQt6.QtGui import QMouseEvent
from PyQt6.QtWidgets import QApplication, QWidget

from src.bootstrap.logging_config import setup_logging
from src.engine.diagnostics.service import build_diagnostics_service
from src.engine.diagnostics.events import observe
from src.bootstrap.build_engine import EngineContext
from src.bootstrap.application_loader import ApplicationLoader
from src.bootstrap.shell_configurator import ShellConfigurator
from src.applications.base.notification_presenter import UserNotificationPresenter
from src.applications.base.robot_connection_notifier import RobotConnectionNotifier
from src.engine.localization.localization_service import LocalizationService
from src.engine.auth.user_session import UserSession
from src.robot_systems.system_builder import SystemBuilder
from src.bootstrap.startup_config import load_bootstrap_provider, load_startup_config, build_configured_robot
from src.bootstrap.ros_backend_launcher import build_ros_backend_launcher_from_env
from src.bootstrap.shell_session_controller import ShellSessionController
from src.bootstrap.startup_splash_runtime import StartupSplashCoordinator
from pl_gui.shell.AppShell import AppShell
from pl_gui.shell.startup_splash_view import StartupSplashView

_LOGGER = logging.getLogger("main")

#
# def _pin_process_to_non_rt_cores() -> None:
#     rt_cores = {14, 15}
#     try:
#         available = sorted(os.sched_getaffinity(0))
#         target = {cpu for cpu in available if cpu not in rt_cores}
#         target={2}
#         if target:
#             os.sched_setaffinity(0, target)
#             _LOGGER.warning("Pinned robot_app_platform to CPUs: %s", sorted(target))
#         else:
#             _LOGGER.warning("No non-RT CPUs available; leaving affinity unchanged")
#     except Exception:
#         _LOGGER.exception("Failed to set CPU affinity")


class _FramelessHeaderDrag(QObject):
    def __init__(self, window: QWidget, drag_widget: QWidget):
        super().__init__(window)
        self._window = window
        self._drag_widget = drag_widget
        self._dragging = False
        self._press_offset = QPoint()
        self._drag_widget.installEventFilter(self)

    def eventFilter(self, watched: QObject, event: QEvent) -> bool:
        if watched is not self._drag_widget:
            return False

        if event.type() == QEvent.Type.MouseButtonPress:
            mouse_event = event
            if isinstance(mouse_event, QMouseEvent) and mouse_event.button() == Qt.MouseButton.LeftButton:
                self._dragging = True
                self._press_offset = mouse_event.globalPosition().toPoint() - self._window.frameGeometry().topLeft()
                return True

        if event.type() == QEvent.Type.MouseMove and self._dragging:
            mouse_event = event
            if isinstance(mouse_event, QMouseEvent):
                self._window.move(mouse_event.globalPosition().toPoint() - self._press_offset)
                return True

        if event.type() in (QEvent.Type.MouseButtonRelease, QEvent.Type.Leave):
            self._dragging = False

        return False


def _install_terminal_signal_handlers(qt_app: QApplication) -> None:
    """Route terminal shutdown signals through Qt so normal cleanup runs."""
    shutdown_requested = {"value": False}

    def _request_shutdown(signum, _frame) -> None:
        if shutdown_requested["value"]:
            return
        shutdown_requested["value"] = True
        try:
            signal_name = signal.Signals(signum).name
        except ValueError:
            signal_name = str(signum)
        _LOGGER.info("Received %s; requesting Qt application shutdown", signal_name)
        qt_app.quit()

    def _keep_python_signal_handlers_active() -> None:
        pass

    signal.signal(signal.SIGINT, _request_shutdown)
    signal.signal(signal.SIGTERM, _request_shutdown)

    timer = QTimer(qt_app)
    timer.timeout.connect(_keep_python_signal_handlers_active)
    timer.start(200)
    qt_app._terminal_signal_timer = timer


def main() -> None:
    setup_logging()
    # _pin_process_to_non_rt_cores()
    startup_config = load_startup_config()
    diagnostics_service = build_diagnostics_service(startup_config.diagnostics)
    try:
        diagnostics_service.start()
        status = diagnostics_service.status
        if status['state'] == 'unavailable':
            _LOGGER.warning('Diagnostics capture unavailable: %s', status['last_error'])
        else:
            _LOGGER.info('Diagnostics capture: %s', status['state'])
        _run_application(startup_config, diagnostics_service)
    finally:
        # Includes startup failures and cleanup, before the final writer drain.
        diagnostics_service.close()


def _run_application(startup_config, diagnostics_service) -> None:
    observe(_LOGGER, 'platform.configuration_loaded', robot_system=startup_config.robot_system,
            build_info={key: startup_config.system_config[key] for key in (
                'release_version', 'platform_version', 'backend_version',
                'robot_driver', 'backend', 'backend_profile')})
    dev_skip_login = startup_config.ui.dev_skip_login and not startup_config.ui.kiosk_mode
    skip_splash = startup_config.ui.skip_splash
    kiosk_mode = startup_config.ui.kiosk_mode
    fullscreen = startup_config.ui.fullscreen or kiosk_mode
    window_width = startup_config.ui.window_width
    window_height = startup_config.ui.window_height
    show_account_button_when_dev_skip_login = (
        startup_config.ui.show_account_button_when_dev_skip_login
    )
    show_power_off_button = startup_config.ui.show_power_off_button
    bootstrap_provider = load_bootstrap_provider(startup_config)

    logging.getLogger("MessageBroker").setLevel(logging.WARNING)
    logging.getLogger("RobotStatePublisher").setLevel(logging.WARNING)
    logging.getLogger("urllib3.connectionpool").setLevel(logging.WARNING)
    logging.getLogger("HttpCellTransport").setLevel(logging.WARNING)
    logging.getLogger("HttpCellTransport[cell=0]").setLevel(logging.WARNING)
    logging.getLogger("HttpCellTransport[cell=1]").setLevel(logging.WARNING)
    logging.getLogger("HttpCellTransport[cell=2]").setLevel(logging.WARNING)
    logging.getLogger("WeightCellService").setLevel(logging.WARNING)

    kiosk_password = None
    if kiosk_mode:
        from src.bootstrap.kiosk_password import KioskPassword
        kiosk_password = KioskPassword(Path(startup_config.ui.kiosk_password_file))

    # 1 — engine singletons
    ctx = EngineContext.build(diagnostics_service=diagnostics_service)

    from src.bootstrap.account_runtime import prepare_account_runtime, configure_account_runtime
    prepared_accounts = None if dev_skip_login else prepare_account_runtime(bootstrap_provider.system_class)

    # 2 — robot app (settings loaded, services wired)
    robot_app = None
    ros_backend = None
    try:
        ros_backend = build_ros_backend_launcher_from_env(startup_config.ros_backend, startup_config.robot_system)
        ros_backend.start()
        robot_app = (
            SystemBuilder()
            .with_robot(build_configured_robot(startup_config))
            .with_messaging_service(ctx.messaging_service)
            .with_development_mode(dev_skip_login)
            .build(bootstrap_provider.system_class)
        )
        session = UserSession()
        configure_account_runtime(robot_app, session, prepared=prepared_accounts)
    except Exception:
        if robot_app is not None:
            try:
                robot_app.stop()
            except Exception:
                _LOGGER.exception("Failed to clean up robot system after account initialization failure")
        if ros_backend is not None:
            ros_backend.stop()
        if prepared_accounts is not None:
            prepared_accounts.close()
        raise

    # 3 — shell folder layout from app metadata
    ShellConfigurator.configure(bootstrap_provider.system_class)

    # 4 — Qt app + localization
    qt_app = QApplication(sys.argv)
    from pl_gui.theme.palette import theme_palette
    from pl_gui.theme.runtime import install_theme
    from src.applications.platform_settings.service.platform_settings_service import PlatformSettingsService
    try:
        theme_palette.set_colors(PlatformSettingsService().get_colors())
    except (OSError, ValueError):
        logging.getLogger(__name__).exception("Could not load appearance preferences; using defaults")
    install_theme(qt_app)
    _install_terminal_signal_handlers(qt_app)
    localization_svc = _build_localization_service(robot_app, ctx.messaging_service)
    robot_app.localization_service = localization_svc
    localization_svc.set_language(localization_svc.get_language())

    kiosk_exit_guard = None
    if kiosk_mode:
        from src.bootstrap.kiosk_exit_guard import KioskExitGuard
        kiosk_exit_guard = KioskExitGuard(
            kiosk_password,
        )

    from src.bootstrap.shutdown_guard import ShutdownGuard
    shutdown_guard = ShutdownGuard(
        robot_app.get_shutdown_block_reason,
        next_guard=kiosk_exit_guard,
    )

    # 4b — Create shell BEFORE login (empty content area, header + language selector visible)
    shell = AppShell(
        app_descriptors=[],
        widget_factory=lambda _: QWidget(),   # placeholder, never invoked during login
        languages=localization_svc.available_languages(),
        close_guard=shutdown_guard,
    )
    shutdown_guard.parent = shell
    if kiosk_exit_guard is not None:
        kiosk_exit_guard.parent = shell
    shell.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Window)
    if not fullscreen:
        shell.setFixedSize(window_width, window_height)
    shell._header_drag = _FramelessHeaderDrag(shell, shell.header)
    localization_svc.sync_selector(shell.header.language_selector)
    shell.header.language_selector.languageChanged.connect(localization_svc.set_language)
    shell.header.power_toggle_button.setVisible(show_power_off_button or kiosk_mode)

    remote_support_monitor = None
    if sys.platform == "linux" and bootstrap_provider.system_class.__module__.startswith("src.robot_systems.paint."):
        from src.engine.remote_support.service_status_client import RustDeskServiceStatusClient
        from src.engine.remote_support.session_client import RustDeskSessionClient
        from src.bootstrap.shell_remote_support_controller import ShellRemoteSupportController

        remote_support_monitor = ShellRemoteSupportController(
            shell.header, RustDeskServiceStatusClient(timeout=2), RustDeskSessionClient(),
        )
        qt_app.aboutToQuit.connect(remote_support_monitor.stop)
        remote_support_monitor.start()

    shutdown_requested = {"value": False}

    def _on_power_off_requested() -> None:
        if shutdown_requested["value"]:
            return
        shutdown_requested["value"] = True
        shell.header.power_toggle_button.setEnabled(False)
        _LOGGER.info("Platform shutdown requested from header")
        if not shell.close():
            shutdown_requested["value"] = False
            shell.header.power_toggle_button.setEnabled(True)

    shell.header.power_off_requested.connect(_on_power_off_requested)

    startup_splash_coordinator = None
    notification_presenter = UserNotificationPresenter(
        shell,
        ctx.messaging_service,
        translate=lambda key: localization_svc.translate("Notifications", key),
    )
    shell._notification_presenter = notification_presenter
    robot_connection_notifier = None
    if not skip_splash:
        startup_splash = StartupSplashView(shell)
        startup_splash.set_active_step(2)
        startup_splash.set_message("Loading applications")
        shell.stacked_widget.addWidget(startup_splash)
        shell.stacked_widget.setCurrentWidget(startup_splash)
        shell.header.language_selector.languageChanged.connect(startup_splash.retranslateUi)
        startup_splash_coordinator = StartupSplashCoordinator(shell, startup_splash, ctx.messaging_service)
        robot_connection_notifier = RobotConnectionNotifier(ctx.messaging_service, suppress_until_ready=True)
        shell._robot_connection_notifier = robot_connection_notifier
        shell._startup_splash = startup_splash
        shell._startup_splash_coordinator = startup_splash_coordinator

    from src.engine.diagnostics.actions import ActionRecorder
    from src.bootstrap.navigation_diagnostics import NavigationDiagnostics
    actions = ActionRecorder(session, authentication_mode='development_bypass' if dev_skip_login else 'authenticated')
    robot_app._diagnostic_actions = actions
    shell._navigation_diagnostics = NavigationDiagnostics(shell, actions)
    shell._navigation_diagnostics.start()
    qt_app.aboutToQuit.connect(shell._navigation_diagnostics.stop)
    active_login_view = {"widget": None}

    # Wire broker → shell navigation
    # Used to automatically open the workpiece editor when the "open in editor"
    # button is clicked in the library
    from src.shared_contracts.events.shell_events import ApplicationShortcut, ShellTopics

    def _on_navigate(payload: dict) -> None:
        if not session.is_authenticated():
            _LOGGER.warning("Ignoring shell navigation while logged out")
            return
        app_name = payload.get("app") if isinstance(payload, dict) else str(payload)
        visible_names = {item.name for item in getattr(shell, "_app_descriptors", [])}
        if app_name in visible_names:
            shell.show_app(app_name)
        elif app_name:
            _LOGGER.warning("Ignoring navigation to non-visible application '%s'", app_name)

    def _visible_applications(payload: object) -> list[ApplicationShortcut]:
        excluded = set()
        if isinstance(payload, dict):
            excluded = {str(name) for name in payload.get("exclude", [])}
        folder_specs = {
            item.folder_id: item for item in robot_app.__class__.shell.folders
        }
        return [
            ApplicationShortcut(
                app_name=item.name,
                label=item.name,
                icon=item.icon_str,
                folder_id=item.folder_id,
                folder_name=folder_specs[item.folder_id].display_name
                if item.folder_id in folder_specs
                else "",
                folder_translation_key=folder_specs[item.folder_id].translation_key
                if item.folder_id in folder_specs
                else "",
            )
            for item in getattr(shell, "_app_descriptors", [])
            if item.name not in excluded
        ]

    ctx.messaging_service.subscribe(ShellTopics.NAVIGATE, _on_navigate)
    ctx.messaging_service.subscribe(ShellTopics.VISIBLE_APPLICATIONS, _visible_applications)
    if fullscreen:
        shell.showFullScreen()
    else:
        shell.show()

    notification_presenter.start()
    if not skip_splash:
        robot_connection_notifier.start()

    from src.bootstrap.connection_information_access import ConnectionInformationAccess
    connection_information_access = ConnectionInformationAccess(
        Path(startup_config.ui.kiosk_password_file), kiosk_password,
    )

    def _show_login_view() -> None:
        if startup_splash_coordinator is not None:
            startup_splash_coordinator.stop()
        login_view = bootstrap_provider.build_login_view(robot_app, ctx.messaging_service)   # parent=None; stacked_widget becomes parent
        login_view.set_connection_information_guard(connection_information_access)
        active_login_view["widget"] = login_view
        shell.stacked_widget.addWidget(login_view)
        shell.stacked_widget.setCurrentWidget(login_view)   # show login in shell content area

        # LanguageChange events only reach top-level windows; wire retranslation directly.
        shell.header.language_selector.languageChanged.connect(login_view.retranslateUi)

        def _on_login_accepted():
            shell.header.language_selector.languageChanged.disconnect(login_view.retranslateUi)
            session_controller.login(login_view.result_user())
            active_login_view["widget"] = None
            shell.stacked_widget.removeWidget(login_view)
            login_view.deleteLater()
            pending_initial_navigation["value"] = True
            account_access.refresh()

        login_view.accepted.connect(_on_login_accepted)

    def _can_close_running_apps() -> bool:
        for app_widget in shell.running_widgets.values():
            if app_widget and hasattr(app_widget, "can_close") and not app_widget.can_close():
                return False
        return True

    def _can_expire_session() -> bool:
        return not any(widget.has_active_operations() for widget in shell.running_widgets.values()
                       if widget is not None)

    session_controller = ShellSessionController(
        actions=actions,
        shell=shell,
        session=session,
        dev_skip_login=dev_skip_login,
        show_account_button_when_dev_skip_login=show_account_button_when_dev_skip_login,
        show_login_view=_show_login_view,
        can_close_running_apps=_can_close_running_apps,
        can_expire_session=_can_expire_session,
    )
    session_controller.start()

    from functools import partial
    from src.bootstrap.account_operation_activity import account_operation_idle
    from src.bootstrap.account_runtime import get_account_runtime
    from src.bootstrap.shell_account_access import ShellAccountAccess
    pending_initial_navigation = {"value": False}

    def _replace_navigation(visible_specs):
        initial = pending_initial_navigation["value"]
        _load_apps_into_shell(shell, robot_app, ctx, visible_specs, account_access,
                              show_folders=initial)
        if initial:
            pending_initial_navigation["value"] = False
            if startup_splash_coordinator is not None:
                startup_splash_coordinator.start()

    account_access = ShellAccountAccess(
        shell=shell, session=session, runtime=get_account_runtime(robot_app),
        navigation=bootstrap_provider.build_authorization_service(robot_app),
        specifications=robot_app.__class__.shell.applications,
        replace_navigation=_replace_navigation, expire_session=session_controller.expire_session,
        read_operation_idle=partial(account_operation_idle, robot_app), development_mode=dev_skip_login,
    )
    shell._account_access = account_access
    account_access.start()

    # 4c — Login gate
    if dev_skip_login:
        from src.applications.login.stub_login_application_service import _StubUser
        session_controller.login(_StubUser())
        _LOGGER.warning("ui.dev_skip_login is enabled — bypassing authentication")
        pending_initial_navigation["value"] = True
        account_access.refresh()

    else:
        _show_login_view()

    # # 7 — broker debug window (temporary — remove when no longer needed)
    # _debug_window = _build_broker_debug_window(ctx.messaging_service)
    # _debug_window.show()

    exit_code = 0
    try:
        exit_code = qt_app.exec()
    finally:
        account_access.stop()
        if remote_support_monitor is not None:
            remote_support_monitor.stop()
        if startup_splash_coordinator is not None:
            try:
                startup_splash_coordinator.stop()
            except Exception:
                _LOGGER.exception("Failed to stop startup splash coordinator")
        if robot_connection_notifier is not None:
            try:
                robot_connection_notifier.stop()
            except Exception:
                _LOGGER.exception("Failed to stop robot connection notifier")
        if notification_presenter is not None:
            try:
                notification_presenter.stop()
            except Exception:
                _LOGGER.exception("Failed to stop notification presenter")
        try:
            robot_app.stop()
        except Exception:
            _LOGGER.exception("Failed to stop robot system")
        try:
            ros_backend.stop()
        except Exception:
            _LOGGER.exception("Failed to stop ROS backend")
        if not robot_app.is_running:
            from src.bootstrap.account_runtime import close_account_runtime
            close_account_runtime(robot_app)
    sys.exit(exit_code)
def _load_apps_into_shell(shell, robot_app, ctx, visible_specs, access_guard, *, show_folders=False):
    """Register an authorized worker snapshot without storage work on the UI thread."""
    from src.bootstrap.shell_application_registry import replace_shell_applications
    replace_shell_applications(shell, robot_app, ctx.messaging_service, visible_specs,
                               access_guard, show_folders=show_folders)


def _build_localization_service(robot_app, messaging_service) -> LocalizationService:
    module_path = Path(sys.modules[robot_app.__class__.__module__].__file__).resolve().parent
    translations_dir = module_path / robot_app.metadata.translations_root
    applications_dir = Path(__file__).resolve().parent.parent / "applications"
    shared_translations_dir = applications_dir / "localization"
    application_translation_dirs = sorted(
        path
        for path in applications_dir.glob("*/localization")
        if path.is_dir()
    )
    from src.engine.updates.paths import system_path
    state_file = Path(system_path(type(robot_app), robot_app.metadata.settings_root)) / "localization.json"
    translation_dirs = [
        shared_translations_dir,
        *application_translation_dirs,
        translations_dir,
    ]
    return LocalizationService(
        [str(path) for path in translation_dirs],
        messaging_service=messaging_service,
        state_file=str(state_file),
    )


def _build_broker_debug_window(messaging_service):
    from PyQt6.QtWidgets import QMainWindow
    from src.applications.broker_debug.broker_debug_factory import BrokerDebugFactory
    from src.applications.broker_debug.service.broker_debug_application_service import BrokerDebugApplicationService

    widget = BrokerDebugFactory(messaging_service).build(
        BrokerDebugApplicationService(messaging_service)
    )
    window = QMainWindow()
    window.setWindowTitle("Broker Debug")
    window.setCentralWidget(widget)
    window.resize(1280, 800)
    return window


if __name__ == "__main__":
      main()
