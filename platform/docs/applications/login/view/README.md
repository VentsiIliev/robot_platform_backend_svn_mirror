# `src/applications/login/view`

Qt widgets, user-action signals and data setters for the owning application.

`LoginView` places an animated WebGL fluid surface behind the native Qt login,
first-run and QR cards. `fluid_assets/index.html` owns the canvas and decorative
image bridge; `fluid.js` owns the simulation. Qt sends the displayed logo as a
PNG data URL and maps its coordinates through global screen space, avoiding
sibling-widget offsets after resize. Authentication and controller signals remain
native and unchanged.

The fluid assets are production resources, not optional demo files. Keep them in
the PyInstaller data list and frozen self-test whenever their paths change.

[Parent guide](../README.md).

<!-- source-navigation:start -->
## Source navigation

[Module reference](MODULES.md) — signatures, fields, imports and source links for every Python file in this directory.

[Complete source index](../../../SOURCE_INDEX.md).
<!-- source-navigation:end -->
