# Paint-head detector setup application — implementation plan

Status: implementation and automated verification complete. Physical station acceptance remains pending.

Date: 2026-10-30.

This plan records the agreed scope, proposed architecture, implementation order
and confirmed implementation decisions. The application, shared calibration library
and runtime snapshot integration are now implemented. Station acceptance remains
a separate hardware verification step.

## 1. Objective and scope

Create a developer application under `src/robot_systems/paint/applications/` for
capturing references, editing detector calibration, testing a draft and selecting
the saved calibration/settings used by runtime inspections. Opening the screen
must not require a production cycle.

The application must support:

- Live primary-camera preview, explicit capture and reference preview/confirmation.
- Present and missing reference images for the selected inspection configuration.
- Visual editing of inspection and empty-mount regions, excluded regions and
  present/missing landmarks, using the detector's existing supported geometry.
- On-demand detection and optional continuous evaluation with diagnostic overlays.
- Typed results, reasons, available matching evidence and alignment measurements.
- Persisted drafts, validated saved revisions, explicit runtime selection and
  revision/profile deletion with reference and usage checks.
- Per-robot-system storage through the existing settings/repository mechanisms.
- English/Bulgarian localization, shared styles and shared input components.
- Developer-restricted registration, isolated tests and deterministic cleanup.

Do not change recognition algorithms or the detector's public result types.
Do not alter production scheduling/reactions, the operator alignment popup or
automatic cycle control. Wiring production to the explicitly selected calibration
is in scope; changing how the cycle reacts to detection is not. Camera mounting,
lighting installation and automatic robot positioning are outside this scope.

## 2. Existing implementation to reuse

| Existing component | Reuse |
|---|---|
| `src/applications/APPLICATION_BLUEPRINT/` | Application/service/model/view/controller/factory structure and standalone runner |
| `src/engine/repositories/interfaces/` | Settings service, repository and serializer contracts |
| `src/engine/repositories/json/base_json_settings_repository.py` | Validated loads, typed storage failures, store locking and atomic JSON saves |
| `src/engine/core/durable_files.py` | Existing durable file operations where suitable for reference assets |
| `src/robot_systems/paint/paint_head_detection/` | Typed configuration, validation, references, update APIs and `get_status()` |
| `src/robot_systems/paint/paint_head_check/adapters/` | Existing camera freshness and detector-boundary behavior to reuse through narrow seams |
| `src/robot_systems/paint/paint_robot_system.py` | Runtime composition, application registration and settings declarations |
| `src/robot_systems/paint/application_wiring.py` | Lazy application construction |

The existing `paint_head_settings` application configures the paint-head
peripheral/presets, not the image detector. Keep this application distinct.
Proposed application package: `paint_head_detector_setup`.

Before this change, runtime constructed `PaintHeadDetector()` with bundled configuration.
The new application must not create a separate configuration source that production
never reads. A shared calibration provider must supply both development and
runtime consumers while preserving their independent detector instances.

The detector already supports inspection/empty-mount/excluded regions, feature
properties, typed configuration updates and reference replacement. Its references
must have compatible image dimensions. Keep these invariants intact.

## 3. Agreed profile and draft behavior

### Profile contents

A calibration profile groups one coherent set of reference assets, regions,
landmarks and detector settings. Use typed stable profile/revision/asset identities.
Do not offer independent selectors that can accidentally combine incompatible
references, geometry and tuning.

Each saved revision records its camera role, image dimensions and inspection
context, together with the configuration needed to reproduce evaluation. The
inspection context is fixed as recorded in section 4.

### Separate editing, saving and runtime selection

| Operation | Contract |
|---|---|
| Save draft | Persist incomplete work without changing runtime selection |
| Test draft | Evaluate a snapshot of the current draft without publishing it |
| Save calibration | Validate all required data and create a saved immutable revision |
| Use for runtime | Explicitly select an eligible saved revision, never a draft |

A persisted draft may be incomplete but must still be structurally readable and
report its validation issues. A saved revision must satisfy the full detector and
reference validation rules. Editing a saved revision creates a draft derived from
it; it does not overwrite the revision.

Show the editing profile/revision, dirty state, persisted-draft state, validation
issues and selected runtime revision separately. Saving/testing must never silently
activate a draft. Switching profiles or leaving with unsaved edits offers Save
draft / Discard / Cancel.

Runtime selection points to a specific revision, not a moving "latest" target.
Revision identifiers remain stable after deletion; do not renumber surviving
revisions or reuse deleted identities. Normal edits do not affect other profiles
or unrelated settings.

### Revision and profile deletion

