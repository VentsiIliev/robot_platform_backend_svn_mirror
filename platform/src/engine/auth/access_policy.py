"""Small role/target policy; extending action groups requires no engine edits."""
from dataclasses import dataclass
from enum import Enum
from types import MappingProxyType

from src.engine.auth.i_access_condition import IAccessCondition
from src.engine.auth.i_access_policy import IAccessPolicy
from src.shared_contracts.authorization.access import (
    AccessContext, AccessDecision, AccessKind, AccessRequest, DenialReason,
)


class GrantScope(str, Enum):
    ALL = "all"
    SELF = "self"
    TARGET_ROLE = "target_role"


@dataclass(frozen=True)
class RoleGrant:
    role: str
    scope: GrantScope = GrantScope.ALL
    target_roles: frozenset[str] = frozenset()

    def __post_init__(self) -> None:
        object.__setattr__(self, "target_roles", frozenset(self.target_roles))
        if not self.role or not isinstance(self.scope, GrantScope):
            raise ValueError("A grant requires a role and a supported scope")
        if (self.scope == GrantScope.TARGET_ROLE) != bool(self.target_roles):
            raise ValueError("Only TARGET_ROLE grants require target roles")


@dataclass(frozen=True)
class AccessRule:
    kind: AccessKind
    key: str
    grants: tuple[RoleGrant, ...] = ()
    target_kind: str | None = None
    denied_roles: frozenset[str] = frozenset()
    condition: IAccessCondition | None = None

    def __post_init__(self) -> None:
        object.__setattr__(self, "grants", tuple(self.grants))
        object.__setattr__(self, "denied_roles", frozenset(self.denied_roles))
        if not isinstance(self.kind, AccessKind) or not self.key:
            raise ValueError("A rule requires a supported kind and stable key")
        if any(g.scope != GrantScope.ALL for g in self.grants) and not self.target_kind:
            raise ValueError("Scoped grants require a target kind")


class AccessPolicy(IAccessPolicy):
    """Immutable grants supplied by the application/robot-system composition root."""

    def __init__(
        self, *, roles: frozenset[str], manufacturer_role: str,
        rules: tuple[AccessRule, ...], revision: int = 1,
    ) -> None:
        roles = frozenset(roles)
        if manufacturer_role not in roles or revision < 1:
            raise ValueError("Policy requires a known Manufacturer role and positive revision")
        index = {}
        for rule in rules:
            key = (rule.kind, str(getattr(rule.key, "value", rule.key)))
            if key in index:
                raise ValueError(f"Duplicate access rule: {key}")
            if not rule.denied_roles <= roles or any(
                g.role not in roles or not g.target_roles <= roles for g in rule.grants
            ):
                raise ValueError("Rule refers to an unknown role")
            index[key] = rule
        self._roles = roles
        self._manufacturer_role = manufacturer_role
        self._rules = MappingProxyType(index)
        self._revision = revision

    @property
    def revision(self) -> int:
        return self._revision

    def decide(self, request: AccessRequest, context: AccessContext) -> AccessDecision:
        actor = context.actor
        if actor is None:
            return AccessDecision(False, False, DenialReason.AUTHENTICATION_REQUIRED)
        if actor.role not in self._roles:
            return AccessDecision(False, False, DenialReason.UNKNOWN_ROLE)
        rule = self._rules.get((request.kind, request.key))
        if rule is None:
            return AccessDecision(False, False, DenialReason.UNKNOWN_REQUIREMENT)

        manufacturer = actor.role == self._manufacturer_role
        grants = tuple(g for g in rule.grants if g.role == actor.role)
        eligible = manufacturer or (bool(grants) and actor.role not in rule.denied_roles)
        if not eligible:
            return AccessDecision(False, False, DenialReason.ROLE_DENIED)
        if rule.target_kind is not None:
            if request.target is None:
                return AccessDecision(False, True, DenialReason.TARGET_REQUIRED)
            target = context.target
            if target is None:
                return AccessDecision(False, True, DenialReason.TARGET_NOT_FOUND)
            if target.reference != request.target or target.reference.kind != rule.target_kind:
                return AccessDecision(False, True, DenialReason.TARGET_DENIED)
        elif request.target is not None:
            return AccessDecision(False, True, DenialReason.TARGET_DENIED)

        allowed = manufacturer or any(
            g.scope == GrantScope.ALL
            or (g.scope == GrantScope.SELF
                and context.target.owner_account_id == actor.account_id)
            or (g.scope == GrantScope.TARGET_ROLE
                and context.target.role in g.target_roles)
            for g in grants
        )
        if allowed and not manufacturer and rule.condition is not None:
            allowed = rule.condition.matches(actor, context.target)
        return AccessDecision(
            allowed, True, DenialReason.ALLOWED if allowed else DenialReason.TARGET_DENIED,
        )
