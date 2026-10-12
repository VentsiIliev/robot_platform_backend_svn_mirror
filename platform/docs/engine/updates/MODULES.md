# Update module responsibilities

Source directory: [src/engine/updates](../../../src/engine/updates/).

| Module | Responsibility |
| --- | --- |
| `config.py` | Machine-owned update-source configuration and validation |
| `updater.py` | Discovery, staging, offline activation, recovery and rollback |
| `releases.py` | Platform manifest validation, extraction and release identity |
| `robot_releases.py` | Exact platform/backend selection validation and robot archive extraction |
| `repository_releases.py` | Shared complete-release selection and manifest verification |
| `github_source.py` | GitHub repository release discovery and confined asset URLs |
| `gitlab_source.py` | GitLab project release links, nested groups and custom API roots |
| `svn_source.py` | Bounded, non-interactive SVN feed reads with cached station credentials |
| `gitea_source.py` | Compatibility discovery for existing Gitea station configurations |
| `service.py` | Local IPC client, per-user daemon and offline backend-stop/activation loop |
| `service_install.py` | User systemd unit installation and service marker |
| `remote_support.py` | Literal release configuration parsing and installed package version reconciliation |
| `migrations.py` | Explicit JSON data migrations |
| `factory_defaults.py` | Initial allowed settings defaults without overwriting live data |
| `files.py` | Atomic JSON, filesystem durability and cooperative locks |
| `environment.py` | Clean subprocess environment outside frozen applications |
| `paths.py` | Mutable robot-system paths independent of release code |

`PlatformUpdater.apply_pending(before_activation=None)` runs the optional callback
under offline locks before recovery/activation. The service uses this to stop the
current bundled backend. Candidate remote-support reconciliation runs before the
data/pointer transaction for an existing installation.

`remote_support.release_settings(release)` returns the required settings or `None`
for older archives without the config. `remote_support.reconcile(release)` skips a
matching configured package version and raises if a required upgrade fails.

Privileged package installation lives outside this package in the root-owned copy
of [update_package.py](../../../packaging/remote_support/update_package.py).
