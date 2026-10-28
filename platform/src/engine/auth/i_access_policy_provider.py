from abc import ABC, abstractmethod

from src.engine.auth.i_access_policy import IAccessPolicy


class IAccessPolicyProvider(ABC):
    @abstractmethod
    def capture(self) -> IAccessPolicy:
        """Return an immutable policy and revision from one consistent grant read.

        May block; infrastructure failures use shared ServiceException subclasses.
        """
