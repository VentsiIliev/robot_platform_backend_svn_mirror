from abc import ABC, abstractmethod
from typing import List


class ISafetyChecker(ABC):

    @abstractmethod
    def is_within_safety_limits(self, position: List[float]) -> bool:
        """Return whether limits are satisfied; unavailable/invalid checks raise."""
        raise NotImplementedError

    @abstractmethod
    def is_escape_move(self, current: List[float], target: List[float]) -> bool:
        """Whether this checker authorizes an escape; unsupported policies return False."""
        raise NotImplementedError

    @abstractmethod
    def get_violations(self, position: List[float]) -> List[str]:
        """Return violations, empty only after a successful check.

        Unavailable settings or failed validation raise. Callers must reject the
        command on exceptions, including when applying recovery exceptions.
        """
        ...
