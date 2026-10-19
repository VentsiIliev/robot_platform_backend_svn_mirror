from abc import ABC, abstractmethod


class IWorkpieceDuplicator(ABC):
    """Optional library capability for saving an independent workpiece copy."""

    @abstractmethod
    def duplicate(self, storage_id: str) -> tuple[bool, str]:
        """Copy a saved record to a new ID and storage location; return success and a message."""
