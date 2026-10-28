"""Qt-only adapters; changing access never changes widget styling."""
from abc import ABC, abstractmethod

from PyQt6.QtGui import QAction
from PyQt6.QtWidgets import QTabWidget, QWidget

from .contracts import ControlState


class PresentationAdapter(ABC):
    @abstractmethod
    def state(self) -> ControlState:
        """Read the initial ordinary state before permission binding."""

    @abstractmethod
    def apply(self, state: ControlState) -> None:
        """Set presentation only; no policy, session, or I/O access."""

    def close(self) -> None:
        """Release any signal connections before the view is destroyed."""


class WidgetAdapter(PresentationAdapter):
    def __init__(self, widget: QWidget | QAction) -> None:
        self._widget = widget

    def state(self) -> ControlState:
        visible = (self._widget.isVisible() if isinstance(self._widget, QAction)
                   else not self._widget.isHidden())
        enabled = (self._widget.isEnabled() if isinstance(self._widget, QAction)
                   else self._widget.isEnabledTo(self._widget.parentWidget()))
        return ControlState(visible, enabled)

    def apply(self, state: ControlState) -> None:
        self._widget.setEnabled(state.enabled)
        self._widget.setVisible(state.visible)


class TabAdapter(PresentationAdapter):
    """Address a tab by page identity even when pages are reordered or removed."""

    def __init__(self, tabs: QTabWidget, page: QWidget) -> None:
        if tabs.indexOf(page) < 0:
            raise ValueError("The protected page must belong to the tab widget")
        self._tabs = tabs
        self._page = page
        self._allowed = True
        self._connected = True
        self._redirecting = False
        tabs.currentChanged.connect(self._on_current_changed)

    def state(self) -> ControlState:
        index = self._tabs.indexOf(self._page)
        if index < 0:
            return ControlState(False, False)
        return ControlState(self._tabs.isTabVisible(index), self._tabs.isTabEnabled(index))

    def apply(self, state: ControlState) -> None:
        self._allowed = state.visible and state.enabled
        index = self._tabs.indexOf(self._page)
        if index < 0:
            return
        self._tabs.setTabEnabled(index, state.enabled)
        self._tabs.setTabVisible(index, state.visible)
        self._on_current_changed(self._tabs.currentIndex())

    def _on_current_changed(self, index: int) -> None:
        if self._redirecting or self._allowed or self._tabs.currentWidget() is not self._page:
            return
        self._redirecting = True
        try:
            for candidate in range(self._tabs.count()):
                if (self._tabs.widget(candidate) is not self._page
                        and self._tabs.isTabVisible(candidate)
                        and self._tabs.isTabEnabled(candidate)):
                    self._tabs.setCurrentIndex(candidate)
                    return
            # No permitted fallback: leave the current page inaccessible.
            self._page.hide()
        finally:
            self._redirecting = False

    def close(self) -> None:
        if self._connected:
            self._tabs.currentChanged.disconnect(self._on_current_changed)
            self._connected = False
