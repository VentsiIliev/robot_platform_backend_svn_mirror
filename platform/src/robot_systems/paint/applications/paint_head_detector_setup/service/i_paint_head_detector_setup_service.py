"""The application boundary: immutable values, no platform, detector, Qt or image library."""

from abc import ABC, abstractmethod

from src.robot_systems.paint.contracts.paint_head_calibration.errors import CalibrationResult
from src.robot_systems.paint.contracts.paint_head_calibration.models import (
    CalibrationCatalog,
    CalibrationChange,
    CalibrationDefinition,
    CalibrationEvaluation,
    ImageFrame,
    ImagePixels,
    ProfileId,
    ReferenceAsset,
    ReferenceRole,
    RevisionRef,
)


class IPaintHeadDetectorSetupService(ABC):
    @abstractmethod
    def load_catalog(self) -> CalibrationResult[CalibrationCatalog]: ...

    @abstractmethod
    def in_use_revisions(self) -> CalibrationResult[tuple[RevisionRef, ...]]: ...

    @abstractmethod
    def create_profile(
        self, version: int, name: str, description: str
    ) -> CalibrationResult[CalibrationChange]: ...

    @abstractmethod
    def import_factory_profile(
        self, version: int, name: str
    ) -> CalibrationResult[CalibrationChange]: ...

    @abstractmethod
    def save_draft(
        self,
        version: int,
        profile_id: ProfileId,
        definition: CalibrationDefinition,
        base_revision: int | None,
    ) -> CalibrationResult[CalibrationChange]: ...

    @abstractmethod
    def save_revision(
        self,
        version: int,
        profile_id: ProfileId,
        definition: CalibrationDefinition,
        description: str,
    ) -> CalibrationResult[CalibrationChange]: ...

    @abstractmethod
    def edit_revision(
        self, version: int, reference: RevisionRef
    ) -> CalibrationResult[CalibrationChange]: ...

    @abstractmethod
    def select_revision(
        self, version: int, reference: RevisionRef
    ) -> CalibrationResult[CalibrationChange]: ...

    @abstractmethod
    def delete_revision(
        self, version: int, reference: RevisionRef
    ) -> CalibrationResult[CalibrationChange]: ...

    @abstractmethod
    def delete_profile(
        self, version: int, profile_id: ProfileId
    ) -> CalibrationResult[CalibrationChange]: ...

    @abstractmethod
    def discard_draft(
        self, version: int, profile_id: ProfileId
    ) -> CalibrationResult[CalibrationChange]: ...

    @abstractmethod
    def start_preview(self) -> CalibrationResult[None]: ...

    @abstractmethod
    def stop_preview(self) -> None:
        """Nonblocking cancellation/unsubscribe; never shuts down the shared camera."""

    @abstractmethod
    def latest_frame(self) -> CalibrationResult[ImageFrame]: ...

    @abstractmethod
    def reference_preview(self, asset: ReferenceAsset) -> CalibrationResult[ImagePixels]: ...

    @abstractmethod
    def capture_reference(
        self, definition: CalibrationDefinition, frame: ImageFrame, role: ReferenceRole
    ) -> CalibrationResult[CalibrationDefinition]: ...

    @abstractmethod
    def evaluate(
        self, definition: CalibrationDefinition, frame: ImageFrame, generation: int
    ) -> CalibrationResult[CalibrationEvaluation]: ...

    @abstractmethod
    def end_session(self) -> None:
        """Release editor ownership after workers finish; does not perform filesystem I/O."""
