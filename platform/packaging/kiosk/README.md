# Ubuntu 24.04 robot kiosk

The complete platform installation also installs `/usr/local/bin/auto_login.sh`.
From a local terminal or SSH, run `sudo auto_login.sh off` to disable automatic
and timed login, or `sudo auto_login.sh on` to enable automatic login for the
saved GDM account. `sudo auto_login.sh on pl_user` selects an explicit account.
Changes apply on the next login/reboot; no session is stopped. This does not
change the selected GNOME session or any packaged application settings.

Run these steps on the target Ubuntu machine with GDM3 and an existing non-root
account. The installer uses GNOME Kiosk's X11 session, matching the existing
deployment. It installs kiosk packages, creates the launcher and log directory,
selects the account's kiosk session, and optionally enables automatic login.
It does not create accounts, configure hardware permissions, or install your app.

## Integrated platform installation

New platform and combined robot release installers configure kiosk on first
installation only, using this script. Automatic login defaults to enabled.
Use `--kiosk manual` for a manual-login test or `--kiosk off` to skip kiosk.
Subsequent installs and software updates preserve the kiosk configuration;
`--setup-system` explicitly reruns setup on an existing machine. Pending first
setup is retried after failure. See [installation policy](../platform/README.md#first-installation-versus-software-updates).

## Install and test

From the platform checkout, prepare the robot application **as the kiosk user**:

```bash
./launch_robot_app.sh --setup-only
./launch_robot_app.sh
```

Close the application, then install the kiosk with automatic login disabled:

```bash
sudo bash ./packaging/kiosk/setup_kiosk.sh install --user pl_user --directory "$PWD" -- ./launch_robot_app.sh
```

Log out, select the user and choose **Kiosk Script Session (X11 Display Server)**
from the login screen gear menu. Check application startup and normal exit.
Normal exit logs out; a nonzero exit retries after five seconds. The launcher
must wait for its application and propagate its exit code.

After the manual test succeeds, enable automatic login:

```bash
sudo bash ./packaging/kiosk/setup_kiosk.sh install --user pl_user --directory "$PWD" --autologin yes -- ./launch_robot_app.sh
sudo reboot
```

Verify automatic startup after reboot. Logs are at
`~/.local/state/robot-kiosk/session.log`; they are appended and not automatically
rotated. Test crash recovery only when the robot is idle and safe to restart.

## Configuration

Arguments after `--` are passed directly to the launcher, preserving spaces;
they are not evaluated as shell code. For example:

```bash
sudo bash ./packaging/kiosk/setup_kiosk.sh install --user pl_user --directory /home/pl_user --restart always --delay 10 -- /usr/bin/firefox --kiosk https://example.org
```

`--restart failure` logs out on exit code zero and restarts on failure.
`--restart always` restarts even after a successful exit.
`--autologin no` disables both automatic and timed login globally in GDM.
X11 mode also applies globally. Other users retain their desktop sessions.

For extra programs, point the installer at a user-owned wrapper that starts
them and then runs the main application in the foreground. The wrapper must
clean up its background programs on exit and preserve the main exit status.
System services such as SSH or remote support are configured separately.
GNOME Kiosk provides no desktop menu or configurable application allowlist;
controls inside the robot app remain the responsibility of the app's roles.
This script does not block virtual terminals, SSH, or other login sessions.

## Restore / redo

```bash
sudo bash ./packaging/kiosk/setup_kiosk.sh uninstall --user pl_user
sudo reboot
```

Uninstall restores the first saved GDM configuration, account session file,
and kiosk script. If the machine already had a kiosk setup before installation,
that original setup is restored. Select Ubuntu on Xorg at login to use the
desktop. Packages, application files and logs are retained.

Backups live in `/var/lib/platform-kiosk/pl_user`. Repeated installs keep that
original baseline. Restore uses whole files, so review any GDM or account-file
changes made since installation before uninstalling. Configure one kiosk
account per machine with this script. It never restarts GDM or reboots for you.

References: [GNOME automatic login](https://help.gnome.org/system-admin-guide/login-automatic.html)
and [default user session](https://help.gnome.org/system-admin-guide/session-user.html).
