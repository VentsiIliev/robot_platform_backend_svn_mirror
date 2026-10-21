"""Shared, transport-neutral response and error contracts for all four APIs."""
from contextlib import contextmanager
from contextvars import ContextVar
from dataclasses import dataclass
from functools import wraps
import inspect
from enum import Enum
import logging
import math
from typing import Any, Callable, Generic, Literal, Mapping, NotRequired, TypeVar, TypedDict
from uuid import uuid4

from runtime_gateway.errors import GatewayError

logger = logging.getLogger(__name__)
Source = Literal['validation', 'gateway', 'runtime', 'storage', 'controller', 'transport']


class ErrorInfo(TypedDict):
    code: str
    message: str
    source: Source
    operation: str
    retryable: bool
    outcome_unknown: bool
    details: dict[str, Any]


class ResponseBody(TypedDict):
    success: bool
    request_id: str
    error: NotRequired[str]
    error_info: NotRequired[ErrorInfo]


@dataclass(frozen=True)
class OperationContext:
    request_id: str
    operation: str = ''


_context: ContextVar[OperationContext | None] = ContextVar('runtime_api_operation', default=None)


@contextmanager
def request_context(request_id: str, operation: str = ''):
    token = _context.set(OperationContext(request_id, operation))
    try:
        yield
    finally:
        _context.reset(token)


def to_jsonable(value: Any) -> Any:
    if isinstance(value, Mapping):
        return {str(key): to_jsonable(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [to_jsonable(item) for item in value]
    if hasattr(value, 'tolist'):
        return to_jsonable(value.tolist())
    if hasattr(value, 'item'):
        return to_jsonable(value.item())
    if isinstance(value, float) and not math.isfinite(value):
        raise GatewayError('invalid_runtime_response', 'Runtime response contains a non-finite number')
    if isinstance(value, Enum):
        return to_jsonable(value.value)
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    raise GatewayError('invalid_runtime_response', f'Unsupported runtime response type: {type(value).__name__}')


def error_code(status: int) -> str:
    return {400: 'invalid_request', 404: 'not_found', 409: 'runtime_conflict',
            415: 'unsupported_media_type', 422: 'invalid_request', 501: 'unsupported',
            503: 'runtime_unavailable', 504: 'gateway_timeout'}.get(status, 'runtime_failure')


Body = TypeVar('Body', bound=Mapping[str, Any])


@dataclass(frozen=True)
class ApiResponse(Generic[Body]):
    body: Body
    status: int = 200

    def __post_init__(self):
        if not 100 <= self.status <= 599:
            raise ValueError('Invalid API response status')
        body = to_jsonable(dict(self.body))
        context = _context.get() or OperationContext(uuid4().hex)
        body.setdefault('request_id', context.request_id)
        body.setdefault('success', self.status < 400 and not bool(body.get('error')))
        if self.status >= 400:
            body['success'] = False
        application_error = body.get('application_error')
        if body.get('pending_application') and application_error:
            info = body.get('application_error_info') or {}
            body['application_error_info'] = ErrorInfo(
                code=info.get('code', 'configuration_application_pending'), message=application_error,
                source=info.get('source', 'runtime'), operation=context.operation, retryable=info.get('retryable', False),
                outcome_unknown=info.get('outcome_unknown', False), details=info.get('details', {}))
        if body.get('success') is False:
            info = body.get('error_info')
            detail = body.get('detail') or body.get('application_error')
            servo = body.get('servo')
            if not detail and isinstance(servo, dict):
                detail = servo.get('error')
            message = str(detail or body.get('error') or body.get('reason') or body.get('message')
                          or f"Runtime operation failed (result={body.get('result', 'not supplied')})")
            body.setdefault('error', message)
            if not isinstance(info, dict):
                code = body.get('code')
                info = ErrorInfo(
                    code=code if isinstance(code, str) else error_code(self.status),
                    message=message, source='validation' if self.status in (400, 415, 422) else 'runtime',
                    operation=context.operation, retryable=False,
                    outcome_unknown=body.get('accepted') is True and body.get('final') is False,
                    details={key: body[key] for key in ('result', 'reason', 'state', 'task_id', 'detail',
                                                       'application_error', 'motion_stack_fault') if key in body},
                )
            body['error_info'] = info
            # Preserve the legacy string field, while reporting the actual cause in both representations.
            body['error'] = info['message']
        object.__setattr__(self, 'body', body)

    @property
    def error(self) -> ErrorInfo | None:
        return self.body.get('error_info')


def response_error(message: str, status_code: int, *, code: str | None = None,
                   source: Source | None = None, retryable: bool = False,
                   outcome_unknown: bool = False, details: dict[str, Any] | None = None,
                   **extra: Any) -> ApiResponse[ResponseBody]:
    context = _context.get() or OperationContext(uuid4().hex)
    info = ErrorInfo(code=code or error_code(status_code), message=message,
                     source=source or ('validation' if status_code in (400, 415, 422) else 'runtime'),
                     operation=context.operation, retryable=retryable, outcome_unknown=outcome_unknown,
                     details=dict(details or {}))
    return ApiResponse({'success': False, 'error': message, 'error_info': info, **extra}, status_code)


def exception_response(error: Exception) -> ApiResponse[ResponseBody]:
    if isinstance(error, GatewayError):
        status = {'invalid_request': 400, 'not_found': 404, 'conflict': 409, 'unavailable': 503,
                  'timeout': 504, 'unsupported': 501, 'internal': 500}[error.kind]
        return response_error(str(error), status, code=error.code, source='gateway',
                              retryable=error.retryable, outcome_unknown=error.outcome_unknown,
                              details=error.details)
    cause = error.__cause__
    details = {'exception_type': type(error).__name__}
    if cause is not None:
        details.update(cause_type=type(cause).__name__, cause=str(cause))
        if isinstance(cause, OSError):
            details['errno'] = cause.errno
    code = getattr(error, 'code', None)
    if code:
        status = getattr(error, 'status', 500)
        source: Source = 'storage' if code == 'configuration_unavailable' else 'validation'
    elif isinstance(error, TimeoutError):
        status, code, source = 504, 'gateway_timeout', 'gateway'
    elif isinstance(error, ConnectionError):
        status, code, source = 503, 'gateway_unavailable', 'gateway'
    elif isinstance(error, ValueError):
        status, code, source = 400, 'invalid_request', 'validation'
    else:
        status, code, source = 500, 'unexpected_runtime_error', 'runtime'
    return response_error(str(error) or type(error).__name__, status, code=code, source=source, details=details,
                          outcome_unknown=isinstance(error, TimeoutError))


def api_operation(name: str):
    """Give every entry point the same validation, correlation and exception boundary."""
    def decorate(function: Callable):
        signature = inspect.signature(function)
        @wraps(function)
        def call(*args, **kwargs):
            parent = _context.get()
            token = _context.set(OperationContext(parent.request_id if parent else uuid4().hex, name))
            try:
                bound = signature.bind(*args, **kwargs)
                data = bound.arguments.get('data')
                if data is not None and not isinstance(data, dict):
                    return response_error('Request body must be a JSON object', 400)
                response = function(*args, **kwargs)
                if not isinstance(response, ApiResponse):
                    raise TypeError(f'{name} did not return ApiResponse')
                return response
            except Exception as error:
                logger.exception('API operation failed operation=%s request_id=%s', name, _context.get().request_id)
                return exception_response(error)
            finally:
                _context.reset(token)
        return call
    return decorate
