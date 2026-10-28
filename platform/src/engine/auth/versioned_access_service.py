from uuid import uuid4

from src.engine.auth.access_service import AccessService
from src.engine.auth.i_access_context_provider import IAccessContextProvider
from src.engine.auth.i_access_policy_provider import IAccessPolicyProvider
from src.engine.auth.i_access_service import IAccessService
from src.shared_contracts.authorization.errors import ErrorCode, ServiceError
from src.shared_contracts.authorization.results import Failure, Success


class VersionedAccessService(IAccessService):
    """Snapshot policy per batch and reject advice racing a permission change."""
    def __init__(self, contexts: IAccessContextProvider, policies: IAccessPolicyProvider) -> None:
        self._contexts, self._policies = contexts, policies

    def evaluate(self, requests):
        policy = self._policies.capture()
        result = AccessService(self._contexts, policy).evaluate(requests)
        if isinstance(result, Success) and self._policies.capture().revision != policy.revision:
            return Failure(ServiceError(ErrorCode.CONFLICT, "access.policy_changed", uuid4().hex))
        return result
