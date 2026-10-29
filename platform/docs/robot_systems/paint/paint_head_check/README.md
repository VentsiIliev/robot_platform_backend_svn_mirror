# Paint-head checks and operator guidance

Paint-head inspection is an optional checkpoint before a scheduled paint cycle.
It is **disabled by default**. The primary camera inspects the head at the taught
shaft-alignment position. Normal painting does not run a continuous head monitor;
there is no check at drop-off or on the return trajectory. The implementation is
shared by the paint variants, with settings owned by the active system.

## Configuration and scheduling

Use **Paint process settings** to enable checks, select frequency, set the timeout
and configure each reaction. The serializer persists `head_check` inside
`storage/settings/paint/process.json` (`SettingsID.PAINT_PROCESS_CONFIG`). Existing
station settings take precedence over these factory defaults:

```json
{
  "head_check": {
    "enabled": false,
    "policy_id": "every_cycle",
    "interval_cycles": 1,
    "timeout_seconds": 1.0,
    "present_action": "continue",
    "missing_action": "stop",
    "misaligned_action": "stop",
    "unknown_action": "report_only",
    "failure_action": "report_only",
    "timeout_action": "report_only",
    "report_until_confirmed": true
  }
}
```

| Policy ID | Scheduled checks |
|---|---|
| `every_cycle` | Before each painted workpiece |
| `first_cycle` | Before the first painted workpiece after each accepted Start |
| `first_then_interval` | First, then every N completed painted workpieces; N=5 checks workpieces 1, 6, 11 |

A new accepted Start creates fresh progress and a configuration snapshot.
Pause/resume retains the session. Stopped/failed checks do not satisfy the
checkpoint; only completed painting advances the count. Dry-run and adjustment
modes also check. Pickup-only bypasses checks. Disabling the feature prevents
inspection motion and acquisition.

| Response | Effect |
|---|---|
| `continue` | Satisfy the checkpoint and continue production |
| `report_only` | Report and continue; with `report_until_confirmed`, UNKNOWN waits for confirmation within the same timeout |
| `retry` | Acquire another observation within the current bounded window |
| `pause` | Pause at the checkpoint; it remains due on resume |
| `stop` | End in STOPPED; Start retries without Reset |
| `reject` | End in ERROR; Reset is required before Start |

Acquisition failures and timeout have separate reactions from head states.
`retry` is invalid as a timeout reaction; it cannot extend an expired window.
Timeout does not erase the last detected state, so a retained MISSING/MISALIGNED
state and timeout notice can both appear.

## Position and process call site

The mandatory taught group is **Vertical Shaft Alignment**
(`MovementGroupID.VERTICAL_SHAFT_ALIGNMENT`). Its pose, enabled state, velocity,
acceleration and motion type must be valid. Invalid configuration raises a typed
inspection-target error before startup motion. There is no default or fallback
pose. Camera selection is fixed to `CameraRoleID.PRIMARY_VISION`.

Startup routes due checks to `BEFORE_CYCLE_HEAD_CHECK`. The call site is
`src/robot_systems/paint/processes/paint/workflow/handlers/workflow/head_check_handler.py`,
in `handle_before_cycle_head_check()`, which calls the run's
`check_before_cycle(control)` through `IPaintHeadCheckRun`. Registration lives in
`workflow/machine_factory.py`; initial routing is in
`workflow/handlers/lifecycle/startup_handler.py`. After success, the configured
production/calibration return route runs before pickup/painting. A stopped check
leaves the robot at the inspection position.

Start after an inspection stop may reuse that position, skipping already completed
startup recovery/unwind and approach. Reuse requires fresh stationary feedback,
the unchanged taught target/reference frame and agreement with both retained
actual position and target within **0.5 mm / 0.2 degrees**. Cached pose alone is
insufficient. Invalid/changed feedback selects normal startup; a change after
preparing the shortcut fails explicitly before acquisition.

## Camera and detector boundary

`PrimaryVisionPaintHeadInspector` consumes raw frames from the existing camera
owner and never opens another camera. `CameraFrameMetadata` carries sequence and
monotonic capture time. Stale, duplicate, out-of-order and invalid frames cannot
become fresh observations. The inspector keeps only the latest pending frame;
evaluation runs on its worker rather than the broker callback. Subscriptions and
buffers are released on every exit.

`PaintHeadDetectorAdapter` maps the [image-only detector](../paint_head_detection/README.md)
into typed observations, failures and schematic correction directions. Composition
currently creates `PaintHeadDetector()` with bundled calibration/configuration.
Verify it against the station camera and inspection pose before enabling checks;
process settings do not teach detector calibration.

