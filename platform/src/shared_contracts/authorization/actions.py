"""Stable shared operation identifiers; domain-specific enums may live elsewhere."""
from enum import Enum


class UserAction(str, Enum):
    VIEW = "users.view"
    CREATE = "users.create"
    EDIT_PROFILE = "users.edit_profile"
    DELETE = "users.delete"
    CHANGE_ROLE = "users.change_role"
    CHANGE_PASSWORD = "users.change_password"
    REVEAL_PASSWORD = "users.reveal_password"
    ISSUE_LOGIN_TOKEN = "users.issue_login_token"


class PermissionAction(str, Enum):
    MANAGE = "permissions.manage"


class AuditAction(str, Enum):
    VIEW = "audit.view"


class RecoveryAction(str, Enum):
    ISSUE = "recovery.issue"
    COMPLETE = "recovery.complete"
