# Account recovery and Manufacturer maintenance

For authorized installation/service staff and account administrators. Never put
real passwords, recovery codes, encryption keys, or OS credentials in this guide,
Git, screenshots, command history, or service reports.

## Current availability

Login and user-management providers use the new SQLite services. The maintenance
entry point and idle-gated live navigation expiry are implemented and tested in
source. A standalone stdlib maintenance payload and root-owned installer are
included in new bundles. On-machine provisioning/handover must still be performed
for the identified station. This command works with an initialized **new SQLite account
database**, not a CSV-backed login. It does not initialize, migrate, replace, or
install a database. No live accounts were modified during development.

The confirmed pre-production rollout starts with an **empty account list**, new
credentials, and new cards. `src/bootstrap/account_setup.py` initializes that empty
installation. There is no old-account import or role-conversion step. See the
[clean-cutover procedure](credential_storage.md#fresh-setup-and-clean-cutover)
before provisioning the first Manufacturer. Old passwords/cards are not a
compatibility requirement, and ordinary startup must never fall back to them.

Production must use a verified, root-owned installation and interpreter. The
example paths below are placeholders, not current installer defaults. The actual
tool and active database paths must be recorded during deployment. The verified
payload installer publishes `/usr/local/sbin/robot-account-maintenance`; see
[packaging](../../../packaging/accounts/README.md) and
[commissioning/handover](../../installation/account-handover.md).

## Recovery authority

| Situation | Authorized recovery |
|---|---|
| Operator forgets password | Admin or Manufacturer assigns a new password |
| Admin has a personal recovery code | Admin redeems it for their own account |
| Admin loses both password and codes | Authenticated Manufacturer assigns a new Admin password |
| Manufacturer cannot log in; another Manufacturer can | Other Manufacturer assigns a new password |
| No Manufacturer can log in | Authorized OS administrator uses maintenance |
| OS administrator access is also lost | Authorized physical-service/OS recovery and approved backups |

Platform Manufacturer and OS administrator are separate authorities. A platform
Admin cannot reset another Admin or manage Manufacturer accounts. A platform role
does not grant `sudo`. The maintenance service requires host effective UID 0.

## Admin recovery codes

1. The authenticated Admin confirms their current password and generates their
   personal set of eight random codes. The plaintext set is returned once.
2. The Admin stores it outside the platform in a secure personal/company password
   vault or other controlled offline location. The database stores only digests.
3. Recovery requires the login ID, an unused code, and a new password. A code
   proves possession; someone who steals it can use it. It does not identify the
   physical person entering it.
4. Successful recovery changes the password, invalidates previous credential/
   session claims and the entire old code set, and returns replacement codes once.
   Save the replacements, discard the old set, then log in normally.
5. Regenerating codes revokes the previous set. A Manufacturer password reset also
   invalidates old Admin codes. The Admin then logs in and generates new codes.

Default recovery limits are five failures per identifier and fifty globally in a
sixty-second window. Counters survive restart. Wait for the window before retrying;
do not delete counters or account data. These limits affect recovery, not normal
login, and are configurable through `RecoveryLimits` during composition. Normal
password/card login has its own persistent limits (the same default five per
identifier/fifty global/sixty seconds), configurable through
`AuthenticationLimits`. Password and card attempts share the normal-login global
budget; recovery retains a separate budget. These services are used by the login
screen through application-owned typed results and workers.

Admin/Manufacturer passwords and existing recovery codes cannot be looked up in the new store.
An authenticated Manufacturer performs a reset through the account service.

Changes that invalidate the current session, including password recovery for it,
are refused while an operation is running/paused/stopping. Permission writes also
require idle. Wait for the normal operation to finish and retry; a busy recovery
attempt leaves the saved code usable. Authorization never stops a robot operation.

## Prepare for OS-authorized maintenance

1. Verify the service request/personnel and identify the intended machine/profile
   and Manufacturer login ID through the organization's approved procedure.
2. Put the robot in a safe service state and stop the platform using the installed
   procedure. This command sends no robot motion or stop command and cannot verify
   physical safety.
   Create/reset commands enforce an exclusive database runtime lease and return
   `busy` while the platform or another maintenance writer holds it. Inspection
   remains available. Do not remove the `.runtime.lock` file to bypass the lease.
3. Locate the active SQLite database from the deployment record, confirm its
   profile, and take an approved consistent backup.
4. Use an authorized OS administrator and interactive terminal. Execute only
   trusted root-owned code/interpreters. Do not give kiosk users passwordless
   general-purpose Python access or run a user-writable checkout as root.

Replace these placeholders with the installation's recorded values:

```bash
ACCOUNT_MAINTENANCE=/usr/local/sbin/robot-account-maintenance
ACCOUNT_DATABASE=/ABSOLUTE/PATH/TO/EXISTING/accounts.sqlite3
MANUFACTURER_LOGIN=900
```

The installed wrapper uses isolated system Python and a root-owned stdlib-only
archive. Manufacturer maintenance does not require the Operator encryption key.
The source entry point remains available for trusted development environments;
do not run a user-writable checkout/interpreter as root.

## Reset an existing Manufacturer password

Inspect identity, revision, and enabled state without revealing credentials:

```bash
sudo "$ACCOUNT_MAINTENANCE" --database "$ACCOUNT_DATABASE" inspect-manufacturer --login-id "$MANUFACTURER_LOGIN"
```

Set a new password:

```bash
sudo "$ACCOUNT_MAINTENANCE" --database "$ACCOUNT_DATABASE" reset-manufacturer --login-id "$MANUFACTURER_LOGIN"
```

Enter and confirm the password privately. There is no password argument or
environment-variable input. Pipes and terminals that cannot suppress echo are
refused. Cancellation or mismatched confirmation does not update the password.

Reset targets the inspected technical account ID and revision, so concurrent edits
return a conflict. It updates the hash, advances the credential version, removes
old recovery verifiers, and commits its audit atomically. Original identity and
creation metadata, other users, permissions, and settings are preserved.

Only an **existing enabled Manufacturer** can be reset. The command does not
promote another role, silently enable a disabled account, or recreate a missing
one. Verify deliberate disablement through the service process. An OS administrator
may provision a separate Manufacturer account when explicitly approved.

## Provision a Manufacturer account

Use an unused numeric login ID for compatibility with the current login form.
Use the actual responsible person's name; the following is an example:

```bash
sudo "$ACCOUNT_MAINTENANCE" --database "$ACCOUNT_DATABASE" create-manufacturer --login-id "$MANUFACTURER_LOGIN" --first-name Service --last-name Engineer
```

An optional `--email` supplies contact information. Password entry is private and
confirmed. The role is always Manufacturer; duplicate login IDs are refused. This
does not mark customer Admin commissioning complete or substitute for their setup.

## Verify, audit, and hand over

After the success message, restart through the approved procedure and verify
normal login on the installation using the new backend. Hand over the password
through a confidential channel; the owner may change it after login.

Expected audit actions are `maintenance.manufacturer_created` and
`maintenance.manufacturer_password_reset`. Records contain UTC time, target ID,
`actor_method=os_maintenance`, `actor_id=os:0`, effective OS username/UID, and a
password-change marker. Matching `SUDO_UID`/`SUDO_USER` are recorded as origin
context when available. Root environment values are not independent identity
proof; correlate them with the host's sudo/journal/service records. No secret
values or hashes are logged. This local audit does not claim protection against
an administrator who controls the operating system itself.

## Refusals and recovery failures

| Exit | Meaning | Response |
|---|---|---|
| `0` | Inspection succeeded, or mutation and audit committed | Verify login and handover |
| `2` | Invalid input/business refusal | Check path, target, revision, account state, terminal, and confirmation |
| `3` | OS authority denied | Use an authorized OS administrator |
| `4` | Structured infrastructure failure | Keep correlation reference; inspect storage/audit availability |
| `130` | Interactive cancellation | No password update is reported |

Missing/corrupt storage is not first-run setup. Never delete the database to reopen
commissioning, edit hashes manually, or bypass audit failures. Audit-write failure
rolls back the change; inspect state/history before retrying infrastructure errors.

If OS access is lost, follow authorized physical-service/OS recovery with verified
backups. Restoring an older database can restore old passwords, grants, and codes;
review and rotate privileged credentials/recovery codes after restoration. Operator
encryption-key loss is a separate incident: this tool cannot decrypt Operator
secrets without that key.

## Developer verification

These tests use temporary stores and mocked OS authority, with no real root login
or hardware:

```bash
.venv/bin/python -m unittest tests.engine.auth.test_account_maintenance tests.bootstrap.test_account_maintenance tests.engine.auth.test_recovery_service -v
```

See [Account services and durable history](account_services.md) for the typed
contracts, backend, fresh setup, and current application integration boundary.
