# Role capabilities and password recovery

**Clean-cutover decision (2026-10-27):** systems are not in production, so old
passwords and password-bearing cards do not need compatibility. New credentials
and new cards replace them. **The confirmed choice is an empty account list**:
no old IDs/names/roles/passwords or grants are imported. This supersedes the earlier
Viewer/Developer conversion proposal. No legacy-login fallback is allowed. No
installed account data has been deleted or migrated. See
[fresh setup](../engine/auth/credential_storage.md#fresh-setup-and-clean-cutover).

Track implementation in the [execution TODO list](access_control_todo.md).

Status: shared services, fresh setup, login/recovery/user-management adapters,
worker-based controls, role catalogs, provider wiring, shell navigation, and
idle-gated access changes are implemented. Twin's typed activity/reservation
integration, maintenance packaging, installed setup/path commands and disposable
handover/restore acceptance are also implemented. Actual machine commissioning
and its external backend adapter must be verified on the identified station.

Concrete service boundaries, typed results/errors, persistence, and UI integration
are designed in [Access control and account services architecture](access_control_architecture.md).

This plan extends the existing application-level authorization described in
[role_based_authorization.md](role_based_authorization.md). For the requirements
below, this document takes precedence over that historical plan. Paths labelled
as proposed do not exist yet.

## 1. Outcome and agreed requirements

Support multiple individual accounts per role. Add `Manufacturer` alongside
`Admin` and `Operator`; do not treat Admin as a single special account.

| Behavior | Operator | Admin | Manufacturer |
|---|---|---|---|
| Application access | Explicitly permitted apps | Configured permissions | All registered apps, including future additions |
| Administration and Service folders | Hidden and inaccessible | Configured permissions | Visible and accessible |
| Change own password while authenticated | No | Yes | Yes |
| Change an Operator password | No | Yes | Yes |
| Change another Admin password | No | No | Yes |
| Reveal an Operator password | No | Yes | Yes |
| Reveal an Admin or Manufacturer password | No | No | No; these passwords are not retrievable |
| Forgotten-password recovery through login | No | Own account only, after recovery verification | No ordinary self-service recovery |
| Create/manage Manufacturer accounts | No | No | Yes, through controlled provisioning/management |
| View/edit App Permissions in User Management | No | No; tab hidden | Yes; tab visible |

Manufacturer has unrestricted application/action authorization. This does not
create otherwise unsupported operations, such as revealing a hashed Admin
password, and does not bypass authentication, input validation, operation state,
or robot safety checks. Recovery is a separate identity-verification flow, not an
authenticated action permission override.

Existing control styles must be preserved: stylesheets, palette, dimensions,
fonts, icons, and spacing. New workflows add controls using the existing or shared
styles. Permission handling changes visibility/enabled state using existing
disabled appearances.

## 2. Decisions to settle before affected implementation

The following are proposals or open choices, not additional agreed requirements:

| Decision | Proposed direction |
|---|---|
| Existing accounts | Confirmed: start empty. Remove Viewer/Developer roles and do not import any old identities, passwords, or grants. |
| Admin account creation/deletion | Confirmed: Admin manages Operators and their own profile/password; other Admin and Manufacturer account management remains Manufacturer-only. |
| Role changes | Confirmed: Manufacturer-only. Admin cannot promote themselves or demote another Admin to bypass password restrictions. |
| Persistence and documentation | Confirmed: SQLite behind service contracts, with account/permission/audit consistency; update affected guides during implementation. |
| Admin access to Service | Continue explicit application permissions; the discussion only mandates that Operators are excluded. |
| Recovery mechanism | Confirmed: Admin saves personal single-use codes generated in advance. Possession is the recovery proof. Manufacturer can perform an audited password reset if password and codes are lost; stored hashes do not allow looking up the old values. |
| First Manufacturer and loss of all Manufacturer access | Confirmed: authorized OS staff use a local maintenance command. Implemented in source, with effective-UID checks, private password entry, and atomic audit; installation/runtime cutover remain pending. See the operational runbook. |
| Permission denial presentation | Hide controls for roles with no access by default. Explicitly support visible-but-disabled controls where useful; temporary operational unavailability remains disabled. |
| Access changes during operations | Confirmed: reject changes affecting the current session until idle. Never stop robot work for authorization. |
| Implementation rollout | Build shared foundations, integrate user management/login and Paint first, then verify all systems and Paint variants before declaring platform completion. |

Proceed with independent foundations while resolving these choices; do not ship
affected account mutations or migrations with implicit permissive defaults.

## 3. Current implementation and gaps

Typed account/permission services, SQLite transactional audit, scrypt hashing,
Operator encryption, key provisioning, fresh installation, commissioning,
recovery, maintenance, application adapters and provider wiring are implemented.
All supported systems now declare Manufacturer/Admin/Operator. See the execution
TODO for the remaining shell, active-operation and deployment checks.

The following list records the baseline that motivated the refactor. Its old CSV
and role descriptions are historical findings, not the active login/account path:

- `RolePolicy` is in `src/shared_contracts/declarations/system_specs.py`.
  Concrete systems declare role strings, default app permissions, and protected
  app-role mappings. Paint dryer variants inherit Paint's declaration.
- Paint currently declares Admin, Operator, Developer. Glue, Welding, and Twin
  Robot also declare Viewer. A separate application-level `Role` enum and default
  schema exist; runtime wiring must be audited rather than changing the enum alone.
- `src/engine/auth/authorization_service.py` checks role membership for an app.
  Protected app-role mappings preserve guaranteed access during permission edits;
  they are not exclusive allowlists. There is no target-aware action check yet.
- `src/bootstrap/run_main.py` already filters application specs before loading.
  The historical plan's pending filtering status is stale. Trace lazy loading and
  shell session changes before adding runtime access guards.
- User-management application service exposes generic CRUD and currently has no
  acting-user authorization checks. Generic updates can change password and role
  together; all mutation paths need enforcement.
- Authentication compares plaintext passwords. User records and QR generation
  expose password values. General user-list DTOs must stop carrying protected
  credentials even when a table masks their display.
- `CsvUserRepository` currently creates a missing store and returns an empty list
  on read failure. Login uses an empty list to detect first run. Established
  installation storage failures must not reopen initial-admin creation.
- Shared application construction and teardown live in
  `src/applications/base/application_factory.py`; common view behavior lives in
  `src/applications/base/i_application_view.py`. These are integration seams,
  not reasons to introduce authorization services into views.

## 4. Shared action contracts

Proposed package: `src/shared_contracts/authorization/`.

Keep contracts stdlib-only. Define small action groups using string enums with
stable, namespaced values. For example, `user_action.py`:

```python
class UserAction(str, Enum):
    CREATE = "users.create"
    DELETE = "users.delete"
    CHANGE_ROLE = "users.change_role"
    CHANGE_PASSWORD = "users.change_password"
    REVEAL_PASSWORD = "users.reveal_password"
```

Add other actions only for distinct protected operations, such as editing user
details or permissions. App-specific groups belong with their owning application;
genuinely shared groups belong in shared contracts. A new group must not require
editing the generic authorization or widget code. Python enums with members are
not extended by subclassing.

Add shared `PermissionAction.MANAGE = "permissions.manage"` in the proposed
`permission_action.py`. For now, grant it only to Manufacturer; it covers viewing
and editing application permissions at the service boundary. The tab has a
separate role-visibility requirement described in section 6. Later policy changes
can grant another role without rewriting the tab or introducing widget-specific
flags.

Authorization consumes normalized action IDs rather than importing every enum.
Unknown roles/actions and missing required target context deny access for normal
roles. Manufacturer receives the explicit global application/action grant, so new
supported operations do not require updating its grant list. Unsupported actions
still have no executable endpoint.

Avoid role objects with an ever-growing list of `can_*` boolean attributes. The
policy relates an action to the actor and target; role membership alone cannot
express self versus another Admin.

## 5. Central policy and trusted enforcement

Extend existing read-only authorization with a narrow action-check contract, or
compose a dedicated action authorizer alongside app authorization if that keeps
the interfaces smaller. Use one shared policy implementation for UI queries and
execution checks, with robot-system policy supplied through composition.

Conceptual trusted policy API:

```python
policy.can(actor, UserAction.CHANGE_PASSWORD, target)
```

Application services obtain the actor from injected `ISessionService` and load
the target from trusted storage by ID. Do not trust roles, actor IDs, or password
fields supplied by the view. UI-facing contracts expose plain permission results
through each application's own stdlib-only service interface.

For Admin password changes, allow only the same account ID or an Operator target.
Reauthenticate for own-password changes. Operator password reveal permits only
an Operator target. Enforce these rules on the current stored target role at
execution time, not only when the selection was displayed.

Separate account-detail edits, role changes, and password changes, or strictly
validate changed fields on every generic update. Audit create/delete, imports,
QR/email exports, and other paths so they cannot bypass the same rules. Protect
Manufacturer provisioning and permissions administration at the service boundary.
Preserve at least one usable Admin account when defining deletion/demotion rules.

Application access remains a separate `can_access(user, app_id)` decision. Extend
system declarations with stable folder restrictions for Operator and a configured
Manufacturer role value. Resolve folders through system metadata, not translated
labels or universal numeric folder IDs. The Operator ADMIN/SERVICE denial wins
over editable app grants and covers future apps placed in those folders.

Filter disallowed apps before lazy registration so empty restricted folders vanish.
Guard actual application opening as well; cached descriptors or a direct request
must not bypass current authorization. Use bootstrap/session integration first;
change shared `pl_gui` only if a concrete missing hook requires it.

## 6. Reusable UI permission binding without restyling

Start with composition: one permission-binding coordinator with small adapters
for existing buttons, `QAction` objects, tab pages, sections, and editable controls.
Support buttons and tabs in the first integration. Other adapters can be added
when a concrete screen needs them, without creating a parallel permission system.
A thin optional `ActionButton` may make declarations convenient, but existing
applications do not need to replace their buttons or tab widgets.

Support two independent policy decisions: visibility and execution. Shared,
stable feature IDs identify pages/sections when no executable action represents
their visibility. Ordinary action controls can derive role visibility from their
action grant, without requiring a separate visibility ID for every button.
Policies define allowed roles centrally; views declare requirements, not role
allowlists or `if role == ...` checks. A visible feature never implicitly grants
its child actions, and hiding a feature never revokes an otherwise granted action.
If the intent is to forbid that operation, its execution policy must deny it too.

Conceptual declarations (names are illustrative):

```python
binding.require(
    button,
    action=UserAction.CHANGE_PASSWORD,
    hide_when_role_denied=True,
)
binding.require_tab(
    tabs,
    permissions_page,
    visibility=UserFeature.APP_PERMISSIONS,
)
```

`UserFeature.APP_PERMISSIONS` is a proposed shared visibility identifier. Its
current policy permits only Manufacturer. Permission reads/writes independently
require `PermissionAction.MANAGE`, also Manufacturer-only for now. Both decisions
live in the central policy and are covered by tests together.

Declarations identify presentation/action requirements; they do not look up a
session or execute policy. The controller supplies results through a shared binding
coordinator using model/application-service queries. Selected-target context is
resolved outside the view. Views only emit events and apply presentation state;
engine services and models remain Qt-free.

Define predictable defaults:

- No requirement: ordinary existing behavior.
- A requirement is registered: keep hidden/disabled until the first relevant
  policy result arrives; do not briefly display forbidden controls at startup.
- Selection, session, role, or permission change: invalidate old decisions and
  refresh. Clear revealed secrets when the target/session changes.
- Role has no visibility or action grant: hide by default. Explicit per-binding
  configuration may keep a control visible but disabled to explain availability.
- Role can perform the action in some contexts, but the selected target is
  forbidden: disable the visible control by default. For example, an Admin sees
  Change Password, but cannot use it for another Admin. A binding can explicitly
  hide on target denial when the workflow benefits from that behavior.
- Final enabled state combines permission with existing selection, validation,
  and busy state. Regranting permission must not override a disabled operational
  state. Track these inputs separately rather than reading the already combined
  `isEnabled()` value back into the calculation.
- A late asynchronous result for an old session/selection cannot reenable a
  control. Use synchronous in-memory decisions where possible.
- Factory/base integration owns coordinator lifetime and cleanup. Broker callbacks
  use named bound methods, cross-thread Qt updates use the established bridge
  pattern, and every subscription has matching teardown.

Do not inject an engine authorizer into widgets, add role checks in views, replace
stylesheets, or recursively force every button into a new visual component.

### Presentation and execution gates

The first gate controls what the role sees and can interact with in the UI. The
second gate lives in the application service and checks the current actor,
requested action, and trusted target immediately before execution. The UI may
also reject a stale interaction early, but that does not replace service checks.

If a forbidden control is accidentally shown or enabled, its signal is emitted
programmatically, or a caller invokes the service directly, the service must deny
the operation without changing data. Visibility configuration cannot bypass the
execution gate. Record denied protected attempts using the audit policy.

### Tab and container behavior

In User Management, keep the Users tab available according to its existing app
access policy. Show App Permissions only for Manufacturer. Admin still uses User
Management for the permitted account operations, with no App Permissions tab.
No other existing role receives this capability by default.

Bind tab requirements to the page widget or another stable page identity, not a
numeric tab index, because indices can change as pages are added or removed.
Preserve labels, icons, order, styling, and normal translation behavior. Use the
existing tab widget's visibility/enabled mechanisms rather than restyling it.

When a selected tab becomes forbidden, move to an allowed page and prevent direct
or programmatic opening of the forbidden page. Initialize a protected page and
load its data only after authorization; do not fetch permission data simply to
build a hidden tab. On revocation or session change, clear protected data, stop
associated activity, and invalidate the page until access is granted again.
Child controls retain their own operational state and any narrower requirements.

The permission service checks `PermissionAction.MANAGE` for both reads and writes,
including direct calls and exports. Hiding a tab alone cannot enforce this rule.
Successful permission changes record actor, time, and changed grants in the
action history without weakening the non-editable role/folder restrictions.

## 7. Password storage, reveal, and recovery

Implement credential handling before enabling Operator reveal in production.

- Admin and Manufacturer credentials: salted password hashes using a suitable
  supported password-hashing library. No reveal API, plaintext exports, or raw
  credentials in general records returned to the UI.
- Operator credentials: hashed for login, with a separately encrypted recoverable
  value to satisfy the agreed reveal requirement. Use authenticated encryption;
  keep its key outside source control, release artifacts, and user data files.
  Define key provisioning, backup, and key-loss behavior before rollout. Missing
  keys must not fall back to plaintext or weaken login verification.
- Reveal: explicit authorized service operation, masked by default; record actor,
  target, action, time, and outcome without logging the secret. Avoid persistent
  plaintext QR images or email packages bypassing this operation.
- Inventory existing QR login/card workflows. Admin/Manufacturer QR credentials
  must not embed passwords; propose independent revocable tokens and an explicit
  card transition. Operator export behavior must be specified and authorized.
- Migrate existing plaintext stores with backup, validated versioned conversion,
  atomic durable writes, and restart/retry handling. Restrict and retire plaintext
  backups after the agreed rollback period; do not leave legacy passwords as an
  indefinite alternate login route. Coordinate writes/revalidation so concurrent
  account edits cannot replace a newly changed credential with stale data.
- Distinguish missing/corrupt established user storage from genuinely new setup.
  First-admin creation is allowed once, from trusted installation state, and
  cannot be reopened by an empty/missing file alone.

Proposed Admin recovery flow, subject to the commissioning decision in section 2:

1. Provision random single-use codes per Admin and installation; show them once
   for secure external custody and store only their verification hashes.
2. Login presents recovery with a generic response. Only eligible Admin accounts
   can complete it, after code verification and persisted retry throttling.
3. A recovery grant permits only setting that account's new password. Atomically
   consume the code and persist the new credential; handle concurrent redemption.
4. Invalidate existing sessions, outstanding grants, and remaining recovery codes;
   issue replacement codes through the verified flow. Require normal login after
   reset and record an audit event without secret values.
5. Operator sees guidance to contact an Admin, with no reset or forced-password-
   change flow. Manufacturer recovery uses the separately documented procedure.

The existing platform exit password is not a universal recovery credential.

### User metadata and action history

Store both a small current summary and a separate append-only history. A single
`edited_by`/`edited_at` pair alone loses earlier changes and cannot answer who
changed the password before the latest profile edit.

Each user record contains service-owned metadata:

- `created_at`, `created_by`: creation time and actor; immutable after creation.
- `updated_at`, `updated_by`: time and actor of the latest successful change.

Use UTC timestamps and stable account identifiers. Capture metadata at the service
boundary from the trusted session, not editable form fields. Existing accounts
with unknown creation details retain an explicit unknown value; a migration event
records when they were imported without inventing their original creation date.

For every successful creation, effective update, and deletion, append an audit
event with `event_id`, `occurred_at`, `actor_id`, `actor_role`, `target_id`,
`action_id`, `outcome`, and the changed fields. Preserve account identity across
deletion/recreation so a reused login ID does not merge two people's histories.
One update produces one event containing all its effective field changes.

For approved non-secret fields, record previous/new values using an explicit
allowlist. For credentials, record only markers such as `password_changed: true`;
never retain old/new passwords, hashes, encrypted credentials, recovery codes, or
tokens in audit data. Password-change actor and time can be obtained from this
history without adding another metadata pair for every editable field.

Also log password reveal, credential export, recovery, and permission-management
actions with their outcome. Reads/reveals do not alter the user's edit metadata.
No-op saves do not update edit metadata or create a successful-change event;
denied/failed attempts may produce separate attempt events, never successful
change records. Recovery uses an explicit verified-recovery actor/method rather
than pretending there was a normal authenticated session.

Persist each account mutation, summary metadata, and its audit event consistently
under the chosen storage transaction or recovery mechanism; do not report success
if its required audit event cannot be durably recorded. Keep history after account
deletion and do not expose editing/removing audit records as an application action,
including to Manufacturer. History viewing follows explicit authorization rules.

## 8. Delivery sequence

1. **Inventory and policy:** enumerate runtime account stores, role usages, folder
   membership, app permissions, QR/email paths, and existing session lifecycle.
   Settle relevant open choices; preserve the existing local Paint role edit.
2. **Contracts and policy tests:** add shared action IDs and plain decision/target
   contracts, implement trusted policy, Manufacturer grants, and Operator folder
   exclusions. Establish the agreed allow/deny matrix before UI integration.
3. **Service enforcement:** inject session/policy at composition boundaries; guard
   all user and permission mutations, return credential-free summaries, and
   prevent generic update/role-transition bypasses. Add trusted creation/update
   metadata and append-only per-account action history as described above.
4. **Credentials and migration:** introduce hashing/encryption, safe installation
   state, durable migration, secret-free auditing, and the QR transition. Validate
   against copies of data; do not rewrite live accounts during development.
5. **Reusable binding pilot:** integrate user management using existing buttons
   and tabs; cover own/other Admin and Operator selections, operational enabled
   state, and Manufacturer-only App Permissions visibility and service access.
6. **Recovery:** integrate the selected Admin-only recovery flow in login and
   commissioning, including replacement-code handling and session invalidation.
7. **System wiring and access:** wire shared services into Paint, dryer variants,
   Glue, Welding, Twin Robot, and the blueprint as applicable. Verify filtered
   registration, direct opening, logout/login rebuild, and Manufacturer visibility
   for every system's registered apps. No hidden factory creation for Operators.
8. **Documentation and rollout:** update authorization and credential procedures,
   app/engine/shared-contract/system guides, and the application blueprint guide
   if the binding changes a shared pattern. Follow AGENTS.md's documentation
   update prompt when implementing code in the affected paths.

Keep each stage reviewable. Unrelated motion, hardware, shell styling, release
publication, and root `scripts/` work are outside this plan. Do not deploy or
publish as part of implementation without a separate delivery request.

## 9. Verification and completion criteria

Use targeted unit tests with stub services and no real hardware. Add tests for
policy boundaries and bypasses rather than tests mirroring widget constructors.

- Multiple Admin and Operator accounts authenticate independently.
- Admin changes own password with reauthentication; another Admin's password is
  hidden and cannot be changed through UI, service, generic update, export, or
  role-transition bypass. Operator password reveal/change succeeds for Admin.
- Operator cannot change own password, recover it, open restricted apps directly,
  or see Administration/Service; stale grants cannot undo folder restrictions.
- Admin cannot create/grant Manufacturer or change its credentials. Test settled
  create/delete/demotion rules and last-Admin protection.
- Manufacturer sees all registered apps and folders without individual permission
  entries; a newly added test app/action is covered by its global grant.
- Unknown normal roles/actions, unauthenticated callers, and incomplete target
  context deny. Queries and execution checks agree, with execution revalidation.
- Bindings preserve style properties and correctly combine permission, selection,
  and busy state through grant/deny transitions; session changes and cleanup leave
  no stale callback capable of reenabling an old view.
- Test role visibility separately from action execution: hidden-but-allowed and
  visible-but-denied presentations behave as explicitly configured. Deliberately
  show/enable a forbidden control and invoke its signal/service; authorization
  still denies the action without mutation. Role changes cannot expose protected
  content during initial render or stale refreshes.
- Admin can use permitted user-management features but cannot see or open App
  Permissions, or read/write its data through direct service calls. Manufacturer
  sees the tab and can manage app permissions. Test changed tab order, translation,
  selection fallback, session changes, and no protected data loading while denied;
  existing tab labels, icons, ordering, and styles remain unchanged when allowed.
- Recovery: valid Admin code succeeds once; invalid/reused/wrong-account/wrong-
  installation codes fail; concurrent redemption yields at most one success;
  throttling survives restart; interrupted persistence cannot leave a reusable
  redeemed code; recovery cannot be used by Operator or Manufacturer.
- Password reset invalidates relevant sessions and QR/token credentials. Passwords,
  recovery codes, and encryption keys never appear in logs, lists, or diagnostics.
- Creation metadata remains immutable; each effective update records its actor,
  UTC time, and permitted field differences. Password edits use redacted markers.
  No-op/failed saves cannot overwrite last-editor metadata. History survives
  deletion, distinguishes recreated accounts, and stays consistent after interrupted
  writes. Password reveal records an action without marking the account edited.
- Corrupt/missing established storage cannot trigger first-admin setup. Migration
  handles interrupted writes, concurrent updates, retries, and missing keys without
  granting access or silently discarding accounts.
- Compare representative existing screens before/after under matching conditions:
  allowed states look unchanged; denied controls use existing styling. Check
  English/Bulgarian initial render and runtime language switching. New text belongs
  in both catalogs; password fields use shared touch-keyboard widgets.
- Compile changed Python modules, validate changed JSON catalogs, and run relevant
  auth, bootstrap, user-management, login, and system integration tests. Run the
  required repository suite before completion and report any unrelated failures.

Completion means agreed rules hold at both presentation and service boundaries,
all supported systems are wired, migrations and credential workflows are verified,
and current styles are preserved. A filtered shell or disabled button alone is
not sufficient enforcement.

## 10. Security references

- [OWASP authorization guidance](https://cheatsheetseries.owasp.org/cheatsheets/Authorization_Cheat_Sheet.html):
  deny by default, account for the target, and validate each protected operation.
- [OWASP password recovery guidance](https://cheatsheetseries.owasp.org/cheatsheets/Forgot_Password_Cheat_Sheet.html):
  secure single-use recovery credentials and limited reset access.
- [OWASP password storage guidance](https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html):
  salted password hashing; Operator reveal is an explicit product requirement
  needing separately protected recoverable material.
