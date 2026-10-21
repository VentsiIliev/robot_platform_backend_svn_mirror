"""Transport-independent failures raised by gateway implementations."""
from typing import Any, Literal

FailureKind = Literal['invalid_request', 'not_found', 'conflict', 'unavailable', 'timeout', 'unsupported', 'internal']


class GatewayError(RuntimeError):
    def __init__(self, code: str, message: str, *, kind: FailureKind = 'internal',
                 retryable: bool = False, details: dict[str, Any] | None = None,
                 outcome_unknown: bool = False):
        super().__init__(message)
        self.source = 'gateway'
        self.code = code
        self.kind = kind
        self.retryable = retryable
        self.details = dict(details or {})
        self.outcome_unknown = outcome_unknown