- Confirm deletion with the profile name and exact revision(s).
- Allow deletion of inactive, unused revisions.
- Block deletion of the selected runtime revision until another valid revision
  is explicitly selected. Never silently choose a replacement.
- Block deletion while a runtime inspection, live-guidance session or development
  evaluation owns the revision. Track ownership through explicit leases/handles,
  with release on success, failure, cancellation and shutdown.
- Treat the selection/usage check and deletion as one coordinated service action,
  so a concurrent selection or acquisition cannot bypass the check.
- Deleting a whole profile applies the same checks to all revisions and resolves
  any draft before proceeding. Offer explicit draft deletion/discard as well.
- Delete reference assets only when no remaining draft or saved revision uses
  them. Preserve the currently usable calibration on failures.
- Enforce these rules below the UI and return typed blocked/failure results.

## 4. Confirmed implementation decisions

| Decision | Confirmed behavior |
|---|---|
| Inspection points | One inspection point: Primary vision + Vertical Shaft Alignment, with multiple profiles |
| Runtime activation boundary | Selection changes only while stopped after cleanup; each accepted Start uses one fixed revision through the run and its associated stopped-position guidance |
| Existing calibration | Approved one-time import of the bundled calibration into each system's managed storage as a named saved revision and explicit runtime selection |
| Startup without usable selection | Checks remain disabled by default; enabled checks fail clearly when an existing catalog has no usable selection. Existing empty/corrupt catalogs are never reseeded |
| Editing parameter scope | Alignment/confirmation controls plus the existing matching/preprocessing parameters; no algorithm changes |
| Developer access | Manufacturer-only in a dedicated Development folder |

Primary vision and the mandatory taught Vertical Shaft Alignment position remain
the existing production constraints. Multiple profiles do not imply new automatic
motion routes. Do not add move-to-pose behavior without a separate decision.

## 5. Architecture and contracts

Use the platform MVC structure and narrow injected interfaces:

```text
View signals -> Controller -> Model -> Application service interface
                                           |
                                  Application service
                                  /       |         \
                          repositories  camera    evaluator adapter
                                  \       |
                            shared calibration provider
                                      |
                              runtime detector adapter
```

- The application exposes a stdlib-only service contract and immutable DTOs;
  detector/NumPy/platform objects do not leak into that contract.
- Model holds editing state and delegates operations; no Qt, files or hardware.
- View owns widgets, image-space interaction and presentation only. No broker,
  settings service, detector calls or filesystem paths.
- Controller coordinates model/view and uses the existing Qt worker and queued
  bridge patterns. No direct settings, repository or robot-service access.
- Concrete application service adapts settings/repositories, frame source,
  evaluator and profile-use ownership through injected ports; no Qt.
- Robot-system composition owns service lifetimes, storage roots and runtime
  provider injection. Do not import the RobotSystem from application layers.
- Reuse platform factory ownership/cleanup; do not manually duplicate its
  controller-retention behavior or add cross-application dependencies.

Define typed IDs, operation results and custom errors for missing profiles,
invalid drafts, incompatible images, unavailable/stale frames, storage failures,
revision conflicts and blocked deletion/activation. Preserve underlying storage
failure detail without using exception messages as control flow.

Use explicit enum/typed-ID mappings at JSON and UI boundaries. No raw string
business dispatch, reflective class loading, `getattr`/`setattr` or mutation of
another component's private fields.

## 6. Persistence design

All calibration metadata, draft data and reference images belong beneath the
active robot system's resolved storage root. Respect installed data-root overrides
and keep paint, paint_tray_dry and other paint variants isolated. Do not write into
the detector's bundled `config/` or `references/` directories.

Proposed layout, to finalize against existing storage conventions:

```text
<active-system>/storage/
  settings/paint/head_detector.json       # typed catalog, drafts, revisions, selection
  calibration/paint_head/references/      # managed reference-image assets
```

Use a system-owned `SettingsSpec`, enum settings ID and serializer with
`ISettingsService`/`ISettingsRepository`/`BaseJsonSettingsRepository`. A narrow
paint-owned repository/service may provide profile operations on the aggregate;
do not create an unrelated JSON persistence framework or change the generic
repository interface just to add a profile-delete button.

Reference-image bytes need a dedicated repository boundary using suitable existing
durable file primitives. Store system-relative asset identities/paths, validate
ownership and preserve immutable revision references. UI-provided names must not
become unrestricted filesystem paths.

Persist new assets before atomically publishing catalog references to them. A
failed operation must not leave a saved revision or runtime selection pointing to
missing/partial data. Publish successful catalog updates before removing newly
unreferenced assets; cleanup failures must be reported accurately and must not
invalidate surviving revisions. A single-file atomic save is not a multi-file
transaction: test interrupted publication and asset cleanup explicitly.

