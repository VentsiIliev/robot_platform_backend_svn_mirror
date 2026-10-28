"""Asynchronous shell authorization for cached and lazily created applications."""
from dataclasses import dataclass
from functools import partial

from PyQt6.QtCore import QTimer

from src.applications.base.background_worker import BackgroundWorker
from src.shared_contracts.authorization.results import Success


@dataclass(frozen=True)
class _NavigationState:
    session_revision: int
    valid: bool
    visible: tuple


class ShellAccountAccess(BackgroundWorker):
    def __init__(self, *, shell, session, runtime, navigation, specifications,
                 replace_navigation, expire_session, read_operation_idle, development_mode=False):
        super().__init__()
        self._shell, self._session, self._runtime = shell, session, runtime
        self._navigation = navigation
        self._specs = tuple(specifications)
        self._by_name = {spec.name: spec for spec in self._specs}
        self._replace_navigation, self._expire_session = replace_navigation, expire_session
        self._read_operation_idle = read_operation_idle
        self._development_mode = development_mode
        self._visible = ()
        self._visible_revision = None
        self._ticket = self._factory_ticket = None
        self._query_busy = self._opening = self._stopped = False
        self._pending_expiry = None
        self._checking_expiry = False
        self._timer = QTimer(shell)
        self._timer.setInterval(1000)
        self._timer.timeout.connect(self.refresh)
        self._expiry_timer = QTimer(shell)
        self._expiry_timer.setInterval(100)
        self._expiry_timer.timeout.connect(self._retry_expiry)

    def start(self):
        self._shell.set_application_access_guard(self.can_open)
        self._timer.start()

    def stop(self):
        self._stopped = True
        self._timer.stop()
        self._expiry_timer.stop()
        self._ticket = self._factory_ticket = None
        self._shell.set_application_access_guard(self._deny)
        self._stop_threads()

    @staticmethod
    def _deny(_name):
        return False

    def can_open(self, name):
        """Nonblocking gate. A service grant is consumed on the subsequent opening."""
        snapshot = self._session.snapshot()
        revision = snapshot.revision
        if self._stopped or not self._session.is_authenticated():
            return False
        if self._pending_expiry is not None:
            return False
        if self._ticket == (name, revision):
            self._ticket = None
            return True
        if (self._opening or name not in self._by_name or name not in {spec.name for spec in self._visible}
                or revision != self._visible_revision):
            return False
        self._opening = True
        user = snapshot.user
        self._run_in_thread(partial(self._navigation.can_access, user, self._by_name[name].app_id),
                            partial(self._opening_authorized, name, revision), self._opening_failed)
        return False

    def _opening_authorized(self, name, revision, allowed):
        self._opening = False
        if self._stopped or revision != self._session.snapshot().revision or not allowed:
            return
        self._ticket = self._factory_ticket = (name, revision)
        try:
            self._shell.show_app(name)
        finally:
            self._ticket = self._factory_ticket = None

    def _opening_failed(self, _unsafe_message):
        self._opening = False

    def guard_factory(self, factory):
        """Prevent calls around show_app from creating a protected widget directly."""
        return partial(self._create_widget, factory)

    def _create_widget(self, factory, name):
        if self._factory_ticket != (name, self._session.snapshot().revision):
            raise PermissionError("Application opening requires a fresh authorization grant")
        self._factory_ticket = None
        return factory(name)

    def refresh(self):
        if self._stopped or self._query_busy or not self._session.is_authenticated():
            return
        self._query_busy = True
        snapshot = self._session.snapshot()
        self._run_in_thread(partial(self._read_navigation, snapshot), self._navigation_loaded,
                            partial(self._navigation_failed, snapshot.revision))

    def _read_navigation(self, snapshot):
        valid = snapshot.user is not None
        if valid and not self._development_mode:
            status = self._runtime.sessions.status()
            valid = (isinstance(status, Success) and status.value.authenticated
                     and status.value.session_revision == snapshot.revision)
        specs = tuple(self._navigation.get_visible_apps(snapshot.user, self._specs)) if valid else ()
        return _NavigationState(snapshot.revision, valid, specs)

    def _navigation_loaded(self, result):
        if self._stopped:
            return
        self._query_busy = False
        if result.session_revision != self._session.snapshot().revision:
            return
        if not result.valid:
            self._request_expiry()
            return
        names = {spec.name for spec in result.visible}
        running = set(getattr(self._shell, "running_widgets", {}))
        if self._shell.current_running_app:
            running.add(self._shell.current_running_app)
        if running - names:
            self._request_expiry()
            return
        if self._visible != result.visible or self._visible_revision != result.session_revision:
            self._visible, self._visible_revision = result.visible, result.session_revision
            self._replace_navigation(result.visible)

    def _navigation_failed(self, revision, _unsafe_message):
        if not self._stopped:
            self._query_busy = False
            if revision == self._session.snapshot().revision:
                self._request_expiry()

    def _request_expiry(self):
        self._pending_expiry = self._session.snapshot().revision
        self._retry_expiry()

    def _retry_expiry(self):
        if self._stopped or self._checking_expiry:
            return
        if self._pending_expiry != self._session.snapshot().revision:
            self._expiry_timer.stop()
            self._pending_expiry = None
            return
        self._checking_expiry = True
        revision = self._pending_expiry
        self._run_in_thread(self._read_operation_idle, partial(self._idle_checked, revision), self._idle_failed)

    def _idle_checked(self, revision, idle):
        self._checking_expiry = False
        if self._stopped or revision != self._session.snapshot().revision:
            return
        if not idle:
            self._expiry_timer.start()
            return
        try:
            finished = self._expire_session()
        finally:
            self._checking_expiry = False
        if finished:
            self._expiry_timer.stop()
            self._pending_expiry = None
        else:
            self._expiry_timer.start()

    def _idle_failed(self, _unsafe_message):
        self._checking_expiry = False
        if not self._stopped:
            self._expiry_timer.start()
