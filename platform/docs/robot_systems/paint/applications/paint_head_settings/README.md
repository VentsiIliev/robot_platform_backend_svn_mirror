# `src/robot_systems/paint/applications/paint_head_settings`

This panel edits paint-head direction, preset spacing and preset count while preserving the peripheral binding. Settings saves run through `BackgroundWorker`.

`PaintHeadSettingsController` implements `IApplicationController`, including `has_active_operations()`. It reports submitted save workers as active until their GUI-thread cleanup completes. The Devices controller includes this panel's status in its navigation/shutdown guard, so leaving the screen or closing the shell waits for an active save and an idle panel no longer raises an attribute error. `stop()` marks the controller inactive and joins its workers.

Regression coverage in `tests/robot_systems/paint/test_paint_head_settings.py` exercises the Devices guard with the actual paint-head controller, checking idle, active-worker and completed-worker states.

[Parent guide](../README.md).

<!-- source-navigation:start -->
## Source navigation

[Module reference](MODULES.md) — signatures, fields, imports and source links for every Python file in this directory.

[Complete source index](../../../../SOURCE_INDEX.md).
<!-- source-navigation:end -->