Use existing locking plus explicit update/version conflict checks where needed
for read-modify-write operations. Update only the requested profile/draft/selection,
preserve unrelated records and reject unsupported/corrupt data explicitly. No
silent fallback write or automatic overwrite of saved station calibration.

## 7. Camera, editing and evaluation behavior

- Subscribe to the existing named primary-camera stream; never open a competing
  handle to the camera already owned by VisionSystem.
- Validate capture identity, sequence, age, image format and calibration size.
  A repeated buffered frame is not a new observation.
- Freeze an owned image snapshot for capture preview and editing. Confirm its
  present/missing reference role before committing it to the draft/profile.
- Draw/edit regions in original image coordinates with correct transforms for
  fit, zoom, pan, aspect ratio and high-DPI display. Support selecting, moving,
  resizing and deleting the supported region/feature shapes.
- Validate bounds and feature properties, including threshold, role, required,
  orientation-invariant, support shape and template-rotation limit where applicable.
- Label evaluation as using the draft or a named saved revision. Results carry
  the frame identity and editing/configuration generation that produced them.
- Run detector construction/evaluation, image encoding, persistence and any
  blocking source operations outside the GUI thread. Keep only the latest pending
  live frame, not an unbounded evaluation queue.
- Keep development detector state separate from production and live guidance.
  Reset confirmation at explicit evaluation-session/configuration boundaries;
  preserve it across fresh frames in a continuous session.
- Show `status` and `observed_status`, reason, held-warning/confirmation state,
  existing diagnostic matching evidence and available alignment measurements.
  The current result has no overall confidence percentage: do not invent one.
- A single-frame test may legitimately be UNKNOWN while confirming. Explain that
  state without silently changing confirmation requirements or reusing a frame.
- Show unavailable measurements as unavailable. Distinguish valid UNKNOWN from
  stale/unusable image, missing camera, evaluation failure and invalid calibration.
- Leaving/hiding the screen stops its live work and releases its subscriptions,
  buffers and leases without shutting down the shared camera service. Reopening
  starts a fresh screen session; late results cannot update destroyed widgets or
  overwrite a different draft/profile.

## 8. Step-by-step implementation

### Step 1 — Resolve the remaining behavior decisions

- [x] Confirm section 4 choices and record them here.
- [x] Check current settings/calibration asset storage, navigation lifecycle and
      authorization patterns before selecting exact modules.
- [x] Finalize typed contracts, storage layout and the profile state transitions.

Exit criterion: activation, migration, inspection-point and access behavior are
explicit; implementation does not guess the unresolved product choices.

### Step 2 — Implement profile contracts and persistence

- [x] Add profile, draft, revision, selection, compatibility and asset DTOs.
- [x] Add serializers/settings registration and a narrow repository boundary.
- [x] Implement create/load/update draft, publish validated revision and explicit
      selection, preserving unrelated records.
- [x] Implement confirmed revision/profile deletion, asset reference checks,
      usage ownership and typed failure/conflict reporting.
- [x] Cover missing/corrupt storage, failed writes, interrupted asset publication,
      update conflicts, deletion failures and per-system isolation in tests.

Exit criterion: the complete profile lifecycle works through repositories in
temporary storage without Qt, cameras or robot hardware.

### Step 3 — Implement application service, model and stub

- [x] Start from APPLICATION_BLUEPRINT and use a distinct application identity.
- [x] Define the narrow stdlib-only service contract and implement a faithful stub.
- [x] Implement draft state, validation, dirty tracking and profile/revision picker
      behavior in the model/service, not the view.
- [x] Add camera/evaluator adapters and typed frame/result presentation DTOs.
- [x] Test model behavior against the stub and concrete service against temporary
      repositories/fake camera/evaluator ports.

Exit criterion: draft capture/test/save/select/delete operations have explicit
contracts and isolated tests before widget integration.

### Step 4 — Build camera preview and visual editor

- [x] Add the application view and factory using shared styles/input widgets.
- [x] Add profile/revision selection, draft/runtime labels and reference preview.
- [x] Implement region/landmark tools, reference-role confirmation and validation.
- [x] Expose agreed tuning controls and existing detector diagnostic overlays.
- [x] Verify original-image coordinate mapping with scaling, zoom and image sizes.

Exit criterion: a developer can create/edit a draft and inspect reference assets
without a production cycle or direct detector/file access from the view.

### Step 5 — Wire asynchronous interaction and cleanup

- [x] Implement controller signal routing, named broker callbacks and Qt bridges.
- [x] Add worker ownership, cancellation and generation checks for blocking work.
- [x] Implement on-demand and continuous evaluation with bounded frame handling.
- [x] Implement Save draft / Discard / Cancel navigation behavior and confirmations.
- [x] Pair every subscription with cleanup; release workers, buffers and revision
      usage handles on all termination paths.
