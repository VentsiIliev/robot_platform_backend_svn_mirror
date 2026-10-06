# Module reference: `tests/applications/login`

[Package guide](README.md) · [Complete source index](../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [test_login_application_service.py](#test_login_application_servicepy)
- [test_login_controller.py](#test_login_controllerpy)
- [test_login_model.py](#test_login_modelpy)

## `__init__.py`

Source: [tests/applications/login/__init__.py](../../../../tests/applications/login/__init__.py).

No top-level functions, classes or public value declarations; inspect the source for imports or entry-point statements.

## `test_login_application_service.py`

Source: [tests/applications/login/test_login_application_service.py](../../../../tests/applications/login/test_login_application_service.py).

Tests for: src/applications/login/i_login_application_service.y_pixels src/applications/login/login_application_service.y_pixels src/applications/login/stub_login_application_service.y_pixels LoginApplicationService delegates auth to IAuthenticationService, manages first-run detection, admin creation, robot positioning, and QR scanning. All hardware dependencies are optional and safely no-op when absent.

Imports (including optional/function-local imports; not a startup dependency list): `src.applications.login.i_login_application_service`, `src.applications.login.i_qr_scanner`, `src.applications.login.login_application_service`, `src.applications.login.stub_login_application_service`, `src.applications.user_management.domain.i_user_repository`, `src.applications.user_management.domain.user`, `src.applications.user_management.domain.user_schema`, `src.engine.auth.i_authenticated_user`, `src.engine.auth.i_authentication_service`, `src.engine.robot.interfaces.i_robot_service`, `typing`, `unittest`, `unittest.mock`.

### `_mock_auth`

```python
def _mock_auth(user: Optional[IAuthenticatedUser]=None) -> IAuthenticationService
```

### `_mock_repo`

```python
def _mock_repo(records: list=None) -> IUserRepository
```

### `_mock_user`

```python
def _mock_user() -> IAuthenticatedUser
```

### `_mock_scanner`

```python
def _mock_scanner(payload: Optional[str]=None) -> IQrScanner
```

### `_make_service`

```python
def _make_service(auth=None, repo=None, robot=None, scanner=None, login_position=None) -> LoginApplicationService
```

### `TestInterface`

```python
class TestInterface(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_login_application_service_satisfies_interface(self)
```

```python
def test_stub_satisfies_interface(self)
```

### `TestAuthenticate`

```python
class TestAuthenticate(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_delegates_to_auth_service(self)
```

```python
def test_returns_none_when_auth_fails(self)
```

```python
def test_delegates_qr_to_auth_service(self)
```

### `TestIsFirstRun`

```python
class TestIsFirstRun(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_returns_true_when_repo_is_empty(self)
```

```python
def test_returns_false_when_repo_has_users(self)
```

### `TestCreateFirstAdmin`

```python
class TestCreateFirstAdmin(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_returns_true_on_success(self)
```

```python
def test_calls_repo_add(self)
```

```python
def test_stored_record_has_admin_role(self)
```

```python
def test_stored_record_has_correct_fields(self)
```

```python
def test_returns_false_when_repo_add_fails(self)
```

### `TestMoveToLoginPos`

```python
class TestMoveToLoginPos(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_calls_robot_move_ptp_with_configured_position(self)
```

```python
def test_move_to_login_pos_without_robot_service_returns_none(self)
```

```python
def test_does_nothing_when_no_position_configured(self)
```

### `TestTryQrLogin`

```python
class TestTryQrLogin(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_returns_none_when_no_scanner(self)
```

```python
def test_returns_none_when_scanner_finds_nothing(self)
```

```python
def test_returns_user_id_and_password_on_valid_payload(self)
```

```python
def test_returns_none_on_malformed_payload(self)
```

```python
def test_password_may_contain_colon(self)
```

Split on first colon only — password colons are preserved.

### `TestStubLoginApplicationService`

```python
class TestStubLoginApplicationService(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def setUp(self)
```

```python
def test_authenticate_always_returns_stub_user(self)
```

```python
def test_authenticate_qr_always_returns_stub_user(self)
```

```python
def test_is_first_run_returns_false_by_default(self)
```

```python
def test_create_first_admin_returns_success(self)
```

```python
def test_move_to_login_pos_returns_none(self)
```

```python
def test_try_qr_login_returns_none_by_default(self)
```

## `test_login_controller.py`

Source: [tests/applications/login/test_login_controller.py](../../../../tests/applications/login/test_login_controller.py).

Tests for src/applications/login/controller/login_controller.y_pixels

Imports (including optional/function-local imports; not a startup dependency list): `src.applications.login.controller.login_controller`, `src.applications.login.model.login_model`, `src.engine.auth.i_authenticated_user`, `unittest`, `unittest.mock`.

### `_make_user`

```python
def _make_user() -> IAuthenticatedUser
```

### `_make_model`

```python
def _make_model(user=None, first_run: bool=False, validation_error: str=None, admin_result=(True, 'Created'), qr_result=None) -> LoginModel
```

### `_make_view`

```python
def _make_view()
```

### `TestLoginControllerLoad`

```python
class TestLoginControllerLoad(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_load_shows_setup_page(self)
```

```python
def test_load_connects_setup_confirmed(self)
```

```python
def test_load_connects_login_submitted(self)
```

```python
def test_load_connects_qr_scan_requested(self)
```

```python
def test_load_connects_qr_tab_activated(self)
```

```python
def test_load_connects_first_admin_submitted(self)
```

```python
def test_load_does_not_call_show_login_or_first_run(self)
```

### `TestOnSetupConfirmed`

```python
class TestOnSetupConfirmed(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_shows_login_when_not_first_run(self)
```

```python
def test_shows_first_run_when_first_run(self)
```

### `TestOnLoginSubmitted`

```python
class TestOnLoginSubmitted(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_validation_error_shown_without_authenticate(self)
```

```python
def test_failed_auth_shows_error(self)
```

```python
def test_successful_auth_calls_accept_login(self)
```

### `TestOnQrTabActivated`

```python
class TestOnQrTabActivated(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_calls_move_to_login_pos(self)
```

### `TestOnQrScanRequested`

```python
class TestOnQrScanRequested(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_no_result_does_nothing(self)
```

```python
def test_qr_result_authenticates_and_accepts(self)
```

```python
def test_qr_bad_credentials_shows_error(self)
```

### `TestOnFirstAdminSubmitted`

```python
class TestOnFirstAdminSubmitted(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_create_success_logs_in(self)
```

```python
def test_create_failure_shows_error(self)
```

## `test_login_model.py`

Source: [tests/applications/login/test_login_model.py](../../../../tests/applications/login/test_login_model.py).

Tests for src/applications/login/model/login_model.y_pixels LoginModel is a thin delegation layer over ILoginApplicationService plus input validation logic.

Imports (including optional/function-local imports; not a startup dependency list): `src.applications.login.i_login_application_service`, `src.applications.login.model.login_model`, `src.engine.auth.i_authenticated_user`, `unittest`, `unittest.mock`.

### `_make_user`

```python
def _make_user() -> IAuthenticatedUser
```

### `_svc`

```python
def _svc(user=None, first_run: bool=False, admin_result: tuple=(True, 'Created')) -> ILoginApplicationService
```

### `TestLoginModelDelegation`

```python
class TestLoginModelDelegation(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_is_first_run_delegates_to_service(self)
```

```python
def test_authenticate_delegates_to_service(self)
```

```python
def test_authenticate_qr_delegates_to_service(self)
```

```python
def test_try_qr_login_delegates_to_service(self)
```

```python
def test_move_to_login_pos_delegates_to_service(self)
```

```python
def test_create_first_admin_delegates_to_service(self)
```

### `TestValidateLoginInput`

```python
class TestValidateLoginInput(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def setUp(self)
```

```python
def test_valid_input_returns_none(self)
```

```python
def test_empty_user_id_returns_error(self)
```

```python
def test_non_numeric_user_id_returns_error(self)
```

```python
def test_empty_password_returns_error(self)
```

```python
def test_whitespace_user_id_treated_as_empty(self)
```

```python
def test_whitespace_password_treated_as_empty(self)
```
