"""Session-aware evaluation service; query results never replace execution checks."""
from uuid import uuid4

from src.engine.auth.i_access_context_provider import IAccessContextProvider
from src.engine.auth.i_access_policy import IAccessPolicy
from src.engine.auth.i_access_service import IAccessService
from src.shared_contracts.authorization.access import (
    AccessKind, AccessRequest, AccessSnapshot, ResourceRef,
)
from src.shared_contracts.authorization.errors import ErrorCode, ServiceError
from src.shared_contracts.authorization.results import Failure, Result, Success


class AccessService(IAccessService):
    def __init__(self, context_provider: IAccessContextProvider, policy: IAccessPolicy) -> None:
        self._contexts = context_provider
        self._policy = policy

    def evaluate(self, requests: tuple[AccessRequest, ...]) -> Result[AccessSnapshot]:
        if not isinstance(requests, tuple) or any(not self._valid(r) for r in requests):
            return self._failure(ErrorCode.INVALID_INPUT, "access.invalid_request")
        initial = self._contexts.capture()
        decisions = []
        for request in requests:
            context = self._contexts.capture(request.target) if request.target else initial
            if (context.session_revision, context.actor) != (
                initial.session_revision, initial.actor,
            ):
                return self._failure(ErrorCode.CONFLICT, "access.session_changed")
            decisions.append(self._policy.decide(request, context))
        final = self._contexts.capture()
        if (final.session_revision, final.actor) != (initial.session_revision, initial.actor):
            return self._failure(ErrorCode.CONFLICT, "access.session_changed")
        return Success(AccessSnapshot(
            initial.session_revision, self._policy.revision, requests, tuple(decisions),
        ))

    @staticmethod
    def _valid(request: AccessRequest) -> bool:
        return (
            isinstance(request, AccessRequest)
            and isinstance(request.kind, AccessKind)
            and isinstance(request.key, str) and bool(request.key)
            and (request.target is None or (
                isinstance(request.target, ResourceRef)
                and isinstance(request.target.kind, str) and bool(request.target.kind)
                and isinstance(request.target.resource_id, str) and bool(request.target.resource_id)
            ))
        )

    @staticmethod
    def _failure(code: ErrorCode, message_key: str) -> Failure:
        return Failure(ServiceError(code, message_key, uuid4().hex))
