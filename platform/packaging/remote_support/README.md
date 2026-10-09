# Ubuntu boot-managed remote support

The platform installer and source `launch_robot_app.sh --setup-only` install
OpenSSH server and the bundled PL PROJECT RustDesk build. Both system services
are enabled at boot and started immediately. The platform has no Remote Support screen or password-management controls.
Manage RustDesk passwords outside the platform; the shell retains its active
remote-session indicator.

Run the provisioning step independently as follows:

```bash
sudo bash packaging/remote_support/install.sh ROBOT_UI_USER \
  --vendor-installer packaging/remote_support/install_pl_remote_support.sh
```

Release bundles contain the equivalent payload at `installation/remote-support`.
Downloads require network access and administrator privileges. Existing SSH
configuration and RustDesk credentials/relay settings remain in place. The
installer validates SSH configuration and checks both services are active;
errors stop installation and rerunning retries provisioning.

Migration disables the old controller socket, controller service, expiry timer
and expiry service, and removes its RustDesk ExecCondition drop-in. Old state
files are retained but no longer control remote access. This also migrates
machines previously configured OFF. No GUI or robot process is started by this
step. The system RustDesk service provides remote access independently of the
platform application.

Verify on the target machine:

```bash
systemctl is-enabled ssh.service rustdesk.service
systemctl is-active ssh.service rustdesk.service
journalctl -u ssh.service -u rustdesk.service --no-pager -n 100
```

Reboot and verify SSH login and a RustDesk connection, including at the X11
login screen and inside kiosk mode. Existing firewall rules still apply. A saved
RustDesk `stop-service` option can prevent startup; the installer reports a
service failure rather than silently rewriting its credentials or configuration.

The packaged vendor installer reads `release.conf` beside its script. Edit that
file to set `DOWNLOAD_BASE_URL`, `RELEASE`, `PACKAGE` and `EXPECTED_VERSION`.
The download URL is `DOWNLOAD_BASE_URL/RELEASE/PACKAGE`; package verification
checks the configured expected version. The payload bundles this configuration,
so changes apply to newly built robot releases. Existing archives and installed
payloads retain their original configuration.

`release.conf` uses literal Bash assignments (no variable expansion or commands)
and is sourced by the privileged installer;
keep it with the trusted installer files. Copy it alongside the script when
running the vendor installer manually. A missing or incomplete config stops
before provisioning. Alternate vendor scripts with their own adjacent
`release.conf` bundle that file; otherwise the project config is copied.

The packaged vendor installer is pinned to the configured release. Build payloads
with `python3 packaging/remote_support/build_payload.py DESTINATION`;
`PL_SUPPORT_VENDOR_INSTALLER` can select an alternative trusted installer during
platform release builds. Vendor installers must support `--provision-only`.

Complete-system update activation compares the installed, configured `rustdesk`
package version with the candidate release's `EXPECTED_VERSION`. Matching versions
skip installation. A different or missing version invokes a root-owned helper;
failure keeps the previous robot release active. Kiosk settings are preserved.
Backend and platform versions continue to activate together from the robot archive.

Initial system setup installs `/usr/local/libexec/robot-remote-support-update`,
pins its trusted download source in `/etc/robot-remote-support.json`, and grants
the desktop user only the helper's `upgrade` command through sudoers. The helper
validates identifiers and Debian package metadata before installing with APT.
Changing the trusted source requires a trusted installer run with administrator
authentication. The user update service permits this scoped sudo elevation.

Existing installations need one trusted installer maintenance run to provision
the helper and refresh their user service before automatic package upgrades work.
Remote-support package installation is a machine-wide change: application rollback
restores platform/backend and data, but does not undo an installed support package.
