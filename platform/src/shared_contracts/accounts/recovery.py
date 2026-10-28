from dataclasses import dataclass, field


@dataclass(frozen=True)
class GenerateRecoveryCodes:
    current_password: str = field(repr=False)


@dataclass(frozen=True)
class RecoverAdminAccount:
    login_id: str
    recovery_code: str = field(repr=False)
    new_password: str = field(repr=False)


@dataclass(frozen=True)
class RecoveryCodes:
    account_id: str
    codes: tuple[str, ...] = field(repr=False)
