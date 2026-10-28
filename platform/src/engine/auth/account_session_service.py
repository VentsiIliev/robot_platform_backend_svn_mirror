from uuid import uuid4

from src.engine.auth.i_account_session_service import IAccountSessionService
from src.engine.auth.i_access_context_provider import IAccessContextProvider
from src.engine.auth.i_session_service import ISessionService
from src.shared_contracts.accounts.sessions import AccountSessionStatus
from src.shared_contracts.authorization.errors import ErrorCode, ServiceError
from src.shared_contracts.authorization.results import Failure, Result, Success


class AccountSessionService(IAccountSessionService):
    def __init__(self, contexts: IAccessContextProvider, session: ISessionService):
        self._contexts, self._session = contexts, session

    def status(self) -> Result[AccountSessionStatus]:
        snapshot = self._session.snapshot()
        context = self._contexts.capture()
        if snapshot.revision != context.session_revision or self._session.snapshot().revision != snapshot.revision:
            return Failure(ServiceError(ErrorCode.CONFLICT, "access.session_changed", uuid4().hex))
        valid = context.actor is not None and context.actor.role == getattr(getattr(snapshot.user, "role", None), "value", None)
        return Success(AccountSessionStatus(snapshot.revision, valid))
