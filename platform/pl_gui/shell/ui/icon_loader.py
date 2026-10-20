import os

import qtawesome as qta
from PyQt6.QtCore import QSize
from PyQt6.QtGui import QColor, QIcon, QPainter, QPixmap
from pl_gui.theme.icon import themed_icon
from pl_gui.theme.palette import SOURCE_ROLES


_icon_cache = {}


def _tint_icon(icon, color, size):
    """Tint an existing QIcon's pixmap to the given color.

    Args:
        icon:  QIcon to tint
        color: Color string (e.g. "#FFFFFF")
        size:  QSize for the pixmap extraction

    Returns:
        QIcon with tinted pixmap, or the original icon on failure
    """
    try:
        pixmap = icon.pixmap(size)
        if pixmap.isNull():
            return icon
        tinted = QPixmap(pixmap.size())
        tinted.fill(QColor(color))
        painter = QPainter(tinted)
        painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_DestinationIn)
        painter.drawPixmap(0, 0, pixmap)
        painter.end()
        return QIcon(tinted)
    except Exception:
        return icon


def load_icon(source, color=None, size=None):
    """Single source of truth for icon loading.

    Args:
        source: QIcon object, file path string, or qtawesome string (e.g. "fa5s.cog")
        color:  Optional color string for tinting (e.g. "#FFFFFF")
        size:   Optional QSize — required when tinting a QIcon object

    Returns:
        QIcon (empty QIcon if loading fails)
    """
    if isinstance(source, QIcon):
        if color and size:
            return _tint_icon(source, color, size)
        return source

    if not isinstance(source, str) or not source:
        return QIcon()

    cache_key = (source, color)
    cached = _icon_cache.get(cache_key)
    if cached is not None:
        return cached

    icon = None

    # Try filesystem path first
    if os.path.exists(source):
        icon = QIcon(source)
        if icon.isNull():
            icon = None
    else:
        # Try qtawesome icon string
        try:
            if color:
                icon = qta.icon(source, color=color)
                if not icon.isNull() and SOURCE_ROLES.get(str(color).lower()) in ("primary", "primary_dark", "text"):
                    def create_icon(resolved_color):
                        return qta.icon(source, color=resolved_color)
                    icon = themed_icon(create_icon, color)
            else:
                icon = qta.icon(source)
            if icon.isNull():
                icon = None
        except Exception:
            icon = None

    if icon is not None:
        _icon_cache[cache_key] = icon
        return icon

    return QIcon()
