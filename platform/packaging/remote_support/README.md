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

The packaged vendor installer is pinned to the branded release. Build payloads
with `python3 packaging/remote_support/build_payload.py DESTINATION`;
`PL_SUPPORT_VENDOR_INSTALLER` can select an alternative trusted installer during
platform release builds. Vendor installers must support `--provision-only`.
