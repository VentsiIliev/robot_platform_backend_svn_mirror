import os
from typing import Callable, Optional

from PyQt6.QtCore import QSize, Qt, QEvent, pyqtSignal
from PyQt6.QtWidgets import (
    QHBoxLayout, QPushButton, QFrame, QLabel
)

from pl_gui.shell.ui.icon_loader import load_icon
from pl_gui.shell.ui.styles import BORDER, PRIMARY, PRIMARY_DARK
from pl_gui.settings.settings_view.styles import BG_COLOR, ERROR_COLOR



from .LanguageSelectorWidget import LanguageSelectorWidget
# from modules.shared.MessageBroker import MessageBroker

# Resource paths
RESOURCE_DIR: str = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "resources")
MENU_ICON_PATH: str = os.path.join(RESOURCE_DIR, "pl_ui_icons", "SANDWICH_MENU.png")
LOGO_ICON_PATH: str = os.path.join(RESOURCE_DIR, "pl_ui_icons", "logo.ico")
DASHBOARD_BUTTON_ICON_PATH: str = os.path.join(RESOURCE_DIR, "pl_ui_icons", "DASHBOARD_BUTTON_SQUARE.png")


class Header(QFrame):
    user_account_clicked = pyqtSignal()
    power_off_requested = pyqtSignal()
    help_requested = pyqtSignal()
    fps_updated = pyqtSignal(float)  # Signal to emit updated FPS values

    def __init__(
        self,
        screen_width: int,
        screen_height: int,
        toggle_menu_callback: Optional[Callable[[], None]],
        dashboard_button_callback: Optional[Callable[[], None]],
        languages: Optional[list] = None,
    ) -> None:
        super().__init__()

        self.setContentsMargins(0, 0, 0, 0)
        self.screen_width: int = screen_width
        self.screen_height: int = screen_height
        self.setStyleSheet("background-color: white;")

        self.header_layout: QHBoxLayout = QHBoxLayout(self)
        self.header_layout.setContentsMargins(10, 0, 10, 0)
        self.header_layout.setAlignment(Qt.AlignmentFlag.AlignVCenter)

        # Dashboard Button
        self.dashboardButton: QPushButton = QPushButton()
        self.dashboardButton.setIcon(load_icon(DASHBOARD_BUTTON_ICON_PATH))
        self.dashboardButton.clicked.connect(
            dashboard_button_callback if dashboard_button_callback else lambda: print("dashboard_button_callback is none")
        )
        self.dashboardButton.setStyleSheet("border: none; background: transparent; padding: 0px;")
        self.header_layout.addWidget(self.dashboardButton)

        # Menu Button
        self.menu_button: QPushButton = QPushButton()
        self.menu_button.setIcon(load_icon("fa5s.bars", color="white"))
        self.menu_button.clicked.connect(
            toggle_menu_callback if toggle_menu_callback else lambda: print("toggle_menu_callback is none")
        )
        self.menu_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.header_layout.addWidget(self.menu_button)

        # Left stretch
        self.header_layout.addStretch()

        # Language Selector (centered) — hidden when no languages are configured
        self.language_selector: LanguageSelectorWidget = LanguageSelectorWidget(languages=languages)
        self.language_selector.setObjectName("language_selector_combo")
        self.language_selector.languageChanged.connect(self.handle_language_change)
        self.language_selector.setFixedWidth(200)
        if languages is None:
            self.language_selector.setVisible(False)

        self.header_layout.addWidget(self.language_selector)

        # Right stretch
        self.header_layout.addStretch()

        self._remote_support_state = "disabled"
        self.remote_support_badge = QLabel()
        self.remote_support_badge.setFixedSize(48, 48)
        self.remote_support_badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.remote_support_badge.setPixmap(
            load_icon("fa5s.desktop", color=ERROR_COLOR).pixmap(QSize(26, 26))
        )
        self.remote_support_badge.setStyleSheet(
            f"background-color: {BG_COLOR}; border: 2px solid {ERROR_COLOR};"
            "border-radius: 8px;"
        )
        self.remote_support_badge.hide()
        self.header_layout.addWidget(self.remote_support_badge)

        # Context-sensitive application help. AppShell shows this only when the
        # active application exposes an onboarding tour.
        self.help_button: QPushButton = QPushButton()
        self.help_button.setIcon(load_icon("fa5s.question", color=PRIMARY))
        self.help_button.setFixedSize(48, 48)
        self.help_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.help_button.setStyleSheet(f"""
            QPushButton {{
                background: white;
                border: 1px solid {BORDER};
                border-radius: 8px;
                padding: 0px;
            }}
            QPushButton:hover {{
                border: 2px solid {PRIMARY};
                background-color: rgba(122, 90, 248, 0.08);
            }}
            QPushButton:pressed {{
                background-color: rgba(122, 90, 248, 0.14);
                border: 2px solid {PRIMARY_DARK};
            }}
        """)
        self.help_button.clicked.connect(self._on_help_clicked)
        self.help_button.hide()
        self.header_layout.addWidget(self.help_button)

        # Platform shutdown button. Runtime wiring decides whether it is visible.
        self.power_toggle_button: QPushButton = QPushButton()
        self.power_toggle_button.setIcon(load_icon('fa5s.power-off', color=PRIMARY))
        self.power_toggle_button.setFixedSize(48, 48)
        self.power_toggle_button.setStyleSheet(f"""
            QPushButton {{
                background: white;
                border: 1px solid {BORDER};
                border-radius: 8px;
                padding: 0px;
            }}
            QPushButton:hover {{
                border: 2px solid {PRIMARY};
                background-color: rgba(122, 90, 248, 0.08);
            }}
            QPushButton:pressed {{
                background-color: rgba(122, 90, 248, 0.14);
                border: 2px solid {PRIMARY_DARK};
            }}
        """)
        self.power_toggle_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.power_toggle_button.clicked.connect(self._on_power_off_clicked)
        self.header_layout.addSpacing(20)
        self.header_layout.addWidget(self.power_toggle_button)

        self.userAccountButton: QPushButton = QPushButton()
        self.userAccountButton.setIcon(load_icon('fa5s.user', color=PRIMARY))
        self.userAccountButton.setFixedSize(48, 48)
        self.userAccountButton.setCursor(Qt.CursorShape.PointingHandCursor)
        self.userAccountButton.setStyleSheet(f"""
            QPushButton {{
                background: white;
                border: 1px solid {BORDER};
                border-radius: 8px;
                padding: 0px;
            }}
            QPushButton:hover {{
                border: 2px solid {PRIMARY};
                background-color: rgba(122, 90, 248, 0.08);
            }}
            QPushButton:pressed {{
                background-color: rgba(122, 90, 248, 0.14);
                border: 2px solid {PRIMARY_DARK};
            }}
        """)
        self.userAccountButton.clicked.connect(self.on_user_account_clicked)
        self.userAccountButton.setVisible(True)
        self.header_layout.addWidget(self.userAccountButton)

        # FPS Label
        self.fps_label = QLabel("FPS: --")
        self.fps_label.setStyleSheet("font-size: 14px; color: black;")
        # self.header_layout.addWidget(self.fps_label)


        self.setMinimumHeight(int(self.screen_height * 0.08))
        self.setMaximumHeight(100)

        # Subscribe to FPS updates - connect signal first, then subscribe to broker
        self.fps_updated.connect(self.update_fps_label)
        self.retranslateUi()
        # self.broker.subscribe(VisionTopics.FPS, self._on_broker_fps)
        # print(f"[Header] Subscribed to topic: {VisionTopics.FPS}")
        # print(f"[Header] Broker subscriber count for FPS: {self.broker.get_subscriber_count(VisionTopics.FPS)}")

    def handle_language_change(self, language_code: str) -> None:
        print(f"[Header] Language changed to: {language_code}")

    def _on_broker_fps(self, fps: float) -> None:
        """Broker callback - runs in VisionService thread, emit signal for thread-safe UI update."""
        # print(f"[Header._on_broker_fps] Received FPS from broker: {fps}")
        try:
            fps_value = float(fps)
            # print(f"[Header._on_broker_fps] Emitting signal with FPS: {fps_value}")
            self.fps_updated.emit(fps_value)
        except Exception as e:
            # print(f"[Header._on_broker_fps] Error processing FPS value: {e}")
            import traceback
            traceback.print_exc()

    def update_fps_label(self, fps: float) -> None:
        """Update FPS label when new FPS value is received."""
        try:
            fps_value = float(fps)
            self.fps_label.setText(f"FPS: {fps_value:.1f}")
        except Exception:
            import traceback
            traceback.print_exc()
            self.fps_label.setText("FPS: --")

    def on_user_account_clicked(self):
        self.user_account_clicked.emit()

    def _on_power_off_clicked(self) -> None:
        self.power_off_requested.emit()

    def _on_help_clicked(self) -> None:
        self.help_requested.emit()

    def retranslateUi(self) -> None:
        self.power_toggle_button.setToolTip(self.tr("Turn Off Platform"))
        help_text = self.tr("Take a tour") or "Take a tour"
        self.help_button.setToolTip(help_text)
        self.help_button.setAccessibleName(help_text)
        source = "Remote session active"
        translated = self.tr(source) or source
        self.remote_support_badge.setToolTip(translated)
        self.remote_support_badge.setAccessibleName(translated)

    def set_remote_support_state(self, state: str) -> None:
        """Display confirmed session state supplied by the shell controller."""
        if state not in ("disabled", "ready", "connected", "unavailable"):
            raise ValueError("Unknown remote support state")
        self._remote_support_state = state
        self.remote_support_badge.setVisible(state == "connected")
        self.retranslateUi()

    def changeEvent(self, event: QEvent) -> None:
        if event.type() == QEvent.Type.LanguageChange:
            self.retranslateUi()
        super().changeEvent(event)

    def resizeEvent(self, event: QEvent) -> None:
        new_width: int = self.width()
        icon_size: int = int(new_width * 0.05)

        diameter = max(48, icon_size + 16)
        self.menu_button.setFixedSize(diameter, diameter)
        self.menu_button.setIconSize(QSize(diameter // 3, diameter // 3))
        self.menu_button.setStyleSheet(f"""
            QPushButton {{ background: {PRIMARY}; border: none; border-radius: {diameter // 2}px; }}
            QPushButton:hover {{ background: {PRIMARY_DARK}; }}
        """)
        self.power_toggle_button.setIconSize(QSize(26, 26))
        self.help_button.setIconSize(QSize(26, 26))
        self.dashboardButton.setIconSize(QSize(icon_size, icon_size))
        self.userAccountButton.setIconSize(QSize(26, 26))
        super().resizeEvent(event)





if __name__ == "__main__":
    from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
    import sys

    app = QApplication(sys.argv)

    main_window = QMainWindow()
    main_window.setWindowTitle("Header Widget Test")
    main_window.resize(800, 600)

    central_widget = QWidget()
    main_layout = QVBoxLayout(central_widget)

    header = Header(
        screen_width=800,
        screen_height=600,
        toggle_menu_callback=lambda: print("Menu toggled"),
        dashboard_button_callback=lambda: print("Dashboard button clicked"),
    )
    main_layout.addWidget(header)

    main_window.setCentralWidget(central_widget)
    main_window.show()

    sys.exit(app.exec())