- [x] Test controller behavior with the stub, including late-result rejection and
      repeated load/hide/show/stop without hardware.

Exit criterion: live evaluation stays responsive and screen navigation neither
leaks work nor interrupts the shared camera owner.

### Step 6 — Connect runtime to the selected revision

- [x] Inject the shared calibration provider into development and runtime wiring.
- [x] Replace bundled-only runtime construction with the agreed explicit selection
      and migration behavior, without changing detector algorithms/results.
- [x] Implement the agreed snapshot boundary and pin its revision/assets while
      inspections or associated guidance own them.
- [x] Enforce selection/deletion restrictions in the shared service; settings UI
      disabling alone is insufficient.
- [x] Verify retries/guidance cannot pick up different settings mid-session and
      saving/testing a draft cannot change a running detector.

Exit criterion: production uses exactly the selected saved revision under the
agreed lifecycle rules; the operator popup and cycle policies remain unchanged.

### Step 7 — Register, localize and verify the application

- [x] Register lazy construction and agreed developer-folder/role restrictions.
- [x] Add English/Bulgarian catalogs for the applicable paint variants; verify
      initial translation and runtime LanguageChange handling.
- [x] Verify shared numeric/text input controls and keyboard placement.
- [x] Provide a standalone stub runner and offscreen construction/interaction
      checks; do not launch the hardware application for automated smoke tests.
- [x] Compile touched Python modules, validate catalogs and run focused tests.
- [x] Update application, persistence and integration docs to reflect final code.

Exit criterion: the application is discoverable only under agreed permissions,
localized and verified independently of real hardware.

## 9. Acceptance checklist

- [x] Opens from the agreed developer location without starting production.
- [x] Loads the active system's persisted profile library and draft state.
- [x] Captures, previews, confirms, saves and reopens both reference roles.
- [x] Visually edits all supported regions/landmarks with correct pixel coordinates.
- [x] Tests unsaved drafts without changing runtime selection or saved revisions.
- [x] Shows typed status, reason, evidence and measurements without fabricated
      confidence or misleading zero values.
- [x] Live evaluation handles fresh frames, errors and invalid images explicitly.
- [x] Saving creates a validated revision; selecting it is a separate explicit act.
- [x] Runtime uses the selected revision at the agreed snapshot boundary.
- [x] Can delete inactive revisions and profiles; blocks selected/in-use revisions,
      preserves shared assets and never silently switches runtime selection.
- [x] Failed saves/deletions leave surviving calibration/settings usable.
- [x] Unrelated settings and other robot systems' data remain unchanged.
- [x] Leaving/closing stops application-owned live work and releases resources;
      reopening and late worker completion are covered by tests.
- [x] Developer authorization and English/Bulgarian initial/retranslation work.
- [x] Model/controller tests use a stub; repository/worker/UI checks use temporary
      storage and fakes/offscreen Qt without physical hardware.
- [x] Compilation and focused regression checks pass before station acceptance.

Station acceptance separately verifies the actual camera resolution, reference
quality, region editing, measured offsets/rotation and lifecycle interaction with
production. Automatic hardware motion is not part of that application workflow.

## 10. Work boundaries

The user subsequently authorized implementation and confirmed section 4.
OpenProject changes, source publication and release builds remain outside this task.
Keep the existing local `.gitignore` change and unrelated artwork outside this
task's source changes.

## 11. Implementation and verification record

- Application: `src/robot_systems/paint/applications/paint_head_detector_setup/`.
- Portable contracts: `src/robot_systems/paint/contracts/paint_head_calibration/`.
- Shared library, adapters and run ownership: `src/robot_systems/paint/paint_head_calibration/`.
- User guide: [Detector setup application](../robot_systems/paint/applications/paint_head_detector_setup/README.md).
- Storage/runtime guide: [Calibration ownership](../robot_systems/paint/paint_head_calibration/README.md).
- The standalone runner and all automated verification use stubs, temporary
  storage, fake camera subscriptions or offscreen Qt. No hardware cycle was run.
- English and Bulgarian pages were rendered and inspected at 1280 × 900.
  Shared keyboard checks exercised typing, cursor movement and top/bottom field
  visibility above the popup.
- Verification: 241 focused calibration/head-check tests pass; strict typing
  passes across 57 source modules; 58 touched Python modules compile; all eight
  changed JSON catalogs validate. Ruff and whitespace checks pass.
- Physical station camera, image quality and production acceptance remain
  outstanding. No OpenProject changes, commit or publication were performed.
