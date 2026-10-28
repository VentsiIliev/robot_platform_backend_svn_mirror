# Account maintenance payload

This stdlib-only Python archive provides the OS-authorized Manufacturer commands.
It contains no account database, passwords, Operator key, GUI, or third-party
packages. Ubuntu's `/usr/bin/python3` supplies sqlite3 and scrypt. Every new
platform bundle includes it under `installation/account-maintenance/`.

Build locally without a robot release or kiosk credential:

```bash
.venv/bin/python packaging/accounts/build_payload.py dist/account-maintenance
/usr/bin/python3 -I dist/account-maintenance/account-maintenance.pyz --help
```

An OS administrator reviews/verifies the delivered artifact, then runs its
installer using trusted code. Never run an unreviewed, user-writable checkout or
interpreter as root. A checksum detects damage; it does not authenticate a release.

```bash
sudo /usr/bin/python3 -I /ABSOLUTE/VERIFIED/PAYLOAD/install.py
sudo /usr/local/sbin/robot-account-maintenance --database /ABSOLUTE/DATA/accounts.sqlite3 inspect-manufacturer --login-id 900
```

The installer uses fixed root-owned locations under
`/usr/local/lib/robot-platform/accounts/<sha256>/` and publishes the stable
`/usr/local/sbin/robot-account-maintenance` wrapper. It rejects symlink paths and
directories writable by other users. The wrapper uses isolated system Python;
it cannot execute a user-writable GUI installation through sudo. No sudoers grant
is installed. Updating this root tool requires an OS administrator; the ordinary
user's software updater cannot replace it.

Create/reset commands require a private interactive terminal and refuse while the
platform holds the account database runtime lease. `ensure-manufacturer` is the
installer's required commissioning command: it verifies an existing enabled
Manufacturer or prompts for numeric login ID, name and privately confirmed
password. It preserves existing accounts/passwords and never enables a disabled
account. Cancellation, busy, invalid input and audit failures return nonzero so
deployment setup cannot be marked complete. First-Admin setup remains separate.
These commands work without the
Operator encryption key. See [recovery procedures](../../docs/engine/auth/account_recovery_runbook.md)
and [handover](../../docs/installation/account-handover.md).
