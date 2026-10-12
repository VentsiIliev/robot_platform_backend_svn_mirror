# `twin_robot` — Synchronized choreography composition

`TwinRobotSystem` owns choreography storage and two MVC applications: `TwinDashboard` and `ChoreographySetup`. It also declares Network Settings and an admin Software Update screen. It has empty shared robot service/settings/movement-group/work-area declarations in this checkout.

`on_start()` constructs `ChoreographyRepository` from system-owned choreography storage and shares it with dashboard/setup services. `set_twin_runtime(runtime)` injects the runtime/transport adapter and updates already-created services. `on_stop()` calls a callable runtime `stop()` and logs failures. The system does not construct its synchronized execution transport itself.

Choreography models, repository serialization and validation live in `storage/` and application service/model packages. Exact step/anchor/capability contracts are in their module references and `tests/robot_systems/twin_robot/`. UI availability does not establish that a runtime has been attached.

`TwinBootstrapProvider.build_robot()` supplies a `fake://local` ROS placeholder, but current `run_main.py` calls `build_configured_robot()` instead, returning the configured localhost ROS bridge. Startup does not attach a twin runtime. This integration limitation is recorded in [issues](../../CODE_ISSUES.md); the provider path should not be presented as the current startup execution path.

The package/product exists in `config/release_targets.json`, but the checked-in startup `supported_robot_systems` list omits it. Deployment or a standalone composition must explicitly configure selection and supply the runtime. Login/user/permission storage remains owned by this system.

## Update source

This system owns [storage/update_source.json](../../../src/robot_systems/twin_robot/storage/update_source.json),
selected through its `update_source` entry in `config/release_targets.json`.
The checked-in seed uses `feed` with remote updates disabled; existing station
`updates.json` files are preserved. See [per-system source configuration](../update_sources.md)
for URLs, authentication, trust and migration.

<!-- source-navigation:start -->
## Source navigation

[Module reference](MODULES.md) — signatures, fields, imports and source links for every Python file in this directory.

[Resource reference](RESOURCES.md) — non-Python files and their formats; values remain in the owning storage/source files.

| Source subdirectory | Guide |
|---|---|
| `applications/` | [applications](applications/README.md) |
| `domain/` | [domain](domain/README.md) |
| `runtime/` | [runtime](runtime/README.md) |
| `storage/` | [storage](storage/README.md) |

[Complete source index](../../SOURCE_INDEX.md).
<!-- source-navigation:end -->
