# Tray placement and occupancy

`plate_layout.py` owns placement configuration, geometry, reservation records and `PlateLayoutService`. Allocation reserves space before release; commit makes a reservation an occupied placement. Cancel/remove/clear affect occupancy separately from commanding motion. Footprints conservatively represent occupied geometry; normalized workpiece outlines support visualization.

The dashboard and dropoff executor share one service instance. New Tray is process-state guarded by the dashboard service; individual committed placement removal is currently allowed during production. Occupancy is runtime state, not a persistent record restored after restart. System profile restrictions determine whether plate layout is an allowed strategy.

Review bounds, margins, release offsets, pending reservation and commit/cancel behavior in the module reference before changing tray planning.

<!-- source-navigation:start -->
## Source navigation

[Module reference](MODULES.md) — signatures, fields, imports and source links for every Python file in this directory.

[Complete source index](../../../../../SOURCE_INDEX.md).
<!-- source-navigation:end -->
