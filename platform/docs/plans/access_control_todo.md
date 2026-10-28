# Access control implementation TODO

This is the execution checklist for
[requirements](role_capabilities_and_password_recovery.md) and
[architecture](access_control_architecture.md). Check an item only after its code
and relevant verification are complete. Backend availability is separate from
adoption by the running application. Tests use temporary stores. No installed
machine's accounts have been erased, initialized, or migrated by this work.

## Implemented foundations

- [x] Shared action/feature IDs and typed request, result, error, account, and audit contracts.
- [x] Replaceable target-aware access policy, context provider boundary, and query service.
- [x] Atomic session snapshots and revisions for stale-result rejection.
- [x] Reusable existing-widget/action/tab bindings preserving current styles.
- [x] SQLite account/credential/permission store and transactional append-only audit.
- [x] Authorized account/permission/history services with safe summaries and explicit commands.
- [x] Salted scrypt password hashing and typed account login service.
- [x] Explicit, idempotent empty-store setup. Legacy account import was removed after the confirmed empty-account decision.
- [x] Admin recovery-code backend with persisted throttling and atomic redemption/replacement.
- [x] Manufacturer-to-Admin password-reset fallback and audit verification.
- [x] OS-authorized Manufacturer creation/reset service and interactive maintenance command.
- [x] English/Bulgarian recovery runbooks and current-backend documentation.

## Credentials and installation state — current work

- [x] C1. Install/record the maintained encryption dependency used by the credential implementation (`cryptography==50.0.2` in root requirements; build requirements inherit it).
- [x] C2. Add a replaceable key-provider contract and protected local-file provider; explicit provisioning only.
- [x] C3. Implement authenticated Operator encryption with no plaintext fallback; keep password verification independent of key availability.
- [x] C4. Verify key permissions, corruption/loss, wrong-key behavior, backup/restore, concurrency, and unchanged Admin/Manufacturer hash-only storage (isolated tests; station backup rollout remains D1/D2).
- [x] C5. Add durable installation-state handling so missing established storage cannot reopen commissioning or re-import old credentials (explicit initialization and ordinary-open paths).
- [x] C6. Replace the previous import/mapping work with the confirmed empty-account cutover. Fresh initialization reads no old users, passwords, or grants.
- [x] C7. Document clean credential cutover: fresh accounts/passwords/cards, no required plaintext rollback backup, explicit retirement of old test credentials after live wiring is verified (see the credential storage guide).
- [x] C8. Add explicit fresh installation with no CSV/JSON sources, no default accounts, interruption recovery, immutable setup-mode choice, and an audited setup command.

## Runtime and role rollout

- [x] R1. Compose one shared account/access runtime and session per platform instance (backend composition and navigation adapter tested; live adoption is R2).
- [x] R2. Wire it into Paint, both Paint dryer variants, Glue, Welding, Twin Robot, and the blueprint; share the bootstrap session and application adapters.
- [x] R3. Replace live role catalogs/default schemas with Manufacturer/Admin/Operator alongside service enforcement; verify every supported system's catalog.
- [x] R4. Wire safe first-customer-Admin commissioning independent of Manufacturer provisioning; use a worker and the durable setup flag.
- [x] R5. Add application navigation authorization: Manufacturer sees all apps; Operator cannot open ADMIN/SERVICE apps even through stale grants/direct requests.
- [x] R6. Observe permission/session/account revisions and guard lazy opening/cached views. Both production startup and the blueprint adopt the async guard. Reject active-session access changes until idle; invalid session cleanup waits for domain/screen activity. Root mutation requires the platform's runtime lease to be released.
- [x] R7. Adopt persistent normal-login throttling in the running login flow; verify password/card shared global limits, restart, expiry, and credential invalidation.
- [x] R8. Add Twin's typed `get_activity()`/atomic `hold_idle()` runtime contract and account adapter. Account commits hold both process and external idle reservations; unknown/legacy adapters refuse changes. Tests cover concurrent starts, all active states, adapter replacement and rollback. A real external backend must implement the declared contract when deployed; none is shipped by this checkout.

## Application integration

