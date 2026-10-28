"""Presentation identifiers are independent of executable operation identifiers."""
from enum import Enum


class UserFeature(str, Enum):
    APP_PERMISSIONS = "users.app_permissions"
