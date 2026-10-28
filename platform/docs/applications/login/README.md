# Login and Admin recovery

Bootstrap calls `prepare_qt_application()` before constructing `QApplication`.
This enables shared OpenGL contexts so lazy login imports can load Qt WebEngine
after Qt starts. Production startup, the blueprint runner and the frozen self-test
use the same preparation hook; standalone views imported before Qt still work.

The login application uses the shared SQLite account runtime through
`ILoginApplicationService`. Its interface and DTOs depend only on Python's
standard library. The concrete application service is the adapter to the engine.

The deployment starts with an **empty account list**. Account setup is explicit;
the login screen does not import CSV files or initialize missing storage. See
[credential setup](../../engine/auth/credential_storage.md#fresh-setup-and-clean-cutover)
and the [recovery runbook](../../engine/auth/account_recovery_runbook.md).

## Contracts and flow

| Operation | Result |
|---|---|
| `authenticate(id, password)` | `LoginResult[LoginUser]` |
| `authenticate_qr(payload)` | `LoginResult[LoginUser]` |
| `scan_qr()` | `LoginResult[str | None]`, an opaque card payload |
| `is_first_run()` | `LoginResult[bool]`, from the durable commissioning flag |
| `create_first_admin(AdminSetup)` | `LoginResult[None]` |
| `recover_admin(AdminRecovery)` | `LoginResult[RecoveryCodeDisplay]` |
| `get_connection_information()` | Read-only connection identifiers |
| `move_to_login_pos()` | Optional existing robot-positioning operation |

`LoginSuccess(value)` and `LoginFailure(LoginError)` carry typed public outcomes.
`LoginErrorCode` distinguishes invalid input/proof, attempt limits, closed setup,
duplicate ID, and service unavailability. Infrastructure details stay behind the
adapter; controllers never display arbitrary exception text.

The model preserves password whitespace and trims only the login ID. The current
login form uses numeric IDs. First-Admin creation has a fixed Admin role and uses
commissioning state rather than counting users: a pre-provisioned Manufacturer
does not suppress first-customer-Admin setup.

Only a successful proof produces a safe `AccountPrincipal`. Bootstrap creates
the session after acceptance. Proof does not disclose hashes or credentials.

## Recovery and cards

An Admin enters a saved personal recovery code and a new matching password through
“Recover Admin account”. Recovery changes the password, revokes old credentials
and the entire old code set, and displays replacement codes once. It then returns
to ordinary login. Operators contact an Admin. Manufacturer/OS fallbacks are
documented in the runbook.

The shared private text dialog clears its content when closed and creates no file
or automatic clipboard export. Recovery commands and returned codes have redacted
representations.

Cards contain random `robot-login-v1:` tokens. Password-bearing QR formats are
rejected by the token service. `OpenCvQrScanner` implements `IQrScanner` using an
injected fresh image source; bootstrap injects the optional vision service's
`capture_corrected_image`. QR login therefore requires available calibrated fresh
capture. Acquisition failure does not fall back to a frozen frame. A system with
no vision service can still use normal login.

OpenCV, NumPy, qrcode and Pillow already have tested versions in root
`requirements.txt`. The scanner changes no camera or processing settings.

## Workers, lifecycle, and presentation

Authentication, commissioning queries/creation, recovery, QR scanning, and optional
robot positioning run through `BackgroundWorker`. Repeated submissions are blocked
while an operation is pending. `stop()` rejects late callbacks, joins workers,
and unsubscribes the named camera broker callback.

Camera frames arrive through a retained `_Bridge(QObject)`; Qt updates occur on
the GUI thread. Connection-information access retains its separate existing gate.

The existing fluid background, cards, button styles, and login/QR layout remain.
The recovery button uses the existing ghost style. New forms use shared touch
text inputs and shared styles. Login and recovery strings live in the app-local
English/Bulgarian catalogs. Static text and controller error text are retranslated.

`LoginFactory` owns the model/controller/dialog lifetime; this factory returns a
`QDialog`, so it intentionally has a separate lifecycle from `ApplicationFactory`.

## Verification

```bash
QT_QPA_PLATFORM=offscreen QTWEBENGINE_DISABLE_SANDBOX=1 .venv/bin/python -m unittest discover -s tests/applications/login -t . -q
```

Use `example_usage.py` for a standalone view with the application stub. Real account
adapter flows are covered under `tests/bootstrap/test_account_application_flow.py`.

<!-- source-navigation:start -->
## Source navigation

[Module reference](MODULES.md) — signatures, fields, imports and source links for every Python file in this directory.

| Source subdirectory | Guide |
|---|---|
| `controller/` | [controller](controller/README.md) |
| `localization/` | [localization](localization/README.md) |
| `model/` | [model](model/README.md) |
| `view/` | [view](view/README.md) |

[Complete source index](../../SOURCE_INDEX.md).
<!-- source-navigation:end -->
