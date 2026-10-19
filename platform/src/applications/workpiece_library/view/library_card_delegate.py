"""Paint compact library cards without creating widgets for every stored record."""
from PyQt6.QtCore import QRect, QSize, Qt
from PyQt6.QtGui import QColor, QFont, QPen
from PyQt6.QtWidgets import QStyledItemDelegate, QStyle
from pl_gui.settings.settings_view.styles import BORDER, PRIMARY, PRIMARY_LIGHT, SECONDARY_BG, TEXT_COLOR, TERTIARY_TEXT

class LibraryCardDelegate(QStyledItemDelegate):

    def __init__(self, view):
        super().__init__(view)
        self.view = view
        self.grid = False

    def sizeHint(self, option, index):
        return QSize(194, 210) if self.grid else QSize(400, 76)

    def paint(self, painter, option, index):
        record = index.data(Qt.ItemDataRole.UserRole)
        if record is None:
            return
        painter.save()
        painter.setRenderHint(painter.RenderHint.Antialiasing)
        rect = option.rect.adjusted(3, 3, -3, -5)
        selected = bool(option.state & QStyle.StateFlag.State_Selected)
        painter.setPen(QPen(QColor(PRIMARY if selected else BORDER), 2 if selected else 1))
        painter.setBrush(QColor('white'))
        painter.drawRoundedRect(rect, 12, 12)
        icon = index.data(Qt.ItemDataRole.DecorationRole)
        x = rect.left() + 12
        if self.grid:
            preview = QRect(x, rect.top() + 10, rect.width() - 24, 85)
        else:
            preview = QRect(x, rect.top() + 10, 48, 48)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor(SECONDARY_BG))
        painter.drawRoundedRect(preview, 9, 9)
        if icon and (not icon.isNull()):
            icon.paint(painter, preview.adjusted(5, 5, -5, -5))
        if self.grid:
            x, y, width = (rect.left() + 12, rect.top() + 105, rect.width() - 24)
        else:
            x, y, width = (preview.right() + 12, rect.top() + 14, rect.width() - 86)
            if rect.width() > 440:
                width = rect.width() // 2 - 86
        if self.view._selection_mode:
            check = index.data(Qt.ItemDataRole.CheckStateRole)
            painter.setPen(QPen(QColor(PRIMARY), 1))
            painter.setBrush(QColor(PRIMARY_LIGHT if check == Qt.CheckState.Checked.value else 'white'))
            painter.drawRoundedRect(QRect(rect.right() - 24, rect.top() + 10, 16, 16), 4, 4)
            if check == Qt.CheckState.Checked.value:
                painter.drawText(QRect(rect.right() - 24, rect.top() + 8, 16, 20), Qt.AlignmentFlag.AlignCenter, '✓')
            width -= 22
        name = str(record.get(self.view._schema.name_key, ''))
        description = str(record.get('description', ''))
        painter.setPen(QColor(TEXT_COLOR))
        font = QFont(option.font)
        font.setBold(True)
        painter.setFont(font)
        painter.drawText(QRect(x, y, width, 22), Qt.AlignmentFlag.AlignLeft, painter.fontMetrics().elidedText(name, Qt.TextElideMode.ElideRight, width))
        font.setBold(False)
        font.setPointSize(9)
        painter.setFont(font)
        painter.setPen(QColor(TERTIARY_TEXT))
        painter.drawText(QRect(x, y + 24, width, 20), Qt.AlignmentFlag.AlignLeft, painter.fontMetrics().elidedText(description, Qt.TextElideMode.ElideRight, width))
        meta = self.view.record_summary(record)
        if self.grid:
            painter.drawText(QRect(x, y + 50, width, 20), Qt.AlignmentFlag.AlignLeft, painter.fontMetrics().elidedText(meta, Qt.TextElideMode.ElideRight, width))
            height = record.get('height_mm', record.get('height', ''))
            if height != '':
                painter.drawText(QRect(x, y + 72, width, 20), Qt.AlignmentFlag.AlignLeft, f'{height} mm')
        elif rect.width() > 440:
            painter.setPen(QColor(TERTIARY_TEXT))
            painter.drawText(QRect(rect.left() + rect.width() // 2, rect.top() + 25, rect.width() // 2 - 18, 22), Qt.AlignmentFlag.AlignRight, painter.fontMetrics().elidedText(meta, Qt.TextElideMode.ElideRight, rect.width() // 2 - 18))
        painter.restore()
