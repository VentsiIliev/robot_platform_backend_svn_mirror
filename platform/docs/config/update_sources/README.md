# Former central update-source configuration

The JSON declarations have moved into each RobotSystem package at
`src/robot_systems/SYSTEM/storage/update_source.json`. Build targets point to
these files via `update_source` in `config/release_targets.json`.

See [per-system source configuration](../../robot_systems/update_sources.md)
for provider URLs, machine-owned settings and migration.
