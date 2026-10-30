# Paint-head calibration storage and runtime ownership

The developer application and production use one system-owned calibration
library. Portable immutable contracts live in
`src/robot_systems/paint/contracts/paint_head_calibration/`; repository, camera,
detector and runtime adapters live in
`src/robot_systems/paint/paint_head_calibration/`.

## Storage

Each concrete robot system resolves its own writable roots through
`BaseRobotSystem.storage_path()`, including when `ROBOT_PLATFORM_DATA_ROOT` is
configured. The paint, tray-dryer and automatic-dryer systems remain isolated.

| Data | System-relative path |
|---|---|
| Profile catalog and exact runtime selection | `storage/settings/paint/head_detector.json` |
| Catalog transaction lock | `storage/settings/paint/head_detector.transaction.lock` |
| Content-addressed lossless PNG references | `storage/calibration/paint_head/references/<sha256>.png` |

`SettingsID.PAINT_HEAD_CALIBRATION` declares an optional `SettingsSpec` with
`CalibrationCatalogSerializer`. `SettingsCalibrationCatalogRepository` uses the
existing `ISettingsService`, JSON repository, durable-file operations and store
locks. An outer transaction lock covers reload, expected-version check, mutation
and save; stale writes return a typed conflict. The catalog is separate from
process scheduling/reaction settings and never replaces unrelated settings.

Profiles contain a persisted draft, immutable revisions and a monotonically
increasing next revision number. The selected value identifies an exact profile
and revision. A revision contains inspection binding, reference identities/sizes,
regions, landmarks and all matching/preprocessing/alignment tuning. JSON paths
are not embedded in the view or the portable definition.

On first library use, a missing catalog triggers the approved one-time import of
the bundled calibration into a named **Imported factory calibration**, revision
1, with a draft and explicit runtime selection. Both images are copied into that
system's managed reference store and validated before catalog publication.
Composition itself does no import I/O. An existing catalog is never reseeded,
including an intentionally empty or corrupt one. Invalid catalogs/assets fail
with typed errors; they do not fall back to bundled production settings.

## Runtime boundary

`CalibratedHeadCheckRunFactory` acquires the selected immutable definition once
for each new enabled run, before startup inspection motion or the bounded frame
window. Disabled checks and pickup-only mode do not acquire calibration. The
existing schedule, strict taught target and reaction policies still own cycle
behavior; they do not depend on the detector implementation.

Runtime selection is allowed only in IDLE/STOPPED after cleanup. Publication
reserves the existing `SystemManager`, so another process cannot be admitted
between the state check and saved selection. The GUI does not hold the process
lock across disk I/O. Production and prepared-workpiece execution release their
run in `finally`, including early failures and exceptions.

A stopped-position guidance offer clones ownership of the same run revision.
It constructs its own inspector and detector confirmation history from that
snapshot. It never reads a newly selected revision mid-session. Pending cancel,
active worker exit, failure and shutdown release guidance ownership independently
of the completed production run. A later accepted Start cancels old guidance and
acquires the then-selected revision.

## Deletion and errors

Selection and usage checks are enforced in the library, not just by disabled UI
buttons. Selected revisions and profiles containing them cannot be deleted.
In-use revision leases prevent deletion until every owner releases them.
Captured images and development evaluations hold asset leases. Shared references
are deleted only after no catalog definition or active owner uses them; cleanup
failures are returned as warnings after catalog publication. Lease close itself
performs no filesystem I/O and does not wait for catalog saves.

Typed failures distinguish invalid data/calibration, missing selection, busy
process, selected/in-use revision, stale catalog, missing/invalid asset,
load/save/cleanup failure and invalid/stale camera frame. Persistence failures
retain whether a replacement was already published, avoiding a false rollback
claim after a durability error.

The detector adapter translates portable values to the existing image-only
`PaintHeadDetector`; no recognition algorithm or public detector result changes
are required. Each development evaluation generation and production/guidance
session owns independent confirmation state.
