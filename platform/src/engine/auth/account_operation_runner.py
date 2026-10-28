"""Shared trusted execution boundary for account, permission, and history services."""
from datetime import datetime, timezone
from contextlib import ExitStack
from uuid import uuid4

from src.engine.auth.account_access_context import verified_session_account
from src.engine.auth.account_store import IAccountStore
from src.engine.auth.access_change_guard import NoActiveOperationGuard
from src.engine.auth.i_access_change_guard import IAccessChangeGuard
from src.engine.auth.i_access_policy import IAccessPolicy
from src.engine.auth.i_session_service import ISessionService
from src.shared_contracts.accounts.events import AuditEvent
from src.shared_contracts.authorization.access import (
    AccessContext, AccessKind, AccessRequest, Actor, ResourceFacts,
)
from src.shared_contracts.authorization.errors import ErrorCode, ServiceError
from src.shared_contracts.authorization.results import Failure


class _AbortCommand(Exception):
    def __init__(self, failure):
        self.failure = failure


class AccountOperationRunner:
    def __init__(self, store: IAccountStore, session: ISessionService,
                 policy: IAccessPolicy, *, clock=None, activity_guard: IAccessChangeGuard | None = None) -> None:
        self._store = store
        self._session = session
        self._policy = policy
        self._activity = activity_guard or NoActiveOperationGuard()
        self.clock = clock or (lambda: datetime.now(timezone.utc).isoformat())

    def execute(self, action, reference, expected_revision, operation):
        """Authorize using current facts; commit only successful, current-session work."""
        return self._execute(action, reference, expected_revision, operation, None)

    def execute_change(self, action, reference, expected_revision, operation):
        """Additionally reserve idle execution for changes affecting the active session."""
        return self._execute(action, reference, expected_revision, operation, self._activity)

    def _execute(self, action, reference, expected_revision, operation, activity):
        snapshot = self._session.snapshot()
        try:
            with ExitStack() as scope, self._store.transaction() as transaction:
                actor = verified_session_account(transaction, snapshot)
                if actor is None:
                    return self.failure(ErrorCode.AUTHENTICATION_REQUIRED)
                target = transaction.get(reference.resource_id) if reference and reference.kind == "account" else None
                facts = (ResourceFacts(reference, target.summary.account_id, target.summary.role) if target
                         else ResourceFacts(reference, role=reference.resource_id)
                         if reference and reference.kind == "new_account_role" else None)
                decision = self._policy.decide(
                    AccessRequest(AccessKind.ACTION, action, reference),
                    AccessContext(Actor(actor.summary.account_id, actor.summary.role), snapshot.revision, facts),
                )
                if not decision.allowed:
                    self.record(transaction, actor, reference.resource_id if reference else "accounts",
                                action, outcome="denied")
                    return self.failure(ErrorCode.ACCESS_DENIED)
                if target is not None and expected_revision is not None and expected_revision != target.summary.revision:
                    return self.failure(ErrorCode.CONFLICT)
                lease = None
                if activity is not None:
                    reserved = scope.enter_context(activity.hold(action, reference))
                    if isinstance(reserved, Failure):
                        return reserved
                    lease = reserved.value
                result = operation(transaction, actor, target)
                if isinstance(result, Failure):
                    raise _AbortCommand(result)
                if self._session.snapshot().revision != snapshot.revision:
                    raise _AbortCommand(self.failure(ErrorCode.CONFLICT))
                if lease is not None:
                    ready = lease.validate()
                    if isinstance(ready, Failure):
                        raise _AbortCommand(ready)
                return result
        except _AbortCommand as exc:
            return exc.failure

    def record(self, transaction, actor, target_id, action, *, outcome="succeeded",
               changes=(), password_changed=False):
        transaction.append_event(AuditEvent(
            uuid4().hex, self.clock(), actor.summary.account_id, actor.summary.role,
            "authenticated", target_id, str(getattr(action, "value", action)), outcome,
            changes, password_changed,
        ))

    @staticmethod
    def failure(code):
        return Failure(ServiceError(code, "account." + code.value, uuid4().hex))
