# `tests/applications/base`

This page follows the source directory. The reference below records its modules and contracts; follow child guides for nested implementations.

[Parent guide](../README.md).

<!-- source-navigation:start -->
## Source navigation

[Module reference](MODULES.md) — signatures, fields, imports and source links for every Python file in this directory.

[Complete source index](../../../SOURCE_INDEX.md).
<!-- source-navigation:end -->

`test_navigation_guard.py` verifies factory wiring, submitted/blocked worker ownership, worker failure cleanup without an error callback, running/paused/stopping paint, cached-screen switches, close vetoes before cleanup, and initial/live English-Bulgarian warning translation. `test_jog_controller.py` verifies that ordered servo start/stop remains guarded until the stop completes.
