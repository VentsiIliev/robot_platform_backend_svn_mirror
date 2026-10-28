"""Offline Admin recovery with random single-use codes and durable retry limits."""
from dataclasses import dataclass, replace
from datetime import datetime, timezone
from contextlib import ExitStack
import hashlib
import hmac
import secrets
import time
from uuid import uuid4

from src.engine.auth.account_access_context import verified_session_account
from src.engine.auth.account_store import IAccountStore, RecoveryAttempts, RecoveryVerifier, StoredAccount
from src.engine.auth.i_access_policy import IAccessPolicy
from src.engine.auth.i_credential_protector import ICredentialProtector
from src.engine.auth.i_recovery_service import IRecoveryService
from src.engine.auth.i_session_service import ISessionService
from src.engine.auth.access_change_guard import NoActiveOperationGuard
from src.engine.auth.i_access_change_guard import IAccessChangeGuard
from src.shared_contracts.accounts.events import AuditEvent
from src.shared_contracts.accounts.records import UserRole
from src.shared_contracts.accounts.recovery import GenerateRecoveryCodes, RecoverAdminAccount, RecoveryCodes
from src.shared_contracts.authorization.access import AccessContext, AccessKind, AccessRequest, Actor, ResourceRef
from src.shared_contracts.authorization.actions import RecoveryAction
from src.shared_contracts.authorization.errors import ErrorCode, ServiceError, StorageIntegrityError
from src.shared_contracts.authorization.results import Failure, Success


@dataclass(frozen=True)
class RecoveryLimits:
    codes_per_set: int = 8
    failures_per_account: int = 5
    failures_global: int = 50
    window_seconds: int = 60

    def __post_init__(self):
        if not 1 <= self.codes_per_set <= 32 or min(
            self.failures_per_account, self.failures_global, self.window_seconds,
        ) < 1:
            raise ValueError("Recovery limits must be positive and code count bounded")


class _SessionChanged(Exception):
    pass


class _ChangeRefused(Exception):
    def __init__(self, failure):
        self.failure = failure


