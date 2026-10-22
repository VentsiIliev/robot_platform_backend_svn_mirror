"""Outer operation boundaries, including exits before an execution context exists."""
from dataclasses import asdict
from functools import wraps
import logging
from time import monotonic
from uuid import uuid4

from src.engine.diagnostics.actions import ActionRecorder
from src.engine.diagnostics.events import current_context, diagnostic_context, observe

_logger = logging.getLogger(__name__)


def observed_operation(name, *, cycle=False):
    def decorate(method):
        @wraps(method)
        def run(service, *args, **kwargs):
            token = current_context()
            if not token.get('operation_id'):
                token = {**ActionRecorder().operation_context(), **token}
            if cycle:
                token.update(cycle_id=uuid4().hex, cycle_index=kwargs.get('cycle_index'))
            started = monotonic()
            with diagnostic_context(**token):
                observe(_logger, name + '.requested', outcome='started')
                try:
                    result = method(service, *args, **kwargs)
                except Exception:
                    observe(_logger, name + '.request_exception', level=logging.ERROR,
                            outcome='failed', duration_s=monotonic() - started,
                            evidence=_evidence(service, token))
                    raise
                observe(_logger, name + '.request_result',
                        level=logging.ERROR if result.failure else logging.INFO,
                        outcome=result.outcome.value, message=result.message,
                        failure=asdict(result.failure) if result.failure else None,
                        duration_s=monotonic() - started, evidence=_evidence(service, token))
                return result
        return run
    return decorate


def _evidence(service, token):
    try:
        context = service._last_execution_context
        if context is not None and (
            context.diagnostic_context.get('operation_id') == token.get('operation_id')
            and (not token.get('cycle_id') or context.diagnostic_cycle_id == token['cycle_id'])
        ):
            return {'cycle_id': context.diagnostic_cycle_id, 'snapshots': context.diagnostic_evidence,
                    'images': 'not_included', 'geometry': 'not_included'}
    except Exception:
        pass
    return {'configuration': 'not_captured', 'workpiece': 'not_captured',
            'images': 'not_captured', 'geometry': 'not_captured'}
