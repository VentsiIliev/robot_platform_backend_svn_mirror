# `packaging/` — Releases, installation and deployment

Packaging creates/install product releases and support-service assets. It is separate from application runtime startup.

- [Platform packaging](../../packaging/platform/README.md) is the deployment guide for signed artifacts, update compatibility, factory defaults, migration and rollback.
- [Release workflow](../../packaging/robot/README.md) describes product release preparation.
- [Per-system sources](../robot_systems/update_sources.md) describes GitHub, GitLab, SVN and feed URLs and installed configuration migration.
- [Legacy Gitea Actions](../../packaging/platform/GITEA_ACTIONS.md) is retained as historical reference; current publication uses SVN and GitHub.
- [Remote support](../../packaging/remote_support/README.md) describes initial provisioning and version reconciliation through a restricted privileged helper.
- [Root packaging guide](../../packaging/README.md) covers the packaging layout and entry points.

`config/release_targets.json` provides product/profile/package identity and the path to each system-owned update declaration. Packaging includes only the selected system's source; installed machine settings remain independent and are preserved on update. `src/engine/updates/` provides the runtime updater; `src/applications/software_update/` provides its admin UI. Do not confuse packaging scripts with application factories or machine processes. Source references below cover every packaging Python module; shell scripts, units, manifests and templates remain documented in the deployment guides.

<!-- source-navigation:start -->
## Source navigation

[Module reference](MODULES.md) — signatures, fields, imports and source links for every Python file in this directory.

[Resource reference](RESOURCES.md) — non-Python files and their formats; values remain in the owning storage/source files.

| Source subdirectory | Guide |
|---|---|
| `robot/` | [Complete robot releases](../../packaging/robot/README.md) |
| `runtime/` | [Installed runtime](../../packaging/runtime/README.md) |
| `shared/` | [Shared packaging helpers](../../packaging/shared/README.md) |
| `kiosk/` | [Kiosk setup](../../packaging/kiosk/README.md) |
| `platform/` | [platform](platform/README.md) |
| `remote_support/` | [remote_support](remote_support/README.md) |

[Complete source index](../SOURCE_INDEX.md).
<!-- source-navigation:end -->
