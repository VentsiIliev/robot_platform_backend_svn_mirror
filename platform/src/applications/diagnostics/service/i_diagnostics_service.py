"""Read-only diagnostics boundary; no platform or Qt dependencies."""
from abc import ABC, abstractmethod


class IDiagnosticsService(ABC):
    @abstractmethod
    def initial_directory(self) -> str:
        """Default retained-history directory, without starting a recorder."""

    @abstractmethod
    def query(self, filters: dict) -> dict:
        """Return bounded events, warnings and scan completeness for these filters."""

    @abstractmethod
    def export_incident(self, filters: dict, destination: str) -> dict:
        """Export retained selection/operation to a new ZIP, or raise without overwriting."""
