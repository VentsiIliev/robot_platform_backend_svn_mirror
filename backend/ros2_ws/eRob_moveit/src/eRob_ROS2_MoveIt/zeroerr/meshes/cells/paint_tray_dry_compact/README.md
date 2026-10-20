# Compact paint tray meshes

All corrected and simplified meshes use millimeters, +Z up, and the origin at
the center of the four robot mounting holes on the upper mounting surface.

- `paint_tray_dry_compact.stl`: full-detail, corrected orientation and origin.
- `paint_tray_dry_compact.original.stl`: untouched source backup, before the transform.
- `paint_tray_dry_compact.transform.json`: coordinate transform and original hole dimensions.
- `paint_tray_dry_compact.surface_3levels.stl`: final surface approximation, 10 triangles.
- `paint_tray_dry_compact.surface_3levels_above.stl`: final surface plus simplified equipment, 262 triangles; used by the `paint_tray_dry` profile for collision geometry.
- `paint_tray_dry_compact.surface_3levels.json`: surface dimensions and approximation notes.
- `paint_tray_dry_compact.three_level_comparison.FCStd`: final self-contained FreeCAD overlay; detailed mesh blue, surface plus equipment orange, surface-only green (initially hidden). Select an object and press Space to toggle visibility.

The three surface heights are front tray +9 mm, mounting plate 0 mm, and dryer
-26 mm, joined by vertical steps. Small holes, lips, grille recesses and other
details are omitted. The surface meshes have zero thickness and do not define
a solid volume beneath the surface. The original backup uses its original coordinates.
