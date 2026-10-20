"""Apply shared colors to existing and lazily created Qt widgets.

Keep each widget's original stylesheet so repeated changes never remap a
previously selected color. StyleChange also covers controller-driven restyling.
No widget ownership or application lifecycle changes are needed.
"""

import re

from PyQt6.QtCore import QEvent, QObject, Qt, pyqtSignal
from PyQt6.QtGui import QColor, QPalette
from PyQt6.QtWidgets import QApplication, QWidget

from .palette import DEFAULT_COLORS, theme_palette

_COLOR = re.compile(r"#[0-9a-fA-F]{8}\b|#[0-9a-fA-F]{6}\b|#[0-9a-fA-F]{3}\b|\b(?:white|black|gray|grey)\b", re.IGNORECASE)
_DECLARATION = re.compile(r"([\w-]+\s*:\s*)([^;{}]+)")
_ACCENT_RGBA = re.compile(r"rgba\(\s*122\s*,\s*90\s*,\s*248\s*,", re.IGNORECASE)


def themed_stylesheet(source: str) -> str:
    """Render a source stylesheet against the active palette in one pass."""
    def declaration(match):
        prefix, value = match.groups()
        property_name = prefix.split(":")[0].strip().lower()

        def color(color_match):
            source_color = color_match.group()
            # Surface customization must not recolor text on filled buttons.
            if property_name in ("color", "selection-color") and source_color.lower() in ("white", "#fff", "#ffffff"):
                return source_color
            if property_name not in ("color", "selection-color") and source_color.lower() in ("black", "#000", "#000000"):
                return source_color
            return theme_palette.resolve(source_color, foreground=property_name in ("color", "selection-color"))

        value = _COLOR.sub(color, value)
        primary = theme_palette.colors()["primary"]
        if primary != DEFAULT_COLORS["primary"] or theme_palette.is_dark():
            rgb = [str(int(primary[index:index + 2], 16)) for index in (1, 3, 5)]
            value = _ACCENT_RGBA.sub("rgba(" + ", ".join(rgb) + ",", value)
        return prefix + value

    return _DECLARATION.sub(declaration, source)


def source_stylesheet(widget: QWidget) -> str:
    """Read the unrendered stylesheet when composing or modifying widget styles."""
    source = widget.property("_theme_source_style")
    return source if source is not None else widget.styleSheet()


class ThemeRuntime(QObject):
    refresh_requested = pyqtSignal()
    colors_changed = pyqtSignal()

    def __init__(self, app: QApplication):
        super().__init__(app)
        self._app = app
        self._applying = False
        self._base_palette = QPalette(app.palette())
        # Repaint on the next GUI turn, never inside a widget's teardown or a
        # color dialog's own currentColorChanged handler.
        self.refresh_requested.connect(self.refresh, Qt.ConnectionType.QueuedConnection)
        theme_palette.subscribe(self._palette_changed)
        app.installEventFilter(self)
        self.refresh()

    def _palette_changed(self):
        # Queued automatically if a preference is changed outside the GUI thread.
        if not QApplication.closingDown():
            self.refresh_requested.emit()

    def eventFilter(self, watched, event):
        if not self._applying and isinstance(watched, QWidget):
            if event.type() in (QEvent.Type.StyleChange, QEvent.Type.Polish, QEvent.Type.Show):
                self._style_widget(watched)
        return False

    def _style_widget(self, widget):
        if widget.property("themeLiteralColors"):
            return
        current = widget.styleSheet()
        rendered = widget.property("_theme_rendered_style")
        if current != rendered:
            # Existing widgets sometimes append rules to their current QSS.
            # Preserve the original prefix rather than baking in active colors.
            if rendered and current.startswith(rendered):
                source = source_stylesheet(widget) + current[len(rendered):]
            else:
                source = current
            widget.setProperty("_theme_source_style", source)
        source = widget.property("_theme_source_style") or ""
        result = themed_stylesheet(source)
        widget.setProperty("_theme_rendered_style", result)
        if current != result:
            self._applying = True
            try:
                widget.setStyleSheet(result)
            finally:
                self._applying = False
        widget.update()

    def refresh(self):
        if QApplication.closingDown():
            return
        colors = theme_palette.colors()
        palette = QPalette(self._base_palette)
        for role, key in (
            (QPalette.ColorRole.Window, "background"),
            (QPalette.ColorRole.Base, "surface"),
            (QPalette.ColorRole.Button, "surface"),
            (QPalette.ColorRole.WindowText, "text"),
            (QPalette.ColorRole.Text, "text"),
            (QPalette.ColorRole.ButtonText, "text"),
            (QPalette.ColorRole.Highlight, "primary"),
        ):
            palette.setColor(role, QColor(colors[key]))
        if theme_palette.is_dark():
            muted = QColor(theme_palette.resolve("#7D5260"))
            for role, color in (
                (QPalette.ColorRole.AlternateBase, theme_palette.resolve("#F0F0F0")),
                (QPalette.ColorRole.ToolTipBase, colors["surface"]),
                (QPalette.ColorRole.ToolTipText, colors["text"]),
                (QPalette.ColorRole.PlaceholderText, muted.name()),
                (QPalette.ColorRole.Light, colors["border"]),
                (QPalette.ColorRole.Midlight, colors["border"]),
                (QPalette.ColorRole.Mid, colors["border"]),
                (QPalette.ColorRole.Dark, colors["border"]),
                (QPalette.ColorRole.Shadow, colors["border"]),
                (QPalette.ColorRole.Link, theme_palette.resolve(DEFAULT_COLORS["primary"], foreground=True)),
                (QPalette.ColorRole.HighlightedText, "#FFFFFF"),
            ):
                palette.setColor(role, QColor(color))
            for role in (QPalette.ColorRole.Text, QPalette.ColorRole.ButtonText, QPalette.ColorRole.WindowText):
                palette.setColor(QPalette.ColorGroup.Disabled, role, muted)
        self._app.setPalette(palette)
        for widget in self._app.allWidgets():
            self._style_widget(widget)
        self.colors_changed.emit()


def install_theme(app: QApplication) -> ThemeRuntime:
    """Install once per QApplication; retain the filter for the app lifetime."""
    runtime = getattr(app, "_platform_theme_runtime", None)
    if runtime is None:
        runtime = ThemeRuntime(app)
        app._platform_theme_runtime = runtime
    return runtime
