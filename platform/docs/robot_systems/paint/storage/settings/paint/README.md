# `src/robot_systems/paint/storage/settings/paint`

System-owned persistent data, defaults, calibration artifacts or catalogs. Resolve this directory through the owning system's storage helpers; installed writable data may be relocated by `ROBOT_PLATFORM_DATA_ROOT`. Shared implementation does not make these files interchangeable between machines/profiles.

`head_detector.json` is the optional system-owned detector profile catalog,
persisted drafts, immutable revisions and exact runtime selection. Reference PNG
assets live under the same system's `storage/calibration/paint_head/references/`.
See [the calibration lifecycle guide](../../../paint_head_calibration/README.md).

[Parent guide](../README.md).

<!-- source-navigation:start -->
## Source navigation

[Resource reference](RESOURCES.md) — non-Python files and their formats; values remain in the owning storage/source files.

[Complete source index](../../../../../SOURCE_INDEX.md).
<!-- source-navigation:end -->
