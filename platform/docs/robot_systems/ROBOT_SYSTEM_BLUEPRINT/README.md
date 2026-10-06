# Robot-system blueprint

This template demonstrates the declaration and composition seams for a new robot system: metadata, settings/services, roles/folders/applications, bootstrap provider, targeting, calibration, height measuring and dashboard MVC. It is a template/demo, not an installed production system.

Start with the source-owned [robot-system guide](../../../src/robot_systems/ROBOT_SYSTEM_BLUEPRINT/ROBOT_SYSTEM_GUIDE.MD) and [settings guide](../../../src/robot_systems/ROBOT_SYSTEM_BLUEPRINT/settings/README.md). Replace placeholder names/IDs and declare the system in startup/release configuration. Runtime composition belongs in `on_start()`/`on_stop()` and providers; shared interfaces stay in engine/shared contracts.

The dashboard factory follows the shared application lifecycle, including controller retention and cleanup. Settings defaults are serializer contracts; persisted machine values belong to the new system's storage. Use the blueprint's demo runner/tests to establish a shared pattern before copying it into machine systems; inspect the runner before use because dependencies can vary.

<!-- source-navigation:start -->
## Source navigation

[Module reference](MODULES.md) — signatures, fields, imports and source links for every Python file in this directory.

[Resource reference](RESOURCES.md) — non-Python files and their formats; values remain in the owning storage/source files.

| Source subdirectory | Guide |
|---|---|
| `applications/` | [applications](applications/README.md) |
| `calibration/` | [calibration](calibration/README.md) |
| `domain/` | [domain](domain/README.md) |
| `height_measuring/` | [height_measuring](height_measuring/README.md) |
| `processes/` | [processes](processes/README.md) |
| `settings/` | [settings](settings/README.md) |
| `storage/` | [storage](storage/README.md) |
| `targeting/` | [targeting](targeting/README.md) |

[Complete source index](../../SOURCE_INDEX.md).
<!-- source-navigation:end -->
