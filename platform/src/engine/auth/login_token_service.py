from datetime import datetime, timezone
import hashlib
import secrets
from uuid import uuid4

from src.engine.auth.account_operation_runner import AccountOperationRunner
from src.engine.auth.account_store import IAccountStore
from src.engine.auth.authentication_throttle import AuthenticationThrottle
from src.engine.auth.i_access_policy import IAccessPolicy
from src.engine.auth.i_login_token_service import ILoginTokenService
from src.engine.auth.i_session_service import ISessionService
from src.shared_contracts.accounts.authentication import AccountIdentity
from src.shared_contracts.accounts.events import AuditEvent
from src.shared_contracts.accounts.login_tokens import IssueLoginToken, IssuedLoginToken
from src.shared_contracts.accounts.records import UserRole
from src.shared_contracts.authorization.access import ResourceRef
from src.shared_contracts.authorization.actions import UserAction
from src.shared_contracts.authorization.errors import ErrorCode, ServiceError
from src.shared_contracts.authorization.results import Failure, Result, Success


class LoginTokenService(ILoginTokenService):
    _PREFIX = "robot-login-v1:"

    def __init__(self, store: IAccountStore, session: ISessionService, policy: IAccessPolicy,
                 *, throttle: AuthenticationThrottle | None = None) -> None:
        self._store = store
        self._operations = AccountOperationRunner(store, session, policy)
        self._throttle = throttle or AuthenticationThrottle()

    def issue(self, command: IssueLoginToken) -> Result[IssuedLoginToken]:
        if (not command.account_id or type(command.expected_revision) is not int or command.expected_revision < 1):
            return self._failure(ErrorCode.INVALID_INPUT)
        def issue(transaction, actor, target):
            if not target.summary.enabled:
                return self._failure(ErrorCode.POLICY_VIOLATION)
            payload = self._PREFIX + secrets.token_urlsafe(32)
            transaction.replace_login_token(target.summary.account_id, hashlib.sha256(payload.encode()).hexdigest(),
                                            target.credential_version)
            self._operations.record(transaction, actor, target.summary.account_id, UserAction.ISSUE_LOGIN_TOKEN)
            return Success(IssuedLoginToken(target.summary.account_id, payload))
        return self._operations.execute(UserAction.ISSUE_LOGIN_TOKEN, ResourceRef("account", command.account_id),
                                         command.expected_revision, issue)

    def authenticate(self, payload: str) -> Result[AccountIdentity]:
        if not isinstance(payload, str) or not payload.startswith(self._PREFIX) or len(payload) != len(self._PREFIX) + 43:
            return self._failure(ErrorCode.INVALID_PROOF)
        digest = hashlib.sha256(payload.encode()).hexdigest()
        with self._store.transaction() as transaction:
            key = "token:" + digest
            if self._throttle.limited(transaction, key):
                return self._failure(ErrorCode.RATE_LIMITED)
            account = transaction.account_for_login_token(digest)
            valid = account is not None and account.summary.enabled and account.summary.role in {r.value for r in UserRole}
            transaction.append_event(AuditEvent(
                uuid4().hex, datetime.now(timezone.utc).isoformat(),
                account.summary.account_id if valid else None, account.summary.role if valid else None,
                "login_token", account.summary.account_id if valid else "authentication",
                "users.login", "succeeded" if valid else "failed",
            ))
            if not valid:
                self._throttle.failed(transaction, key)
                return self._failure(ErrorCode.INVALID_PROOF)
            self._throttle.succeeded(transaction, key)
            return Success(AccountIdentity(account.summary, account.credential_version))

    @staticmethod
    def _failure(code: ErrorCode) -> Failure:
        return Failure(ServiceError(code, "account." + code.value, uuid4().hex))
