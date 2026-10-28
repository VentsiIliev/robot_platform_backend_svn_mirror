from dataclasses import dataclass
import time
from typing import Callable

from src.engine.auth.account_store import IAccountTransaction, RecoveryAttempts


@dataclass(frozen=True)
class AuthenticationLimits:
    failures_per_identifier: int = 5
    failures_global: int = 50
    window_seconds: int = 60

    def __post_init__(self) -> None:
        values = (self.failures_per_identifier, self.failures_global, self.window_seconds)
        if any(type(value) is not int or value < 1 for value in values):
            raise ValueError("Authentication limits must be positive")


class AuthenticationThrottle:
    def __init__(self, limits: AuthenticationLimits = AuthenticationLimits(),
                 clock: Callable[[], float] = time.time) -> None:
        self._limits, self._clock = limits, clock

    def limited(self, transaction: IAccountTransaction, key: str) -> bool:
        transaction.prune_authentication_attempts(self._clock() - self._limits.window_seconds)
        identity = transaction.authentication_attempts(key)
        total = transaction.authentication_attempts("global")
        return ((identity is not None and identity.failures >= self._limits.failures_per_identifier)
                or (total is not None and total.failures >= self._limits.failures_global))

    def failed(self, transaction: IAccountTransaction, key: str) -> None:
        now = self._clock()
        for identifier in (key, "global"):
            old = transaction.authentication_attempts(identifier)
            transaction.set_authentication_attempts(identifier, RecoveryAttempts(
                old.failures + 1 if old else 1, old.window_started if old else now,
            ))

    def succeeded(self, transaction: IAccountTransaction, key: str) -> None:
        transaction.set_authentication_attempts(key, RecoveryAttempts(0, self._clock()))
