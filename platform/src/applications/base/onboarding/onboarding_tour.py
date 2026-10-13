from __future__ import annotations

from typing import Callable, Sequence

from PyQt6.QtCore import QEvent, QObject, QPoint, QRect, QRectF, QSize, Qt
from PyQt6.QtGui import QColor, QKeyEvent, QKeySequence, QPainter, QPainterPath, QPen, QShortcut
from PyQt6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from pl_gui.settings.settings_view.styles import (
    ACTION_BTN_STYLE,
    BORDER,
    GHOST_BTN_STYLE,
    PRIMARY,
    PRIMARY_LIGHT,
    TEXT_COLOR,
)
from src.applications.base.onboarding.onboarding_step import OnboardingStep


_CARD_WIDTH = 340
_SPOTLIGHT_PADDING = 6
_CARD_GAP = 14
_VIEWPORT_MARGIN = 10


class _ProgressDots(QWidget):
    """Compact visual progress indicator used by the tour card."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._current = 0
        self._total = 0
        self.setFixedHeight(18)
        self.setStyleSheet("background: transparent; border: none;")

    def set_progress(self, current: int, total: int, accessible_text: str) -> None:
        self._current = current
        self._total = total
        self.setAccessibleName(accessible_text)
        self.setFixedWidth(max(1, total) * 8 + 10)
        self.update()

    def sizeHint(self) -> QSize:
        return QSize(max(70, self._total * 8 + 10), 18)

    def paintEvent(self, event) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        x = 2
        center_y = self.height() // 2
        for index in range(self._total):
            if index == self._current:
                painter.setBrush(QColor(PRIMARY))
                painter.setPen(Qt.PenStyle.NoPen)
                painter.drawRoundedRect(QRect(x, center_y - 4, 18, 8), 4, 4)
                x += 18
            else:
                painter.setBrush(QColor(BORDER))
                painter.setPen(Qt.PenStyle.NoPen)
                painter.drawEllipse(QRect(x, center_y - 3, 7, 7))
                x += 8


class _TourOverlay(QWidget):
    """Window-covering veil, spotlight and navigation card."""

    def __init__(
        self,
        host: QWidget,
        *,
        on_back: Callable[[], None],
        on_next: Callable[[], None],
        on_close: Callable[[], None],
    ) -> None:
        super().__init__(host)
        self._spotlight = QRect()
        self.setObjectName("onboardingTourOverlay")
        self.setStyleSheet("QWidget#onboardingTourOverlay { background: transparent; }")
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose, False)

        self._card = QFrame(self)
        self._card.setObjectName("onboardingTourCard")
        self._card.setFixedWidth(_CARD_WIDTH)
        self._card.setStyleSheet(
            f"QFrame#onboardingTourCard {{ background: white; border: 1px solid {BORDER}; "
            "border-radius: 12px; }"
        )
        card_layout = QVBoxLayout(self._card)
        card_layout.setContentsMargins(18, 16, 18, 16)
        card_layout.setSpacing(10)

        title_row = QHBoxLayout()
        title_row.setContentsMargins(0, 0, 0, 0)
        title_row.setSpacing(6)
        self._title = QLabel()
        self._title.setWordWrap(True)
        self._title.setStyleSheet(
            f"color: {PRIMARY}; background: transparent; font-size: 15pt; "
            "font-weight: bold; border: none;"
        )
        title_row.addWidget(self._title, 1)

        self._close = QPushButton("×")
        self._close.setFixedSize(44, 44)
        self._close.setCursor(Qt.CursorShape.PointingHandCursor)
        self._close.setStyleSheet(
            f"QPushButton {{ background-color: white; color: {PRIMARY}; "
            f"border: 2px solid {PRIMARY}; border-radius: 8px; "
            "font-size: 20pt; font-weight: bold; padding: 0px; } "
            f"QPushButton:hover, QPushButton:pressed {{ background-color: {PRIMARY_LIGHT}; }}"
        )
        self._close.clicked.connect(on_close)
        title_row.addWidget(self._close, 0, Qt.AlignmentFlag.AlignTop)
        card_layout.addLayout(title_row)

        self._body = QLabel()
        self._body.setWordWrap(True)
        self._body.setStyleSheet(
            f"color: {TEXT_COLOR}; background: transparent; font-size: 10.5pt; border: none;"
        )
        card_layout.addWidget(self._body)

        self._hint = QLabel()
        self._hint.setWordWrap(True)
        self._hint.setStyleSheet(
            f"background: {PRIMARY_LIGHT}; color: {TEXT_COLOR}; border: none; "
            "border-radius: 6px; padding: 8px;"
        )
        card_layout.addWidget(self._hint)

        navigation = QHBoxLayout()
        navigation.setSpacing(6)

        self._skip = QPushButton()
        self._skip.setStyleSheet(
            f"QPushButton {{ background-color: transparent; border: 0px; color: {TEXT_COLOR}; "
            "padding: 6px; font-size: 10pt; } "
            f"QPushButton:hover {{ color: {PRIMARY}; }}"
        )
        self._skip.setCursor(Qt.CursorShape.PointingHandCursor)
        self._skip.clicked.connect(on_close)
        navigation.addWidget(self._skip)

        self._progress = _ProgressDots()
        navigation.addWidget(self._progress)
        navigation.addStretch(1)

        self._back = QPushButton()
        self._back.setStyleSheet(GHOST_BTN_STYLE)
        self._back.setCursor(Qt.CursorShape.PointingHandCursor)
        self._back.clicked.connect(on_back)
        navigation.addWidget(self._back)

        self._next = QPushButton()
        self._next.setStyleSheet(ACTION_BTN_STYLE)
        self._next.setCursor(Qt.CursorShape.PointingHandCursor)
        self._next.clicked.connect(on_next)
        navigation.addWidget(self._next)
        card_layout.addLayout(navigation)

        self._escape_shortcut = QShortcut(QKeySequence(Qt.Key.Key_Escape), self)
        self._escape_shortcut.activated.connect(on_close)
        self._next_shortcut = QShortcut(QKeySequence(Qt.Key.Key_Right), self)
        self._next_shortcut.activated.connect(on_next)
        self._back_shortcut = QShortcut(QKeySequence(Qt.Key.Key_Left), self)
        self._back_shortcut.activated.connect(on_back)

    def show_step(
        self,
        *,
        target: QWidget,
        title: str,
        body: str,
        hint: str,
        spotlight: bool,
        index: int,
        total: int,
        labels: dict[str, str],
    ) -> None:
        self.setGeometry(self.parentWidget().rect())
        host = self.parentWidget()
        if spotlight:
            target_in_host = target.mapTo(host, QPoint(0, 0))
            target_top_left = self.mapFrom(host, target_in_host)
            self._spotlight = QRect(target_top_left, target.size()).adjusted(
                -_SPOTLIGHT_PADDING,
                -_SPOTLIGHT_PADDING,
                _SPOTLIGHT_PADDING,
                _SPOTLIGHT_PADDING,
            ).intersected(self.rect().adjusted(2, 2, -2, -2))
        else:
            self._spotlight = QRect()

        self._title.setText(title)
        self._body.setText(body)
        self._hint.setText(hint)
        self._hint.setVisible(bool(hint))
        content_width = _CARD_WIDTH - 36
        self._fit_wrapped_label(self._title, content_width - 50)
        self._fit_wrapped_label(self._body, content_width)
        if hint:
            self._fit_wrapped_label(self._hint, content_width - 16)
        progress_text = labels["progress"].format(current=index + 1, total=total)
        self._progress.set_progress(index, total, progress_text)
        self._skip.setText(labels["skip"])
        self._close.setToolTip(labels["close"])
        self._close.setAccessibleName(labels["close"])
        self._back.setText(labels["back"])
        self._back.setVisible(index > 0)
        self._next.setText(labels["finish"] if index == total - 1 else labels["next"])

        self._card.adjustSize()
        self._position_card()
        self.update()

    @staticmethod
    def _fit_wrapped_label(label: QLabel, width: int) -> None:
        """Reserve the full wrapped-text height before sizing the card."""
        label.setFixedWidth(width)
        wrapped_height = label.heightForWidth(width)
        if wrapped_height > 0:
            label.setMinimumHeight(wrapped_height)

    def focus_next(self) -> None:
        self._next.setFocus(Qt.FocusReason.OtherFocusReason)

    def paintEvent(self, event) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        outer = QPainterPath()
        outer.addRect(QRectF(self.rect()))
        hole = QPainterPath()
        hole.addRoundedRect(QRectF(self._spotlight), 10, 10)
        painter.fillPath(outer.subtracted(hole), QColor(20, 12, 28, 184))
        if not self._spotlight.isEmpty():
            painter.setPen(QPen(QColor("white"), 3))
            painter.drawRoundedRect(self._spotlight, 10, 10)

    def keyPressEvent(self, event: QKeyEvent) -> None:
        if event.key() == Qt.Key.Key_Escape:
            self._skip.click()
            return
        if event.key() == Qt.Key.Key_Right:
            self._next.click()
            return
        if event.key() == Qt.Key.Key_Left and self._back.isVisible():
            self._back.click()
            return
        super().keyPressEvent(event)

    def _position_card(self) -> None:
        # The navigation row can have a wider size hint than the deliberately
        # compact card. Position from the actual constrained size, otherwise
        # the visible card is shifted even though its geometry stays 340 px.
        card_size = self._card.size()
        available = self.rect().adjusted(
            _VIEWPORT_MARGIN,
            _VIEWPORT_MARGIN,
            -_VIEWPORT_MARGIN,
            -_VIEWPORT_MARGIN,
        )
        if self._spotlight.isEmpty():
            left = available.center().x() - card_size.width() // 2
            top = available.center().y() - card_size.height() // 2
            self._card.setGeometry(left, top, card_size.width(), card_size.height())
            return
        left = self._spotlight.center().x() - card_size.width() // 2
        left = max(available.left(), min(left, available.right() - card_size.width()))
        below = self._spotlight.bottom() + _CARD_GAP
        above = self._spotlight.top() - _CARD_GAP - card_size.height()
        if below + card_size.height() <= available.bottom():
            top = below
        elif above >= available.top():
            top = above
        else:
            top = max(
                available.top(),
                min(available.center().y() - card_size.height() // 2,
                    available.bottom() - card_size.height()),
            )
            right = self._spotlight.right() + _CARD_GAP
            left_side = self._spotlight.left() - _CARD_GAP - card_size.width()
            if right + card_size.width() <= available.right():
                left = right
            elif left_side >= available.left():
                left = left_side
        self._card.setGeometry(left, top, card_size.width(), card_size.height())


class OnboardingTour(QObject):
    """Coordinates a reusable tour without knowing application internals."""

    def __init__(
        self,
        host_provider: Callable[[], QWidget | None],
        steps: Sequence[OnboardingStep],
        translator: Callable[[str], str],
        parent: QObject | None = None,
    ) -> None:
        super().__init__(parent)
        self._host_provider = host_provider
        self._steps = tuple(steps)
        self._translate = translator
        self._overlay: _TourOverlay | None = None
        self._index = 0
        self._previous_focus: QWidget | None = None

    def start(self) -> None:
        host = self._host_provider()
        if host is None or not self._steps:
            return
        self.stop()
        self._previous_focus = host.focusWidget()
        self._overlay = _TourOverlay(
            host,
            on_back=self.previous,
            on_next=self.next,
            on_close=self.stop,
        )
        host.installEventFilter(self)
        self._overlay.installEventFilter(self)
        self._index = 0
        self._overlay.show()
        self._overlay.raise_()
        self._show_available_step(1)
        self._overlay.focus_next()

    def stop(self) -> None:
        if self._overlay is None:
            return
        host = self._overlay.parentWidget()
        host.removeEventFilter(self)
        self._overlay.removeEventFilter(self)
        self._overlay.hide()
        self._overlay.deleteLater()
        self._overlay = None
        if self._previous_focus is not None:
            self._previous_focus.setFocus(Qt.FocusReason.OtherFocusReason)
        self._previous_focus = None

    def next(self) -> None:
        if self._index >= len(self._steps) - 1:
            self.stop()
            return
        self._index += 1
        self._show_available_step(1)

    def previous(self) -> None:
        if self._index <= 0:
            return
        self._index -= 1
        self._show_available_step(-1)

    def eventFilter(self, watched: QObject, event: QEvent) -> bool:
        if self._overlay is None:
            return False
        if event.type() in (QEvent.Type.Resize, QEvent.Type.Move, QEvent.Type.LayoutRequest):
            self._refresh()
        if event.type() == QEvent.Type.KeyPress:
            key_event = event if isinstance(event, QKeyEvent) else None
            if key_event is not None and key_event.key() == Qt.Key.Key_Escape:
                self.stop()
                return True
            if key_event is not None and key_event.key() == Qt.Key.Key_Right:
                self.next()
                return True
            if key_event is not None and key_event.key() == Qt.Key.Key_Left:
                self.previous()
                return True
        return False

    def _show_available_step(self, direction: int) -> None:
        while 0 <= self._index < len(self._steps):
            target = self._steps[self._index].target()
            if target is not None and target.isVisible() and target.width() > 0 and target.height() > 0:
                self._refresh()
                return
            self._index += direction
        self.stop()

    def _refresh(self) -> None:
        if self._overlay is None or not (0 <= self._index < len(self._steps)):
            return
        step = self._steps[self._index]
        target = step.target()
        if target is None or not target.isVisible():
            return
        translate = lambda source: self._translate(source) or source
        self._overlay.show_step(
            target=target,
            title=translate(step.title),
            body=translate(step.body),
            hint=translate(step.hint) if step.hint else "",
            spotlight=step.spotlight,
            index=self._index,
            total=len(self._steps),
            labels={
                "skip": translate("Skip"),
                "close": translate("Close tour"),
                "back": translate("Back"),
                "next": translate("Next"),
                "finish": translate("Finish"),
                "progress": translate("{current} of {total}"),
            },
        )
