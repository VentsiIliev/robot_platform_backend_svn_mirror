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

Each RobotSystem owns its source declaration in
`src/robot_systems/SYSTEM/storage/update_source.json`. Its entry in
`config/release_targets.json` names that file via `update_source`; omitting the
entry disables remote updates for that target. Packaging includes only the
selected system's declaration and validates its product identity. No robot's
repository URL is built into engine. See the
[per-system setup guide](../../robot_systems/update_sources.md).

`UpdateConfig` selects `feed`, `github`, `gitlab`, `svn`, or legacy `gitea` via
`repository_type`. A feed supplies `stable/latest.json` and its referenced
archive. GitHub and GitLab discover published complete releases tagged
`SYSTEM/robot/vVERSION`, ignoring other systems and component/support releases.
GitLab links must name `manifest.json`, its optional signature, and the archive;
its URL supports nested groups and an optional same-server `api_url` ending in
`/api/v4` for installations under a subpath. GitHub/GitLab private sources use a
machine-local `token_file`; API tokens are stripped on cross-origin redirects.
Legacy Gitea configurations remain readable for existing installations.

SVN is a versioned feed containing the same files as a normal feed, read with
`svn cat --non-interactive`. It requires the SVN client and the service user's
existing credential cache/trusted server certificate. Tokens in `token_file`
are not SVN passwords. SVN reads enforce size limits and an overall download
timeout; set `timeout_seconds` to suit archive transfer time. The client never
automatically accepts an untrusted certificate or prompts for credentials.
Absolute local feed folders support testing. HTTP requires explicit
`allow_insecure_http`; signed sources use the configured public key. Downloads
and extracted archives have size limits, identity validation and checksum checks.
Robot extraction permits only confined archive links required by bundled backend
libraries; platform-only extraction retains its own stricter format rules.

New tray-dryer bundles point to the SVN-backed GitHub mirror. Existing station
`updates.json` files are preserved: migrate `repository_type` and `repository_url`
there explicitly, retain the trusted public-key path, and replace any old Gitea
token with the appropriate GitHub token. A complete robot archive and manifest
must be published before GitHub can offer an update. The source mirror and
RustDesk releases alone are not complete robot releases. The existing tray-dryer
development seed retains its explicit unsigned-update opt-in; provision a public
key and disable that opt-in for signed production updates.

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
