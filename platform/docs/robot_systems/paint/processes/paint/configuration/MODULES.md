# Module reference: `src/robot_systems/paint/processes/paint/configuration`

[Package guide](README.md). Generated from source ASTs; no runtime imports.

## `__init__.py`

[Source](../../../../../../src/robot_systems/paint/processes/paint/configuration/__init__.py).


## `models.py`

[Source](../../../../../../src/robot_systems/paint/processes/paint/configuration/models.py).

- `PickupContactMode`: See source for contract.
- `PickupSensorExecutionMode`: See source for contract.
- `MagazinePickupMode`: See source for contract.
- `MagazineProcessingStrategy`: See source for contract.
- `DropoffStrategy`: See source for contract.
- `normalize_pickup_contact_mode`: See source for contract.
- `normalize_magazine_pickup_mode`: See source for contract.
- `PickupMotionConfig`: Pickup/staging motion tuning.
- `PaintContactStagingConfig`: Plane-aware offsets used immediately before and after paint contact.
- `UnmatchedSecondPassConfig`: Optional second coat for captured contours that were not library-matched.
- `PaintEdgeCleanupConfig`: Optional XY/RZ cleanup pass tuning used after XZ/RY paint.
- `PaintDropoffConfig`: Dropoff/release motion tuning after paint and Joint 6 unwind.
- `PaintMagazineLoadConfig`: Optional pre-run transfer from magazine capture station to calibration table.
- `PaintSafeTravelConfig`: Optional safe waypoints used while carrying the workpiece from calibration to paint.
- `PaintToDropoffSafeTravelConfig`: Optional safe waypoints used while carrying the workpiece from paint to dropoff.
- `PaintNavigationReturnConfig`: Navigation-return motion tuning for paint-system cleanup moves.
- `PaintProjectionTuning`: Numeric tuning values for projected paint-path geometry.
- `PaintMotionPlaneSpec`: Axis and orientation mapping for one supported paint motion plane.
- `PaintProjectionRules`: Projection-time domain mappings used by `PaintSimulationConfig`.
- `PaintPivotProfile`: Derived low-level pivot settings consumed by the paint executor.
- `PaintProcessConfig`: Single source of truth for platform-side paint process behavior.
- `scale_paint_process_accelerations`: Return a cycle-local config with every configured acceleration scaled.
- `PaintSimulationConfig`: Normalized settings that control projected paint motion geometry.

## `serializer.py`

[Source](../../../../../../src/robot_systems/paint/processes/paint/configuration/serializer.py).

- `_section`: See source for contract.
- `_build_dataclass`: See source for contract.
- `PaintProcessConfigSerializer`: See source for contract.
- `_normalize_group_ids`: See source for contract.
- `_normalize_magazine_sources`: See source for contract.

## `service.py`

[Source](../../../../../../src/robot_systems/paint/processes/paint/configuration/service.py).

- `IPaintProcessConfigService`: See source for contract.
- `PaintProcessConfigService`: Runtime access point for persisted Paint process settings.