class RecoveryService(IRecoveryService):
    def __init__(self, store: IAccountStore, session: ISessionService, policy: IAccessPolicy,
                 credentials: ICredentialProtector, *, limits=RecoveryLimits(), clock=time.time,
                 activity_guard: IAccessChangeGuard | None = None) -> None:
        self._store, self._session, self._policy = store, session, policy
        self._credentials, self._limits, self._clock = credentials, limits, clock
        self._activity = activity_guard or NoActiveOperationGuard()

    def generate_codes(self, command: GenerateRecoveryCodes):
        if not isinstance(command.current_password, str):
            return self._failure(ErrorCode.INVALID_PROOF)
        snapshot = self._session.snapshot()
        try:
            with self._store.transaction() as transaction:
                account = verified_session_account(transaction, snapshot)
                if account is None:
                    return self._failure(ErrorCode.AUTHENTICATION_REQUIRED)
                decision = self._policy.decide(
                    AccessRequest(AccessKind.ACTION, RecoveryAction.ISSUE),
                    AccessContext(Actor(account.summary.account_id, account.summary.role), snapshot.revision),
                )
                if not decision.allowed or account.summary.role != UserRole.ADMIN:
                    self._event(transaction, account.summary.account_id, RecoveryAction.ISSUE,
                                "denied", "authenticated", verified_actor=account)
                    return self._failure(ErrorCode.ACCESS_DENIED)
                key = "issue:" + account.summary.account_id
                if self._limited(transaction, key):
                    return self._failure(ErrorCode.RATE_LIMITED)
                if not self._credentials.verify_password(command.current_password, account.password_hash):
                    self._failed_attempt(transaction, key)
                    self._event(transaction, account.summary.account_id, RecoveryAction.ISSUE,
                                "failed", "password", verified_actor=account)
                    return self._failure(ErrorCode.INVALID_PROOF)
                codes = self._replace_codes(transaction, account)
                self._event(transaction, account.summary.account_id, RecoveryAction.ISSUE,
                            "succeeded", "password", verified_actor=account)
                if self._session.snapshot().revision != snapshot.revision:
                    raise _SessionChanged()
                return Success(codes)
        except _SessionChanged:
            return self._failure(ErrorCode.CONFLICT)

    def recover_admin(self, command: RecoverAdminAccount):
        try:
            return self._recover_admin(command)
        except _ChangeRefused as exc:
            return exc.failure

    def _recover_admin(self, command: RecoverAdminAccount):
        if (not isinstance(command.login_id, str) or not command.login_id
                or not isinstance(command.recovery_code, str)
                or not isinstance(command.new_password, str) or not command.new_password):
            return self._failure(ErrorCode.INVALID_PROOF)
        key = "recover:" + hashlib.sha256(command.login_id.encode()).hexdigest()
        with ExitStack() as scope, self._store.transaction() as transaction:
            if self._limited(transaction, key):
                return self._failure(ErrorCode.RATE_LIMITED)
            account = transaction.get_by_login(command.login_id)
            installation = self._installation(transaction)
            normalized = self._normalize(command.recovery_code)
            account_id = account.summary.account_id if account else "unknown"
            digest = self._digest(installation, account_id, normalized)
            verifiers = transaction.recovery_verifiers(account_id) if account else ()
            if len(verifiers) > 32:
                raise StorageIntegrityError()
            verifiers += (RecoveryVerifier(-1, "0" * 64),) * (32 - len(verifiers))
            matched = False
            for verifier in verifiers:
                equal = hmac.compare_digest(verifier.digest, digest)
                matched |= equal and account is not None and verifier.credential_version == account.credential_version
            valid = (bool(normalized) and matched and account is not None
                     and account.summary.enabled and account.summary.role == UserRole.ADMIN)
            if not valid:
                self._failed_attempt(transaction, key)
                self._event(transaction, account_id, RecoveryAction.COMPLETE, "failed", "recovery_code")
                return self._failure(ErrorCode.INVALID_PROOF)
            reserved = scope.enter_context(self._activity.hold(
                RecoveryAction.COMPLETE, ResourceRef("account", account_id)))
            if isinstance(reserved, Failure):
                return reserved
            summary = replace(account.summary, revision=account.summary.revision + 1,
                              updated_at=self._now(), updated_by=account_id)
            changed = StoredAccount(summary, account.credential_version + 1,
                                    self._credentials.hash_password(command.new_password))
            transaction.replace(changed)
            codes = self._replace_codes(transaction, changed)
            transaction.set_recovery_attempts(key, RecoveryAttempts(0, self._clock()))
            self._event(transaction, account_id, RecoveryAction.COMPLETE, "succeeded", "recovery_code",
                        password_changed=True)
            ready = reserved.value.validate()
            if isinstance(ready, Failure):
                raise _ChangeRefused(ready)
            return Success(codes)

    def _replace_codes(self, transaction, account):
        installation = self._installation(transaction)
        codes = []
        for _ in range(self._limits.codes_per_set):
            raw = secrets.token_hex(16).upper()
            codes.append("-".join(raw[index:index + 4] for index in range(0, len(raw), 4)))
        verifiers = tuple(RecoveryVerifier(account.credential_version,
                                          self._digest(installation, account.summary.account_id, self._normalize(code)))
                          for code in codes)
        transaction.replace_recovery_verifiers(account.summary.account_id, verifiers)
        return RecoveryCodes(account.summary.account_id, tuple(codes))

    def _limited(self, transaction, key):
        cutoff = self._clock() - self._limits.window_seconds
        transaction.prune_recovery_attempts(cutoff)
        account = transaction.recovery_attempts(key)
        total = transaction.recovery_attempts("global")
        return ((account is not None and account.failures >= self._limits.failures_per_account)
                or (total is not None and total.failures >= self._limits.failures_global))

    def _failed_attempt(self, transaction, key):
        now = self._clock()
        for identifier in (key, "global"):
            previous = transaction.recovery_attempts(identifier)
            transaction.set_recovery_attempts(identifier, RecoveryAttempts(
                previous.failures + 1 if previous else 1, previous.window_started if previous else now,
            ))

    def _event(self, transaction, identity, action, outcome, method, *, password_changed=False,
               verified_actor=None):
        actor_id = verified_actor.summary.account_id if verified_actor else identity if outcome == "succeeded" else None
        actor_role = verified_actor.summary.role if verified_actor else UserRole.ADMIN.value if outcome == "succeeded" else None
        transaction.append_event(AuditEvent(
            uuid4().hex, self._now(), actor_id, actor_role, method,
            identity, action.value, outcome, password_changed=password_changed,
        ))

    def _now(self):
        return datetime.fromtimestamp(self._clock(), timezone.utc).isoformat()

    @staticmethod
    def _normalize(code):
        normalized = "".join(code.split()).replace("-", "").upper()
        return normalized if len(normalized) == 32 and all(c in "0123456789ABCDEF" for c in normalized) else ""

    @staticmethod
    def _digest(installation, identity, code):
        return hashlib.sha256((installation + "\0" + identity + "\0" + code).encode()).hexdigest()

    @staticmethod
    def _installation(transaction):
        identity = transaction.metadata("installation_id")
        if not identity:
            raise StorageIntegrityError()
        return identity

    @staticmethod
    def _failure(code):
        return Failure(ServiceError(code, "account." + code.value, uuid4().hex))
