# Paint-head detector setup

`PaintHeadDetectorSetup` is a Manufacturer-only application in **Development**.
It opens without a production cycle and never moves the robot. Its fixed
inspection context is **Primary vision + Vertical Shaft Alignment**; multiple
profiles can describe different heads or station calibrations at that point.
It is separate from `paint_head_settings`, which configures the peripheral.

## Working with calibration

1. Choose a profile or create a new one. New profiles start as incomplete drafts.
2. In **Camera & capture**, position the head manually and capture the present and
   missing references. Review each image and confirm its role before accepting it
   into the draft. Preview buttons reopen the draft's stored images.
3. In **Regions & landmarks**, draw or select the inspection region, empty-mount
   region, exclusions and landmarks. Move or resize in original image pixels;
   pan/zoom does not change saved coordinates. Landmark properties include role,
   rectangle/circle support, threshold, required state, orientation invariance and
   the optional template rotation limit.
4. Use **Test & results** for a single frozen-frame test or continuous evaluation.
   Both use the working draft, including unsaved edits. The image shows status
   and match overlays; the panel shows confirmed/observed state, reason, usable
   image state, held warning, available alignment measurements and match scores.
   Unavailable/stale frames clear the previous result. There is no invented
   overall confidence percentage; translation is measured in pixels, not mm.
5. **Settings** edits alignment/confirmation, matching and preprocessing settings
   in the draft, with the camera and current result alongside the controls.
   Opening Settings automatically starts live evaluation; **Live preview** pauses
   or resumes it. Each edit is evaluated from the unsaved draft on fresh frames,
   resetting confirmation for the new settings. Invalid settings show an evaluation
   error and recover after correction. Saving and runtime selection stay separate.
   Existing detector validation is applied when testing or saving a revision;
   recognition algorithms are unchanged.

**Save draft** persists incomplete work. **Save calibration** validates and
creates an immutable numbered revision. **Select for runtime** explicitly selects
one saved revision. Saving or testing never changes runtime selection. The
editing profile, draft state and runtime selection are shown separately.

Unsaved navigation offers Save draft / Discard / Cancel. Choosing Save persists
before navigation is retried. Editing a saved revision asks before replacing a
different persisted draft. Deleting a profile or revision requires confirmation;
selected or in-use revisions are protected. Revision numbers are never reused.

The screen groups profiles, references, editor tools and inspection results in
shared-style cards. Tables reserve room for profile/landmark names and show full
values in tooltips. The editor places coordinates in two columns and shows an
instruction until an object is selected. Settings use a scrollable control column
beside a persistent camera/result column, with zoom and fullscreen preview.
Advanced matching and Advanced preprocessing expand on demand. Numeric precision
and detector behavior are preserved.

Live preview uses the same evaluation mode as **Test & results**. Pausing it on
Settings is reflected on the test page; opening Settings again starts it again.
Scrolling, typing or using the touch steppers keeps the preview beside the
controls. Editing resets the evaluation generation, so a result from the previous
settings cannot replace the new draft's feedback. Camera errors and invalid draft
settings have distinct unavailable messages.

All text and numeric inputs use the shared virtual keyboard controls. The view
supports English/Bulgarian initial translation and language changes. User names,
profile descriptions, landmark names and raw failure details remain data.

## MVC boundaries and lifecycle

Source: `src/robot_systems/paint/applications/paint_head_detector_setup/`.

| Component | Responsibility |
|---|---|
| `service/i_paint_head_detector_setup_service.py` | Typed application port; no Qt, detector or platform service imports |
| `service/paint_head_detector_setup_application_service.py` | Adapter over the shared library, frame source and editor evaluator |
| `model/paint_head_detector_setup_model.py` | Qt-free draft/selection state and evaluation generation |
| `model/editing.py` | Immutable geometry/landmark edits |
| `controller/paint_head_detector_setup_controller.py` | Signal wiring, serialized background work, latest-only live polling and late-result rejection |
| `view/` | Shared-style widgets, image coordinate editing and presentation |
| `view/styles.py` | Application styling composed from shared platform style constants |
| `view/widgets/result_panel.py` | Shared full/compact result display for Test and Settings |
| `paint_head_detector_setup_application_factory.py` | Standard platform MVC construction |

Camera activation, PNG encoding/writes, catalog I/O and evaluation run off the
GUI thread. The camera source subscribes to the existing primary vision owner;
it never opens another camera handle. Hiding the screen stops polling and
unsubscribes, including late preview activation. Destroying it joins its workers,
resets evaluator state and releases reference ownership. The shared camera owner
remains available to other consumers.

Persistence and runtime selection are described in
[Calibration storage and runtime ownership](../../paint_head_calibration/README.md).
Production policies and the operator popup are described in
[Paint-head checks](../../paint_head_check/README.md).

## Hardware-free verification

Run the standalone screen from the platform root:

```bash
.venv/bin/python -m src.robot_systems.paint.applications.paint_head_detector_setup.example_usage
```

The runner uses an in-memory stub and synthetic camera image. It does not connect
to a robot or modify station calibration. Focused automated checks:

```bash
QT_QPA_PLATFORM=offscreen .venv/bin/python -B -m unittest discover \
  -s tests/robot_systems/paint -p 'test_head_*.py' -q
```

Tests cover model/controller behavior with a stub, temporary real repositories,
capture/save/reopen, bundled import, typed failures, reference retention, camera
metadata, runtime/guidance ownership, registration and both translation paths.
UI regressions also cover persisted profile-ID selection, automatic Settings
preview before/after asynchronous load, unsaved tuning changes, pause/re-entry,
evaluation-error recovery and rejection of late results after an edit.
Live station camera, lighting and physical adjustment still require acceptance
on the target robot.
