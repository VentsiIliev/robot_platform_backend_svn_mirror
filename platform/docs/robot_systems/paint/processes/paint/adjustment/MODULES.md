# Module reference: `src/robot_systems/paint/processes/paint/adjustment`

[Package guide](README.md). Generated from source ASTs; no runtime imports.

## `__init__.py`

[Source](../../../../../../src/robot_systems/paint/processes/paint/adjustment/__init__.py).


## `incremental_painting.py`

[Source](../../../../../../src/robot_systems/paint/processes/paint/adjustment/incremental_painting.py).

- `run_incremental_paint_contact`: Compatibility adapter for operator-paced contact execution.
- `run_incremental_paint_contact_result`: Hold after every section; only an explicit Finish proceeds to dropoff.

## `session.py`

[Source](../../../../../../src/robot_systems/paint/processes/paint/adjustment/session.py).

- `AdjustmentStep`: See source for contract.
- `PaintPathCursor`: Consume a six-axis command path by Cartesian XYZ arc length.
- `AdjustmentPhase`: See source for contract.
- `AdjustmentSnapshot`: See source for contract.
- `NextPaintSection`: See source for contract.
- `FinishAdjustment`: See source for contract.
- `CancelAdjustment`: See source for contract.
- `PaintAdjustmentSession`: Single operator command slot with explicit inspect and finish states.

## `settings_serializer.py`

[Source](../../../../../../src/robot_systems/paint/processes/paint/adjustment/settings_serializer.py).

- `PaintAdjustmentSettingsSerializer`: See source for contract.
