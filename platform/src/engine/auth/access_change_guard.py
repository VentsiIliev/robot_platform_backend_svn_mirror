from contextlib import AbstractContextManager, contextmanager, nullcontext
from typing import Callable
from uuid import uuid4

from src.engine.auth.i_access_change_guard import IAccessChangeGuard, IAccessChangeLease
from src.engine.auth.i_session_service import ISessionService
from src.engine.system.i_system_manager import ISystemManager
from src.shared_contracts.authorization.actions import PermissionAction, RecoveryAction, UserAction
from src.shared_contracts.authorization.errors import ErrorCode, ServiceError, ServiceException, ServiceUnavailableError
from src.shared_contracts.authorization.results import Failure, Success


def _busy():
    return Failure(ServiceError(ErrorCode.BUSY, "account.wait_until_idle", uuid4().hex))


class _IdleLease(IAccessChangeLease):
    def validate(self):
        return Success(None)


class NoActiveOperationGuard(IAccessChangeGuard):
    """Standalone composition with no robot/process; production injects its guard."""
    @contextmanager
    def hold(self, action, target):
        yield Success(_IdleLease())


class _SessionLease(IAccessChangeLease):
    def __init__(self, session, revision):
        self._session, self._revision = session, revision

    def validate(self):
        if self._session.snapshot().revision != self._revision:
            return Failure(ServiceError(ErrorCode.CONFLICT, "access.session_changed", uuid4().hex))
        return Success(None)


class _ReservedLease(_SessionLease):
    def __init__(self, session, revision, manager, owner, block_reason):
        super().__init__(session, revision)
        self._manager, self._owner, self._block_reason = manager, owner, block_reason

    def validate(self):
        current = super().validate()
        if isinstance(current, Failure):
            return current
        if ((self._manager is not None and self._manager.active_process_id != self._owner)
                or self._block_reason() is not None):
            return _busy()
        return Success(None)


class SystemAccessChangeGuard(IAccessChangeGuard):
    def __init__(self, session: ISessionService, manager: ISystemManager | None,
                 block_reason: Callable[[], str | None],
                 idle_reservation: Callable[[], AbstractContextManager[bool]] | None = None):
        self._session, self._manager, self._block_reason = session, manager, block_reason
        self._idle_reservation = idle_reservation or self._local_reservation

    @staticmethod
    def _local_reservation():
        return nullcontext(True)

    @contextmanager
    def hold(self, action, target):
        snapshot = self._session.snapshot()
        user = snapshot.user
        affects_current = user is not None and (
            action == PermissionAction.MANAGE
            or (action in {UserAction.CHANGE_PASSWORD, UserAction.CHANGE_ROLE, UserAction.DELETE, RecoveryAction.COMPLETE}
                and target is not None and (
                    target.kind == "account" and target.resource_id == getattr(user, "account_id", None)
                ))
        )
        if not affects_current:
            yield Success(_SessionLease(self._session, snapshot.revision))
            return
        if self._reason() is not None:
            yield _busy()
            return
        owner = "account_access_change:" + uuid4().hex
        try:
            if self._manager is not None and not self._manager.acquire(owner):
                yield _busy()
                return
            with self._idle_reservation() as idle:
                if idle is not True:
                    yield _busy()
                    return
                lease = _ReservedLease(self._session, snapshot.revision, self._manager, owner, self._reason)
                readiness = lease.validate()
                yield readiness if isinstance(readiness, Failure) else Success(lease)
        finally:
            if self._manager is not None:
                self._manager.release(owner)

    def _reason(self):
        try:
            return self._block_reason()
        except ServiceException:
            raise
        except Exception as exc:
            raise ServiceUnavailableError() from exc
