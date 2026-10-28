from dataclasses import dataclass, field


@dataclass(frozen=True)
class AdminSetupStatus:
    required: bool


@dataclass(frozen=True)
class CreateFirstAdmin:
    login_id: str
    first_name: str
    last_name: str
    password: str = field(repr=False)
    email: str = ""
