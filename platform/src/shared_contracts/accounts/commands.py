from dataclasses import dataclass, field


@dataclass(frozen=True)
class CreateAccount:
    login_id: str
    first_name: str
    last_name: str
    role: str
    password: str = field(repr=False)
    email: str = ""


@dataclass(frozen=True)
class EditProfile:
    account_id: str
    expected_revision: int
    first_name: str
    last_name: str
    email: str


@dataclass(frozen=True)
class ChangePassword:
    account_id: str
    expected_revision: int
    new_password: str = field(repr=False)
    current_password: str = field(default="", repr=False)


@dataclass(frozen=True)
class ChangeRole:
    account_id: str
    expected_revision: int
    role: str
    new_password: str | None = field(default=None, repr=False)


@dataclass(frozen=True)
class DeleteAccount:
    account_id: str
    expected_revision: int


@dataclass(frozen=True)
class RevealPassword:
    account_id: str


@dataclass(frozen=True)
class RevealedPassword:
    password: str = field(repr=False)
