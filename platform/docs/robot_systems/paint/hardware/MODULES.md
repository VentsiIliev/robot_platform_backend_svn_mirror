# Module reference: `src/robot_systems/paint/hardware`

[Package guide](README.md). Generated from source ASTs; no runtime imports.

## `__init__.py`

[Source](../../../../src/robot_systems/paint/hardware/__init__.py).

Paint-specific hardware adapters.


## `paint_head_availability_adapter.py`

[Source](../../../../src/robot_systems/paint/hardware/paint_head_availability_adapter.py).

- `PaintHeadAvailabilityAdapter`: Devices-app toggle for the paint head; does not touch hardware.

## `paint_head_device.py`

[Source](../../../../src/robot_systems/paint/hardware/paint_head_device.py).

- `PaintHeadRangeError`: A requested paint-head target exceeds its configured safe range.
- `PaintHeadDevice`: Apply paint-head presets or relative degree moves and verify writes.

## `vacuum_control.py`

[Source](../../../../src/robot_systems/paint/hardware/vacuum_control.py).

- `PaintVacuumControl`: Apply paint pickup/release policy to the platform vacuum controller.
