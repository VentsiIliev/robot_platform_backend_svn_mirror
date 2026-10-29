# `src/robot_systems/paint/applications/dashboard`

This page follows the source directory. The reference below records its modules and contracts; follow child guides for nested implementations.

[Parent guide](../README.md).

## Start diagnostics

The controller obtains a detached actor/action/operation token through its model
before Start confirmations or settings/readiness checks. The service owns engine
diagnostics and the model/interface carry plain dictionaries; views import no
recorder. Pending destination preparation and tray confirmation reuse that token.
Cancelled/rejected requests are visible, and an exception retains the original
error while its diagnostic observation records the traceback. Preparation workers
have an error signal so failures release the worker and restore the Start action.

Process admission is reported separately from execution completion. The process
captures the token into its worker; changing sessions does not reassign the run.
Other dashboard controls remain selectively instrumented. See the
[Paint diagnostics guide](../../diagnostics/README.md) for events/evidence and export.

## Start availability during stopping

The dashboard keeps the existing process-state display and disables Start while the previous production worker or hardware-stop worker is still active. `PaintDashboardService.load_state()` sets `can_start=False` during cleanup; process-state events and periodic dashboard refreshes apply this value to the button. Once both workers exit, the next refresh restores Start availability for `IDLE` or `STOPPED`. The process independently rejects premature starts, including calls outside the dashboard.

Process Status details show "Waiting for paint stopping to finish." during cleanup and "Stopping is taking longer than expected." after ten seconds. English and Bulgarian translations are provided. A delayed stop keeps Start disabled; there is no automatic restart or timeout bypass. See the [production guide](../../processes/paint/README.md) for cancellation and worker-lifetime behavior.

## Paint-head feedback

The optional [paint-head check](../../paint_head_check/README.md) reports through
a separate frameless modal popup. `ui/head_alignment_popup.py` composes the
reusable `PaintHeadAlignmentGuide` from `ui/head_alignment_guide.py`; the immutable
presentation DTOs and state mapping live in `head_alignment_presentation.py`.
The popup has one Close button and no native title bar or window controls.
Asynchronous modal opening keeps live feedback delivery active.

The card owns status and acquisition notices. MISALIGNED shows the schematic
target and correction cues; UNKNOWN greys the retained guide and disables cues;
MISSING additionally hides the head illustration. Fresh confirmed alignment turns
the guide green. No detector regions, landmarks, scores or numeric adjustment
measurements are shown. Closing dismisses only the message and does not start,
resume or cancel stopped-position guidance. Live updates do not reopen it until
a new failed check/session. Start, guidance end, dashboard exit and cleanup clear
stale popups.

The Camera tab keeps its ordinary feed and role selector. Head feedback neither
switches tabs/cameras nor changes camera rendering eligibility. A normal successful
check does not open a popup. The controller bridges typed CHECK, LIVE_GUIDANCE and
GUIDANCE_ENDED status events to the GUI, requests latest-status replay on load and
unsubscribes during stop. Paint and paint_tray_dry include English/Bulgarian strings.

<!-- source-navigation:start -->
## Source navigation

[Module reference](MODULES.md) — signatures, fields, imports and source links for every Python file in this directory.

| Source subdirectory | Guide |
|---|---|
| `assets/` | [assets](assets/README.md) |
| `controller/` | [controller](controller/README.md) |
| `model/` | [model](model/README.md) |
| `onboarding/` | [onboarding](onboarding/README.md) |
| `service/` | [service](service/README.md) |
| `ui/` | [ui](ui/README.md) |
| `view/` | [view](view/README.md) |

[Complete source index](../../../../SOURCE_INDEX.md).
<!-- source-navigation:end -->

## Navigation guard

Leaving is blocked while paint is running, paused or stopping, or finite dashboard workers are pending. The process query reads lifecycle state without hardware I/O. Camera feeds and continuous monitoring are excluded. Stop unlocks navigation only after production and hardware-stop workers finish.

## Operator onboarding tour

The Paint Dashboard opts into the shared onboarding capability through
`PaintDashboardView.start_onboarding_tour()`. While the dashboard is active, the
shell header displays a question-mark button. Hiding or cleaning up the dashboard
stops its window-level overlay.

Paint-owned steps live in
`applications/dashboard/onboarding/paint_dashboard_tour.py`; shared rendering and
navigation live in `src/applications/base/onboarding/`. The shell has no dependency
on paint code.

The tour covers:

1. Welcome — centered, with no spotlight
2. Tray and camera view
3. Drying Duration
4. Drying Time for the selected workpiece
5. Number of Passes
6. Process Scaling
7. Pass Speed
8. Resolved Velocity and Acceleration
9. Press Offset
10. Apply All
11. Paint Control
12. Machine controls
13. Run controls
14. Status and messages

Optional hidden targets are skipped. `PaintDashboardView.onboarding_target()`
routes stable logical IDs to `PaintPlateLayout`, `PaintControlsDrawer`, and the
dashboard panels, avoiding translated-text lookup and layout-index coupling.

The tour is modal. Operators can stop it with the touch-sized top-right close
button, Skip, or Escape. Back and Next/Finish are touch-sized, and arrow-key
navigation remains available.

Card text uses the `PaintDashboardOnboarding` translation context. English entries
currently live in `storage/translations/en.json`; adding matching source keys to
another language catalog localizes the tour without Python changes.
