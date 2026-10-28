from dataclasses import dataclass


@dataclass(frozen=True)
class AccountSessionStatus:
    session_revision: int
    authenticated: bool
