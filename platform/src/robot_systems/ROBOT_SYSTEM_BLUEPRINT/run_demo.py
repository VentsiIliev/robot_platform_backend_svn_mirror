from __future__ import annotations

import sys
from functools import partial
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent.parent))

from PyQt6.QtWidgets import QApplication, QWidget
import logging
from pl_gui.shell.AppShell import AppShell
from src.bootstrap.account_operation_activity import account_operation_idle
from src.bootstrap.account_runtime import (
    close_account_runtime, configure_account_runtime, get_account_runtime, prepare_account_runtime,
)
from src.bootstrap.shell_account_access import ShellAccountAccess
from src.bootstrap.shell_application_registry import replace_shell_applications
from src.bootstrap.shell_session_controller import ShellSessionController
from src.bootstrap.build_engine import EngineContext
from src.bootstrap.logging_config import setup_logging
from src.bootstrap.shell_configurator import ShellConfigurator
from src.engine.auth.user_session import UserSession
from src.engine.localization.localization_service import LocalizationService
from src.robot_systems.ROBOT_SYSTEM_BLUEPRINT.bootstrap_provider import (
    MyRobotSystemBootstrapProvider,
)
from src.robot_systems.system_builder import SystemBuilder


def run_demo() -> None:
    setup_logging()
    logging.getLogger("MessageBroker").setLevel(logging.WARNING)
    logging.getLogger("RobotStatePublisher").setLevel(logging.WARNING)
    logging.getLogger("urllib3.connectionpool").setLevel(logging.WARNING)
    provider = MyRobotSystemBootstrapProvider()
    ctx = EngineContext.build()

    prepared = prepare_account_runtime(provider.system_class)
    try:
        robot_system = (
            SystemBuilder()
            .with_robot(provider.build_robot())
            .with_messaging_service(ctx.messaging_service)
            .build(provider.system_class)
        )
        session = UserSession()
        configure_account_runtime(robot_system, session, prepared=prepared)
    except BaseException:
        prepared.close()
        raise

    ShellConfigurator.configure(provider.system_class)

    from src.bootstrap.qt_application import prepare_qt_application
    prepare_qt_application()
    qt_app = QApplication(sys.argv)
    localization_service = _build_localization_service(robot_system, ctx.messaging_service)
    localization_service.set_language(localization_service.get_language())

    shell = AppShell(
        app_descriptors=[],
        widget_factory=lambda _: QWidget(),
        languages=localization_service.available_languages(),
    )
    localization_service.sync_selector(shell.header.language_selector)
    shell.header.language_selector.languageChanged.connect(localization_service.set_language)
    shell.show()

    pending_initial = {"value": False}

    def show_login():
        login_view = provider.build_login_view(robot_system, ctx.messaging_service)
        shell.stacked_widget.addWidget(login_view)
        shell.stacked_widget.setCurrentWidget(login_view)
        shell.header.language_selector.languageChanged.connect(login_view.retranslateUi)

        def accepted():
            shell.header.language_selector.languageChanged.disconnect(login_view.retranslateUi)
            session_controller.login(login_view.result_user())
            shell.stacked_widget.removeWidget(login_view)
            login_view.deleteLater()
            pending_initial["value"] = True
            account_access.refresh()

        login_view.accepted.connect(accepted)

    def can_close():
        return all(widget.can_close() for widget in shell.running_widgets.values() if widget is not None)

    def can_expire():
        return not any(widget.has_active_operations() for widget in shell.running_widgets.values()
                       if widget is not None)

    session_controller = ShellSessionController(shell=shell, session=session, dev_skip_login=False,
        show_account_button_when_dev_skip_login=False, show_login_view=show_login,
        can_close_running_apps=can_close, can_expire_session=can_expire)
    session_controller.start()

    def replace_navigation(specs):
        replace_shell_applications(shell, robot_system, ctx.messaging_service, specs, account_access,
                                  show_folders=pending_initial["value"])
        pending_initial["value"] = False

    account_access = ShellAccountAccess(shell=shell, session=session, runtime=get_account_runtime(robot_system),
        navigation=provider.build_authorization_service(robot_system),
        specifications=type(robot_system).shell.applications, replace_navigation=replace_navigation,
        expire_session=session_controller.expire_session,
        read_operation_idle=partial(account_operation_idle, robot_system))
    shell._account_access = account_access
    account_access.start()
    show_login()

    try:
        sys.exit(qt_app.exec())
    finally:
        account_access.stop()
        robot_system.stop()
        close_account_runtime(robot_system)


def _build_localization_service(robot_system, messaging_service) -> LocalizationService:
    from src.bootstrap.run_main import _build_localization_service as build_localization
    return build_localization(robot_system, messaging_service)


if __name__ == "__main__":
    run_demo()