## Live adjustment and dashboard

A MISALIGNED check ending in STOP arms a separate read-only guidance session after
the process and stop cleanup finish. Timeout STOP can also arm it when the last
observation was misaligned. The session owns a separate inspector and detector
confirmation history. It updates through PRESENT, UNKNOWN and MISSING without
resuming production or satisfying a future check.

Fresh stationary feedback and the unchanged target are checked before and after
evaluation. Start, robot movement, invalid feedback, disabled settings, pickup-only
configuration or shutdown cancels/ends guidance. Cancelled results cannot overwrite
a new inspection. Camera faults disable corrections and can recover on fresh
frames while the position guard remains valid. Dashboard tab changes and popup
dismissal do not stop guidance.

The dashboard shows an illustrated **frameless modal popup**, independent of the
Camera tab, with no native title bar/window controls and one Close button. It opens
asynchronously so live updates continue while other dashboard input is blocked.
Close only dismisses the message; retry uses the normal Start control afterward.

State text and acquisition notices appear inside the card. A schematic head,
target zone and arrows guide adjustment without numeric pixel/angle instructions,
detector landmarks, regions or scores. UNKNOWN retains the last illustration and
marker in grey with correction disabled. MISSING hides the head image and keeps
the disabled target card. Fresh confirmed alignment enables green feedback;
unknown frames cannot preserve stale green.

Warnings open the popup once per check/session. Live updates and language changes
do not reopen a dismissed popup; a new failed check can open it again. A normal
successful PRESENT check does not open it. Start/new inspection, guidance ending,
dashboard exit and cleanup dismiss stale feedback. The Camera tab keeps its normal
full-width feed and role selector, without head status labels, guide, feed toggle
or automatic tab/camera switching.

The reusable card is `applications/dashboard/ui/head_alignment_guide.py`; the
dialog is `ui/head_alignment_popup.py`. Immutable presentation DTOs live in
`head_alignment_presentation.py`. English and Bulgarian catalogs are supplied for
paint and paint_tray_dry.

## Contracts and extension seams

| Component | Responsibility |
|---|---|
| `contracts/paint_head_check/` | Typed values, results, errors, correction DTOs and narrow ports |
| `IPaintHeadCheckPolicy` | Pure scheduling from immutable `HeadCheckProgress` |
| `PaintHeadCheckSession` | Completed-workpiece count and checkpoint ownership |
| `IPaintHeadReactionPolicy` | Typed decisions from observations/failures, without I/O |
| `PaintHeadCheckCoordinator` | Bounded acquisition, cancellation, pause and reactions |
| `IPaintHeadInspector` | Detector-independent observation lifecycle |
| Target/motion/retry-position ports | Validated positioning and conservative reuse |
| `IPaintHeadCheckObserver` | Reporting side effects independent of policies |
| `PaintHeadLiveGuidance` | Separately owned, cancellable stopped-position feedback |

To add frequency behavior, implement `IPaintHeadCheckPolicy.evaluate()`, assign a
stable `HeadCheckPolicyId`, and explicitly register its description/factory in
`policy_registry.py`. Settings choices use registry descriptions; add translated
labels and tests for count boundaries and Start/resume. This seam uses no
class-name strings, reflective imports or attribute injection.

For custom reactions, inject an `IPaintHeadReactionPolicy` returning existing
typed decisions. A new action kind also needs explicit coordinator, settings and
localization handling. Replace the detector through an inspector or image-side
evaluator adapter; policies and process handlers do not import detector results
or NumPy.

Expected boundary exceptions derive from `PaintHeadCheckError`, carrying
`HeadInspectionFailure` and `HeadInspectionFailureCode`. Contract violations use
`PaintHeadContractError`. Immutable tagged results distinguish success, failure,
pause, cancellation, stop and rejection. Messages never select workflow branches.
Dashboard status/replay events are paint-owned in
`contracts/events/paint_head_check_events.py`.

## Verification

`tests/robot_systems/paint/test_head_check_*.py` covers policies, settings, targets,
freshness, detector mapping, deadlines/reactions, routing, retry positioning,
guidance cancellation and modal/card behavior. Shared camera tests are
`tests/engine/vision/test_camera_stream_publisher.py` and `test_vision_service.py`.
Qt checks run offscreen with one retained QApplication. Station acceptance still
needs to verify calibration, correction direction and physical trajectories.
