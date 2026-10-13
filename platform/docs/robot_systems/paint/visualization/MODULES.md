# Module reference: `src/robot_systems/paint/visualization`

[Package guide](README.md). Generated from source ASTs; no runtime imports.

## `__init__.py`

[Source](../../../../src/robot_systems/paint/visualization/__init__.py).

Paint-system visualization data providers; no robot execution.


## `i_paint_preview_geometry.py`

[Source](../../../../src/robot_systems/paint/visualization/i_paint_preview_geometry.py).

Replaceable provider of editor preview geometry.

- `IPaintPreviewGeometry`: Compute display geometry without executing robot or hardware commands.

## `paint_preview_geometry.py`

[Source](../../../../src/robot_systems/paint/visualization/paint_preview_geometry.py).

Calculate editor preview geometry using shared paint projection mathematics.

- `project_pivot_paths_for_editor`: Project editor-visible pivot center paths for each prepared execution job.
- `project_pivot_motion_snapshots_for_editor`: Return per-step projected shape snapshots for pivot motion plotting.
- `PaintPreviewGeometry`: Default preview provider, injected with planning inputs rather than a process.
