"""Reusable agreed account grants; robot systems supply their role identifiers."""
from src.engine.auth.access_policy import AccessRule, GrantScope, RoleGrant
from src.shared_contracts.authorization.access import AccessKind
from src.shared_contracts.authorization.actions import AuditAction, PermissionAction, RecoveryAction, UserAction
from src.shared_contracts.authorization.features import UserFeature


def user_access_rules(*, admin_role: str, operator_role: str) -> tuple[AccessRule, ...]:
    """Return the currently agreed account/permissions rules.

    Admin manages Operators and their own profile/password. Other Admin and
    Manufacturer account management is reserved for Manufacturer.
    Credential availability, reauthentication, and safety remain service checks.
    """
    rules = [
        AccessRule(AccessKind.ACTION, UserAction.VIEW, (RoleGrant(admin_role),)),
        AccessRule(AccessKind.ACTION, UserAction.CREATE, (
            RoleGrant(admin_role, GrantScope.TARGET_ROLE, frozenset({operator_role})),
        ), target_kind="new_account_role"),
        AccessRule(AccessKind.ACTION, UserAction.EDIT_PROFILE, (
            RoleGrant(admin_role, GrantScope.SELF),
            RoleGrant(admin_role, GrantScope.TARGET_ROLE, frozenset({operator_role})),
        ), target_kind="account"),
        AccessRule(AccessKind.ACTION, UserAction.DELETE, (
            RoleGrant(admin_role, GrantScope.TARGET_ROLE, frozenset({operator_role})),
        ), target_kind="account"),
        AccessRule(AccessKind.ACTION, UserAction.CHANGE_ROLE, target_kind="account"),
        AccessRule(AccessKind.ACTION, UserAction.CHANGE_PASSWORD, (
            RoleGrant(admin_role, GrantScope.SELF),
            RoleGrant(admin_role, GrantScope.TARGET_ROLE, frozenset({operator_role})),
        ), target_kind="account"),
        AccessRule(AccessKind.ACTION, UserAction.REVEAL_PASSWORD, (
            RoleGrant(admin_role, GrantScope.TARGET_ROLE, frozenset({operator_role})),
        ), target_kind="account"),
        AccessRule(AccessKind.ACTION, UserAction.ISSUE_LOGIN_TOKEN, (
            RoleGrant(admin_role, GrantScope.SELF),
            RoleGrant(admin_role, GrantScope.TARGET_ROLE, frozenset({operator_role})),
        ), target_kind="account"),
        AccessRule(AccessKind.ACTION, PermissionAction.MANAGE),
        AccessRule(AccessKind.FEATURE, UserFeature.APP_PERMISSIONS),
        AccessRule(AccessKind.ACTION, AuditAction.VIEW, (
            RoleGrant(admin_role, GrantScope.SELF),
            RoleGrant(admin_role, GrantScope.TARGET_ROLE, frozenset({operator_role})),
        ), target_kind="account_history"),
        AccessRule(AccessKind.ACTION, RecoveryAction.ISSUE, (RoleGrant(admin_role),)),
    ]
    return tuple(rules)
