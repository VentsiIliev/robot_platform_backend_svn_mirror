"""Illustrated operator alignment guide, separate from the unmarked camera feed."""

from math import atan2, cos, hypot, radians, sin
from pathlib import Path

from PyQt6.QtCore import QCoreApplication, QEvent, QPointF, QRectF, QSize, Qt
from PyQt6.QtGui import (
    QColor,
    QFont,
    QPainter,
    QPainterPath,
    QPaintEvent,
    QPen,
    QPixmap,
)
from PyQt6.QtWidgets import QSizePolicy, QWidget

from pl_gui.settings.settings_view.styles import (
    BG_COLOR,
    BORDER,
    DISABLED_BORDER,
    DISABLED_PREVIEW_BG,
    ERROR_COLOR,
    STATUS_OK,
    TEXT_COLOR,
    TEXT_ON_PRIMARY,
)
from src.robot_systems.paint.applications.dashboard.head_alignment_presentation import (
    GuideAvailability,
    GuideRotation,
    HeadAlignmentGuideData,
    unavailable_head_alignment_guide,
)

# Static artwork coordinates only. These never come from the detector or camera calibration.
_ARTWORK_BOUNDS = QRectF(240, 28, 780, 1140)
_ARTWORK_TARGET = QPointF(630, 815)
_ARTWORK_PATH = Path(__file__).resolve().parent.parent / "assets" / "paint_head_reference.png"


class PaintHeadGuideAssetError(RuntimeError):
    """The operator's packaged reference illustration cannot be loaded."""


