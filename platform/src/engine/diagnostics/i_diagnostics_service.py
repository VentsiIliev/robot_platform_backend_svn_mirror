"""Lifecycle contract; diagnostics is never a machine readiness requirement."""
from abc import ABC, abstractmethod


class IDiagnosticsService(ABC):
    @abstractmethod
    def start(self) -> bool:
        """Start optional recording; False means disabled or unavailable."""

    @property
    @abstractmethod
    def status(self) -> dict:
        """Report whether capture is disabled, recording, unavailable or stopped."""

    @abstractmethod
    def close(self) -> None:
        """Stop capture and drain admitted work within the recorder deadline."""
