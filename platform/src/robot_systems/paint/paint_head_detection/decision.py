"""Status confirmation and placement hysteresis, independent of image processing."""

from collections import deque
from dataclasses import dataclass

from .configuration import AlignmentConfig
from .geometry import fitted_pose
from .models import AlignmentMeasurement, DetectionReason, FrameEvidence, HeadStatus, PoseEstimate


class StatusStabilizer:
    def __init__(self, settings: AlignmentConfig) -> None:
        self._settings = settings
        self._history: deque[HeadStatus] = deque(maxlen=settings.stable_frames)
        self._clear_tracking()

    def _clear_tracking(self) -> None:
        self._confirmed = HeadStatus.UNKNOWN
        self._misaligned_hits = 0
        self._weak_frames = 0
        self._last_misaligned_time: float | None = None

    def reset(self) -> None:
        self._history.clear()
        self._clear_tracking()

    @property
    def has_misalignment_evidence(self) -> bool:
        return self._last_misaligned_time is not None

    def update(
        self, observed_status: HeadStatus, *, partial_presence: bool, invalid: bool, now: float
    ) -> HeadStatus:
        self._history.append(observed_status)
        if invalid:
            self._clear_tracking()
            return HeadStatus.UNKNOWN
        if observed_status is HeadStatus.HEAD_MISALIGNED:
            self._misaligned_hits += 1
            self._weak_frames = 0
            self._last_misaligned_time = now
            if self._misaligned_hits >= self._settings.stable_frames:
                self._confirmed = HeadStatus.HEAD_MISALIGNED
            return (
                self._confirmed
                if self._confirmed is HeadStatus.HEAD_MISALIGNED
                else HeadStatus.UNKNOWN
            )
        if observed_status is HeadStatus.UNKNOWN:
            self._weak_frames += 1
            recent = (
                self._last_misaligned_time is not None
                and now - self._last_misaligned_time <= self._settings.unknown_grace_seconds
            )
            if (
                partial_presence
                and recent
                and self._weak_frames <= self._settings.unknown_grace_frames
            ):
                return (
                    self._confirmed
                    if self._confirmed is HeadStatus.HEAD_MISALIGNED
                    else HeadStatus.UNKNOWN
                )
            self._clear_tracking()
            return HeadStatus.UNKNOWN
        self._misaligned_hits = 0
        self._weak_frames = 0
        self._last_misaligned_time = None
        if len(self._history) == self._settings.stable_frames and all(
            status is observed_status for status in self._history
        ):
            self._confirmed = observed_status
        elif (
            observed_status is HeadStatus.HEAD_PRESENT
            and self._confirmed is HeadStatus.HEAD_MISALIGNED
        ):
            return HeadStatus.HEAD_MISALIGNED
        else:
            self._confirmed = HeadStatus.UNKNOWN
        return self._confirmed


@dataclass(frozen=True, slots=True)
class DecisionOutcome:
    status: HeadStatus
    observed_status: HeadStatus
    reason: DetectionReason
    message: str
    alignment: AlignmentMeasurement | None
    pose: PoseEstimate
    held_warning: bool


_MESSAGES: dict[DetectionReason, str] = {
    DetectionReason.ALIGNED: "Head is detected within the configured placement limits.",
    DetectionReason.MISALIGNED: "Head is detected outside the configured placement limits.",
    DetectionReason.EMPTY_MOUNT: "The empty mounting face is positively verified.",
    DetectionReason.INSUFFICIENT_EVIDENCE: "Too few geometrically consistent head features are visible.",
    DetectionReason.CONFLICTING_EVIDENCE: "Present-head and empty-mount evidence conflict.",
    DetectionReason.POSE_UNDETERMINED: "Head features do not provide a measurable placement pose.",
    DetectionReason.TOO_DARK: "The inspection region is too dark to evaluate.",
    DetectionReason.OVEREXPOSED: "The inspection region is overexposed.",
    DetectionReason.LOW_CONTRAST: "The inspection region has insufficient contrast.",
    DetectionReason.CONFIRMING_STATUS: "Waiting for enough consistent observations to confirm the status.",
    DetectionReason.RECHECKING_POSITION: "Rechecking head position; the misalignment warning remains active.",
}


class DecisionPolicy:
    def __init__(self, settings: AlignmentConfig) -> None:
        self._settings = settings
        self._stabilizer = StatusStabilizer(settings)
        self._misalignment_latched = False

    def reset(self) -> None:
        self._misalignment_latched = False
        self._stabilizer.reset()

    def evaluate(self, evidence: FrameEvidence, now: float) -> DecisionOutcome:
        present, missing, quality = evidence.present, evidence.missing, evidence.quality
        pose = present.pose
        alignment = None
        if present.verified and not missing.verified and quality.usable:
            fitted = fitted_pose(present.matches)
            if fitted is not None:
                pose = fitted
                settings = self._settings
                recovery = self._misalignment_latched
                pixel_limit = (
                    settings.recovery_pixels if recovery else settings.max_translation_pixels
                )
                degree_limit = (
                    settings.recovery_degrees if recovery else settings.max_rotation_degrees
                )
                aligned = (
                    pose.translation_pixels <= pixel_limit + 1e-6
                    and abs(pose.rotation_degrees) <= degree_limit + 1e-6
                )
                self._misalignment_latched = not aligned
                alignment = AlignmentMeasurement(
                    aligned,
                    pose.translation_pixels,
                    pose.rotation_degrees,
                    settings.max_translation_pixels,
                    settings.max_rotation_degrees,
                    settings.recovery_pixels,
                    settings.recovery_degrees,
                    recovery,
                )
        observed = HeadStatus.UNKNOWN
        reason = DetectionReason.INSUFFICIENT_EVIDENCE
        if quality.issue is not None:
            reason = quality.issue
        elif present.verified and missing.verified:
            reason = DetectionReason.CONFLICTING_EVIDENCE
        elif present.verified:
            if alignment is None:
                reason = DetectionReason.POSE_UNDETERMINED
            elif alignment.aligned:
                observed, reason = HeadStatus.HEAD_PRESENT, DetectionReason.ALIGNED
            else:
                observed, reason = HeadStatus.HEAD_MISALIGNED, DetectionReason.MISALIGNED
        elif missing.verified:
            observed, reason = HeadStatus.HEAD_MISSING, DetectionReason.EMPTY_MOUNT
        status = self._stabilizer.update(
            observed,
            partial_presence=present.inlier_count > 0,
            invalid=not quality.usable or (present.verified and missing.verified),
            now=now,
        )
        if not self._stabilizer.has_misalignment_evidence and observed is HeadStatus.UNKNOWN:
            self._misalignment_latched = False
        if observed is HeadStatus.HEAD_MISSING or not quality.usable:
            self._misalignment_latched = False
        held = status is HeadStatus.HEAD_MISALIGNED and observed is not status
        if held:
            reason = DetectionReason.RECHECKING_POSITION
        elif status is HeadStatus.UNKNOWN and observed is not HeadStatus.UNKNOWN:
            reason = DetectionReason.CONFIRMING_STATUS
        return DecisionOutcome(status, observed, reason, _MESSAGES[reason], alignment, pose, held)
