# User management and application permissions

The application uses `IUserManagementService`, an application-owned standard-library
contract. Its concrete adapter receives narrow account, access, token, recovery,
history and permission services from the same account runtime/session. Production
wiring does not use CSV repositories.

`UserManagementFactory` uses the base factory's ownership and cleanup. The
controller delegates through the models; views receive data and emit user actions.

## Safe data and explicit commands

`UserEntry` contains identity, profile, role, enabled state, revision, and creation/
edit metadata. It has no password, hash, ciphertext, code or card field.
`DEFAULT_USER_SCHEMA` describes the safe table. Credentials are absent rather than
retrieved for table masking.

Created by / Edited by display the actor's current name and numeric login ID,
such as `Alice Admin (1)`. The model resolves those labels from the full authorized
page before filtering. Stored metadata and audit records retain the stable account
UUID; no database migration is needed. Missing/deleted actors and setup/OS actor
references absent from that page display `—`, without attributing an old action
to a different account that reused the same login ID. Table filters use the same
labels that are displayed. Existing column titles and styles are unchanged.

Commands separate creation, profile edit, password change, role change and deletion:
`NewUser`, `EditUser`, `PasswordChange`, and `RoleChange`. Mutations use the
technical account ID and displayed revision. Login IDs remain numeric for the
shared login form. Reusing a deleted login ID does not reuse its audit identity.

Every service operation returns `UserSuccess[T]` or `UserFailure(UserError)`.
`UserErrorCode` describes expected refusals and safe infrastructure categories.
The correlation reference remains available to callers. Secret commands, reveal
results, recovery-code displays and QR image DTOs have redacted representations.

## Role behavior

| Control | Admin | Manufacturer | Operator |
|---|---|---|---|
| Create/edit/delete accounts | Operators; edit own profile | All supported account operations | Denied |
| Change passwords | Own with current proof, or an Operator | Own with proof, or reset another account | Denied |
| Show password | Operator only | Operator only | Denied |
| Change role | Denied | Allowed; Operator boundary requires a different new password | Denied |
| Issue card | Own or Operator | Enabled accounts | Denied |
| Generate recovery codes | Own with current password | No personal Admin recovery issuance | Denied |
| App Permissions | Denied | Allowed | Denied |
| Account history | Own account and current Operators | All identities, including deleted accounts | Denied |

Privileged passwords are hash-only and cannot be revealed. Last-Admin and
operational/data constraints still apply to Manufacturer actions. Creation and
edit metadata come from the trusted services; no-op profile saves do not rewrite
metadata. History contains actor/time/action and allowlisted changes, with a
password-change marker instead of credential material.

Select a user and choose **Account history** to inspect the latest 100 events,
newest first. The dialog lists UTC time, actor, action and outcome. Selecting an
event shows each changed field's **Before** and **After** values. Password changes
show a marker only; password values never enter audit records. Known actors are
displayed using their current name and login ID; an unavailable actor retains its
stable reference rather than being attributed to a newly created account.
The dialog supports English/Bulgarian language switching and clears its data on
close or session invalidation. Admin can inspect their own account and current
Operators. Other Admins, Manufacturer accounts and deleted identities remain
Manufacturer-only. Both the presentation gate and the history service use the
same target-scoped policy, with roles reloaded from storage on each query.

## Reusable presentation gates

The controller binds the existing widgets through `base/access/AccessBinding`,
`WidgetAdapter` and `TabAdapter`. Action/feature requirements are declarative.
Role denial hides controls; target denial disables them, while Operator-password
reveal and account history are hidden for unauthorized targets. Busy/selection state remains an
independent input and cannot be overwritten by a permission refresh.

Access replies carry session/policy/selection versions. Changed selections and
sessions invalidate pending grants. Same-selection policy refreshes are applied
atomically so that an allowed App Permissions tab stays selected.

The permissions page starts as an empty hidden surface. Its actual table and
controller are constructed only after a feature grant. Programmatic activation of
a forbidden tab redirects to an allowed page. Permission reads/writes also enforce
Manufacturer authorization in the service.

Each `ApplicationGrant` reports `editable_roles`. The adapter derives locked cells
from that contract, so Manufacturer, protected and denied grants are displayed
consistently with backend policy. Updates use the displayed permission revision
and take effect in fresh navigation queries.

For Paint systems (including both dryer variants), `contourmatchingtester` locks
only Manufacturer access. Manufacturer can untick Admin in App Permissions and
save it. The updated policy denies Admin navigation as well as hiding the app.

## Workers and private displays

Storage/crypto/QR operations run through `BackgroundWorker`. Late results from a
different session cannot display a password, card, code set, history or user page.
Session invalidation closes private displays. `stop()` stops timers/workers,
closes bindings, and clears permission state before widget teardown.

Profile/password/role forms use shared `KeyboardLineEdit` widgets and scroll space
for the shared keyboard. Cards are generated as PNG bytes in memory. There is no
plaintext password QR or email-access-package API. Private dialogs clear their
text/image when closed and do not write credentials to temporary files.

The existing main stylesheet is preserved. New controls use that style or shared
style constants. Filters use stable field keys, so translation does not change
their meaning. English/Bulgarian catalogs cover initial labels, runtime changes,
permission notices and controller status/error text.

## Wiring and verification

Robot-system factories call
`src.bootstrap.account_application_wiring.build_account_user_management_application`.
The same runtime is used by login, navigation and account services.
See [account services](../../engine/auth/account_services.md) and the
[execution TODO](../../plans/access_control_todo.md) for external Twin activity and deployment work.

Current-session credential/role/deletion changes and permission writes require
idle operation. A busy reply leaves data unchanged; wait and retry. The shared
shell rechecks cached and lazy navigation in workers and clears invalid sessions
after domain and screen-owned work finish. These checks never stop robot motion.

```bash
QT_QPA_PLATFORM=offscreen .venv/bin/python -m unittest discover -s tests/applications/user_management -t . -q
```

Application tests use stubs. Temporary SQLite adapter integration is under
`tests/bootstrap/test_account_application_flow.py`. `example_usage.py` provides
the standalone stub runner. Historical CSV helpers still in the source tree are
outside the active application path.

<!-- source-navigation:start -->
## Source navigation

[Module reference](MODULES.md) — signatures, fields, imports and source links for every Python file in this directory.

| Source subdirectory | Guide |
|---|---|
| `controller/` | [controller](controller/README.md) |
| `domain/` | [domain](domain/README.md) |
| `localization/` | [localization](localization/README.md) |
| `model/` | [model](model/README.md) |
| `service/` | [service](service/README.md) |
| `ui/` | [ui](ui/README.md) |
| `view/` | [view](view/README.md) |

[Complete source index](../../SOURCE_INDEX.md).
<!-- source-navigation:end -->