class PaintHeadAlignmentGuide(QWidget):
    """Render a fixed illustration and schematic feedback without marking live images."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._guide: HeadAlignmentGuideData | None = unavailable_head_alignment_guide(None)
        self._status_text = ""
        self._status_attention = False
        self._notice = ""
        self._reference = QPixmap(str(_ARTWORK_PATH))
        if self._reference.isNull():
            raise PaintHeadGuideAssetError(
                f"Cannot load paint-head guide illustration: {_ARTWORK_PATH}"
            )
        self.setObjectName("paintHeadAlignmentGuide")
        self.setMinimumWidth(260)
        self.setMaximumWidth(360)
        self.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding)
        self.hide()

    def sizeHint(self) -> QSize:
        return QSize(320, 440)

    def set_status(self, text: str, *, attention: bool) -> None:
        self._status_text = text
        self._status_attention = attention
        self.update()

    def status_text(self) -> str:
        return self._status_text

    def set_notice(self, text: str) -> None:
        self._notice = text
        self.update()

    def notice_text(self) -> str:
        return self._notice

    def set_guide(self, guide: HeadAlignmentGuideData | None) -> None:
        self._guide = guide
        self.setVisible(guide is not None)
        self.update()

    def card_rectangle(self) -> QRectF:
        scale = max(0.0, min(self.width() / 320.0, self.height() / 440.0))
        width, height = 320 * scale, 440 * scale
        return QRectF((self.width() - width) / 2, (self.height() - height) / 2, width, height)

    def changeEvent(self, event: QEvent | None) -> None:
        if event is not None and event.type() == QEvent.Type.LanguageChange:
            self.update()
        super().changeEvent(event)

    def paintEvent(self, event: QPaintEvent | None) -> None:
        guide = self._guide
        card = self.card_rectangle()
        if guide is None or card.isEmpty():
            return
        available = guide.availability is GuideAvailability.AVAILABLE
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        painter.translate(card.topLeft())
        painter.scale(card.width() / 320.0, card.height() / 440.0)
        background = BG_COLOR if available else DISABLED_PREVIEW_BG
        text_color = TEXT_COLOR if available else QColor(DISABLED_BORDER).darker(150).name()
        painter.setBrush(QColor(background))
        painter.setPen(QPen(QColor(BORDER), 1.0))
        painter.drawRoundedRect(QRectF(0.5, 0.5, 319, 439), 14, 14)

        title = "Head aligned" if guide.aligned else "Centre the marker"
        description = "Adjust the paint head until the marker reaches the green target zone."
        if not available:
            title = "Guidance unavailable"
            description = "Correction guidance will resume when reliable feedback returns."
        elif guide.aligned:
            description = "Press Start to check and continue."
        if not self._status_text:
            title = "Paint-head alignment"
            description = "No paint-head inspection result is available yet."
        status_color = ERROR_COLOR if self._status_attention and available else text_color
        if self._status_text:
            _text(
                painter,
                QRectF(16, 10, 288, 58),
                self._status_text,
                status_color,
                size=16,
                bold=True,
                translated=True,
            )
        else:
            _text(painter, QRectF(16, 10, 288, 58), title, text_color, size=19, bold=True)
        if not guide.show_head_reference:
            description = "Fit the paint head, then press Start to check again."
        _text(painter, QRectF(16, 72, 288, 48), description, text_color, size=13)

        scale = min(204 / _ARTWORK_BOUNDS.width(), 280 / _ARTWORK_BOUNDS.height())
        artwork = QRectF(
            8,
            125 + (280 - _ARTWORK_BOUNDS.height() * scale) / 2,
            _ARTWORK_BOUNDS.width() * scale,
            _ARTWORK_BOUNDS.height() * scale,
        )
        if guide.show_head_reference:
            painter.save()
            if not available:
                painter.setOpacity(0.28)
            painter.drawPixmap(artwork, self._reference, _ARTWORK_BOUNDS)
            painter.restore()
        target = artwork.topLeft() + (_ARTWORK_TARGET - _ARTWORK_BOUNDS.topLeft()) * scale
        self._paint_target(painter, guide, target)
        self._paint_direction(painter, guide, text_color)

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor(background))
        painter.drawRoundedRect(QRectF(216, 260, 96, 116), 10, 10)
        target_color = STATUS_OK if available else DISABLED_BORDER
        icon = QPointF(264, 283)
        self._target_zone(painter, icon, 13, target_color)
        _text(
            painter,
            QRectF(222, 306, 84, 62),
            "Target zone (centre)",
            text_color,
            size=12,
            alignment=Qt.AlignmentFlag.AlignCenter,
        )
        if self._notice:
            _text(
                painter,
                QRectF(16, 405, 288, 30),
                self._notice,
                text_color,
                size=12,
                alignment=Qt.AlignmentFlag.AlignCenter,
                translated=True,
            )
        painter.end()

    def _paint_target(
        self, painter: QPainter, guide: HeadAlignmentGuideData, target: QPointF
    ) -> None:
        available = guide.availability is GuideAvailability.AVAILABLE
        target_color = STATUS_OK if available else DISABLED_BORDER
        self._target_zone(painter, target, 41, target_color)
        marker = QPointF(target)
        direction = guide.translation_direction
        if direction is not None:
            x, y = direction
            length = hypot(x, y)
            displacement = 51.0 + 16.0 * guide.translation_extent
            marker -= QPointF(displacement * x / length, displacement * y / length)
        elif guide.rotation_direction is not GuideRotation.NONE:
            # Rotation-only feedback still moves toward the centre as correction improves.
            sign = 1 if guide.rotation_direction is GuideRotation.CLOCKWISE else -1
            angle = radians(90 + sign * (20 + 45 * guide.rotation_extent))
            radius = 51.0 + 16.0 * guide.rotation_extent
            marker += QPointF(radius * cos(angle), -radius * sin(angle))
        painter.setPen(QPen(QColor(TEXT_ON_PRIMARY), 2.0))
        marker_color = (
            DISABLED_BORDER if not available else STATUS_OK if guide.aligned else ERROR_COLOR
        )
        painter.setBrush(QColor(marker_color))
        painter.drawEllipse(marker, 9.0, 9.0)
        if available and direction is not None:
            _arrow(painter, (marker, target))
        elif available and guide.rotation_direction is GuideRotation.NONE and not guide.aligned:
            # No correction is requested while the detector confirms the aligned state.
            return

    @staticmethod
    def _target_zone(painter: QPainter, center: QPointF, radius: float, color: str) -> None:
        fill = QColor(color)
        fill.setAlpha(65)
        painter.setBrush(fill)
        painter.setPen(QPen(QColor(color), 1.8))
        painter.drawEllipse(center, radius, radius)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawEllipse(center, radius * 0.65, radius * 0.65)
        painter.drawEllipse(center, radius * 0.27, radius * 0.27)
        axis = QColor(color)
        axis.setAlpha(180)
        painter.setPen(QPen(axis, 1.0, Qt.PenStyle.DashLine))
        painter.drawLine(center + QPointF(-radius * 1.45, 0), center + QPointF(radius * 1.45, 0))
        painter.drawLine(center + QPointF(0, -radius * 1.45), center + QPointF(0, radius * 1.45))

    @staticmethod
    def _paint_direction(painter: QPainter, guide: HeadAlignmentGuideData, text_color: str) -> None:
        available = guide.availability is GuideAvailability.AVAILABLE
        painter.setBrush(QColor(BG_COLOR if available else DISABLED_PREVIEW_BG))
        painter.setPen(QPen(QColor(BORDER), 0.8))
        painter.drawRoundedRect(QRectF(216, 117, 96, 132), 10, 10)
        center = QPointF(264, 147)
        caption = "Follow the correction arrow"
        if not available:
            caption = "Waiting for reliable feedback"
        elif guide.aligned:
            caption = "Aligned"
        elif guide.rotation_direction is GuideRotation.CLOCKWISE:
            caption = "Rotate clockwise"
        elif guide.rotation_direction is GuideRotation.COUNTERCLOCKWISE:
            caption = "Rotate counterclockwise"
        elif guide.translation_direction is None:
            caption = "Confirming alignment…"
        color = TEXT_COLOR if available else DISABLED_BORDER
        if available and guide.rotation_direction is not GuideRotation.NONE:
            start, span = (
                (150, -260) if guide.rotation_direction is GuideRotation.CLOCKWISE else (30, 260)
            )
            _arrow(
                painter,
                tuple(
                    center
                    + QPointF(
                        17 * cos(radians(start + span * index / 32)),
                        -17 * sin(radians(start + span * index / 32)),
                    )
                    for index in range(33)
                ),
                color=TEXT_COLOR,
            )
        else:
            painter.setPen(QPen(QColor(STATUS_OK if available and guide.aligned else color), 2.0))
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawEllipse(center, 16, 16)
            if available and guide.aligned:
                painter.drawLine(center + QPointF(-8, 0), center + QPointF(-2, 6))
                painter.drawLine(center + QPointF(-2, 6), center + QPointF(9, -7))
            else:
                painter.drawLine(center + QPointF(-7, 0), center + QPointF(7, 0))
        _text(
            painter,
            QRectF(222, 173, 84, 68),
            caption,
            text_color,
            size=12,
            bold=True,
            alignment=Qt.AlignmentFlag.AlignCenter,
        )


def _text(
    painter: QPainter,
    rectangle: QRectF,
    source: str,
    color: str,
    *,
    size: int,
    bold: bool = False,
    alignment: Qt.AlignmentFlag = Qt.AlignmentFlag.AlignLeft,
    translated: bool = False,
) -> None:
    text = source if translated else QCoreApplication.translate("PaintDashboard", source) or source
    font = QFont(painter.font())
    font.setPixelSize(size)
    font.setBold(bold)
    painter.setFont(font)
    painter.setPen(QColor(color))
    painter.drawText(
        rectangle,
        int(alignment | Qt.AlignmentFlag.AlignVCenter) | int(Qt.TextFlag.TextWordWrap),
        text,
    )


def _arrow(painter: QPainter, points: tuple[QPointF, ...], *, color: str = STATUS_OK) -> None:
    if len(points) < 2:
        return
    path = QPainterPath(points[0])
    for point in points[1:]:
        path.lineTo(point)
    end, previous = points[-1], points[-2]
    angle = atan2(end.y() - previous.y(), end.x() - previous.x())
    for turn in (-0.55, 0.55):
        path.moveTo(end)
        path.lineTo(end.x() - 9 * cos(angle + turn), end.y() - 9 * sin(angle + turn))
    painter.setBrush(Qt.BrushStyle.NoBrush)
    painter.setPen(
        QPen(
            QColor(TEXT_ON_PRIMARY),
            4.5,
            Qt.PenStyle.SolidLine,
            Qt.PenCapStyle.RoundCap,
            Qt.PenJoinStyle.RoundJoin,
        )
    )
    painter.drawPath(path)
    painter.setPen(
        QPen(
            QColor(color),
            2.5,
            Qt.PenStyle.SolidLine,
            Qt.PenCapStyle.RoundCap,
            Qt.PenJoinStyle.RoundJoin,
        )
    )
    painter.drawPath(path)
