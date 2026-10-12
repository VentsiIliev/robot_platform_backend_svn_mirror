# `config/` — Deployment and startup configuration

[platform.json](../../config/platform.json) selects the robot system, UI flags, ROS launch/stop scripts and the selected system's backend/profile/version identity. The current checkout selects `paint_tray_dry`; `supported_robot_systems` lists `glue`, `paint`, `paint_auto_dry`, `paint_tray_dry`, and `welding`. Being packaged is different from being enabled in this file: twin-robot code and product metadata also exist.

[release_targets.json](../../config/release_targets.json) maps each release target to its product, profile, storage-system name and included robot-system packages. Its optional `update_source` field points to that system's `src/robot_systems/SYSTEM/storage/update_source.json`; omitting it disables remote updates. The paint variants include both shared `paint` and their variant package; they own separate storage and update declarations. [updates.example.json](../../config/updates.example.json) is the generic machine configuration example and is disabled. The former central `config/update_sources/` files have moved into the owning system packages; see [provider URLs and migration](../robot_systems/update_sources.md).

`factory_defaults/` contains product/profile seed data. The updater/startup factory-default service creates missing files and preserves existing files. These templates include machine settings and are distinct from Python serializer defaults. See [updates](../engine/updates/README.md) for seeding, compatibility and activation details.

Configuration is not a global mutable store: settings serializers and `SettingsSpec.storage_key` define runtime file ownership. Installed systems can relocate writable data with `ROBOT_PLATFORM_DATA_ROOT`. Do not copy a paint variant's data into another system merely because it shares implementation.

For startup field types/defaults and validation see [bootstrap](../bootstrap/README.md). For signed releases, OS/ROS requirements and installation see [platform packaging](../../packaging/platform/README.md).

<!-- source-navigation:start -->
## Source navigation

[Resource reference](RESOURCES.md) — non-Python files and their formats; values remain in the owning storage/source files.

| Source subdirectory | Guide |
|---|---|
| `factory_defaults/` | [factory_defaults](factory_defaults/README.md) |
| System-owned update declarations | [GitHub, GitLab, SVN and feeds](../robot_systems/update_sources.md) |

[Complete source index](../SOURCE_INDEX.md).
<!-- source-navigation:end -->
