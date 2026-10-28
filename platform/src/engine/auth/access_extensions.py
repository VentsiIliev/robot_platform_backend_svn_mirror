"""Robot-system composition seam for domain actions and trusted resource facts."""
from dataclasses import dataclass
from contextlib import AbstractContextManager
from typing import Callable

from src.engine.auth.access_policy import AccessRule
from src.engine.auth.i_access_resource_resolver import IAccessResourceResolver


@dataclass(frozen=True)
class AccountAccessExtensions:
    rules: tuple[AccessRule, ...] = ()
    resources: IAccessResourceResolver | None = None
    activity_check: Callable[[], str | None] | None = None
    idle_reservation: Callable[[], AbstractContextManager[bool]] | None = None

    def __post_init__(self):
        object.__setattr__(self, "rules", tuple(self.rules))
