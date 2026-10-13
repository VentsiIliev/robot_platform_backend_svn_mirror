# Operator kiosk mode

In `config/platform.json`, set `ui.kiosk_mode` to `true` and launch using the
normal launcher. Set it to `false` for development. The generated GNOME kiosk
session launcher sets the narrowly scoped `ROBOT_PLATFORM_KIOSK_MODE=1`
deployment override, so entering that session always enables the same guard even
when source configuration remains in development mode. No other override value
is accepted.

When enabled, the app forces fullscreen, disables the development login bypass,
and always shows the header exit control. Closing requires a separate kiosk exit
password, including Alt+F4 when delivered by the window manager. It does not change
the operator session or use account passwords. Cancel or incorrect passwords deny
exit. Five failed attempts trigger a 30-second cooldown shared across exit dialogs.
Running applications can still veto closing.

## Set or rotate the password

Only a salted PBKDF2-HMAC-SHA256 hash (600,000 iterations) is stored. Enter passwords
twice through a hidden terminal prompt, never command arguments, JSON configuration,
environment variables or logs. Minimum length: 12 characters. There is no
hard-coded plaintext password.
Missing, corrupt, symlinked or overly permissive hash files prevent kiosk startup
before hardware/backend initialization.

Production releases embed one administrator-generated hash and therefore install
the same kiosk exit password on every newly provisioned station by default. The
plaintext password is never embedded. Create the build credential once, outside
the repository, before building a release:

```bash
mkdir -p /home/ilv/.config/pl-project
chmod 700 /home/ilv/.config/pl-project
cd /home/ilv/Desktop/25488_ZeroErr_git/platform
.venv/bin/python -m src.bootstrap.kiosk_password \
  --file /home/ilv/.config/pl-project/kiosk-password.json
chmod 600 /home/ilv/.config/pl-project/kiosk-password.json
```

The build uses that path by default. Set `PL_KIOSK_PASSWORD_FILE` only when the
hash is stored elsewhere. A build without a valid shared hash fails rather than
producing a release that asks each station for a different password. Existing
stations keep their local hash during updates, so an SSH rotation is not undone.
Before packaging, the build asks whether to use the selected hash, rotate it
through a hidden prompt, or cancel. Non-interactive automation fails closed
unless `PL_KIOSK_PASSWORD_CONFIRMED=1` is explicitly set after reviewing the
credential for that release; this variable is only an approval flag and never
contains the password.

Development: create a private directory outside the repository, then run:

```bash
mkdir -p /tmp/robot-kiosk-dev
chmod 700 /tmp/robot-kiosk-dev
cd platform
.venv/bin/python -m src.bootstrap.kiosk_password --file /tmp/robot-kiosk-dev/password.json
```

Set `ui.kiosk_password_file` to `/tmp/robot-kiosk-dev/password.json` for this test.
This temporary file is for development only. Default production path:
`/etc/robot-platform/kiosk-password.json`.

Production provisioning by a system administrator (replace `operator` with the
station's operator account):

```bash
sudo groupadd -f robot-kiosk
sudo usermod -aG robot-kiosk operator
sudo install -d -o root -g robot-kiosk -m 0750 /etc/robot-platform
cd platform
sudo .venv/bin/python -m src.bootstrap.kiosk_password --read-group robot-kiosk
```

The hash file is atomically written with mode 0600, or 0640 with `--read-group`.
The commands above make root the directory/file owner; operators can read the hash
but cannot replace it. Log out/in after group membership changes. Keep code and
production configuration administrator-owned and deny operators sudo access.
The hash is read at startup; restart after rotation. Repeat the command including
`--read-group` when rotating, to preserve operator read access.

For packaged installations, use the platform executable:

```bash
sudo /absolute/path/to/platform-executable --set-kiosk-password --read-group robot-kiosk
```

Provisioning exits without starting hardware. Protect hash backups; keep the actual
password in your organization's password manager. Operator-owned development files
do not provide production tamper protection. Hashing reference:
https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html

An accepted close follows the existing cleanup path: the robot system is stopped
and the managed ROS backend is stopped according to its configuration. This has
not been commissioned on hardware. The mode does not replace the emergency stop.

## Ubuntu session deployment still required

The application flag alone does not restrict GNOME shortcuts, virtual consoles,
terminal signals, task managers, or processes that can kill the application.
Use a dedicated restricted operator account and GNOME Kiosk session in production.
Keep the normal GNOME session for development and administrator maintenance.

The station deployment must configure and test:

- Automatic login/start in the dedicated kiosk session.
- No desktop shell, terminals, Alt+Tab escape, workspace switching or console access.
- Account-scoped shortcut and logout/reboot restrictions.
- A supervisor that restarts unexpected app exits without exposing a desktop.
- An authenticated session exit that returns to the display manager, where the
  maintenance account requires its own authentication.

Do not blindly restart every clean exit: that would restart the app after an
administrator intentionally closes it. The supervisor and session exit need an
explicit handoff design. The session installer is `packaging/kiosk/setup_kiosk.sh`; see [Ubuntu kiosk setup](README.md).
Its default policy restarts failed exits and logs out on a clean exit.

Upstream kiosk project: https://gitlab.gnome.org/GNOME/gnome-kiosk
