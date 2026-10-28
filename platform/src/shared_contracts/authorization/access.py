"""Immutable, storage-independent access requests and trusted evaluation facts."""
from dataclasses import dataclass
from enum import Enum


class AccessKind(str, Enum):
    ACTION = "action"
    FEATURE = "feature"
    APPLICATION = "application"


@dataclass(frozen=True)
class ResourceRef:
    kind: str
    resource_id: str


@dataclass(frozen=True)
class AccessRequest:
    kind: AccessKind
    key: str
    target: ResourceRef | None = None


@dataclass(frozen=True)
class Actor:
    """Verified account identity; supplied by trusted context, never the view."""

    account_id: str
    role: str


@dataclass(frozen=True)
class ResourceFacts:
    reference: ResourceRef
    owner_account_id: str | None = None
    role: str | None = None


@dataclass(frozen=True)
class AccessContext:
    """One consistent actor/target snapshot from a context provider."""

    actor: Actor | None
    session_revision: int
    target: ResourceFacts | None = None


class DenialReason(str, Enum):
    ALLOWED = "allowed"
    AUTHENTICATION_REQUIRED = "authentication_required"
    UNKNOWN_ROLE = "unknown_role"
    UNKNOWN_REQUIREMENT = "unknown_requirement"
    ROLE_DENIED = "role_denied"
    TARGET_REQUIRED = "target_required"
    TARGET_NOT_FOUND = "target_not_found"
    TARGET_DENIED = "target_denied"


@dataclass(frozen=True)
class AccessDecision:
    """Display advice only; this object must never authorize a later mutation."""

    allowed: bool
    role_eligible: bool
    reason: DenialReason


@dataclass(frozen=True)
class AccessSnapshot:
    session_revision: int
    policy_revision: int
    requests: tuple[AccessRequest, ...]
    decisions: tuple[AccessDecision, ...]

    def __post_init__(self) -> None:
        if len(self.requests) != len(self.decisions):
            raise ValueError("Every request must have exactly one access decision")
