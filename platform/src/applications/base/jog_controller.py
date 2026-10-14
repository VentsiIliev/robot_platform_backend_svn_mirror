import logging
import threading
from functools import partial
from typing import Any

from PyQt6.QtCore import QObject, QRunnable, QThreadPool, QTimer, pyqtSignal, pyqtSlot

from src.applications.base.robot_jog_service import RobotJogService
from src.engine.core.i_messaging_service import IMessagingService
from src.shared_contracts.events.robot_events import RobotTopics

_logger = logging.getLogger(__name__)


def _coerce_joint_degrees(value: Any) -> list[float]:
    if isinstance(value, dict):
        value = value.get("degrees", value.get("positions", value.get("radians")))
    if isinstance(value, str) or not isinstance(value, (list, tuple)):
        return []
    if len(value) < 6:
        return []
    try:
        return [float(v) for v in value[:6]]
    except (TypeError, ValueError):
        return []


class _Bridge(QObject):
    frame_options_received = pyqtSignal(object, str)
    recovery_mode_result = pyqtSignal(bool)

    def __init__(self, view, apply_frame_options):
        super().__init__()
        self._view = view
        self._apply_frame_options = apply_frame_options
        self._lock = threading.Lock()
        self._latest_position: list = []
        self._latest_joints: list = []
        self._position_dirty = False
        self._joints_dirty = False
        self._position_timer = QTimer(self)
        self._position_timer.setInterval(100)
        self._position_timer.timeout.connect(self.flush_position)
        self._position_timer.start()
        self.frame_options_received.connect(self.handle_frame_options)
        self.recovery_mode_result.connect(self.handle_recovery_mode_result)
        self._destroy_slot_connected = True
        view.destroyed.connect(self.handle_view_destroyed)

    def ingest_position(self, pos: list) -> None:
        with self._lock:
            self._latest_position = list(pos or [])
            self._position_dirty = True

    def ingest_joints(self, joints: list) -> None:
        joints = _coerce_joint_degrees(joints)
        with self._lock:
            self._latest_joints = joints
            self._joints_dirty = True

    @pyqtSlot()
    def flush_position(self) -> None:
        if self._view is None:
            return
        with self._lock:
            if not self._position_dirty and not self._joints_dirty:
                return
            position = list(self._latest_position)
            position_dirty = self._position_dirty
            joints = list(self._latest_joints)
            joints_dirty = self._joints_dirty
            self._position_dirty = False
            self._joints_dirty = False
        if position_dirty:
            self._view.set_jog_position(position)
        if joints_dirty and hasattr(self._view, "set_joint_position"):
            self._view.set_joint_position(joints)

    @pyqtSlot(object, str)
    def handle_frame_options(self, names_obj, default: str) -> None:
        if self._view is None:
            return
        self._apply_frame_options(names_obj, default)

    @pyqtSlot(bool)
    def handle_recovery_mode_result(self, enabled: bool) -> None:
        if self._view is not None and hasattr(self._view, "set_recovery_mode_checked"):
            self._view.set_recovery_mode_checked(enabled)

    @pyqtSlot()
    def handle_view_destroyed(self) -> None:
        self.stop()

    def stop(self) -> None:
        self._position_timer.stop()
        try:
            self.frame_options_received.disconnect(self.handle_frame_options)
        except (RuntimeError, TypeError):
            pass
        if self._view is not None and self._destroy_slot_connected:
            try:
                self._view.destroyed.disconnect(self.handle_view_destroyed)
            except (RuntimeError, TypeError):
                pass
            self._destroy_slot_connected = False
        self._view = None


class _FireAndForget(QRunnable):
    def __init__(self, fn):
        super().__init__()
        self._fn = fn
        self.setAutoDelete(True)

    def run(self):
        try:
            self._fn()
        except Exception:
            pass


