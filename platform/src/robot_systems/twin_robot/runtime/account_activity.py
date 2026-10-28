"""Adapt the external Twin execution contract to the account activity boundary."""
from contextlib import ExitStack, contextmanager

from src.shared_contracts.authorization.errors import ServiceException, ServiceUnavailableError

from .activity import TwinRuntimeActivity


class TwinAccountActivity:
    def __init__(self, runtime_provider):
        self._runtime_provider = runtime_provider

    def block_reason(self):
        runtime = self._runtime_provider()
        if runtime is None:
            return None
        try:
            activity = runtime.get_activity()
            if not isinstance(activity, TwinRuntimeActivity) or activity == TwinRuntimeActivity.UNKNOWN:
                raise ServiceUnavailableError()
            return None if activity == TwinRuntimeActivity.IDLE else "twin_runtime_active"
        except ServiceException:
            raise
        except Exception as exc:
            raise ServiceUnavailableError() from exc

    @contextmanager
    def hold_idle(self):
        runtime = self._runtime_provider()
        if runtime is None:
            yield True
            return
        with ExitStack() as scope:
            try:
                idle = scope.enter_context(runtime.hold_idle())
            except ServiceException:
                raise
            except Exception as exc:
                raise ServiceUnavailableError() from exc
            if not isinstance(idle, bool) or runtime is not self._runtime_provider():
                raise ServiceUnavailableError()
            # Do not translate exceptions thrown by the protected operation.
            yield idle
