"""Plain UI contracts. Application adapters map engine outcomes into these DTOs."""
from dataclasses import dataclass


@dataclass(frozen=True)
class AccessRequirement:
    action: str | None = None
    feature: str | None = None
    hide_when_role_denied: bool = True
    hide_when_target_denied: bool = False

    def __post_init__(self) -> None:
        if any(value is not None and (not isinstance(value, str) or not value)
               for value in (self.action, self.feature)):
            raise ValueError("Action and feature requirements must be nonempty identifiers")

    @property
    def protected(self) -> bool:
        return self.action is not None or self.feature is not None


@dataclass(frozen=True)
class PresentationAccess:
    feature_visible: bool = True
    role_eligible: bool = True
    action_allowed: bool = True


@dataclass(frozen=True)
class AccessVersion:
    session_revision: int
    policy_revision: int
    selection_revision: int = 0


@dataclass(frozen=True)
class ControlState:
    visible: bool = True
    enabled: bool = True