class JogController:
    """Reusable controller fragment — wires a jog-capable view to robot jog + live position display.

    The host view must expose:
        - jog_requested  pyqtSignal(str, str, str, float)   # command, axis, direction, step
        - jog_stopped    pyqtSignal(str)                     # key
        - set_jog_position(pos: list) -> None

    Usage inside a host application controller::

        class MyController(IApplicationController):
            def __init__(self, model, view, messaging, jog_service):
                ...
                self._jog = JogController(view, jog_service, messaging)

            def load(self):
                ...
                self._jog.start()

            def stop(self):
                self._jog.stop()
                ...
    """

    def __init__(self, view, jog_service: RobotJogService, messaging: IMessagingService):
        self._view      = view
        self._service   = jog_service
        self._messaging = messaging
        # Cartesian jog commands must retain submission order. In particular, a
        # quick servo press/release must never let the stop run before the start.
        self._operation_lock = threading.Lock()
        self._pending_operations = 0
        self._servo_held = False
        self._stopped = False
        self._jog_pool = QThreadPool()
        self._jog_pool.setMaxThreadCount(1)
        self._bridge    = _Bridge(view, self._apply_frame_options)
        self._subs      = []
        view.jog_requested.connect(self._on_jog)
        view.jog_stopped.connect(self._on_jog_stop)
        if hasattr(view, "joint_jog_requested"):
            view.joint_jog_requested.connect(self._on_joint_jog)
        if hasattr(view, "recovery_mode_changed"):
            view.recovery_mode_changed.connect(self._on_recovery_mode_changed)

    def start(self) -> None:
        if bool(getattr(self._view, "JOG_LIVE_POSITION_ENABLED", True)):
            cb = self._on_position
            self._messaging.subscribe(RobotTopics.POSITION, cb)
            self._subs.append((RobotTopics.POSITION, cb))
            state_cb = self._on_state
            self._messaging.subscribe(RobotTopics.STATE, state_cb)
            self._subs.append((RobotTopics.STATE, state_cb))
        targeting_cb = self._on_targeting_definitions_changed
        self._messaging.subscribe(RobotTopics.TARGETING_DEFINITIONS_CHANGED, targeting_cb)
        self._subs.append((RobotTopics.TARGETING_DEFINITIONS_CHANGED, targeting_cb))
        self._refresh_frame_options()

    def has_active_operations(self) -> bool:
        with self._operation_lock:
            return self._pending_operations > 0 or self._servo_held

    def _submit_operation(self, pool: QThreadPool, fn) -> None:
        with self._operation_lock:
            self._pending_operations += 1

        def run() -> None:
            try:
                fn()
            finally:
                with self._operation_lock:
                    self._pending_operations -= 1

        pool.start(_FireAndForget(run))

    def stop(self) -> None:
        if self._stopped:
            return
        self._stopped = True
        for topic, cb in self._subs:
            self._messaging.unsubscribe(topic, cb)
        self._subs.clear()
        try:
            self._view.jog_requested.disconnect(self._on_jog)
        except (RuntimeError, TypeError):
            pass
        try:
            self._view.jog_stopped.disconnect(self._on_jog_stop)
        except (RuntimeError, TypeError):
            pass
        if hasattr(self._view, "joint_jog_requested"):
            try:
                self._view.joint_jog_requested.disconnect(self._on_joint_jog)
            except (RuntimeError, TypeError):
                pass
        if hasattr(self._view, "recovery_mode_changed"):
            try:
                self._view.recovery_mode_changed.disconnect(self._on_recovery_mode_changed)
            except (RuntimeError, TypeError):
                pass
        setter = getattr(self._service, "set_recovery_mode", None)
        if callable(setter):
            # This is queued after all earlier jog/recovery operations, so a
            # screen change cannot leave collision detection suppressed.
            self._submit_operation(self._jog_pool, lambda: setter(False))
        self._bridge.stop()
        self._bridge.deleteLater()

    def _on_recovery_mode_changed(self, enabled: bool) -> None:
        setter = getattr(self._service, "set_recovery_mode", None)
        if callable(setter):
            requested = bool(enabled)

            def apply_recovery_mode() -> None:
                success = bool(setter(requested))
                if not self._stopped:
                    self._bridge.recovery_mode_result.emit(
                        requested if success else self._service.recovery_mode_enabled()
                    )

            self._submit_operation(self._jog_pool, apply_recovery_mode)

    def _on_position(self, pos: list) -> None:
        self._bridge.ingest_position(pos if pos else [])

    def _on_state(self, snapshot) -> None:
        if isinstance(snapshot, dict):
            extra = snapshot.get("extra", snapshot)
        else:
            extra = getattr(snapshot, "extra", None)
        if not isinstance(extra, dict):
            return
        joints = extra.get("joints")
        degrees = _coerce_joint_degrees(joints)
        if degrees:
            self._bridge.ingest_joints(degrees)

    def _on_targeting_definitions_changed(self, _payload=None) -> None:
        return

    def _refresh_frame_options(self) -> None:
        self._bridge.frame_options_received.emit([], "")

    def _apply_frame_options(self, names_obj, default: str) -> None:
        set_options = getattr(self._view, "set_jog_frame_options", None)
        if not callable(set_options):
            return
        set_options([], default="")

    def _on_jog(self, command: str, axis: str, direction: str, step: float) -> None:
        fn = partial(self._service.jog, command, axis, direction, step)
        if command == "SERVO_JOG":
            with self._operation_lock:
                self._servo_held = True
            self._submit_operation(self._jog_pool, fn)
            return
        self._submit_operation(QThreadPool.globalInstance(), fn)

    def _on_joint_jog(self, command: str, joint: str, direction: str, step: float) -> None:
        self._submit_operation(
            QThreadPool.globalInstance(),
            partial(self._service.joint_jog, command, joint, direction, step),
        )

    def _on_jog_stop(self, _key: str) -> None:
        _logger.debug("jog stop: %s", _key)
        self._submit_operation(self._jog_pool, self._service.stop_jog)
        with self._operation_lock:
            self._servo_held = False
