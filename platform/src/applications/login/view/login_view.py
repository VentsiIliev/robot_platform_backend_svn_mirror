import base64
import json
from pathlib import Path
from typing import Optional

import cv2
from PyQt6.QtCore import Qt, QTimer, QSize, pyqtSignal, QEvent, QCoreApplication, QBuffer, QIODevice
from PyQt6.QtGui import QFont, QImage, QPixmap
from PyQt6.QtCore import QUrl
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QStackedLayout, QGraphicsOpacityEffect,
    QLabel, QLineEdit, QPushButton, QFrame, QButtonGroup,
    QSizePolicy, QStackedWidget, QTabWidget, QWidget, QMessageBox,
)

from pl_gui.utils.utils_widgets.camera_view import CameraView


class _FeedOnlyCameraView(CameraView):
    """CameraView with zoom, pan, and toolbar disabled — feed display only."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._toolbar.hide()

    def wheelEvent(self, event) -> None:
        event.ignore()

    def mousePressEvent(self, event) -> None:
        event.ignore()

    def mouseMoveEvent(self, event) -> None:
        event.ignore()

    def mouseReleaseEvent(self, event) -> None:
        event.ignore()

from src.engine.auth.i_authenticated_user import IAuthenticatedUser

# ── Asset paths ───────────────────────────────────────────────────────────────
_RESOURCES = Path(__file__).resolve().parents[2] / "base" / "resources"
_LOGO_PATH          = str(_RESOURCES / "logo.ico")
_MACHINE_IMAGE_PATH = str(_RESOURCES / "MACHINE_BUTTONS_1.png")

# ── Stack page indices ────────────────────────────────────────────────────────
_PAGE_SETUP     = 0
_PAGE_FIRST_RUN = 1
_PAGE_TABS      = 2

# ── Tab indices ───────────────────────────────────────────────────────────────
_TAB_LOGIN = 0
_TAB_QR    = 1

_QR_POLL_MS = 2000

# ── Layout constants ──────────────────────────────────────────────────────────
_CARD_MAX_WIDTH = 480
_FIELD_HEIGHT   = 56
_BUTTON_HEIGHT  = 56


class _HiddenPaintEffect(QGraphicsOpacityEffect):
    def __init__(self, parent):
        super().__init__(parent)
        self.setOpacity(0.0)


class LoginView(QDialog):
    """
    Login dialog layout:

      ┌──────────────┬──────────────────────────────────────┐
      │              │  Page 0: Setup steps                 │
      │  Logo panel  │  Page 1: First-admin creation        │
      │  (fluid bg)  │  Page 2: [Login | QR login] card     │
      └──────────────┴──────────────────────────────────────┘

    The animated fluid background (WebGL) spans the whole dialog. The logo is
    painted by the web layer (see _sync_fluid_images); every other element is a
    native widget. The right-hand pages are rounded, opaque white cards so text
    and inputs stay crisp and readable on top of the moving background.

    Signals
    -------
    setup_confirmed()                        — user clicked "Next" on setup page
    login_submitted(user_id, password)       — normal login button / Enter
    qr_scan_requested()                      — fired by QTimer while QR tab active
    qr_tab_activated()                       — user confirmed QR tab switch
    first_admin_submitted(id, fn, ln, pw)    — first-run form submit
    """

    setup_confirmed       = pyqtSignal()
    login_submitted       = pyqtSignal(str, str)
    qr_scan_requested     = pyqtSignal()
    qr_tab_activated      = pyqtSignal()
    first_admin_submitted = pyqtSignal(str, str, str, str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Login")
        self.setMinimumSize(760, 600)
        self._allow_close = False
        self._result_user: Optional[IAuthenticatedUser] = None

        self._qr_timer = QTimer(self)
        self._qr_timer.setInterval(_QR_POLL_MS)
        self._qr_timer.timeout.connect(self.qr_scan_requested)

        self._logo_pixmap: Optional[QPixmap] = None

        self._setup_ui()
        self.setStyleSheet(self._stylesheet())
        self._fluid_view.loadFinished.connect(self._on_fluid_loaded)
        self._image_sync = QTimer(self)
        self._image_sync.setInterval(250)
        self._image_sync.timeout.connect(self._sync_fluid_images)
        self._image_sync.start()

    # ── Controller-facing API ────────────────────────────────────────────────

    def show_setup(self) -> None:
        self._stack.setCurrentIndex(_PAGE_SETUP)
        QTimer.singleShot(0, self._sync_fluid_images)

    def show_login(self) -> None:
        self._stack.setCurrentIndex(_PAGE_TABS)
        QTimer.singleShot(0, self._sync_fluid_images)
        self._tabs.setCurrentIndex(_TAB_LOGIN)

    def show_first_run(self) -> None:
        self._stack.setCurrentIndex(_PAGE_FIRST_RUN)
        QTimer.singleShot(0, self._sync_fluid_images)

    def show_error(self, message: str) -> None:
        self._error_label.setText(message)
        self._error_label.setVisible(True)

    def accept_login(self, user: IAuthenticatedUser) -> None:
        self._result_user = user
        self._allow_close = True
        self._stop_qr_scanning()
        self._error_label.setVisible(False)
        self.accept()

    def result_user(self) -> Optional[IAuthenticatedUser]:
        return self._result_user

    def start_qr_scanning(self) -> None:
        if not self._qr_timer.isActive():
            self._qr_timer.start()

    def stop_qr_scanning(self) -> None:
        self._stop_qr_scanning()

    # ── UI construction ──────────────────────────────────────────────────────

    def _setup_ui(self) -> None:
        # One WebGL surface spans the ENTIRE dialog. Native widgets sit above it.
        layers = QStackedLayout(self)
        layers.setContentsMargins(0, 0, 0, 0)
        layers.setStackingMode(QStackedLayout.StackingMode.StackAll)

        self._fluid_view = QWebEngineView(self)
        self._fluid_view.setContextMenuPolicy(Qt.ContextMenuPolicy.NoContextMenu)
        self._fluid_view.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        layers.addWidget(self._fluid_view)

        overlay = QWidget(self)
        overlay.setObjectName("fluidOverlay")
        overlay.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        overlay.setAutoFillBackground(False)
        root = QHBoxLayout(overlay)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)
        root.addWidget(self._build_logo_panel(), stretch=2)
        root.addWidget(self._build_right_panel(), stretch=3)
        layers.addWidget(overlay)
        layers.setCurrentWidget(overlay)

        html_path = Path(__file__).resolve().parent / "fluid_assets" / "index.html"
        if not html_path.is_file():
            raise FileNotFoundError(f"Missing WebGL smoke page: {html_path}")
        self._fluid_view.load(QUrl.fromLocalFile(str(html_path)))
        self.retranslateUi()

    # ── Building blocks ──────────────────────────────────────────────────────

    @staticmethod
    def _make_card() -> QFrame:
        """Opaque, rounded white card — keeps content legible over the fluid background."""
        card = QFrame()
        card.setObjectName("card")
        card.setMaximumWidth(_CARD_MAX_WIDTH)
        card.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Maximum)
        return card

    @staticmethod
    def _centered(card: QWidget) -> QWidget:
        """Wrap a card so it sits centred in the right panel."""
        wrapper = QWidget()
        outer = QVBoxLayout(wrapper)
        outer.setContentsMargins(24, 24, 24, 24)
        outer.addStretch(1)
        row = QHBoxLayout()
        row.addStretch(1)
        row.addWidget(card, 8)
        row.addStretch(1)
        outer.addLayout(row)
        outer.addStretch(1)
        return wrapper

    @staticmethod
    def _field_label() -> QLabel:
        lbl = QLabel()
        lbl.setObjectName("fieldLabel")
        return lbl

    @staticmethod
    def _title_label() -> QLabel:
        lbl = QLabel()
        lbl.setObjectName("cardTitle")
        f = QFont(); f.setPointSize(16); f.setBold(True)
        lbl.setFont(f)
        return lbl

    @staticmethod
    def _input() -> QLineEdit:
        edit = QLineEdit()
        edit.setFixedHeight(_FIELD_HEIGHT)
        return edit

    # ── Logo panel ───────────────────────────────────────────────────────────

    def _build_logo_panel(self) -> QWidget:
        panel = QWidget()
        panel.setObjectName("logoPanel")
        layout = QVBoxLayout(panel)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setContentsMargins(16, 16, 16, 16)

        # Invisible placeholder: the web layer paints the logo at this label's position.
        self._logo_label = QLabel()
        self._logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        pixmap = QPixmap(_LOGO_PATH)
        if not pixmap.isNull():
            self._logo_pixmap = pixmap
            self._logo_label.setPixmap(pixmap.scaled(
                240, 240, Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation))
        else:
            font = QFont()
            font.setPointSize(22)
            font.setBold(True)
            self._logo_label.setFont(font)
            self._logo_label.setText(self._t("Robot\nPlatform"))
        layout.addWidget(self._logo_label)
        self._logo_label.setStyleSheet("background: transparent; color: transparent;")
        self._logo_label.setGraphicsEffect(_HiddenPaintEffect(self._logo_label))
        return panel

    # ── Right panel (stacked) ─────────────────────────────────────────────────

    def _build_right_panel(self) -> QWidget:
        container = QWidget()
        container.setObjectName("rightPanel")
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self._stack = QStackedWidget()
        self._stack.setObjectName("loginPages")
        self._stack.addWidget(self._build_setup_page())      # _PAGE_SETUP     = 0
        self._stack.addWidget(self._build_first_run_page())  # _PAGE_FIRST_RUN = 1
        self._stack.addWidget(self._build_tabs_widget())     # _PAGE_TABS      = 2
        layout.addWidget(self._stack, stretch=1)

        self._error_label = QLabel()
        self._error_label.setObjectName("errorLabel")
        self._error_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._error_label.setWordWrap(True)
        self._error_label.setVisible(False)
        err_row = QHBoxLayout()
        err_row.setContentsMargins(24, 0, 24, 20)
        err_row.addStretch(1)
        err_row.addWidget(self._error_label, 8)
        err_row.addStretch(1)
        layout.addLayout(err_row)

        return container

    # ── Setup page ────────────────────────────────────────────────────────────

    def _build_setup_page(self) -> QWidget:
        card   = self._make_card()
        layout = QVBoxLayout(card)
        layout.setContentsMargins(32, 28, 32, 28)
        layout.setSpacing(16)

        # Machine image — a real, visible widget now that it lives on an opaque card.
        self._machine_label = QLabel()
        self._machine_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        machine_px = QPixmap(_MACHINE_IMAGE_PATH)
        if not machine_px.isNull():
            self._machine_pixmap = machine_px
            self._machine_label.setPixmap(
                machine_px.scaled(260, 260,
                                  Qt.AspectRatioMode.KeepAspectRatio,
                                  Qt.TransformationMode.SmoothTransformation)
            )
        else:
            self._machine_pixmap = None
            self._machine_label.setText(self._t("[Machine image not found]"))
            self._machine_label.setObjectName("mutedLabel")
        layout.addWidget(self._machine_label)

        # Instruction
        self._setup_instruction = QLabel()
        self._setup_instruction.setObjectName("setupInstruction")
        self._setup_instruction.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._setup_instruction.setWordWrap(True)
        layout.addWidget(self._setup_instruction)

        # TODO: remove once physical blue-button signal is wired
        self._btn_sim = QPushButton()
        self._btn_sim.setObjectName("secondary")
        self._btn_sim.setFixedHeight(_BUTTON_HEIGHT - 6)
        self._btn_sim.clicked.connect(self._on_setup_next_clicked)
        layout.addWidget(self._btn_sim)

        return self._centered(card)

    # ── First-run page ────────────────────────────────────────────────────────

    def _build_first_run_page(self) -> QWidget:
        card   = self._make_card()
        layout = QVBoxLayout(card)
        layout.setContentsMargins(32, 28, 32, 28)
        layout.setSpacing(6)

        self._fr_title = self._title_label()
        layout.addWidget(self._fr_title)

        self._fr_subtitle = QLabel()
        self._fr_subtitle.setObjectName("mutedLabel")
        self._fr_subtitle.setWordWrap(True)
        layout.addWidget(self._fr_subtitle)
        layout.addSpacing(10)

        self._fa_uid   = self._input()
        self._fa_first = self._input()
        self._fa_last  = self._input()
        self._fa_pw    = self._input()
        self._fa_pw.setEchoMode(QLineEdit.EchoMode.Password)

        self._fr_label_uid   = self._field_label()
        self._fr_label_first = self._field_label()
        self._fr_label_last  = self._field_label()
        self._fr_label_pw    = self._field_label()

        layout.addWidget(self._fr_label_uid)
        layout.addWidget(self._fa_uid)
        layout.addSpacing(6)

        names     = QHBoxLayout(); names.setSpacing(12)
        first_col = QVBoxLayout(); first_col.setSpacing(6)
        last_col  = QVBoxLayout(); last_col.setSpacing(6)
        first_col.addWidget(self._fr_label_first); first_col.addWidget(self._fa_first)
        last_col.addWidget(self._fr_label_last);   last_col.addWidget(self._fa_last)
        names.addLayout(first_col)
        names.addLayout(last_col)
        layout.addLayout(names)
        layout.addSpacing(6)

        layout.addWidget(self._fr_label_pw)
        layout.addWidget(self._fa_pw)
        layout.addSpacing(14)

        self._fr_btn = QPushButton()
        self._fr_btn.setObjectName("primary")
        self._fr_btn.setFixedHeight(_BUTTON_HEIGHT)
        self._fr_btn.clicked.connect(self._on_first_admin_clicked)
        self._fa_pw.returnPressed.connect(self._on_first_admin_clicked)
        layout.addWidget(self._fr_btn)
        return self._centered(card)

    # ── Login / QR tabs ───────────────────────────────────────────────────────

    def _build_tabs_widget(self) -> QWidget:
        card   = self._make_card()
        layout = QVBoxLayout(card)
        layout.setContentsMargins(28, 28, 28, 28)
        layout.setSpacing(18)

        # A segmented control drives the (tab-bar-less) QTabWidget, so the existing
        # tab logic — including the QR warning / cancel flow — is untouched.
        seg = QFrame()
        seg.setObjectName("seg")
        seg_layout = QHBoxLayout(seg)
        seg_layout.setContentsMargins(4, 4, 4, 4)
        seg_layout.setSpacing(4)
        self._seg_login = QPushButton()
        self._seg_qr    = QPushButton()
        self._seg_group = QButtonGroup(self)
        self._seg_group.setExclusive(True)
        for idx, btn in ((_TAB_LOGIN, self._seg_login), (_TAB_QR, self._seg_qr)):
            btn.setObjectName("segBtn")
            btn.setCheckable(True)
            btn.setFixedHeight(48)
            btn.setFocusPolicy(Qt.FocusPolicy.NoFocus)
            btn.setProperty("tab_index", idx)
            self._seg_group.addButton(btn, idx)
            seg_layout.addWidget(btn)
            btn.clicked.connect(self._on_segment_clicked)
        self._seg_login.setChecked(True)
        layout.addWidget(seg)

        self._tabs = QTabWidget()
        self._tabs.setObjectName("loginTabs")
        self._tabs.tabBar().hide()
        self._tabs.addTab(self._build_login_tab(), "Login")
        self._tabs.addTab(self._build_qr_tab(),    "QR Login")
        self._tabs.currentChanged.connect(self._on_tab_changed)
        self._tabs.currentChanged.connect(self._sync_segmented)
        layout.addWidget(self._tabs)

        return self._centered(card)

    def _build_login_tab(self) -> QWidget:
        page   = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)

        self._login_title = self._title_label()
        layout.addWidget(self._login_title)
        layout.addSpacing(6)

        self._uid_label = self._field_label()
        layout.addWidget(self._uid_label)
        self._uid_input = self._input()
        layout.addWidget(self._uid_input)
        layout.addSpacing(6)

        self._pw_label = self._field_label()
        layout.addWidget(self._pw_label)
        self._pw_input = self._input()
        self._pw_input.setEchoMode(QLineEdit.EchoMode.Password)
        self._pw_input.setTextMargins(0, 0, 76, 0)
        # Show / Hide toggle lives inside the field
        self._pw_toggle = QPushButton(self._pw_input)
        self._pw_toggle.setObjectName("ghost")
        self._pw_toggle.setCheckable(True)
        self._pw_toggle.setCursor(Qt.CursorShape.PointingHandCursor)
        self._pw_toggle.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self._pw_toggle.setFixedSize(68, _FIELD_HEIGHT - 12)
        self._pw_toggle.toggled.connect(self._on_toggle_password)
        pw_row = QHBoxLayout(self._pw_input)
        pw_row.setContentsMargins(0, 0, 6, 0)
        pw_row.addStretch(1)
        pw_row.addWidget(self._pw_toggle)
        layout.addWidget(self._pw_input)

        layout.addSpacing(14)
        self._login_btn = QPushButton()
        self._login_btn.setObjectName("primary")
        self._login_btn.setFixedHeight(_BUTTON_HEIGHT)
        self._login_btn.clicked.connect(self._on_login_clicked)
        self._uid_input.returnPressed.connect(self._on_login_clicked)
        self._pw_input.returnPressed.connect(self._on_login_clicked)
        layout.addWidget(self._login_btn)
        layout.addStretch(1)
        return page

    def _build_qr_tab(self) -> QWidget:
        page   = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)

        self._qr_title = self._title_label()
        layout.addWidget(self._qr_title)

        frame = QFrame()
        frame.setObjectName("camFrame")
        frame_layout = QVBoxLayout(frame)
        frame_layout.setContentsMargins(6, 6, 6, 6)
        self._camera_view = _FeedOnlyCameraView()
        self._camera_view.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )
        self._camera_view.setMinimumHeight(240)
        frame_layout.addWidget(self._camera_view)
        layout.addWidget(frame, stretch=1)

        self._qr_info = QLabel()
        self._qr_info.setObjectName("mutedLabel")
        self._qr_info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._qr_info.setWordWrap(True)
        layout.addWidget(self._qr_info)

        return page

    def update_camera_frame(self, frame) -> None:
        """Push a BGR numpy frame to the camera view. Called from the controller."""
        if frame is None:
            return
        try:
            rgb   = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, ch = rgb.shape
            qimg  = QImage(rgb.data, w, h, ch * w, QImage.Format.Format_RGB888)
            self._camera_view.set_frame(QPixmap.fromImage(qimg))
        except RuntimeError:
            pass  # C++ widget already deleted — queued signal arrived after teardown

    # ── Internal slots ───────────────────────────────────────────────────────

    def _on_setup_next_clicked(self) -> None:
        self._error_label.setVisible(False)
        self.setup_confirmed.emit()

    def _sync_segmented(self, *_) -> None:
        """Keep the segmented control in step with the current tab (also after a cancelled QR switch)."""
        btn = self._seg_group.button(self._tabs.currentIndex())
        if btn is not None:
            btn.setChecked(True)

    def _on_segment_clicked(self) -> None:
        button = self.sender()
        if button is not None:
            self._tabs.setCurrentIndex(int(button.property("tab_index")))

    def _on_tab_changed(self, index: int) -> None:
        self._error_label.setVisible(False)
        if index == _TAB_QR:
            confirmed = QMessageBox.warning(
                self,
                self._t("Warning"),
                self._t("The robot will move to the login position.\n"
                        "Please ensure the area is clear before proceeding."),
                QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel,
            )
            if confirmed == QMessageBox.StandardButton.Ok:
                self.qr_tab_activated.emit()
                self.start_qr_scanning()
            else:
                self._tabs.setCurrentIndex(_TAB_LOGIN)
        else:
            self._stop_qr_scanning()

    def _on_toggle_password(self, shown: bool) -> None:
        self._pw_input.setEchoMode(
            QLineEdit.EchoMode.Normal if shown else QLineEdit.EchoMode.Password
        )
        self._pw_toggle.setText(self._t("Hide") if shown else self._t("Show"))

    def _on_login_clicked(self) -> None:
        self._error_label.setVisible(False)
        self.login_submitted.emit(
            self._uid_input.text().strip(),
            self._pw_input.text(),
        )

    def _on_first_admin_clicked(self) -> None:
        self._error_label.setVisible(False)
        self.first_admin_submitted.emit(
            self._fa_uid.text().strip(),
            self._fa_first.text().strip(),
            self._fa_last.text().strip(),
            self._fa_pw.text(),
        )

    def _stop_qr_scanning(self) -> None:
        if self._qr_timer.isActive():
            self._qr_timer.stop()

    # ── Localization ─────────────────────────────────────────────────────────

    @staticmethod
    def _t(text: str) -> str:
        translated = QCoreApplication.translate("Login", text)
        return translated or text

    def retranslateUi(self, *_) -> None:
        self.setWindowTitle(self._t("Login"))
        if self._logo_pixmap is None:
            self._logo_label.setText(self._t("Robot\nPlatform"))
        if getattr(self, "_machine_pixmap", None) is None:
            self._machine_label.setText(self._t("[Machine image not found]"))
        self._setup_instruction.setText(self._t("Press the blue button on the machine to continue."))
        self._btn_sim.setText(self._t("⬤  Simulate Blue Button"))
        self._btn_sim.setToolTip(self._t("Temporary — simulates the physical blue button press"))
        self._fr_title.setText(self._t("First-time setup"))
        self._fr_subtitle.setText(self._t("No users found. Create the first admin account."))
        self._fr_label_uid.setText(self._t("User ID:"))
        self._fr_label_first.setText(self._t("First name:"))
        self._fr_label_last.setText(self._t("Last name:"))
        self._fr_label_pw.setText(self._t("Password:"))
        self._fr_btn.setText(self._t("Create Admin & Login").replace("&", "&&"))  # "&&" = literal & (single & is a mnemonic)
        self._login_title.setText(self._t("Login"))
        self._qr_title.setText(self._t("QR Login"))
        self._uid_label.setText(self._t("User ID:"))
        self._pw_label.setText(self._t("Password:"))
        self._login_btn.setText(self._t("Login"))
        self._qr_info.setText(self._t("Point the camera at a user QR code to log in automatically."))
        self._tabs.setTabText(_TAB_LOGIN, self._t("Login"))
        self._tabs.setTabText(_TAB_QR,    self._t("QR Login"))
        self._seg_login.setText(self._t("Login"))
        self._seg_qr.setText(self._t("QR Login"))
        self._pw_toggle.setText(self._t("Hide") if self._pw_toggle.isChecked() else self._t("Show"))
        self._uid_input.setPlaceholderText(self._t("Numeric user ID"))
        self._pw_input.setPlaceholderText(self._t("Password"))
        self._fa_uid.setPlaceholderText(self._t("Numeric ID"))
        self._fa_first.setPlaceholderText(self._t("First name"))
        self._fa_last.setPlaceholderText(self._t("Last name"))
        self._fa_pw.setPlaceholderText(self._t("Password"))

    def changeEvent(self, event) -> None:
        if event.type() == QEvent.Type.LanguageChange:
            self.retranslateUi()
        super().changeEvent(event)

    # ── Block ESC / accidental close ─────────────────────────────────────────

    def keyPressEvent(self, event) -> None:
        if event.key() == Qt.Key.Key_Escape:
            event.ignore()
            return
        super().keyPressEvent(event)

    def closeEvent(self, event) -> None:
        if not self._allow_close:
            event.ignore()
            return
        super().closeEvent(event)

    # ── Responsive resize ─────────────────────────────────────────────────────

    def resizeEvent(self, event) -> None:
        if self._logo_pixmap:
            size = int(min(self.width() * 0.26, 300))
            self._logo_label.setPixmap(
                self._logo_pixmap.scaled(
                    size, size,
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation,
                )
            )
        if hasattr(self, "_machine_pixmap") and self._machine_pixmap:
            size = int(min(self.height() * 0.32, 260))
            self._machine_label.setPixmap(
                self._machine_pixmap.scaled(
                    size, size,
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation,
                )
            )
        super().resizeEvent(event)
        QTimer.singleShot(0, self._sync_fluid_images)

    # Render the logo inside the SAME browser surface as the smoke, so the smoke
    # flows around it. This avoids unreliable transparent WebEngine-over-QWidget
    # stacking. (The machine image is now a normal widget on the setup card.)
    @staticmethod
    def _pixmap_data_url(pixmap):
        if pixmap is None or pixmap.isNull():
            return ""
        array = QBuffer()
        array.open(QIODevice.OpenModeFlag.WriteOnly)
        pixmap.save(array, "PNG")
        encoded = base64.b64encode(bytes(array.data())).decode("ascii")
        return "data:image/png;base64," + encoded

    def _on_fluid_loaded(self, ok):
        if not ok:
            return
        self._fluid_ready = True
        self._sync_fluid_images()

    def _sync_fluid_images(self):
        if not getattr(self, "_fluid_ready", False):
            return
        payload = {"machine": {"visible": False}}
        label, pixmap = self._logo_label, self._logo_pixmap
        displayed = label.pixmap() if label is not None else None
        if pixmap is None or pixmap.isNull() or displayed is None or displayed.isNull():
            payload["logo"] = {"visible": False}
        else:
            # Convert through screen coordinates; mapTo() between sibling widgets
            # can introduce an incorrect panel offset on some Qt layouts.
            point = self._fluid_view.mapFromGlobal(
                label.mapToGlobal(label.rect().topLeft())
            )
            # Match Qt.KeepAspectRatio pixmap size centered inside QLabel.
            w, h = displayed.width(), displayed.height()
            payload["logo"] = {
                "visible": True,
                "x": point.x() + (label.width() - w) / 2,
                "y": point.y() + (label.height() - h) / 2,
                "w": w, "h": h,
                "src": self._pixmap_data_url(displayed),
            }
        self._fluid_view.page().runJavaScript(
            "window.setDecorations(" + json.dumps(payload) + ");"
        )

    # ── Stylesheet ────────────────────────────────────────────────────────────

    @staticmethod
    def _stylesheet() -> str:
        # Tokens: purple #905BA9 / dark #6F4388 / tint #F1E9F6 / ink #241C2C
        #         muted #756983 / line #E8DFEF / border #CDBFD8
        return """
            QDialog { background-color: white; color: #241c2c; }

            /* Layers above the WebGL surface stay see-through */
            QWidget#fluidOverlay, QWidget#logoPanel, QWidget#rightPanel,
            QStackedWidget#loginPages, QStackedWidget#loginPages > QWidget {
                background: transparent;
            }

            /* Opaque rounded card */
            QFrame#card {
                background-color: white;
                border: 1px solid #e8dfef;
                border-radius: 20px;
            }
            QFrame#card QLabel { background: transparent; color: #241c2c; }
            QFrame#card QLabel#fieldLabel  { color: #756983; font-size: 13px; }
            QFrame#card QLabel#mutedLabel  { color: #756983; font-size: 14px; }
            QFrame#card QLabel#setupInstruction { font-size: 17px; }

            QLabel#errorLabel {
                background-color: #fdecea; color: #b3362f;
                border: 1px solid #f3c4c0; border-radius: 12px;
                font-weight: bold; font-size: 14px; padding: 10px 16px;
            }

            QLineEdit {
                border: 1.5px solid #cdbfd8; border-radius: 12px;
                padding: 0 16px; font-size: 17px;
                color: #241c2c; background: white;
                selection-background-color: #925cad;
            }
            QLineEdit:focus { border: 2px solid #905ba9; }

            /* Login / QR segmented control */
            QFrame#seg { background-color: #f1e9f6; border: none; border-radius: 16px; }
            QPushButton#segBtn {
                background: transparent; color: #756983; border: none;
                border-radius: 12px; font-size: 15px; font-weight: bold;
            }
            QPushButton#segBtn:checked { background-color: #905ba9; color: white; }

            /* Buttons */
            QPushButton#primary {
                background-color: #905ba9; border: none; color: white;
                font-size: 18px; font-weight: bold; border-radius: 14px;
            }
            QPushButton#primary:hover    { background-color: #7a4d92; }
            QPushButton#primary:pressed  { background-color: #6f4388; }
            QPushButton#primary:disabled { background-color: #d5bfe0; color: white; }

            QPushButton#secondary {
                background-color: #f1e9f6; border: none; color: #6f4388;
                font-size: 15px; font-weight: bold; border-radius: 14px;
            }
            QPushButton#secondary:hover   { background-color: #e6d9ee; }
            QPushButton#secondary:pressed { background-color: #905ba9; color: white; }

            QPushButton#ghost {
                background: transparent; border: none; color: #6f4388;
                font-size: 14px; font-weight: bold; border-radius: 10px;
            }
            QPushButton#ghost:hover { background-color: #f1e9f6; }

            /* Chrome-less tab pane: the segmented control replaces the tab bar */
            QTabWidget#loginTabs::pane { border: none; background: transparent; }
            QTabWidget#loginTabs > QWidget { background: transparent; }

            /* QR camera frame */
            QFrame#camFrame { background-color: #1c1622; border: none; border-radius: 16px; }

            /* Message boxes (QR warning) */
            QMessageBox { background-color: white; }
            QMessageBox QLabel { color: #241c2c; background: transparent; }
            QMessageBox QPushButton {
                background-color: #905ba9; color: white; border: none;
                border-radius: 10px; padding: 8px 24px; min-width: 80px; font-size: 14px;
            }
            QMessageBox QPushButton:hover { background-color: #7a4d92; }
        """
