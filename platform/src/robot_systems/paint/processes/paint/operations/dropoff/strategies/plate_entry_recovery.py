"""Bounded, pre-release recovery for explicit tray-transfer planning rejections."""
from __future__ import annotations

import logging
import math

from src.robot_systems.paint.processes.paint.motion.pose_sampling import wait_for_stable_pose

_logger = logging.getLogger(__name__)


def is_recoverable_entry_rejection(error: object) -> bool:
    """Generic codes, execution faults and unavailable diagnostics fail closed."""
    if not isinstance(error, str):
        return False
    text = error.lower()
    if any(word in text for word in (
        "timeout", "timed out", "cancel", "abort", "hardware", "controller",
        "protective", "emergency", "communication", "connection",
    )):
        return False
    planning_rejection = any(word in text for word in ("planning", "planner", "rejected"))
    return planning_rejection and ("collision" in text or "no_ik_solution" in text
                                   or "no safe ptp ik candidate" in text)


def recover_plate_entry_unwind(executor, error, *, idle_checker) -> tuple[bool, str]:
    """Unwind once through the normal backend planner, leaving vacuum untouched.

    Caller must be in standalone tray entry after successful painting, before
    release. Replanning/retrying the transfer is deliberately the caller's job.
    """
    if not is_recoverable_entry_rejection(error):
        return False, "unwind recovery skipped: failure is not an explicit collision/IK planning rejection"
    control_getter = getattr(executor, "_execution_control", None)
    control = control_getter() if callable(control_getter) else None

    def allowed():
        return control is None or (not control.should_stop() and not control.pause_requested())

    def stable_pose():
        return wait_for_stable_pose(
            executor._robot_service, logger=_logger,
            read_error_message="Could not verify tray-entry recovery pose",
            timeout_message="Robot did not settle for tray-entry recovery",
        )

    if not allowed() or not executor._robot_service.is_healthy() or not idle_checker(executor):
        return False, "unwind recovery skipped: stop/pause requested or robot is not idle"
    try:
        status = executor._robot_service.get_execution_status()
        chain = status.get("ordered_motion_chain") if isinstance(status, dict) else None
        # Do not infer planning-only failure from a generic negative result or
        # a possibly stale error string. A partially executed entry is uncertain.
        if (not isinstance(chain, dict) or chain.get("phase") != "error"
                or chain.get("active") is not False
                or type(chain.get("executed_segments_count")) is not int
                or chain["executed_segments_count"] != 0
                or type(chain.get("planned_segments_count")) is not int
                or chain["planned_segments_count"] != 0
                or not is_recoverable_entry_rejection(chain.get("error"))):
            return False, "unwind recovery skipped: backend did not confirm rejection before any tray motion was planned/executed"
        before = stable_pose()
        if before is None or not allowed():
            return False, "unwind recovery skipped: robot pose is not stable or stop/pause requested"
        config = executor._paint_process_config()
        _logger.warning("[PLATE_ENTRY_RECOVERY] Transfer rejected: %s; trying one in-place unwind", error)
        # queue_if_busy=False prevents recovery from being queued behind unknown
        # work. The backend's normal collision/IK and motion checks remain active.
        if not executor._robot_service.unwind_joint6(
            blocking=True, queue_if_busy=False,
            vel=config.navigation_return.unwind_vel_percent,
            acc=config.navigation_return.unwind_acc_percent,
        ):
            return False, "tray-entry recovery unwind failed; no transfer retry"
        if not allowed() or not idle_checker(executor):
            return False, "tray-entry recovery stopped or backend remained active after unwind"
        after = stable_pose()
        if after is None or not allowed():
            return False, "tray-entry recovery could not verify the settled unwind pose"
        if math.dist(before[:3], after[:3]) > 2.0:
            return False, "tray-entry unwind changed XYZ by more than 2 mm; no transfer retry"
    except Exception:
        _logger.exception("[PLATE_ENTRY_RECOVERY] Could not complete/verify unwind")
        return False, "tray-entry recovery could not complete or verify unwind"
    executor._last_process_end_pose = list(after)
    executor._dropoff_paint_detach_pose = None
    executor._plate_entry_completed_in_paint_chain = False
    executor._dropoff_unwind_prepared = True
    _logger.warning("[PLATE_ENTRY_RECOVERY] Unwind completed; rebuilding tray transfer once from fresh pose=%s", after)
    return True, ""
