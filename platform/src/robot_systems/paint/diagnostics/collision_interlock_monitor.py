from __future__ import annotations

import logging
import threading
import time

from src.shared_contracts.events.notification_events import (
    DismissNotificationEvent,
    NotificationAction,
    NotificationActionEvent,
    NotificationSeverity,
    NotificationTopics,
    UserNotificationEvent,
)


class PaintCollisionInterlockMonitor:
    """System-lifetime collision notification and acknowledgement coordinator."""

    SOURCE = "paint_collision_interlock"
    ACTION_KEEP_HELD = "keep_collision_held"
    ACTION_RELEASE = "release_collision_hold"
    PROGRESS_KEY = "paint-collision-recovery-progress"
    def __init__(
        self,
        robot_service,
        messaging,
        *,
        vacuum_pump=None,
        acknowledge_collision=None,
        poll_period_s: float = 0.05,
    ) -> None:
        self._robot = robot_service
        self._messaging = messaging
        self._vacuum_pump = vacuum_pump
        self._acknowledge_collision = acknowledge_collision
        self._poll_period_s = max(0.05, float(poll_period_s))
        self._stop_event = threading.Event()
        self._thread: threading.Thread | None = None
        self._last_event_key: str | None = None
        self._last_publish_monotonic = 0.0
        self._active_notice_key: str | None = None
        self._vacuum_off_event_key: str | None = None
        self._last_vacuum_attempt_monotonic = 0.0
        self._release_in_progress = threading.Event()
        self._logger = logging.getLogger(self.__class__.__name__)

    def start(self) -> None:
        if self._thread is not None and self._thread.is_alive():
            return
        self._stop_event.clear()
        self._messaging.subscribe(NotificationTopics.ACTION, self._on_notification_action)
        self._thread = threading.Thread(
            target=self._run,
            daemon=True,
            name="PaintCollisionInterlockMonitor",
        )
        self._thread.start()

    def stop(self) -> None:
        self._stop_event.set()
        self._messaging.unsubscribe(NotificationTopics.ACTION, self._on_notification_action)
        thread = self._thread
        if thread is not None and thread is not threading.current_thread():
            thread.join(timeout=1.0)
        self._thread = None

    def _run(self) -> None:
        while not self._stop_event.wait(self._poll_period_s):
            self._poll_once()

    def _poll_once(self) -> None:
        try:
            status = self._robot.get_execution_status()
        except Exception:
            self._logger.debug("Collision interlock status unavailable", exc_info=True)
            return
        if not isinstance(status, dict):
            return
        # The worker owns the progress popup through backend AND local process reset.
        if self._release_in_progress.is_set():
            return
        interlock = status.get("motion_interlock")
        active = isinstance(interlock, dict) and bool(interlock.get("active", False))
        if not active:
            self._last_event_key = None
            self._last_publish_monotonic = 0.0
            self._vacuum_off_event_key = None
            self._last_vacuum_attempt_monotonic = 0.0
            self._dismiss_active_notice()
            return
        collision = status.get("collision_event")
        timestamp = collision.get("timestamp") if isinstance(collision, dict) else None
        reason = str(
            (interlock or {}).get("reason")
            or (collision or {}).get("detail")
            or "The robot collision interlock is active."
        )
        event_key = f"{timestamp!r}:{reason}"
        now = time.monotonic()
        self._turn_vacuum_off_for_collision(event_key, now)
        if self._release_in_progress.is_set():
            return
        # One actionable notice per backend collision event. Reopening the
        # same modal every few seconds prevents the operator from reaching
        # diagnostics/settings while motion remains safely interlocked.
        if event_key == self._last_event_key:
            return
        self._last_event_key = event_key
        self._last_publish_monotonic = now
        self._publish_collision_notice(reason, event_key)

    def _turn_vacuum_off_for_collision(self, event_key: str, now: float) -> None:
        pump = self._vacuum_pump
        if pump is None or self._vacuum_off_event_key == event_key:
            return
        if now - self._last_vacuum_attempt_monotonic < 0.5:
            return
        self._last_vacuum_attempt_monotonic = now
        turn_off = getattr(pump, "turn_off_nonblocking", None)
        if not callable(turn_off):
            turn_off = getattr(pump, "turn_off", None)
        if not callable(turn_off):
            self._logger.error("Collision detected but vacuum pump has no OFF command")
            return
        try:
            success = bool(turn_off())
        except Exception:
            self._logger.exception("Collision response failed to turn vacuum pump off")
            return
        if success:
            self._vacuum_off_event_key = event_key
            self._logger.warning("Collision response turned vacuum pump OFF")
        else:
            self._logger.error("Collision response could not turn vacuum pump OFF; retrying")

    def _publish_collision_notice(self, reason: str, event_key: str, *, recovery_failed: bool = False) -> None:
        self._logger.warning("Collision notice: %s", reason)
        notice_key = f"paint-collision:{event_key}"
        self._active_notice_key = notice_key
        self._messaging.publish(
            NotificationTopics.USER,
            UserNotificationEvent(
                source=self.SOURCE,
                severity=NotificationSeverity.CRITICAL,
                title_key=("notification.collision.reset_failed_title" if recovery_failed
                           else "notification.collision.title"),
                message_key=("notification.collision.reset_failed_message" if recovery_failed
                             else "notification.collision.message"),
                fallback_title="Reset not completed" if recovery_failed else "Collision Detected",
                fallback_message=(
                    "Motion remains held. Check that the robot is clear of obstructions and stationary, "
                    "then try releasing the hold again."
                    if recovery_failed else
                    "Robot motion is held. Remove the obstruction, then release the "
                    "collision hold when it is safe to move again."
                ),
                dedupe_key=notice_key,
                actions=(
                    NotificationAction(
                        key=self.ACTION_KEEP_HELD,
                        title_key="notification.collision.keep_held",
                        fallback_title="Keep Motion Held",
                        close_dialog=True,
                    ),
                    NotificationAction(
                        key=self.ACTION_RELEASE,
                        title_key="notification.collision.release_hold",
                        fallback_title="Release Collision Hold",
                        primary=True,
                    ),
                ),
            ),
        )

    def _on_notification_action(self, event: NotificationActionEvent) -> None:
        if not isinstance(event, NotificationActionEvent) or event.source != self.SOURCE:
            return
        if event.action_key == self.ACTION_KEEP_HELD:
            self._logger.info("Operator kept the collision motion hold active")
            return
        if event.action_key != self.ACTION_RELEASE or self._release_in_progress.is_set():
            return
        self._release_in_progress.set()
        threading.Thread(
            target=self._release_collision_hold,
            daemon=True,
            name="CollisionHoldRelease",
        ).start()

    def _release_collision_hold(self) -> None:
        self._release_in_progress.set()
        try:
            self._messaging.publish(
                NotificationTopics.USER,
                UserNotificationEvent(
                    source=self.SOURCE,
                    severity=NotificationSeverity.INFO,
                    title_key="notification.collision.resetting_title",
                    message_key="notification.collision.resetting_message",
                    fallback_title="Resetting collision hold",
                    fallback_message=(
                        "Resetting robot protection. Keep the robot stationary and clear of obstructions. "
                        "This usually takes 10–11 seconds. Motion remains held until recovery completes."
                    ),
                    dedupe_key=self.PROGRESS_KEY,
                    busy=True,
                ),
            )
            if self._acknowledge_collision is not None:
                # The process owns both its local fault and backend acknowledgement.
                success, detail = self._acknowledge_collision()
            else:
                acknowledge = getattr(self._robot, "acknowledge_collision_interlock", None)
                if not callable(acknowledge):
                    raise RuntimeError("Robot backend does not support collision acknowledgement")
                result = acknowledge()
                success = isinstance(result, dict) and bool(result.get("success", False))
                detail = (result.get("message") or result.get("error")
                          if isinstance(result, dict) else "Invalid backend response")
            if not success:
                self._logger.error("Collision hold release failed: %s", detail)
                self._show_release_failure(str(detail))
                return
            self._dismiss_active_notice()
            self._logger.warning("Collision hold release accepted by operator")
        except Exception:
            self._logger.exception("Collision hold release request failed")
            self._show_release_failure("Collision hold release request failed")
        finally:
            self._messaging.publish(
                NotificationTopics.DISMISS,
                DismissNotificationEvent(dedupe_key=self.PROGRESS_KEY),
            )
            self._release_in_progress.clear()

    def _show_release_failure(self, detail: str) -> None:
        # Replace the closed action dialog with the reason and a retry action;
        # do not require a separate warning acknowledgement first.
        self._messaging.publish(
            NotificationTopics.DISMISS,
            DismissNotificationEvent(dedupe_key=self.PROGRESS_KEY),
        )
        self._dismiss_active_notice()
        if self._last_event_key is not None:
            self._publish_collision_notice(detail, self._last_event_key, recovery_failed=True)

    def _dismiss_active_notice(self) -> None:
        key = self._active_notice_key
        if key is None:
            return
        self._active_notice_key = None
        self._messaging.publish(
            NotificationTopics.DISMISS,
            DismissNotificationEvent(dedupe_key=key),
        )
