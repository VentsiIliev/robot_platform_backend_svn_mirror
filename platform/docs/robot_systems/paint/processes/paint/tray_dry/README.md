# Tray placement and occupancy

`plate_layout.py` owns placement configuration, geometry, reservation records and `PlateLayoutService`. Allocation reserves space before release; commit makes a reservation an occupied placement. Cancel/remove/clear affect occupancy separately from commanding motion. Footprints conservatively represent occupied geometry; normalized workpiece outlines support visualization.

The dashboard and dropoff executor share one service instance. New Tray is blocked while running, paused, stopping, or while a reservation remains active; individual committed placement removal is currently allowed during production. Occupancy is runtime state, not a persistent record restored after restart. System profile restrictions determine whether plate layout is an allowed strategy.

On application startup the tray readiness is `UNKNOWN`: an empty physical tray is not assumed and occupancy is not persisted. Pressing Start in tray or alternating demo mode prompts “Tray is empty — Start” / “Cancel”. Only an explicit confirmation initializes the empty layout and continues that start. Cancel or dismiss leaves the tray unknown. A confirmed tray stays ready for subsequent starts in the same application instance. Automatic-only production does not require a tray confirmation.

`TrayConfirmationRequiredError`, `TrayBusyError`, `TrayLayoutChangedError`, and `TrayUnavailableError` carry stable `TrayErrorCode` values and convert to immutable `TrayFailure` records. Dashboard confirmation returns the existing `DashboardCommandResult` with an optional typed failure; successful results cannot contain a failure. Process starts, direct production, and reservation allocation also enforce readiness, so non-UI starts cannot bypass confirmation. Paint execution retains typed failures in its context and runs its existing error terminal handler; the process exposes `last_failure`.

Changed layout geometry/spacing cannot discard existing occupancy or a pending reservation. The operator must physically empty the tray and explicitly confirm New Tray before using an incompatible layout. Individual committed workpiece removal remains allowed during production. Release sensor verification remains intentionally skipped; this confirmation change does not change release timing or blow-off behavior.

Review bounds, margins, release offsets, pending reservation and commit/cancel behavior in the module reference before changing tray planning.

`reserve_result()` distinguishes `Ready[PlateDropoffReservation]`, a `TRAY_FULL` outcome and a categorized invalid-configuration failure. The tuple-returning `reserve()` remains an adapter. Production decides full-tray termination from the outcome rather than the text. The complete plate exit route is constructed before entry motion or release, so a missing exit profile cannot be discovered after placing a workpiece. Release verification remains intentionally skipped.

<!-- source-navigation:start -->
## Source navigation

[Module reference](MODULES.md) — signatures, fields, imports and source links for every Python file in this directory.

[Complete source index](../../../../../SOURCE_INDEX.md).
<!-- source-navigation:end -->
