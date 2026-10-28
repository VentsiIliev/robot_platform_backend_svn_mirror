"""Audit DTOs intentionally cannot contain arbitrary request payloads."""
from dataclasses import dataclass

from .maintenance import OperatingSystemActor


@dataclass(frozen=True)
class FieldChange:
    field: str
    before: str | None
    after: str | None

    def __post_init__(self) -> None:
        allowed = {"login_id", "first_name", "last_name", "email", "role", "enabled", "allowed_roles"}
        if self.field not in allowed:
            raise ValueError("Only allowlisted non-secret account fields may be audited")


@dataclass(frozen=True)
class AuditEvent:
    event_id: str
    occurred_at: str
    actor_id: str | None
    actor_role: str | None
    actor_method: str
    target_id: str
    action_id: str
    outcome: str
    changes: tuple[FieldChange, ...] = ()
    password_changed: bool = False
    os_actor: OperatingSystemActor | None = None


@dataclass(frozen=True)
class HistoryQuery:
    target_id: str
    limit: int = 100
    offset: int = 0
