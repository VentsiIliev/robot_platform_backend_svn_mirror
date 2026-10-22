"""Structured observations; no storage or hardware I/O on the caller thread."""
from __future__ import annotations

import logging
import sys
import threading
from contextlib import contextmanager
from contextvars import ContextVar
from time import monotonic

_EVENT_LOGGER = logging.getLogger("diagnostics.events")
_EVENT_LOGGER.setLevel(logging.INFO)

_CONTEXT: ContextVar[dict] = ContextVar('diagnostic_context', default={})
_RECORDER_LOCK = threading.Lock()
_recorders: tuple = ()


def _register_recorder(recorder) -> None:
    """Explicit runtime lifecycle binding for the legacy observe() facade."""
    global _recorders
    with _RECORDER_LOCK:
        _recorders = (*_recorders, recorder)


def _unregister_recorder(recorder) -> None:
    global _recorders
    with _RECORDER_LOCK:
        _recorders = tuple(item for item in _recorders if item is not recorder)


@contextmanager
def diagnostic_context(**fields):
    """Scope correlation fields to this execution, including ordinary logs."""
    token = _CONTEXT.set({**_CONTEXT.get(), **fields})
    try:
        yield
    finally:
        _CONTEXT.reset(token)


def current_context() -> dict:
    return dict(_CONTEXT.get())


def is_recording() -> bool:
    """Cheap hint for optional snapshot work, not an admission/durability receipt."""
    return any(recorder.accepting_observations for recorder in _recorders)


def observe(logger: logging.Logger, event: str, *, metrics: dict[str, float] | None = None,
            output: tuple[str, bool | None] | None = None, level: int = logging.INFO,
            **fields) -> None:
    """Record additive metric samples and an optional successful output transition.

    Output values describe commanded state, never physical operation. None
    means an unsuccessful write left the state unknown. Call after hardware I/O.
    """
    # Recording never traverses synchronous logging/console handlers. Runtimes
    # bind explicitly at start and unbind at close; producers never discover one.
    for recorder in _recorders:
        try:
            recorder.record_observation(
                logger.name, event, level=level, fields=fields,
                metrics={} if metrics is None else metrics, output=output,
                observed_at=monotonic(), context=current_context(),
                exc_info=sys.exc_info() if level >= logging.ERROR else None,
            )
        except Exception:
            # Instrumentation must not replace an original hardware result/error.
            try:
                recorder.reject_observation('adapter_failure')
            except Exception:
                pass
