"""Robot-pose sampling shared by paint pickup workflows."""

from __future__ import annotations

import logging
import math
import time
from collections.abc import Callable


class FreshPoseReadError(RuntimeError):
    """Raised when a required fresh six-axis robot pose cannot be acquired."""


def read_fresh_pose(
    robot_service: object,
    *,
    error_message: str,
) -> list[float]:
    """Read one valid six-axis pose through the required fresh-read API."""
    try:
        pose = robot_service.get_current_position_fresh()
    except AttributeError as exc:
        raise FreshPoseReadError(
            f"{error_message}: get_current_position_fresh() is unavailable"
        ) from exc
    except Exception as exc:
        raise FreshPoseReadError(error_message) from exc
    try:
        values = [float(value) for value in list(pose)[:6]]
    except (TypeError, ValueError) as exc:
        raise FreshPoseReadError(f"{error_message}: pose is not numeric") from exc
    if len(values) != 6 or not all(math.isfinite(value) for value in values):
        raise FreshPoseReadError(f"{error_message}: expected six finite axis values")
    return values


def wait_for_stable_pose(
    robot_service: object,
    *,
    logger: logging.Logger,
    read_error_message: str,
    timeout_message: str,
    timeout_s: float = 1.0,
    minimum_timeout_s: float = 0.0,
    sample_interval_s: float = 0.05,
    minimum_sample_interval_s: float = 0.0,
    required_stable_samples: int = 3,
    xyz_tolerance_mm: float = 0.5,
    angular_tolerance_deg: float = 0.2,
    stable_log_prefix: str | None = None,
    require_feedback_timestamps: bool = False,
    max_sample_age_s: float = 0.05,
    minimum_stable_duration_s: float = 0.2,
    monotonic: Callable[[], float] = time.monotonic,
    sleep: Callable[[float], None] = time.sleep,
) -> list[float] | None:
    """Verify settling; strict mode requires distinct post-request ROS samples."""
    deadline = monotonic() + max(float(minimum_timeout_s), float(timeout_s))
    previous = None
    stable_samples = 0
    feedback_barrier_ns = None
    last_source_ns = None
    anchor_source_ns = None
    age_s = None
    source_age_s = None
    transport_s = 0.0
    reset_counts = {"stale": 0, "xyz_drift": 0, "angular_drift": 0}
    skipped_samples = 0
    last_reset_reason = "none"
    xyz_delta = angular_delta = 0.0
    while monotonic() < deadline:
        if require_feedback_timestamps:
            try:
                sample = robot_service.get_current_position_sample()
            except Exception as exc:
                raise FreshPoseReadError(read_error_message) from exc
            source_ns = sample.get("sample_timestamp_ns") if isinstance(sample, dict) else None
            observed_ns = sample.get("observation_timestamp_ns") if isinstance(sample, dict) else None
            if (type(source_ns) is not int or source_ns <= 0
                    or type(observed_ns) is not int or observed_ns <= 0):
                logger.error("%s: timestamped feedback is unavailable", read_error_message)
                return None
            if feedback_barrier_ns is None:
                # Both stamps use the backend ROS clock. Never compare the
                # client's wall clock with a remote or simulated robot clock.
                feedback_barrier_ns = observed_ns
            transport_s = sample.get("transport_elapsed_s", 0.0)
            if (isinstance(transport_s, bool) or not isinstance(transport_s, (float, int))
                    or not math.isfinite(transport_s) or transport_s < 0):
                logger.error("%s: invalid feedback transport timing", read_error_message)
                return None
            source_age_s = (observed_ns - source_ns) / 1e9
            age_s = source_age_s + transport_s
            if observed_ns < source_ns or age_s > max_sample_age_s:
                reset_counts["stale"] += 1
                last_reset_reason = "future_timestamp" if observed_ns < source_ns else "stale_feedback"
                previous = None
                stable_samples = 0
                anchor_source_ns = None
                sleep(max(float(minimum_sample_interval_s), float(sample_interval_s)))
                continue
            if source_ns <= feedback_barrier_ns or (last_source_ns is not None and source_ns <= last_source_ns):
                skipped_samples += 1
                sleep(max(float(minimum_sample_interval_s), float(sample_interval_s)))
                continue
            last_source_ns = source_ns
            try:
                pose = [float(value) for value in sample["position"][:6]]
                if len(pose) != 6 or not all(math.isfinite(value) for value in pose):
                    raise ValueError("expected six finite axis values")
            except (KeyError, TypeError, ValueError) as exc:
                raise FreshPoseReadError(read_error_message) from exc
        else:
            pose = read_fresh_pose(robot_service, error_message=read_error_message)
        if previous is not None:
            xyz_delta = math.sqrt(sum(
                (pose[index] - previous[index]) ** 2 for index in range(3)
            ))
            angular_delta = max(
                abs((pose[index] - previous[index] + 180.0) % 360.0 - 180.0)
                for index in range(3, 6)
            )
            if xyz_delta <= xyz_tolerance_mm and angular_delta <= angular_tolerance_deg:
                stable_samples += 1
                duration_ok = (not require_feedback_timestamps or
                               (source_ns - anchor_source_ns) / 1e9 >= minimum_stable_duration_s)
                if stable_samples >= max(1, int(required_stable_samples)) and duration_ok:
                    if require_feedback_timestamps:
                        logger.info("[POSE_SETTLED] source_ns=%d observation_ns=%d age_ms=%.1f span_ms=%.1f samples=%d",
                                    source_ns, observed_ns, age_s * 1000,
                                    (source_ns - anchor_source_ns) / 1e6, stable_samples + 1)
                    if stable_log_prefix:
                        logger.info(
                            "%s Robot pose stable: xyz_delta_mm=%.3f "
                            "angular_delta_deg=%.3f samples=%d pose=%s",
                            stable_log_prefix,
                            xyz_delta,
                            angular_delta,
                            stable_samples,
                            [round(value, 3) for value in pose],
                        )
                    return pose
            else:
                stable_samples = 0
                if require_feedback_timestamps:
                    if xyz_delta > xyz_tolerance_mm:
                        reset_counts["xyz_drift"] += 1
                    if angular_delta > angular_tolerance_deg:
                        reset_counts["angular_drift"] += 1
                    last_reset_reason = "pose_drift"
                    previous = pose
                    anchor_source_ns = source_ns
            if not require_feedback_timestamps:
                previous = pose
        else:
            previous = pose
            if require_feedback_timestamps:
                anchor_source_ns = source_ns
        sleep(max(float(minimum_sample_interval_s), float(sample_interval_s)))
    if require_feedback_timestamps:
        span_ms = (0.0 if anchor_source_ns is None or last_source_ns is None
                   else (last_source_ns - anchor_source_ns) / 1e6)
        logger.error("%s: feedback_limit_ms=%.1f last_age_ms=%s accepted_source_ns=%s boundary_ns=%s stable_samples=%d "
                     "stable_span_ms=%.1f required_span_ms=%.1f source_age_ms=%s http_ms=%.1f "
                     "last_xyz_delta_mm=%.3f last_angular_delta_deg=%.3f resets=%s skipped_samples=%d last_reset=%s",
                     timeout_message, max_sample_age_s * 1000,
                     None if age_s is None else round(age_s * 1000, 3),
                     last_source_ns, feedback_barrier_ns, stable_samples,
                     span_ms, minimum_stable_duration_s * 1000,
                     None if source_age_s is None else round(source_age_s * 1000, 3), transport_s * 1000,
                     xyz_delta, angular_delta, reset_counts, skipped_samples, last_reset_reason)
    else:
        logger.error(timeout_message)
    return None
