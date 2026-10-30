"""Shared calibration lifecycle; all mutation and ownership checks live below MVC."""

from __future__ import annotations

from collections.abc import Callable
from contextlib import AbstractContextManager, nullcontext
from dataclasses import replace
from datetime import UTC, datetime
from functools import partial
from threading import Lock, RLock

from src.robot_systems.paint.contracts.paint_head_calibration.errors import (
    CalibrationFailure,
    CalibrationFailureCode,
    PaintHeadCalibrationError,
)
from src.robot_systems.paint.contracts.paint_head_calibration.interfaces import (
    ICalibrationCatalogRepository,
    ICalibrationDefinitionValidator,
    IReferenceAssetRepository,
)
from src.robot_systems.paint.contracts.paint_head_calibration.models import (
    AssetId,
    CalibrationCatalog,
    CalibrationChange,
    CalibrationDefinition,
    CalibrationDraft,
    CalibrationProfile,
    CalibrationRevision,
    ImageSize,
    ProfileId,
    ReferenceAsset,
    RevisionRef,
)


class CalibrationLease:
    """Explicit, idempotent ownership. Closing never performs filesystem I/O."""

    def __init__(self, release: Callable[[], None]) -> None:
        self._release = release
        self._lock = Lock()
        self._closed = False

    def close(self) -> None:
        with self._lock:
            if not self._closed:
                self._closed = True
                self._release()

    def __enter__(self) -> CalibrationLease:
        return self

    def __exit__(self, *_: object) -> None:
        self.close()

    def _while_open[T](self, operation: Callable[[], T]) -> T:
        with self._lock:
            if self._closed:
                raise _failure(
                    CalibrationFailureCode.CANCELLED, "Calibration ownership was released"
                )
            return operation()


class RevisionLease(CalibrationLease):
    def __init__(
        self,
        reference: RevisionRef,
        definition: CalibrationDefinition,
        release: Callable[[], None],
        retain: Callable[[], RevisionLease],
    ) -> None:
        super().__init__(release)
        self._reference = reference
        self._definition = definition
        self._retain = retain

    def clone(self) -> RevisionLease:
        return self._while_open(self._retain)

    @property
    def reference(self) -> RevisionRef:
        return self._reference

    @property
    def definition(self) -> CalibrationDefinition:
        return self._definition


def _failure(code: CalibrationFailureCode, detail: str) -> PaintHeadCalibrationError:
    return PaintHeadCalibrationError(CalibrationFailure(code, detail))


def _utc_now() -> datetime:
    return datetime.now(UTC)


def _unreserved_selection() -> AbstractContextManager[bool]:
    return nullcontext(True)