- [x] U1. Adapt login/user-management/permissions to application-owned typed service contracts and typed error codes.
- [x] U2. Integrate existing buttons and tabs with access bindings and target/selection/busy state; test stale selection/session replies and ordinary-state preservation.
- [x] U3. Hide App Permissions from Admin/Operator, defer protected data loading, and enforce Manufacturer-only reads/writes, including direct calls.
- [x] U4. Provide own-password change, Operator password change/reveal, and the agreed account-management controls.
- [x] U5. Display creation/edit metadata and authorized account history without exposing credential material.
- [x] U6. Add Admin recovery entry, private one-time code display/regeneration, and replacement-code handover; normal login is required after recovery.
- [x] U7. Run blocking authentication/credential/storage operations through the existing worker pattern.
- [x] U8. Add English/Bulgarian initial translations and runtime retranslation for new UI text (catalog parity/source coverage, initial Bulgarian forms and runtime English switch verified).
- [x] U9. Replace password-bearing QR/email exports with authorized revocable credentials. Verify generated PNG -> decoded opaque token -> login -> revocation after password change. Discard old test cards; no legacy password-QR fallback.
- [x] U10. Apply the shared pattern to the agreed protected account/permission entry points, reusable button/tab/action adapters, lazy factory and cached navigation; domain-specific actions have an extension contract. No additional domain role restrictions were specified.

## Completion and delivery

- [x] V1. Verify the role matrix in screen/controller/adapter tests and direct-service/navigation attempts, plus every supported system's catalog. Physical station acceptance remains D2; the actual external Twin backend remains D3.
- [x] V2. Verify recovery/Manufacturer/OS maintenance, interrupted empty setup, missing key/store, and key backup restoration with isolated stores. Production backup verification remains D1/D2.
- [x] V3. Visual comparison of Admin/Manufacturer screens and account/recovery forms; original Login/UserManagement stylesheet ASTs unchanged, shared controls used, touch field checks completed.
- [x] V4. Update system/application/blueprint guides for the final runtime pattern and default/configured storage paths; actual station paths remain D1.
- [x] V5. Run the required repository entry point and relevant integration checks; record unrelated failures separately. The full repository suite is still red; see verification below.
- [x] V6. Build a stdlib-only maintenance payload, fixed-path root-owned installer, and source/frozen location-record command. Both bundle builders include the payload. Exact runtime/setup paths share one resolver; the record includes an explicitly supplied backup location. Real station records are D1 below.
- [x] V7. Document/rehearse empty-store commissioning, first Admin, saved-code recovery, Manufacturer fallback, OS maintenance and separate-key backup/restore using real scrypt/Fernet in disposable storage. Physical station handover remains D1–D3 below.

## Station deployment — requires an identified target

The remaining code and local verification are complete. No machine address or
installation path was supplied, so this work uses disposable installations. See
[commissioning/handover](../installation/account-handover.md).
Read-only inspection found two older local Paint Tray Dryer installations
(combined and platform-only), neither with the new account store. Their existence
does not select one for commissioning. Target selection is pending; neither has
been launched, initialized, or changed by this work.

- [ ] D1. Identify the actual installation/OS account, install the reviewed root maintenance payload, run explicit empty setup and retain its actual path/backup record. No live store was initialized or erased by development.
- [ ] D2. Provision named accounts privately, hand over fresh recovery codes/cards and verify role/recovery/idle behavior and approved backups on that station. Physical robot acceptance cannot be replaced by unit tests.
- [ ] D3. If deploying Twin with an external motion runtime, implement/verify its authoritative activity and atomic idle-reservation contract against both robots. Platform integration is complete; this repository has no concrete external Twin motion adapter.

## Decisions already settled

- Multiple individual Manufacturer, Admin, and Operator accounts; remove Viewer/Developer roles.
- Start with an empty account list. This supersedes the earlier Viewer/Developer conversion proposal; no accounts or passwords are imported.
- Admin manages Operators and their own profile/password; other Admin/Manufacturer management is Manufacturer-only.
- Operator never sees or opens Administration/Service. Manufacturer sees all applications.
- App Permissions is Manufacturer-only. Visibility and execution are independent gates.
- Admin personal offline recovery codes, Manufacturer reset fallback, and OS-authorized last-resort Manufacturer maintenance.
- SQLite behind contracts; user metadata and durable action history; current styles preserved.
- Protected local key storage is the initial implementation behind a replaceable provider; production provisioning/backup must be recorded before cutover.
- These systems are not in production. Use new account storage/passwords/cards for cutover; old credentials, identity import, and legacy-login fallback are unnecessary.
- Confirmed: reject access changes affecting the current session until idle. Keep robot stop semantics unchanged. Busy recovery preserves the saved code for retry.

## Progress notes

