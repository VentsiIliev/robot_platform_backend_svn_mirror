"""Structured observations; no storage or hardware I/O on the caller thread."""
from __future__ import annotations

import logging
from contextlib import contextmanager
from contextvars import ContextVar
from time import monotonic

_EVENT_LOGGER = logging.getLogger("diagnostics.events")
_EVENT_LOGGER.setLevel(logging.INFO)

_CONTEXT: ContextVar[dict] = ContextVar('diagnostic_context', default={})


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


def observe(logger: logging.Logger, event: str, *, metrics: dict[str, float] | None = None,
            output: tuple[str, bool | None] | None = None, level: int = logging.INFO,
            **fields) -> None:
    """Record additive metric samples and an optional successful output transition.

    Output values describe commanded state, never physical operation. None
    means an unsuccessful write left the state unknown. Call after hardware I/O.
    """
    # Metric collection stays enabled even when operators raise console verbosity.
    _EVENT_LOGGER.log(level, event, stacklevel=2,
        extra={'diagnostic_source': logger.name, 'diagnostic_event': {
            'event': event, 'fields': fields, 'metrics': metrics or {},
            'output': output, 'monotonic': monotonic(),
        }})
