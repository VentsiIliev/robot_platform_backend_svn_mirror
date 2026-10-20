"""An icon engine that resolves its tint when painted, including cached icons."""

from PyQt6.QtGui import QIcon, QIconEngine
from PyQt6.QtCore import Qt

from .palette import theme_palette


class ThemeIconEngine(QIconEngine):
    def __init__(self, factory, color):
        super().__init__()
        self._factory = factory
        self._color = color
        self._cached_color = None
        self._icon = None

    def clone(self):
        return ThemeIconEngine(self._factory, self._color)

    def _resolved_icon(self):
        color = theme_palette.resolve(self._color, foreground=True)
        if color != self._cached_color:
            self._icon = self._factory(color)
            self._cached_color = color
        return self._icon

    def paint(self, painter, rect, mode, state):
        self._resolved_icon().paint(painter, rect, Qt.AlignmentFlag.AlignCenter, mode, state)

    def pixmap(self, size, mode, state):
        return self._resolved_icon().pixmap(size, mode, state)


def themed_icon(factory, color):
    return QIcon(ThemeIconEngine(factory, color))