- Login/user-management providers use the shared SQLite runtime. Production/blueprint shell navigation reauthorizes lazy and cached openings, rejects stale replies, and polls session/grants in workers.
- Existing unrelated working changes in motion/backend code are outside this checklist.
- Baseline full-suite issues recorded earlier include a missing `.coveragerc` and existing failures; targeted checks are reported with each implementation slice.
- `pip check` after adding cryptography reports existing ROS-package requirements for missing PyYAML/typeguard; no cryptography dependency conflict is reported. These packages were not introduced by this work.
- Initial consolidated account/login/user-management/bindings/bootstrap/catalog/appearance checks: **455 passing**. Final completion verification expands this to **497 passing** with Twin, payload, installed tools, handover/restore, update interlocks and release-target tests.

## Verification recorded 2026-10-28

- Required `.venv/bin/python tests/run_tests.py` stops before discovery because the existing root `.coveragerc` is missing. No coverage configuration was added as part of account work.
- Direct rooted discovery (`QT_QPA_PLATFORM=offscreen QTWEBENGINE_DISABLE_SANDBOX=1 .venv/bin/python -m unittest discover -s tests -t . -q`) ran **4,142 tests: 9 failures, 18 errors, 24 skipped**. Remaining failures concern existing import-debt expectations, ROS/backend identity, motion completion, updates, settings, and Paint/Glue lifecycle/wiring. They are outside account changes. The single Unix-socket sandbox error passes when rerun outside the sandbox; the other errors remain unrelated.
- The appearance fixture now exercises the lazy permission page and the normal window-close path before native Qt teardown. Its 11 tests pass independently; appearance is also in the 455-test focused run. An isolated Platform Settings interpreter exit without closing windows can still expose a Qt shutdown crash outside that normal close path; authorization code does not alter the theme implementation.
- English/Bulgarian catalog key parity and literal UI source coverage pass. Account/recovery forms were tested with initial Bulgarian and runtime English switching; role IDs and private data stay unchanged by translation.
- Original Login/UserManagement stylesheet ASTs match the checked-in originals exactly. Account/recovery form and Admin/Manufacturer screen previews were inspected. Relevant Python modules compile and diff whitespace checks pass.
- All account/setup/recovery tests use temporary stores. Existing installation databases, keys, users, robot operations and unrelated motion/backend edits were not reset or migrated.

## Completion verification recorded 2026-10-28

- **497 focused tests pass**, including real scrypt/Fernet commissioning and recovery/backup restoration, authoritative Twin activity/reservation cases, isolated-system-Python payload execution, staged installer ownership/mode/path checks, installed setup/path commands, update interlocks and bundle inclusion.
- Independent packaging integration: **4 tests pass**. Relevant implementation modules compile and whitespace checks pass. No new third-party dependencies were introduced in this completion slice.
- The standalone maintenance payload is built at `dist/account-maintenance/` with a checksum, root installer and guide. It was not installed into `/usr/local` on this workstation. New full platform bundles stage it automatically. No full robot release, version bump or remote publication was performed.
- Installed launchers now expose `--account-locations` and explicit `--account-setup`, both before GUI/backend startup. Release preparation forces `ui.dev_skip_login=false`, preserving source development settings while securing installed defaults.
- The selected `paint_tray_dry` release gate ran 139 tests and reported 3 failures: two existing backend-identity cases plus an update-daemon test. The daemon test passes outside the sandbox (local socket restrictions); the two backend cases remain unrelated release blockers. The packaging integration stage was run independently and passes. No failed stage was bypassed to produce a robot release.
- Full-repository failures and the missing `.coveragerc` recorded above remain outside this account task. The handover guide distinguishes local rehearsal from actual station commissioning and records the new Twin backend obligations.
- Final installation checks: **21 tests pass**, including interrupted-update and exclusive updater-lease refusals before account setup can write data. Path reporting/setup honor the updater lock before returning without hardware startup.

## Publication/update preparation

- The test machine is on **1.0.17**, confirmed against the existing test-feed manifest. That version uses backend **1.0.1 / paint_short_links**. The 1.0.18 candidate retains that exact backend and advances robot/platform versions only.
- Restoring the backend target/profile check fixes the two identity-test failures. The required release gate now passes **139 release tests plus 4 packaging integration tests** outside the socket-restricted sandbox.
- The isolated account/release candidate passes **512 focused tests**, including all account checks and the backend-launcher tests. Separate motion/backend/calibration edits remain untouched and excluded pending the requested publication-scope choice.
- Source publication has not run: SVN at the configured `192.168.2.101:8443` reports `No route to host` from the current workstation network. GitHub mirror read access succeeds. The required ordering remains SVN dcommit, then projected GitHub mirror, then official build from synchronized source.
- Kiosk credential reuse and final publication scope are awaiting the release operator's choices. No full 1.0.18 robot archive has been built or promoted. Existing versioned releases and the 1.0.17 test feed remain unchanged.
