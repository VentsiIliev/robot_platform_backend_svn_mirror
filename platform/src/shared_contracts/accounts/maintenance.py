from dataclasses import dataclass, field


@dataclass(frozen=True)
class OperatingSystemActor:
    effective_uid: int
    effective_username: str
    sudo_uid: int | None = None
    sudo_username: str | None = None

    @property
    def reference(self) -> str:
        return "os:" + str(self.effective_uid)


@dataclass(frozen=True)
class CreateManufacturer:
    login_id: str
    first_name: str
    last_name: str
    password: str = field(repr=False)
    email: str = ""


@dataclass(frozen=True)
class ResetManufacturerPassword:
    account_id: str
    expected_revision: int
    new_password: str = field(repr=False)
