# Remote support controller

`src/engine/remote_support/controller.py` is a standalone, root-owned process
installed independently of the application. Its Unix socket accepts only
`status`, `enable`, and `disable` for the fixed `rustdesk.service` unit.
Only `enable` accepts an additional `duration_seconds`, restricted to 900,
7200, or 18000 seconds. Legacy clients default to 15 minutes.

Enabling support writes an atomic, root-owned access window to
`/var/lib/plproject/remote-support/enabled`. It records the Linux boot ID,
a CLOCK_BOOTTIME deadline (including suspended time), and a display timestamp.
Expiry is independent of wall-clock corrections and the GUI. Repeated ON
requests do not renew the deadline; disable and enable to open a new window.

The socket controller checks expiry approximately every second. An independent
systemd expiry timer checks every five seconds if the controller is stopped.
The RustDesk drop-in checks the window before every service start. Reboot
invalidates the window. Expiry removes the marker before stopping RustDesk;
a `stop_pending` marker makes failed stops retryable after controller crashes.

Install or upgrade with:

```bash
sudo bash packaging/remote_support/install.sh ROBOT_UI_USER
```

The installer updates the helper, socket/controller units, expiry service/timer,
and RustDesk drop-in. Legacy indefinite ON markers are invalidated during
upgrade. The new application refuses to enable support through an old controller
that does not advertise timed-access support.

Paint exposes a dedicated Remote Support application in Administration. Other
systems may retain the legacy Network Settings tab. The shell indicator counts
authenticated incoming desktop sessions through RustDesk's user IPC socket;
service availability is not treated as an active session.

`password_client.py` uses RustDesk user IPC to query only password presence,
set or clear the permanent password, and select password-only or local-approval
authentication. Writes require daemon acknowledgements and option readback.
No plaintext password is written to platform settings, passed as a process
argument, or included in errors. RustDesk owns its credential storage.
Password management requires the user's RustDesk daemon to be available;
it does not start support, change its deadline, or terminate an existing session.
Branded preset credentials may remain after removal, but permanent-password
login is disabled and local approval is restored.

Verify expiry with the GUI closed, controller stopped, and across reboot;
verify failed-stop retries and startup refusal for expired markers. Test password
changes against the deployed branded RustDesk version, including rejection,
confirmation, removal, and the platform Admin credential check.
