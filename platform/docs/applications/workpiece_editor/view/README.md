# `src/applications/workpiece_editor/view`

`WorkpieceEditorView` fixes the embedded contour editor's alternating-list
background through `BG_COLOR` from the shared platform palette. The point manager
enables alternating rows; explicitly styling `alternate-background-color` keeps
the Paint row light on machines whose system `AlternateBase` is dark. The list's
selection and action controls retain their existing behavior.

Qt widgets, user-action signals and data setters for the owning application.

[Parent guide](../README.md).

<!-- source-navigation:start -->
## Source navigation

[Module reference](MODULES.md) — signatures, fields, imports and source links for every Python file in this directory.

[Complete source index](../../../SOURCE_INDEX.md).
<!-- source-navigation:end -->
