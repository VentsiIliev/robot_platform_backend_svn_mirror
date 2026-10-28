"""Typed account authentication; the caller owns session creation after success."""
from datetime import datetime, timezone
import secrets
import hashlib
from uuid import uuid4

from src.engine.auth.account_store import IAccountStore
from src.engine.auth.authentication_throttle import AuthenticationThrottle
from src.engine.auth.i_account_login_service import IAccountLoginService
from src.engine.auth.i_credential_protector import ICredentialProtector
from src.shared_contracts.accounts.authentication import AccountIdentity, LoginCredentials
from src.shared_contracts.accounts.events import AuditEvent
from src.shared_contracts.accounts.records import UserRole
from src.shared_contracts.authorization.errors import ErrorCode, ServiceError
from src.shared_contracts.authorization.results import Failure, Result, Success


class AccountLoginService(IAccountLoginService):
    def __init__(self, store: IAccountStore, credentials: ICredentialProtector,
                 *, throttle: AuthenticationThrottle | None = None) -> None:
        self._store = store
        self._credentials = credentials
        self._throttle = throttle or AuthenticationThrottle()
        self._dummy_hash = credentials.hash_password(secrets.token_urlsafe(32))

    def login(self, credentials: LoginCredentials) -> Result[AccountIdentity]:
        if (not isinstance(credentials.login_id, str) or not credentials.login_id
                or not isinstance(credentials.password, str) or not credentials.password):
            return self._invalid_proof()
        with self._store.transaction() as transaction:
            key = "password:" + hashlib.sha256(credentials.login_id.encode()).hexdigest()
            if self._throttle.limited(transaction, key):
                return Failure(ServiceError(ErrorCode.RATE_LIMITED, "account.rate_limited", uuid4().hex))
            account = transaction.get_by_login(credentials.login_id)
            verified = self._credentials.verify_password(
                credentials.password, account.password_hash if account else self._dummy_hash,
            )
            valid = (verified and account is not None and account.summary.enabled
                     and account.summary.role in {role.value for role in UserRole})
            transaction.append_event(AuditEvent(
                uuid4().hex, datetime.now(timezone.utc).isoformat(),
                account.summary.account_id if valid else None,
                account.summary.role if valid else None, "password",
                account.summary.account_id if account else "authentication",
                "users.login", "succeeded" if valid else "failed",
            ))
            if not valid:
                self._throttle.failed(transaction, key)
                return self._invalid_proof()
            self._throttle.succeeded(transaction, key)
            return Success(AccountIdentity(account.summary, account.credential_version))

    @staticmethod
    def _invalid_proof() -> Failure:
        return Failure(ServiceError(ErrorCode.INVALID_PROOF, "account.invalid_proof", uuid4().hex))
