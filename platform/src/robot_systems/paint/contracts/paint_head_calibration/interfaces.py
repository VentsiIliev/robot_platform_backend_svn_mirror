"""Narrow ports for system-owned calibration without platform or detector types."""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Callable
from typing import Protocol

from .models import (
    AssetId,
    CalibrationCatalog,
    CalibrationChange,
    CalibrationDefinition,
    CalibrationEvaluation,
    ImageFrame,
    ImagePixels,
    ImageSize,
    InspectionBinding,
    ProfileId,
    ReferenceAsset,
    RevisionRef,
)


class ICalibrationCatalogRepository(ABC):
    @abstractmethod
    def load(self) -> CalibrationCatalog: ...

    @abstractmethod
    def update(
        self,
        expected_version: int,
        mutation: Callable[[CalibrationCatalog], CalibrationCatalog],
    ) -> CalibrationCatalog:
        """Atomically reject stale edits or publish the complete new catalog."""


class IReferenceAssetRepository(ABC):
    @abstractmethod
    def put_png(self, data: bytes, size: ImageSize) -> ReferenceAsset: ...

    @abstractmethod
    def read_png(self, asset: ReferenceAsset) -> bytes: ...

    @abstractmethod
    def delete(self, identity: AssetId) -> None:
        """Called only after the catalog and active-usage checks permit removal."""


class ICalibrationDefinitionValidator(ABC):
    @abstractmethod
    def validate(self, definition: CalibrationDefinition) -> None:
        """Validate references and prepare the existing detector, or raise a typed error."""


class ICalibrationLease(Protocol):
    def close(self) -> None: ...


class IRevisionLease(ICalibrationLease, Protocol):
    def clone(self) -> IRevisionLease: ...

    @property
    def reference(self) -> RevisionRef: ...

    @property
    def definition(self) -> CalibrationDefinition: ...


class IRuntimeCalibrationProvider(Protocol):
    def acquire_selected(self) -> IRevisionLease: ...


class ICalibrationLibrary(Protocol):
    def load(self) -> CalibrationCatalog: ...

    def in_use_revisions(self) -> tuple[RevisionRef, ...]: ...

    def create_profile(
        self, expected_version: int, name: str, description: str, definition: CalibrationDefinition
    ) -> CalibrationChange: ...

    def import_profile(
        self, expected_version: int, name: str, definition: CalibrationDefinition
    ) -> CalibrationChange: ...

    def save_draft(
        self,
        expected_version: int,
        profile_id: ProfileId,
        definition: CalibrationDefinition,
        base_revision: int | None,
    ) -> CalibrationChange: ...

    def edit_revision(self, expected_version: int, reference: RevisionRef) -> CalibrationChange: ...

    def save_revision(
        self,
        expected_version: int,
        profile_id: ProfileId,
        definition: CalibrationDefinition,
        description: str,
    ) -> CalibrationChange: ...

    def select_revision(
        self, expected_version: int, reference: RevisionRef
    ) -> CalibrationChange: ...

    def discard_draft(self, expected_version: int, profile_id: ProfileId) -> CalibrationChange: ...

    def delete_revision(
        self, expected_version: int, reference: RevisionRef
    ) -> CalibrationChange: ...

    def delete_profile(self, expected_version: int, profile_id: ProfileId) -> CalibrationChange: ...

    def acquire_revision(self, reference: RevisionRef) -> IRevisionLease: ...

    def pin_definition(self, definition: CalibrationDefinition) -> ICalibrationLease: ...

    def store_reference(
        self, png: bytes, size: ImageSize
    ) -> tuple[ReferenceAsset, ICalibrationLease]: ...


class ISetupFrameSource(Protocol):
    def start(self) -> None: ...

    def stop(self) -> None: ...

    def latest(self) -> ImageFrame: ...


class ICalibrationEditorEvaluator(Protocol):
    def empty_template(self, binding: InspectionBinding) -> CalibrationDefinition: ...

    def bundled_template(
        self, binding: InspectionBinding
    ) -> tuple[CalibrationDefinition, ImagePixels, ImagePixels]: ...

    def reference_preview(self, asset: ReferenceAsset) -> ImagePixels: ...

    def encode_reference(self, image: ImagePixels) -> bytes: ...

    def evaluate(
        self, definition: CalibrationDefinition, frame: ImageFrame, generation: int
    ) -> CalibrationEvaluation: ...

    def reset(self) -> None: ...
