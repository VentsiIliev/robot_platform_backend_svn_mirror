from dataclasses import dataclass, field

from .records import AccountSummary


@dataclass(frozen=True)
class LoginCredentials:
    login_id: str
    password: str = field(repr=False)


@dataclass(frozen=True)
class AccountIdentity:
    account: AccountSummary
    credential_version: int
