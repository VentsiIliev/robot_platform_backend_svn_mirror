# `packaging/` — Releases, installation and deployment

Packaging creates/install product releases and support-service assets. It is separate from application runtime startup.

- [Platform packaging](../../packaging/platform/README.md) is the deployment guide for signed artifacts, update compatibility, factory defaults, migration and rollback.
- [Release workflow](../../packaging/robot/README.md) describes product release preparation.
- [Gitea Actions](../../packaging/platform/GITEA_ACTIONS.md) describes release automation.
- [Remote support](../../packaging/remote_support/README.md) describes restricted socket/systemd deployment.
- [Root packaging guide](../../packaging/README.md) covers the packaging layout and entry points.

`config/release_targets.json` provides product/profile/package identity. `src/engine/updates/` provides the runtime updater; `src/applications/software_update/` provides its admin UI. Do not confuse packaging scripts with application factories or machine processes. Source references below cover every packaging Python module; shell scripts, units, manifests and templates remain documented in the deployment guides.

<!-- source-navigation:start -->
## Source navigation

[Module reference](MODULES.md) — signatures, fields, imports and source links for every Python file in this directory.

[Resource reference](RESOURCES.md) — non-Python files and their formats; values remain in the owning storage/source files.

| Source subdirectory | Guide |
|---|---|
| `paint_config/` | [paint_config](paint_config/README.md) |
| `platform/` | [platform](platform/README.md) |
| `remote_support/` | [remote_support](remote_support/README.md) |

[Complete source index](../SOURCE_INDEX.md).
<!-- source-navigation:end -->
