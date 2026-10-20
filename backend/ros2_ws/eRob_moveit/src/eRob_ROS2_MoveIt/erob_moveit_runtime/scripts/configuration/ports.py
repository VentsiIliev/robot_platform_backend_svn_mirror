"""Application-owned contracts implemented by storage and runtime adapters."""
from typing import ContextManager, Protocol


class ConfigurationRepository(Protocol):
    profile: str

    @property
    def sections(self) -> tuple[str, ...]: ...

    def transaction(self, section: str) -> ContextManager[None]: ...

    def read(self, section: str) -> dict: ...

    def write(self, section: str, value: dict, expected_revision: str) -> None: ...


class RuntimeConfiguration(Protocol):
    def snapshot(self, section: str) -> dict | None: ...

    def apply(self, section: str, document: dict) -> str | None:
        """Return None when applied, otherwise the reason application is pending."""
        ...
