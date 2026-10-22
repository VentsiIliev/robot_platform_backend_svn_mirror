"""Small injected action recorder; actor snapshots survive asynchronous work."""
from __future__ import annotations

import logging
from uuid import uuid4

from .events import diagnostic_context, observe

_logger = logging.getLogger(__name__)


class ActionRecorder:
    def __init__(self, session=None, *, authentication_mode='unknown'):
        self._session = session
        self._mode = authentication_mode
        self._auth_session_id = None

    def context(self):
        actor = {'user_id': None, 'role': None, 'authentication_mode': self._mode,
                 'auth_session_id': self._auth_session_id}
        if self._session is not None:
            user = self._session.current_user
            if user is not None:
                actor['user_id'] = str(user.user_id)
                role = user.role
                actor['role'] = str(getattr(role, 'value', role))
        return {'action_id': uuid4().hex, 'actor': actor}

    def session_changed(self, logged_in):
        self._auth_session_id = uuid4().hex if logged_in else None

    def operation_context(self):
        """Allocate identity before application validation or resource acquisition."""
        token = self.context()
        token['operation_id'] = uuid4().hex
        return token

    def record(self, event, *, context=None, outcome='succeeded', **fields):
        """Diagnostics never change the caller's result or original exception."""
        try:
            token = context if context is not None else self.context()
            with diagnostic_context(**token):
                level = logging.ERROR if outcome == 'failed' else logging.INFO
                observe(_logger, event, level=level, outcome=outcome, **fields)
            return token
        except Exception:
            return {}