class PaintHeadCalibrationLibrary:
    def __init__(
        self,
        repository: ICalibrationCatalogRepository,
        assets: IReferenceAssetRepository,
        validator: ICalibrationDefinitionValidator,
        *,
        selection_allowed: Callable[[], bool],
        clock: Callable[[], datetime] = _utc_now,
        initialize: Callable[[], object] | None = None,
        selection_reservation: Callable[[], AbstractContextManager[bool]] = _unreserved_selection,
    ) -> None:
        self._repository = repository
        self._assets = assets
        self._validator = validator
        self._selection_allowed = selection_allowed
        self._selection_reservation = selection_reservation
        self._clock = clock
        self._initialize = initialize
        self._initialized = initialize is None
        self._lock = RLock()
        self._usage_lock = RLock()
        self._revision_uses: dict[RevisionRef, int] = {}
        self._asset_uses: dict[AssetId, int] = {}
        self._pending_cleanup: set[AssetId] = set()

    def load(self) -> CalibrationCatalog:
        with self._lock:
            self._ensure_initialized()
            return self._repository.load()

    def _ensure_initialized(self) -> None:
        if not self._initialized:
            if self._initialize is not None:
                self._initialize()
            self._initialized = True

    def in_use_revisions(self) -> tuple[RevisionRef, ...]:
        with self._usage_lock:
            return tuple(
                sorted(self._revision_uses, key=lambda ref: (ref.profile_id.value, ref.number))
            )

    def create_profile(
        self,
        expected_version: int,
        name: str,
        description: str,
        definition: CalibrationDefinition,
    ) -> CalibrationChange:
        profile = CalibrationProfile(
            ProfileId.new(),
            name,
            description,
            CalibrationDraft(definition, None, self._clock()),
            (),
            1,
        )

        def create(catalog: CalibrationCatalog) -> CalibrationCatalog:
            return replace(catalog, profiles=(*catalog.profiles, profile))

        return self._mutate(expected_version, create)

    def import_profile(
        self, expected_version: int, name: str, definition: CalibrationDefinition
    ) -> CalibrationChange:
        """Publish a fully validated import in one catalog update; never select it implicitly."""

        def create(catalog: CalibrationCatalog) -> CalibrationCatalog:
            self._validator.validate(definition)
            now = self._clock()
            profile = CalibrationProfile(
                ProfileId.new(),
                name,
                "",
                CalibrationDraft(definition, 1, now),
                (CalibrationRevision(1, definition, now, ""),),
                2,
            )
            return replace(catalog, profiles=(*catalog.profiles, profile))

        return self._mutate(expected_version, create)

    def save_draft(
        self,
        expected_version: int,
        profile_id: ProfileId,
        definition: CalibrationDefinition,
        base_revision: int | None,
    ) -> CalibrationChange:
        draft = CalibrationDraft(definition, base_revision, self._clock())

        def save(catalog: CalibrationCatalog) -> CalibrationCatalog:
            profile = catalog.profile(profile_id)
            return self._replace_profile(catalog, replace(profile, draft=draft))

        return self._mutate(expected_version, save)

    def edit_revision(self, expected_version: int, reference: RevisionRef) -> CalibrationChange:
        def edit(catalog: CalibrationCatalog) -> CalibrationCatalog:
            profile = catalog.profile(reference.profile_id)
            definition = profile.revision(reference.number).definition
            draft = CalibrationDraft(definition, reference.number, self._clock())
            return self._replace_profile(catalog, replace(profile, draft=draft))

        return self._mutate(expected_version, edit)

    def save_revision(
        self,
        expected_version: int,
        profile_id: ProfileId,
        definition: CalibrationDefinition,
        description: str,
    ) -> CalibrationChange:
        def publish(catalog: CalibrationCatalog) -> CalibrationCatalog:
            profile = catalog.profile(profile_id)
            self._validator.validate(definition)
            now = self._clock()
            revision = CalibrationRevision(profile.next_revision, definition, now, description)
            updated = replace(
                profile,
                revisions=(*profile.revisions, revision),
                next_revision=profile.next_revision + 1,
                draft=CalibrationDraft(definition, revision.number, now),
            )
            return self._replace_profile(catalog, updated)

        return self._mutate(expected_version, publish)

    def select_revision(self, expected_version: int, reference: RevisionRef) -> CalibrationChange:
        def select(catalog: CalibrationCatalog) -> CalibrationCatalog:
            if not self._selection_allowed():
                raise _failure(
                    CalibrationFailureCode.PROCESS_ACTIVE, "Runtime selection cannot change now"
                )
            definition = catalog.profile(reference.profile_id).revision(reference.number).definition
            self._validator.validate(definition)
            if not self._selection_allowed():
                raise _failure(
                    CalibrationFailureCode.PROCESS_ACTIVE, "Runtime selection cannot change now"
                )
            return replace(catalog, selected=reference)

        with self._selection_reservation() as reserved:
            if not reserved:
                raise _failure(
                    CalibrationFailureCode.PROCESS_ACTIVE,
                    "Runtime selection cannot change while the system is busy",
                )
            return self._mutate(expected_version, select)

    def discard_draft(self, expected_version: int, profile_id: ProfileId) -> CalibrationChange:
        def discard(catalog: CalibrationCatalog) -> CalibrationCatalog:
            return self._replace_profile(catalog, replace(catalog.profile(profile_id), draft=None))

        return self._mutate(expected_version, discard)

    def delete_revision(self, expected_version: int, reference: RevisionRef) -> CalibrationChange:
        def delete(catalog: CalibrationCatalog) -> CalibrationCatalog:
            profile = catalog.profile(reference.profile_id)
            profile.revision(reference.number)
            self._require_deletable(catalog, reference)
            return self._replace_profile(
                catalog,
                replace(
                    profile,
                    revisions=tuple(
                        revision
                        for revision in profile.revisions
                        if revision.number != reference.number
                    ),
                ),
            )

        return self._mutate(expected_version, delete)

    def delete_profile(self, expected_version: int, profile_id: ProfileId) -> CalibrationChange:
        def delete(catalog: CalibrationCatalog) -> CalibrationCatalog:
            profile = catalog.profile(profile_id)
            for revision in profile.revisions:
                self._require_deletable(catalog, RevisionRef(profile_id, revision.number))
            return replace(
                catalog,
                profiles=tuple(
                    profile for profile in catalog.profiles if profile.profile_id != profile_id
                ),
            )

        return self._mutate(expected_version, delete)

    def acquire_revision(self, reference: RevisionRef) -> RevisionLease:
        with self._lock:
            self._ensure_initialized()
            catalog = self._repository.load()
            definition = catalog.profile(reference.profile_id).revision(reference.number).definition
            return self._pin_revision(reference, definition)

    def acquire_selected(self) -> RevisionLease:
        with self._lock:
            self._ensure_initialized()
            catalog = self._repository.load()
            reference = catalog.selected
            if reference is None:
                raise _failure(
                    CalibrationFailureCode.SELECTION_MISSING, "No runtime calibration is selected"
                )
            definition = catalog.profile(reference.profile_id).revision(reference.number).definition
            return self._pin_revision(reference, definition)

    def pin_definition(self, definition: CalibrationDefinition) -> CalibrationLease:
        """Protect working-draft assets while an editor/evaluator owns their snapshot."""
        with self._lock:
            identities = frozenset(asset.asset_id for asset in definition.references.assets())
            self._pin_assets(identities)
            return CalibrationLease(partial(self._release_assets, identities))

    def store_reference(
        self, png: bytes, size: ImageSize
    ) -> tuple[ReferenceAsset, CalibrationLease]:
        with self._lock:
            asset = self._assets.put_png(png, size)
            identities = frozenset((asset.asset_id,))
            self._pin_assets(identities)
            self._pending_cleanup.add(asset.asset_id)
            return asset, CalibrationLease(partial(self._release_assets, identities))

    def cleanup_pending_assets(self) -> tuple[CalibrationFailure, ...]:
        """Worker-only cleanup; lease.close() itself remains nonblocking and I/O-free."""
        with self._lock:
            if not self._pending_cleanup:
                return ()
            return self._cleanup(self._repository.load())

    def _pin_revision(
        self, reference: RevisionRef, definition: CalibrationDefinition
    ) -> RevisionLease:
        with self._usage_lock:
            self._revision_uses[reference] = self._revision_uses.get(reference, 0) + 1
            identities = frozenset(asset.asset_id for asset in definition.references.assets())
            self._pin_assets(identities)
            return RevisionLease(
                reference,
                definition,
                partial(self._release_revision, reference, identities),
                partial(self._pin_revision, reference, definition),
            )

    def _pin_assets(self, identities: frozenset[AssetId]) -> None:
        with self._usage_lock:
            for identity in identities:
                self._asset_uses[identity] = self._asset_uses.get(identity, 0) + 1

    def _release_assets(self, identities: frozenset[AssetId]) -> None:
        with self._usage_lock:
            for identity in identities:
                count = self._asset_uses[identity] - 1
                if count:
                    self._asset_uses[identity] = count
                else:
                    del self._asset_uses[identity]

    def _release_revision(self, reference: RevisionRef, identities: frozenset[AssetId]) -> None:
        with self._usage_lock:
            count = self._revision_uses[reference] - 1
            if count:
                self._revision_uses[reference] = count
            else:
                del self._revision_uses[reference]
            self._release_assets(identities)

    def _require_deletable(self, catalog: CalibrationCatalog, reference: RevisionRef) -> None:
        if reference == catalog.selected:
            raise _failure(
                CalibrationFailureCode.REVISION_SELECTED,
                "Select another runtime revision before deleting this revision",
            )
        with self._usage_lock:
            used = self._revision_uses.get(reference, 0)
        if used:
            raise _failure(CalibrationFailureCode.REVISION_IN_USE, "Revision is currently in use")

    def _mutate(
        self,
        expected_version: int,
        operation: Callable[[CalibrationCatalog], CalibrationCatalog],
    ) -> CalibrationChange:
        with self._lock:
            self._ensure_initialized()
            removed: frozenset[AssetId] = frozenset()

            def mutate(current: CalibrationCatalog) -> CalibrationCatalog:
                nonlocal removed
                updated = operation(current)
                removed = current.referenced_assets() - updated.referenced_assets()
                return updated

            catalog = self._repository.update(expected_version, mutate)
            self._pending_cleanup.update(removed)
            return CalibrationChange(catalog, self._cleanup(catalog))

    def _cleanup(self, catalog: CalibrationCatalog) -> tuple[CalibrationFailure, ...]:
        referenced = catalog.referenced_assets()
        warnings: list[CalibrationFailure] = []
        for identity in tuple(self._pending_cleanup):
            with self._usage_lock:
                used = self._asset_uses.get(identity, 0)
            if identity in referenced:
                self._pending_cleanup.remove(identity)
            elif not used:
                try:
                    self._assets.delete(identity)
                except PaintHeadCalibrationError as error:
                    warnings.append(error.failure)
                else:
                    self._pending_cleanup.remove(identity)
        return tuple(warnings)

    @staticmethod
    def _replace_profile(
        catalog: CalibrationCatalog, updated: CalibrationProfile
    ) -> CalibrationCatalog:
        return replace(
            catalog,
            profiles=tuple(
                updated if profile.profile_id == updated.profile_id else profile
                for profile in catalog.profiles
            ),
        )
