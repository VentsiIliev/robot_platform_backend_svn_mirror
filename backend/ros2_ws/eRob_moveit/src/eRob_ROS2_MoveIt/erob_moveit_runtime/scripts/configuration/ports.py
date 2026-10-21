"""Application-owned contracts implemented by storage and runtime adapters."""
from typing import Any, ContextManager, Protocol
from dataclasses import dataclass, field


class ConfigurationRepository(Protocol):
    profile: str

    @property
    def sections(self) -> tuple[str, ...]: ...

    def transaction(self, section: str) -> ContextManager[None]: ...

    def read(self, section: str) -> dict: ...

    def write(self, section: str, value: dict, expected_revision: str) -> None: ...


@dataclass(frozen=True)
class ApplicationFailure:
    """A durable save whose runtime application is pending or failed."""
    code: str
    message: str
    retryable: bool = False
    outcome_unknown: bool = False
    details: dict[str, Any] = field(default_factory=dict)
    source: str = 'runtime'

    @classmethod
    def from_exception(cls, error: Exception, *, prefix='Saved; runtime application failed'):
        return cls(getattr(error, 'code', 'configuration_application_failed'),
                   f'{prefix}: {str(error) or type(error).__name__}',
                   retryable=getattr(error, 'retryable', False),
                   outcome_unknown=getattr(error, 'outcome_unknown', False),
                   details={**getattr(error, 'details', {}), 'cause_type': type(error).__name__, 'cause': str(error)},
                   source=getattr(error, 'source', 'runtime'))


class RuntimeConfiguration(Protocol):
    def snapshot(self, section: str) -> dict | None: ...

    def apply(self, section: str, document: dict) -> ApplicationFailure | str | None:
        """Return None when applied, otherwise the reason application is pending."""
        ...
