# Account services and durable history

The account backend is implemented behind `IAccountService`, `IPermissionService`,
`IAccountStore`, `IAccessPolicy`, and `ICredentialProtector`. Login and user-management
providers use the shared SQLite runtime through application-owned adapters.
The shell rechecks live/cached navigation asynchronously. Changes affecting the
current session are rejected until its robot operation is idle.
Credential encryption and the explicit installation lifecycle are now implemented;
see [credential storage](credential_storage.md). The approved rollout uses new
accounts and credentials because systems are not in production. The confirmed
decision is to start empty; no Viewer/Developer conversion or account import remains.

`IAccountLoginService` verifies credentials and returns a typed safe identity;
the caller creates an `AccountPrincipal` and logs it into the injected session
only after success. Missing/disabled/retired accounts and bad passwords receive
the same public failure. Login history commits before an identity is returned.
Password/card authentication limits are implemented in the login flow and persist
in SQLite. The default is five failures per identifier and
fifty globally within sixty seconds. Password/card failures share the global
normal-login budget; recovery uses separate counters. Success clears that
identifier's counter without clearing the global failure budget.

`ILoginTokenService` issues random opaque bearer cards through the account
authorization boundary. Admin can issue their own/Operator cards; Manufacturer
can issue any enabled account's card. Only a SHA-256 digest and credential version
are stored. Reissuance revokes the previous card, while password/role changes
invalidate it through version checks. Issuance/login must commit their audit before
returning success. Old plaintext-password QR payloads are rejected. Card issuance
does not change profile metadata or revoke already authenticated sessions.

## Contracts

`IAccountMaintenanceService.has_enabled_manufacturer()` is an OS-authorized
`Result[bool]` readiness query; disabled Manufacturers do not satisfy it. The
installer invokes the root-owned `ensure-manufacturer` command under the exclusive
account runtime lease, then permits kiosk provisioning only on success. The CLI
collects missing identity/password privately and uses the existing atomic,
audited create command. It preserves existing enabled accounts and leaves
first-customer-Admin commissioning independent.

`src/shared_contracts/accounts/` owns safe account summaries, explicit commands,
redacted history, recovery, cards, and session validity. `src/shared_contracts/authorization/`
owns action/feature IDs, access requests/decisions, typed results, errors, and
permission snapshots. These packages depend only on stdlib.

`IAuditHistoryService` exposes authorized paged history reads under `audit.view`.
It requires an `account_history` resource reference. Admin has self and
current-Operator grants; other privileged targets are denied. Both presentation
context and command execution resolve trusted history facts from storage using
the same helper. A history identity survives account deletion with no current
role: Manufacturer's global grant retains access, while Admin cannot read a
deleted identity or gain access through a stale Operator role. History reads
also revalidate the session and discard results if it changes during the query.

Account commands return `Success[T]` or `Failure(ServiceError)`. Expected errors
include access denial, invalid proof/input, revision conflict, and policy violation.
Storage/availability/audit failures raise the shared structured service exceptions.
Callers use typed codes and correlation IDs, never parse exception text. UI
adapters must map these contracts to their application-owned service boundary.

`AccountPrincipal` carries a technical account UUID and credential version. Its
existing-shell compatibility payload contains profile data only. Each service
command reloads the current account and role through `verified_session_account`;
deleted/recreated accounts and old credential versions cannot reuse a session.

## Authorization and concurrency

`user_access_rules(admin_role=..., operator_role=...)` supplies reusable grants.
Admin can create/edit/delete Operators and edit their own profile/password.
Another Admin's password/profile and all role changes are protected from Admin
mutation. Manufacturer has the policy's global grant for supported actions.
Existing Viewer/Developer roles receive no account-service authority.

Explicit commands separate profile, password, role, and deletion changes. Target
commands require an expected revision. A stale revision returns `CONFLICT`; no-op
profile edits preserve metadata and do not append a change event. Own password
changes require current-password proof. Operator reveal is a distinct operation
and never changes the account's edit metadata.

Changing into or out of Operator requires a fresh password: a previously revealed
Operator password cannot become a privileged credential after promotion, and a
hashed Admin password cannot be copied into recoverable Operator storage. Role
changes also invalidate old credential/session claims.

`AccountOperationRunner` composes current-session verification, policy evaluation,
revision checks, atomic execution, and safe audit attribution. A session change
during execution rolls back the command. It is account-specific infrastructure;
other domains can use their own service and resource provider with the same pure
access-policy contracts.

`PermissionService` restricts both reads and writes to `permissions.manage`.
Manufacturer is its only eligible role initially. Updates use a permission
revision and retain hard folder restrictions and protected role access.
Snapshots include `ApplicationGrant.editable_roles`; clients use this contract
to lock cells rather than reconstructing policy from folder names or role strings.

## Active operations and session expiry

`IAccessChangeGuard` is injected into account, permission, and recovery services.
The production `SystemAccessChangeGuard` rejects current-session password, role,
deletion, and recovery changes while an operation is active. Permission writes
also require idle. Reads, profile edits, and changes to another Operator do not
revoke the current session and remain available. A busy result commits no account
mutation, and a busy recovery attempt does not consume the saved code.

