"""Safe errors crossing service boundaries; never include credentials or paths."""
from dataclasses import dataclass
from enum import Enum
from uuid import uuid4


class ErrorCode(str, Enum):
    ACCESS_DENIED = "access_denied"
    INVALID_INPUT = "invalid_input"
    NOT_FOUND = "not_found"
    ALREADY_EXISTS = "already_exists"
    CONFLICT = "conflict"
    AUTHENTICATION_REQUIRED = "authentication_required"
    INVALID_PROOF = "invalid_proof"
    RATE_LIMITED = "rate_limited"
    BUSY = "busy"
    POLICY_VIOLATION = "policy_violation"
    SERVICE_UNAVAILABLE = "service_unavailable"
    STORAGE_INTEGRITY = "storage_integrity"
    AUDIT_PERSISTENCE = "audit_persistence"
    KEY_UNAVAILABLE = "key_unavailable"
    KEY_INTEGRITY = "key_integrity"
    UNSAFE_KEY_STORAGE = "unsafe_key_storage"
    KEY_MISMATCH = "key_mismatch"
    CREDENTIAL_INTEGRITY = "credential_integrity"


@dataclass(frozen=True)
class FieldError:
    field: str
    message_key: str


@dataclass(frozen=True)
class ServiceError:
    code: ErrorCode
    message_key: str
    correlation_id: str
    field_errors: tuple[FieldError, ...] = ()


class ServiceException(Exception):
    """Infrastructure failure with safe structured context and a chained cause."""

    code: ErrorCode
    message_key: str

    def __init__(self, *, correlation_id: str | None = None) -> None:
        self.error = ServiceError(
            self.code, self.message_key, correlation_id or uuid4().hex,
        )
        super().__init__(self.message_key)


class ServiceUnavailableError(ServiceException):
    code = ErrorCode.SERVICE_UNAVAILABLE
    message_key = "service.unavailable"


class AccountRuntimeInUseError(ServiceUnavailableError):
    code = ErrorCode.BUSY
    message_key = "account.runtime_in_use"


class StorageIntegrityError(ServiceException):
    code = ErrorCode.STORAGE_INTEGRITY
    message_key = "service.storage_integrity"


class AuditPersistenceError(ServiceException):
    code = ErrorCode.AUDIT_PERSISTENCE
    message_key = "service.audit_persistence"


class KeyUnavailableError(ServiceUnavailableError):
    code = ErrorCode.KEY_UNAVAILABLE
    message_key = "credential.key_unavailable"


class KeyIntegrityError(StorageIntegrityError):
    code = ErrorCode.KEY_INTEGRITY
    message_key = "credential.key_integrity"


class UnsafeKeyStorageError(StorageIntegrityError):
    code = ErrorCode.UNSAFE_KEY_STORAGE
    message_key = "credential.unsafe_key_storage"


class KeyMismatchError(StorageIntegrityError):
    code = ErrorCode.KEY_MISMATCH
    message_key = "credential.key_mismatch"


class CredentialIntegrityError(StorageIntegrityError):
    code = ErrorCode.CREDENTIAL_INTEGRITY
    message_key = "credential.integrity"
