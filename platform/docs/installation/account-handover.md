# Account commissioning and handover

This procedure starts with an **empty account list**. No CSV users, passwords,
grants, or old QR cards are imported. Ordinary application startup never creates
an absent account store. Execute setup as the platform desktop OS account;
Manufacturer maintenance separately requires an OS administrator.

The implementation is verified with disposable installations. A target machine's
commissioning, physical idle checks, real backup location and staff handover must
be recorded there; local test results do not certify a robot station.

## Installed commands and location record

New platform bundles include `installation/account-maintenance/`. An administrator
installs its verified payload following [the tool guide](../../packaging/accounts/README.md).
The stable command is `/usr/local/sbin/robot-account-maintenance`, using root-owned
code and isolated system Python. The user-owned updater never replaces that tool.

The installed launcher has two hardware-free commands:

```bash
/ABSOLUTE/INSTALL/launch.sh --account-locations
/ABSOLUTE/INSTALL/launch.sh --account-setup
```

`--account-locations` reports the database, marker, private key, OS UID and existing
installation ID. It creates no accounts or missing installation. `--account-setup`
explicitly prepares an empty store and private key, and is safe to retry. Both exit
before Qt, backend startup and factory-settings seeding. Setup also accepts the
three absolute path options of `src/bootstrap/account_setup.py`; defaults already
match this installed launcher's data root and selected system.
Both commands honor the installation/update lease and refuse interrupted update
state. Complete updater recovery first; do not initialize accounts around an
unfinished software update.

Default database/marker:
`<install-root>/data/<robot-system>/storage/users/{accounts.sqlite3,account-installation.json}`.
The default key is
`$XDG_STATE_HOME/robot-platform/account-keys/<database-path-id>/operator.key`, using
`~/.local/state` when XDG state is unset. `ROBOT_PLATFORM_ACCOUNT_KEY_FILE` overrides
it with an absolute path. Use the same OS account/environment for setup and GUI.
Record the key separately from the database/software backup.

Save the actual machine's record with its approved backup location:

```bash
umask 077
/ABSOLUTE/INSTALL/launch.sh --account-locations --backup-location /ABSOLUTE/APPROVED/BACKUP > /ABSOLUTE/PRIVATE/account-deployment.json
```

This record contains paths and identity, never credentials or key material.
It records the chosen backup location; it does not create a backup. Do not place
the record in Git or a release bundle. Confirm `installation_id` is populated
after setup. Missing established database/marker is an error, never a fresh setup.
Release preparation forces `ui.dev_skip_login=false`; source developer settings
do not become installer defaults.

## First accounts and recovery handover

1. Stop the platform and complete explicit empty setup. Confirm the correct system,
   data/key paths, platform OS owner and protected key directory/file (0700/0600).
2. Install the verified root maintenance payload. Provision an individually named
   Manufacturer with private interactive password entry:

   ```bash
   sudo /usr/local/sbin/robot-account-maintenance --database /ABSOLUTE/DATA/accounts.sqlite3 create-manufacturer --login-id 900 --first-name Service --last-name Engineer
   ```

3. Start the application and complete first-customer-Admin setup. Manufacturer
   provisioning does not close that setup gate. There is no default account or
   built-in password. Verify a normal Manufacturer login as well.
4. Have the Admin generate personal recovery codes after confirming their current
   password. Save them in the approved private/offline location; they are shown
   once. Never send real passwords/codes through chat, logs, screenshots or tickets.
5. Add the required Operators. Check Admin can reset/reveal Operator credentials,
   cannot reveal/manage another Admin's password, and cannot open App Permissions.
   Check Operator cannot open ADMIN/SERVICE, including direct navigation. Check
   Manufacturer sees all registered apps and App Permissions.
6. Test recovery with a designated acceptance account: one code changes its
   password, replaces all codes and requires normal login. Verify old proof fails.
   Verify Manufacturer reset fallback and OS Manufacturer reset using the
   [recovery runbook](../engine/auth/account_recovery_runbook.md).
7. During running/paused/stopping work, access changes affecting that session and
   permission writes must refuse with busy. Wait and retry; busy recovery preserves
   the code. Authorization must never stop robot work. Use the station's approved
   operating procedure; software tests do not exercise physical motion.
8. Issue fresh opaque login cards and verify revocation after password change.
   Retire old password-bearing cards, exports and legacy test credential files
   for this exact profile. Preserve unrelated machine settings.

## Offline backup and restore acceptance

Stop the platform through its normal procedure. Its runtime lease must be free;
never delete `.runtime.lock` to bypass an owner. Back up a consistent database
using SQLite's `Connection.backup()` (or SQLite's `.backup` command), together with
the matching `account-installation.json`. Keep those files access-restricted.
Do not copy an active SQLite file without its transaction/WAL state.

Back up the exact Operator key separately in approved protected storage. Keep its
0700 directory/0600 or 0400 file ownership/modes. Do not create a replacement key
to repair a missing one; existing ciphertext requires the original fingerprint.

Before handover, restore the database/marker and separately stored key into an
isolated location with correct ownership/modes. Validate `open_existing()`, normal
Admin/Manufacturer authentication, Operator reveal and immutable history. The
disposable acceptance test exercises this sequence with real scrypt/Fernet.

A restored database can restore old passwords, recovery verifiers and bearer-card
digests. Review that rollback deliberately and reset credentials/reissue codes and
cards as needed before returning it to service. Record verification date, station,
software identity, installation ID, backup/key custodians and responsible staff;
record no secrets. Ordinary startup must not repair/initialize a failed restore.

## External Twin runtimes

`ITwinChoreographyRuntime.get_activity()` must return `TwinRuntimeActivity` from
authoritative combined state. IDLE excludes queued starts, jog, running, paused
and stopping motion. Unknown/disconnected/stale state must not report IDLE.
`hold_idle()` must atomically reserve both robots against all starts until release.
The platform adapter holds this reservation through the account database commit.
Legacy adapters without the contract refuse affected changes. No concrete external
Twin motion adapter is shipped by this checkout; its implementation must satisfy
this contract when attached. There is no guessed conversion from arbitrary robot
status dictionaries or start/stop responses.

## Verification

```bash
QT_QPA_PLATFORM=offscreen .venv/bin/python -m unittest tests.bootstrap.test_account_handover tests.bootstrap.test_installed_account_tools tests.bootstrap.test_account_maintenance_payload tests.robot_systems.twin_robot.test_account_activity -v
```

These checks use temporary stores, simulated activity and an injected OS-authority
double. They do not provision a real machine, run sudo or move robots.
