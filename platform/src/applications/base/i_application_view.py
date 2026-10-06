from abc import abstractmethod
from typing import Callable, Optional

from PyQt6.QtCore import QCoreApplication, pyqtSignal

from pl_gui.shell.base_app_widget.AppWidget import AppWidget
from src.applications.base.styled_message_box import show_warning
from src.applications.base.drawer_toggle import DrawerToggle
from src.applications.base.robot_jog_widget import RobotJogWidget


class IApplicationView(AppWidget):
    """
    Base class for all application views.

    Extends AppWidget — required by the shell (provides app_closed signal).
    Enforces the two rules of the view layer:
      - setup_ui()  : build widgets, wire internal signals to outbound pyqtSignals
      - clean_up()  : stop timers, threads, subscriptions on widget destruction
    """

    SHOW_JOG_WIDGET = False
    JOG_LIVE_POSITION_ENABLED = True
    JOG_FRAME_SELECTOR_ENABLED = False
    JOG_DRAWER_SIDE = "right"
    JOG_DRAWER_WIDTH = 320

    jog_requested = pyqtSignal(str, str, str, float)
    joint_jog_requested = pyqtSignal(str, str, str, float)
    jog_started = pyqtSignal(str)
    jog_stopped = pyqtSignal(str)
    recovery_mode_changed = pyqtSignal(bool)
    language_changed = pyqtSignal()

    def __init__(self, title: str, parent=None):
        self._navigation_guard: Callable[[], bool] | None = None
        self._drawer: Optional[DrawerToggle] = None
        self._jog_widget: Optional[RobotJogWidget] = None
        super().__init__(title, parent)
        self._install_jog_widget()

    def set_navigation_guard(self, has_active_operations: Callable[[], bool]) -> None:
        """Bind a nonblocking activity query supplied by the application factory."""
        self._navigation_guard = has_active_operations

    def can_close(self) -> bool:
        if self._navigation_guard is not None and self._navigation_guard():
            title = "Operation Running"
            message = "An operation is running or stopping. Please stop it or wait for it to finish before leaving."
            show_warning(
                self,
                QCoreApplication.translate("ApplicationNavigation", title) or title,
                QCoreApplication.translate("ApplicationNavigation", message) or message,
            )
            return False
        return super().can_close()

    def _install_jog_widget(self) -> None:
        self._drawer = DrawerToggle(
            self,
            side=self.JOG_DRAWER_SIDE,
            width=self.JOG_DRAWER_WIDTH,
        )
        self._jog_widget = RobotJogWidget()
        self._jog_widget.enable_frame_selector(self.JOG_FRAME_SELECTOR_ENABLED)
        self._drawer.add_widget(self._jog_widget)
        self._jog_widget.jog_requested.connect(self.jog_requested)
        self._jog_widget.joint_jog_requested.connect(self.joint_jog_requested)
        self._jog_widget.jog_started.connect(self.jog_started)
        self._jog_widget.jog_stopped.connect(self.jog_stopped)
        self._jog_widget.recovery_mode_changed.connect(self.recovery_mode_changed)

        frame_changed = getattr(self, "_on_jog_frame_changed", None)
        if callable(frame_changed):
            self._jog_widget.frame_changed.connect(frame_changed)

        configure = getattr(self, "_configure_jog_widget", None)
        if callable(configure):
            configure()

        self.enable_jog_widget(self.SHOW_JOG_WIDGET)

    def enable_jog_widget(self, enabled: bool) -> None:
        if self._drawer is not None:
            self._drawer.set_visible(enabled)

    def set_jog_position(self, pos: list) -> None:
        if self._jog_widget is not None:
            self._jog_widget.set_position(pos)

    def set_joint_position(self, joints: list) -> None:
        if self._jog_widget is not None:
            self._jog_widget.set_joint_position(joints)

    def set_jog_frame_options(self, names: list[str], default: str | None = None) -> None:
        if self._jog_widget is not None:
            self._jog_widget.set_frame_options(names, default=default)

    def set_jog_frame(self, name: str) -> None:
        if self._jog_widget is not None:
            self._jog_widget.set_frame(name)

    def get_jog_frame(self) -> str:
        if self._jog_widget is None:
            return ""
        return self._jog_widget.get_frame()

    def retranslateUi(self) -> None:
        """Override in subclasses to refresh widget-owned text."""
        pass

    def on_language_changed(self) -> None:
        """Default localization hook for all application views."""
        self.retranslateUi()
        self.language_changed.emit()

    @abstractmethod
    def setup_ui(self) -> None: ...

    @abstractmethod
    def clean_up(self) -> None: ...
