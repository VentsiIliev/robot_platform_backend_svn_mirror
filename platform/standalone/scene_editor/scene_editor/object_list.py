"""Scene list with an independent, clickable lock indicator on every row."""
from PyQt6.QtCore import QRect, QRectF, QSize, Qt, pyqtSignal
from PyQt6.QtGui import QPalette, QPainter, QPainterPath, QPen
from PyQt6.QtWidgets import QAbstractItemView, QListWidget, QStyledItemDelegate, QStyleOptionViewItem, QStyle, QToolTip

OBJECT_ID_ROLE = Qt.ItemDataRole.UserRole
LOCKED_ROLE = Qt.ItemDataRole.UserRole + 1
LOCK_ENABLED_ROLE = Qt.ItemDataRole.UserRole + 2


class _ObjectDelegate(QStyledItemDelegate):
    @staticmethod
    def lock_rect(rect):
        return QRect(rect.right()-31, rect.top(), 32, rect.height())

    def sizeHint(self, option, index):
        size = super().sizeHint(option, index)
        return QSize(size.width()+32, max(size.height(), 34))

    def paint(self, painter, option, index):
        style = option.widget.style()
        style.drawPrimitive(QStyle.PrimitiveElement.PE_PanelItemViewItem, option, painter, option.widget)
        text_option = QStyleOptionViewItem(option)
        text_option.rect.adjust(0, 0, -32, 0)
        super().paint(painter, text_option, index)
        rect = self.lock_rect(option.rect)
        locked = bool(index.data(LOCKED_ROLE))
        enabled = bool(index.data(LOCK_ENABLED_ROLE)) and bool(option.state & QStyle.StateFlag.State_Enabled)
        painter.save()
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.translate(rect.center().x()-10, rect.center().y()-11)
        painter.setOpacity((1 if locked else .65) if enabled else .4)
        color = option.palette.color(QPalette.ColorRole.Link if locked else QPalette.ColorRole.Text)
        painter.setPen(QPen(color, 1.8, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        path = QPainterPath()
        if locked:
            path.moveTo(5, 10)
            path.lineTo(5, 6)
            path.cubicTo(5, 0, 15, 0, 15, 6)
            path.lineTo(15, 10)
        else:
            path.moveTo(10, 10)
            path.lineTo(10, 5)
            path.cubicTo(10, -1, 20, -1, 20, 5)
        painter.drawPath(path)
        painter.drawRoundedRect(QRectF(2, 10, 16, 11), 2, 2)
        painter.drawLine(10, 14, 10, 17)
        painter.restore()

    def helpEvent(self, event, view, option, index):
        if self.lock_rect(option.rect).contains(event.pos()):
            state = 'Locked' if index.data(LOCKED_ROLE) else 'Unlocked'
            action = 'Click to unlock' if index.data(LOCKED_ROLE) else 'Click to lock'
            QToolTip.showText(event.globalPos(), state+' — '+(action if index.data(LOCK_ENABLED_ROLE) else 'unavailable during live viewing or an operation'), view)
            return True
        return super().helpEvent(event, view, option, index)


class ObjectList(QListWidget):
    lock_requested = pyqtSignal(object)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self._object_delegate = _ObjectDelegate(self)
        self.setItemDelegate(self._object_delegate)
        self._lock_press = None
        self.setMouseTracking(True)

    def _lock_index(self, point):
        index = self.indexAt(point)
        return index if index.isValid() and self._object_delegate.lock_rect(self.visualRect(index)).contains(point) else None

    def mousePressEvent(self, event):
        index = self._lock_index(event.position().toPoint())
        if event.button() == Qt.MouseButton.LeftButton and index is not None:
            self._lock_press = index.data(OBJECT_ID_ROLE)
            event.accept()
            return
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton and self._lock_press is not None:
            pressed, self._lock_press = self._lock_press, None
            index = self._lock_index(event.position().toPoint())
            if index is not None and index.data(OBJECT_ID_ROLE) == pressed and index.data(LOCK_ENABLED_ROLE):
                self.lock_requested.emit(pressed)
            event.accept()
            return
        super().mouseReleaseEvent(event)

    def mouseDoubleClickEvent(self, event):
        if self._lock_index(event.position().toPoint()) is not None:
            event.accept()
            return
        super().mouseDoubleClickEvent(event)

    def mouseMoveEvent(self, event):
        index = self._lock_index(event.position().toPoint())
        self.viewport().setCursor(Qt.CursorShape.PointingHandCursor if index is not None and index.data(LOCK_ENABLED_ROLE) else Qt.CursorShape.ArrowCursor)
        if self._lock_press is None:
            super().mouseMoveEvent(event)
