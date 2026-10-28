from dataclasses import dataclass
from enum import Enum


class UserRole(str, Enum):
    MANUFACTURER = "Manufacturer"
    ADMIN = "Admin"
    OPERATOR = "Operator"


@dataclass(frozen=True)
class AccountSummary:
    account_id: str
    login_id: str
    first_name: str
    last_name: str
    role: str
    email: str
    enabled: bool
    revision: int
    created_at: str | None
    created_by: str | None
    updated_at: str | None
    updated_by: str | None


@dataclass(frozen=True)
class AccountChange:
    account: AccountSummary
    changed: bool
