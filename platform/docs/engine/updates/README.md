# Release installation and updates

The Qt-free, ROS-free updater supports platform-only releases and complete robot
releases. For complete-system operation, use
[the robot release guide](../../../packaging/robot/README.md).
[Platform-only operation](../../../packaging/platform/README.md) remains separate.

## Complete-system activation

The Software Update screen delegates check, download, queue and status requests
to a per-user systemd service over a local Unix socket. The service stages the
complete robot archive. It waits for the runtime locks to become available after
normal application shutdown, stops the current bundled backend, and activates
the exact platform/backend pair declared by the robot manifest. The stable
launcher waits for activation and reopens the application.

`PlatformUpdater.apply_pending()` validates candidate identity and version,
reconciles remote support, prepares migrated data and updater tools, then journals
the pointer/data changes. Interrupted activation is recovered before launching.
An activation error records a failed result and clears the pending request;
the previous robot release remains available. Application rollback restores the
previous component pair and its data snapshot.

For an existing installation, `remote_support.reconcile()` reads the candidate's
`platform/installation/remote-support/release.conf` as literal assignments and
compares `EXPECTED_VERSION` with the configured `rustdesk` package reported by
`dpkg-query`. A matching version skips installation. A mismatch invokes the
root-owned, source-restricted helper through noninteractive sudo. Failure blocks
activation. Older archives without this configuration skip reconciliation.
Initial provisioning installs the package and helper separately.

The support package is a machine-wide OS change. Application rollback does not
revert it. Kiosk updates are deferred: automatic updates preserve kiosk/session
and automatic-login settings rather than rerunning kiosk setup.

## Installed layout

```text
~/.local/share/robot-releases/paint_tray_dry/
    current -> releases/VERSION
    releases/VERSION/{platform,backend,manifest.json}
    launch.sh
    tools -> updater-tools/ID
    data/
    backups/
    updates.json
    update-state/
```

`data/` and `updates.json` are machine-owned and preserved across software updates.
`update-state/` contains locks, latest/staged/pending metadata, transaction and
rollback records, result status, and system/service provisioning markers.
The IPC socket is restricted to the desktop user. The service requires a running
user manager; the installer does not enable user lingering.

## Update sources and trust

`UpdateConfig` selects `feed` or `gitea` via `repository_type`. A feed supplies
`stable/latest.json` and its referenced archive; Gitea supplies complete robot
release attachments. Private Gitea sources use a machine-local `token_file`.
Absolute local feed folders support testing. HTTP requires explicit
`allow_insecure_http`; signed sources use the configured public key. Downloads
and extracted archives have size limits, identity validation and checksum checks.
Robot extraction permits only confined archive links required by bundled backend
libraries; platform-only extraction retains its own stricter format rules.

Remote support has a separate trust boundary: initial/maintenance provisioning
installs a root-owned helper and `/etc/robot-remote-support.json`, pinning its
HTTPS download base. A narrow sudoers command allows only helper upgrades.
The helper validates identifiers and package name, version, architecture and
maintainer before APT installation. The user service permits this elevation and
therefore does not use `NoNewPrivileges=true`. Release-owned installer scripts
are not executed by the automatic privileged helper. Changing the approved
source requires an administrator-authenticated installer run.

See [remote-support operation](../../../packaging/remote_support/README.md) for
configuration and bootstrap requirements, and [module responsibilities](MODULES.md).
