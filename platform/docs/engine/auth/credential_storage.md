# Credential encryption, keys, and installation state

Login and user-management providers now use the shared SQLite account runtime.
Live navigation checks use workers, and changes affecting the current session
require idle operation. No installed machine's keys/databases were provisioned by these tests.
Track completion in the
[TODO list](../../plans/access_control_todo.md).

## Dependencies and contracts

`cryptography==50.0.2` is a direct runtime dependency in root `requirements.txt`.
`packaging/requirements-build.txt` includes the root file, so builds receive the
same pin. Its transitive cffi/pycparser requirements are installed by pip. Every
new direct dependency must be added to the root manifest when introduced.

`IEncryptionKeyProvider` supplies secret key material to the credential backend.
`IEncryptionKeyProvisioner` is a separate explicit setup operation. Application
screens receive neither contract. A hardware/OS key implementation can replace
the file provider without changing account services or widgets.

`FernetCredentialProtector` implements `ICredentialProtector`. Password hashing
and verification delegate to `IPasswordHasher`/scrypt and do not load an Operator
key. Admin/Manufacturer credentials have no recoverable ciphertext. Operator
credentials have a verification hash plus authenticated ciphertext for the
separately authorized reveal operation.

Fernet handles encryption/authentication through the maintained library; stored
values carry a `fernet-v1:` envelope. It uses random IVs, and altered ciphertext
is rejected before a password is returned. See the
[versioned library documentation](https://cryptography.io/en/50.0.0/fernet/).

## Protected local key provider

`ProtectedFileKeyProvider` requires a dedicated private parent directory (0700)
and a regular key file (0600 or read-only 0400). The file belongs to the platform
OS account; root maintenance can access it. Symlink key files/directories and
nonregular files are rejected. Loading never creates missing material, changes
permissions, regenerates a key, or falls back to plaintext.

Explicit `provision_new()` generates a random key, publishes a complete file
without overwriting an existing path, synchronizes it, and returns only a safe
fingerprint. Existing/corrupt keys are not overwritten. Concurrent cooperative
setup is serialized through the shared store lock.

The key must live separately from the database and outside the software/source
tree, release payload, and Git. Exact production locations and ownership are
assigned during runtime/deployment integration. File permissions protect against
other OS accounts, not arbitrary code running as the platform OS account. Root
or a full-machine compromise can access both data and keys; hardware-backed
storage is a future provider option, not a property claimed for this backend.

## Key binding, loss, backup, and restore

The installation marker and database metadata retain the expected key fingerprint,
not key material. The credential implementation checks it on every encryption/
decryption operation and does not cache a usable key indefinitely. A replacement
key with different content is rejected before writing new Operator ciphertext;
it cannot silently mix keys in one installation.

| Failure | Structured error | Expected response |
|---|---|---|
| Missing/unreadable key | `KEY_UNAVAILABLE` | Restore access/original key; password verification remains available |
| Invalid key encoding | `KEY_INTEGRITY` | Investigate/restore; no automatic repair |
| Insecure file/directory or symlink | `UNSAFE_KEY_STORAGE` | Authorized staff correct storage/permissions |
| Valid but different key | `KEY_MISMATCH` | Restore the key matching the recorded fingerprint |
| Invalid/tampered ciphertext | `CREDENTIAL_INTEGRITY` | Investigate data/key pairing; no plaintext return |

Keep a protected backup of the original key separately from the robot and database
backup, with access controlled by authorized staff. Restore the exact key into
the private location with the required ownership/mode, then confirm the recorded
fingerprint and an authorized reveal. The restoration test verifies that existing
ciphertext works with the original backup without rewriting accounts.

Do not generate a new random key to repair a lost one. If the original key and all
its backups are lost, existing Operator ciphertext is unrecoverable. Existing
password verification and Admin/Manufacturer recovery remain independent of that
key. Rebinding a new key and resetting affected Operator passwords requires an
explicit reviewed maintenance workflow; automatic rotation/rebinding and a
production backup/restore command are not implemented by this slice.

## Explicit setup versus normal opening

`AccountInstallationPaths` identifies the database, separate state marker, and
private key path. Paths must be distinct, and the key must have a different parent
directory from the database. There is no legacy account-import API.

`AccountInstallation.initialize_new()` provides explicit empty-store setup for
these pre-production systems. It reads no old account/password/grant files, creates no
default users or passwords, leaves customer Admin commissioning open, and commits
an `installation.created` audit event once. Setup intent is recorded before
storage creation, and retries resume the same installation. Its persisted stages are:

```text
creating_store -> store_ready -> key_ready -> active
```

Setup binds the key fingerprint and marks the installation active only after its
audit commits. Repeated setup preserves accounts created afterward and does not
duplicate the installation event. Corrupt or unsupported setup state is an
integrity error, not an instruction to import or reset accounts.

`open_existing()` is the normal startup operation. It requires an active matching
marker/database identity and fingerprint. Missing/corrupt established storage
cannot reopen commissioning or cause an automatic legacy import. Opening an active
installation does not eagerly load the key, preserving privileged authentication
and recovery when only Operator key material is unavailable.

Startup must never catch an opening error and call initialization as a fallback.
Explicit setup requires trusted commissioning/deployment composition; it is not
an operation exposed to the normal login screen. Restoring both old marker and
database can also restore old credentials/codes; the recovery runbook's backup
review requirements still apply.

## Fresh setup and clean cutover

The systems are not in production. Old passwords and password-bearing QR cards
do not require compatibility. **The confirmed decision is to start with an empty
account list.** No old IDs/names/roles/passwords or app grants are imported. Set up
new Manufacturer/Admin accounts and issue new cards. Initialization does not
delete unrelated source files or an established account database.

1. Complete the deployment/handover checks in the TODO before production use.
   Stop the old application for cutover.
2. Assign and record absolute per-system database/state locations and a private
   key directory outside the repository, software payload, and database directory.
   Run setup as the platform OS account so that it owns the resulting files.
3. Use the trusted installation's Python environment with the root requirements
   installed. Substitute the recorded paths below; these are placeholders:

   ```bash
   /ABSOLUTE/INSTALL/.venv/bin/python -I /ABSOLUTE/INSTALL/src/bootstrap/account_setup.py --database /ABSOLUTE/DATA/accounts.sqlite3 --state /ABSOLUTE/DATA/account-installation.json --operator-key /ABSOLUTE/PRIVATE/operator.key
   ```

4. Provision a named Manufacturer through the OS-authorized maintenance command
   in the [recovery runbook](account_recovery_runbook.md#provision-a-manufacturer-account).
   That command requires trusted root-owned installed code. Complete customer
   first-Admin setup separately; no built-in password or Manufacturer is created.
5. Verify new login, role/navigation gates, Operator reveal, recovery-code handover,
   and Manufacturer/OS recovery. Back up the new database/state and separately
   protected encryption key, and verify restoration before production handover.
6. Retire the old test credential sources for this exact profile: the resolved
   `storage/users/users.csv` and `storage/settings/permissions.json`, old
   password-bearing QR images (the old implementation used
   `/tmp/qr_user_<login>.png`), printed cards, and exported access packages.
   Use the actual resolved system storage root, which may differ from the source
   checkout. Do not remove unrelated settings or other robot systems' data.
   There is no requirement to keep plaintext credential backups for rollback.
   If another requirement mandates retention, keep those files outside the
   repository/release under restricted access and record a deletion date.

New SQLite storage can be backed up for rollback of the new architecture; old CSV
credentials are never an authentication fallback. Old cards must be discarded
and replaced. The new QR service rejects old password payload formats. New cards
contain opaque bearer tokens; only digests are stored. Reissuing a card revokes
its predecessor, and changing password/role invalidates existing cards through
the account credential version. Treat a card as a credential when handing it over.

The setup command is explicit and safe to retry. It refuses existing unbound
material, reports typed errors with correlation references, and does not replace
an established database or key. Its exit codes are `0` success, `2` invalid
input/business refusal, `4` infrastructure failure, and `130` cancellation.

## Shared runtime composition

`AccountRuntime` composes login, account, access, permission, recovery, audit,
and navigation contracts around the same injected `ISessionService`. It is owned
by bootstrap; individual application services receive narrow contracts rather
than the whole bundle.

`AccountPolicyProvider` merges current editable app grants with the immutable
system catalog (`ApplicationAccess` defaults/protected/denied roles). Manufacturer
receives access to every registered application; a denied Operator grant wins
over editable permissions. `VersionedAccessService` rejects a permission change
during evaluation. The navigation adapter also rejects old session results.

Systems supply application restrictions through their catalog. Domain-specific
actions use extra `AccessRule` entries and an `IAccessResourceResolver` for trusted
domain facts, without extending the engine's role enum or importing applications
into the shared policy. Account facts remain owned by the account store.

Paint (including both dryer variants), Glue, Welding, Twin Robot, and the blueprint
use this composition. Normal startup opens existing storage. Explicit development
login bypass uses temporary empty storage and a separate navigation bypass; its
stub has no account-management authority and creates no hidden persisted
Manufacturer account.

Default database/state paths are the selected system's resolved
`storage/users/accounts.sqlite3` and `storage/users/account-installation.json`.
The default key is under
`$XDG_STATE_HOME/robot-platform/account-keys/<data-path-id>/operator.key`, with
`~/.local/state` as the XDG fallback. `<data-path-id>` is the first 24 hexadecimal
characters of SHA-256 of the absolute database path. An absolute
`ROBOT_PLATFORM_ACCOUNT_KEY_FILE` overrides the key path. Record the exact
locations during installation; moving a database does not move its key.
`account_installation_paths()` returns the resolved paths.

The installed launcher reports those same paths with `--account-locations`
and explicitly initializes an empty store with `--account-setup`, before any
Qt/backend/hardware startup. Use the platform OS account and the same environment
as normal launch. `--account-locations --backup-location /ABSOLUTE/BACKUP` emits
a secret-free JSON deployment record for private retention. Source CLI explicit
paths remain supported. See [handover](../../installation/account-handover.md).

Normal startup validates established storage and acquires
`<database-path>.runtime.lock` before starting the backend/robot. The lock is a
cooperative OS lease released on shutdown/process exit. A second runtime or
account-changing maintenance command gets `BUSY`; do not delete the lock file
to bypass a running owner. The file may remain after clean exit; its existence
does not mean the lease is held. Root maintenance creates it with database-owner
ownership so the platform OS account can start afterward.

`AdminCommissioningService` uses the trusted `commissioned` state rather than
counting all users. A Manufacturer can be provisioned before the customer's first
Admin without skipping customer setup. Initial Admin creation is fixed-role,
transactional with its audit record, and closes the setup gate once. Missing
commissioning metadata is an integrity error. Manufacturer creation of an Admin
through the normal account service also closes that gate. The login screen uses
a worker and shows first-customer-Admin setup only when the durable flag requires it.

## Verification

```bash
.venv/bin/python -m unittest tests.engine.auth.test_credential_protection tests.engine.auth.test_fresh_account_installation tests.engine.auth.test_login_credentials tests.bootstrap.test_account_setup tests.engine.auth.test_account_runtime -v
```

These tests use temporary files and include real Fernet/scrypt protection,
fresh setup, corruption/loss, permission checks, backup restoration,
interrupted setup, concurrent initialization, fresh grants, custom resource
extension, and stale-session/policy rejection.