For an idle change, the guard reserves the shared `ISystemManager` until after
database commit, preventing a platform process from starting during the change.
It rechecks the session and robot-system activity hook before commit. Unknown
activity is unavailable, never assumed idle. Standalone tests without robots may
use `NoActiveOperationGuard`; platform bootstrap always injects the system guard.
Domain motion outside the process manager must participate in the system's
activity hook and execution ownership; Manufacturer does not bypass this gate.
An optional `AccountAccessExtensions.idle_reservation` holds an external runtime's
atomic lease through database commit. Twin's `ITwinChoreographyRuntime` now declares
typed `get_activity()` and `hold_idle()` methods; `TwinAccountActivity` adapts them.
Legacy adapters, unknown activity and failed reservations refuse affected changes.

`ShellAccountAccess` checks navigation in workers every second and before opening
an app, including cached apps. A session revision binds each reply and one-use
factory grant. Revoked or invalid sessions return to login once the background
system activity query and screen-owned activity queries are idle. Failed activity
queries defer expiry. No authorization component sends robot stop commands.

The runtime and root maintenance command share an OS file lock. Account-changing
maintenance and a second platform process are refused while the runtime owns it.
The lock complements SQLite transactions; arbitrary direct database edits remain
unsupported. See the recovery runbook for the offline procedure.

## SQLite and audit

`SQLiteAccountStore.initialize(path)` is an explicit commissioning operation.
Ordinary construction opens an existing database with `mode=rw`; missing,
corrupted, unsupported, or incomplete storage cannot become an empty account list.
Transactions use an independent connection, foreign keys, `BEGIN IMMEDIATE`,
and full synchronization. Account/credential writes and their audit event commit
together. Audit-write failure rolls back the account mutation.

Creation and edit metadata is service-owned. Each audit event records stable actor/target identity, UTC time,
action, outcome, and allowlisted non-secret field differences. Password changes
use a marker. Passwords, hashes, ciphertext, and recovery material are not audit
fields. SQL triggers prevent audit update/deletion through the ordinary backend;
this does not claim protection against an operating-system administrator.

Operator secrets require an injected authenticated-encryption implementation.
`ScryptPasswordHasher` implements salted password verification using Python's
OpenSSL-backed scrypt (`N=2^17, r=8, p=1`). `FernetCredentialProtector` and the protected
file key provider implement Operator encryption without a plaintext fallback.
Production provisioning and on-machine verification remain pending.

## Fresh setup

`AccountInstallation.initialize_new()` supports empty setup with no CSV/JSON input.
It creates an empty store with no default credentials and no imported grants.
New accounts/cards are provisioned explicitly. Source accounts are not imported.
See the
[setup and retirement procedure](credential_storage.md#fresh-setup-and-clean-cutover).

The CSV import helper and migration contracts were removed after the empty-account
decision. Ordinary startup never reimports CSV/JSON or initializes missing
established storage. Repeated explicit setup preserves new credentials.

Retained-source cleanup, Manufacturer provisioning, recovery,
and the application's role catalogs are tracked in the
[implementation plan](../../plans/role_capabilities_and_password_recovery.md).

## Admin recovery and Manufacturer fallback

`IRecoveryService.generate_codes()` reauthenticates the current Admin, revokes
their previous set, and returns eight random single-use recovery codes once.
Only verification digests are persisted; code DTO representations and audit
events exclude the raw values. Issuing codes does not edit profile metadata.

`recover_admin()` verifies a code for an enabled Admin, changes the password,
advances the credential version, replaces the entire code set, and writes its
audit event in one transaction. It never creates a logged-in session. Codes are
bound to account identity, credential version, and the database installation ID.
Copying the entire database also copies that installation identity; hardware
binding is not claimed. A password change/reset invalidates older code sets
through their credential version.

Recovery requests have persistent per-identifier and global retry counters.
`RecoveryLimits` defaults to five failures per identifier and fifty globally in a
sixty-second window; throttling affects recovery, not ordinary account login.
The service can be configured at composition. Issuance also requires password
proof and is throttled. Missing, ineligible, and bad-code recovery requests receive
the same public invalid-proof result.

If an Admin loses both password and codes, an authenticated Manufacturer uses
`IAccountService.change_password()` to assign a new password. This is an audited
reset, not a lookup of the old password. The Admin then logs in normally and
generates new personal recovery codes. Neither the UI nor a repository API can
retrieve an existing Admin password or raw recovery code. Manual database editing
is not a supported recovery workflow. Login offers Admin recovery; user management
offers own code generation after current-password proof. Both use workers and
private one-time displays; recovery requires normal login afterward.

## OS-authorized maintenance

OS-authorized Manufacturer provisioning/reset is implemented behind
`IAccountMaintenanceService` and `IMaintenanceAuthority`. The Linux authority
checks effective UID 0 independently for every operation. `OperatingSystemActor`
captures structured audit context. `IPasswordHasher` lets this path use scrypt
without the Operator encryption key. No maintenance service is injected into
ordinary application screens.

`src/bootstrap/account_maintenance.py` provides interactive commands; it opens
existing storage only after OS authorization and refuses password arguments,
non-interactive input, and unsafe echo. See the
[operational runbook](account_recovery_runbook.md) for commands and limits.
New bundles contain the stdlib-only archive and fixed-path root installer under
`installation/account-maintenance/`. The stable command uses isolated system
Python, independent of GUI releases or the Operator key. See
[maintenance packaging](../../../packaging/accounts/README.md) and
[commissioning/handover](../../installation/account-handover.md).

## Verification

Targeted suites:

```bash
.venv/bin/python -m unittest tests.engine.auth.test_access_service tests.engine.auth.test_account_service tests.engine.auth.test_fresh_account_installation tests.applications.base.test_access_binding -v
```

These use temporary databases and an injected test credential protector. Hashing
also has real scrypt verification tests. No live account stores or hardware are
used by these tests.
