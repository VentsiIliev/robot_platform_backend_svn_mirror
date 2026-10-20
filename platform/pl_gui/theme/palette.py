"""Qt-free theme state. Defaults remain the source colors for legacy styles."""

import re
from weakref import WeakMethod


DEFAULT_COLORS = {
    "primary": "#905BA9",
    "primary_dark": "#5B3ED6",
    "background": "#F8F9FA",
    "surface": "#FFFFFF",
    "text": "#1A1A2E",
    "border": "#E0E0E0",
}

THEME_PRESETS = {
    "light": dict(DEFAULT_COLORS),
    "dark": {
        "primary": "#905BA9",
        "primary_dark": "#754D8C",
        "background": "#17141D",
        "surface": "#211C28",
        "text": "#F2EDF5",
        "border": "#514759",
    },
}


def mix_colors(first: str, second: str, fraction: float) -> str:
    """Blend RGB colors, with fraction 0 retaining first and 1 selecting second."""
    first_rgb = [int(first[index:index + 2], 16) for index in (1, 3, 5)]
    second_rgb = [int(second[index:index + 2], 16) for index in (1, 3, 5)]
    return "#" + "".join(f"{round(a + (b - a) * fraction):02X}" for a, b in zip(first_rgb, second_rgb))

# Shared shell and application palettes historically use different shades.
SOURCE_ROLES = {
    **{value.lower(): role for role, value in DEFAULT_COLORS.items()},
    "#6d4ed6": "primary_dark",
    "#4a2ec6": "primary_dark",
    "#f6f7fb": "background",
    "#fff": "surface",
    "white": "surface",
    "#1d1b20": "text",
    "#333333": "text",
    "#333": "text",
    "#000000": "text",
    "#000": "text",
    "black": "text",
    "#e4e6f0": "border",
}

_ACCENT_TINTS = {
    "#8b6ff9": 0.15,
    "#ede7f6": 0.88,
    "#e0d6f0": 0.78,
    "#d4cae4": 0.68,
    "#f3edf7": 0.94,
    "#f7f1fb": 0.95,
}

_MUTED_TEXT = {"#7d5260", "#9c9a9e", "#79747e", "#666666", "#666", "#888888", "#888", "gray", "grey"}
_NEUTRAL_SURFACES = {"#f0f0f0", "#f5f5f5", "#edeef2", "#e5e6ea", "#fffbfe", "#eeeeee"}
_NEUTRAL_BORDERS = {"#b0a7bc", "#c4c0ca", "#cac4d0", "#d0d0d0", "#cccccc", "#ccc", "#e7e0ec"}


def validate_colors(colors: dict[str, str]) -> dict[str, str]:
    """Return a complete normalized palette; reject unknown keys and CSS input."""
    if not isinstance(colors, dict) or colors.keys() - DEFAULT_COLORS.keys():
        raise ValueError("Unknown appearance color settings")
    result = dict(DEFAULT_COLORS)
    for role, color in colors.items():
        if not isinstance(color, str) or re.fullmatch(r"#[0-9a-fA-F]{6}", color) is None:
            raise ValueError(f"Invalid color for {role}: expected #RRGGBB")
        result[role] = color.upper()
    return result


class ThemePalette:
    """Process-wide palette with weak bound-method listeners and snapshot reads."""

    def __init__(self):
        self._colors = dict(DEFAULT_COLORS)
        self._listeners = []

    def colors(self) -> dict[str, str]:
        return dict(self._colors)

    def is_dark(self) -> bool:
        """Derive surface brightness so custom dark palettes behave like presets."""
        color = self._colors["surface"]
        channels = [int(color[index:index + 2], 16) / 255 for index in (1, 3, 5)]
        linear = [value / 12.92 if value <= 0.04045 else ((value + 0.055) / 1.055) ** 2.4 for value in channels]
        return sum(value * weight for value, weight in zip(linear, (0.2126, 0.7152, 0.0722))) < 0.179

    def resolve(self, source: str, *, foreground: bool = False) -> str:
        source_key = source.lower()
        dark = self.is_dark()
        if dark:
            if source_key in _MUTED_TEXT:
                return mix_colors(self._colors["text"], self._colors["surface"], 0.25)
            if source_key in _NEUTRAL_SURFACES:
                return mix_colors(self._colors["surface"], self._colors["text"], 0.05)
            if source_key in _NEUTRAL_BORDERS:
                return self._colors["border"]
            if foreground and source_key in ("#c62828", "#2e7d32"):
                return mix_colors(source.upper(), self._colors["text"], 0.45)
        if source_key in _ACCENT_TINTS and (dark or self._colors["primary"] != DEFAULT_COLORS["primary"]):
            target = self._colors["surface"] if dark else "#FFFFFF"
            return mix_colors(self._colors["primary"], target, _ACCENT_TINTS[source_key])
        role = SOURCE_ROLES.get(source_key)
        if dark and foreground and role in ("primary", "primary_dark"):
            return mix_colors(self._colors[role], self._colors["text"], 0.3)
        if role and self._colors[role] != DEFAULT_COLORS[role]:
            return self._colors[role]
        return source

    def subscribe(self, callback) -> None:
        listener = WeakMethod(callback)
        if listener not in self._listeners:
            self._listeners.append(listener)

    def unsubscribe(self, callback) -> None:
        listener = WeakMethod(callback)
        if listener in self._listeners:
            self._listeners.remove(listener)

    def set_colors(self, colors: dict[str, str]) -> None:
        validated = validate_colors(colors)
        if validated == self._colors:
            return
        self._colors = validated
        for listener in tuple(self._listeners):
            callback = listener()
            if callback is None:
                self._listeners.remove(listener)
            else:
                callback()


theme_palette = ThemePalette()


class ThemePreview:
    """A reversible runtime preview; the caller owns durable persistence."""

    def __init__(self):
        self._original = None

    def update(self, colors: dict[str, str]) -> None:
        validated = validate_colors(colors)
        if self._original is None:
            self._original = theme_palette.colors()
        theme_palette.set_colors(validated)

    def accept(self, colors: dict[str, str]) -> None:
        """Accept only after persistence succeeds; future previews start here."""
        theme_palette.set_colors(colors)
        self._original = None

    def discard(self) -> None:
        if self._original is not None:
            original, self._original = self._original, None
            theme_palette.set_colors(original)
