# Module reference: `src/applications/login`

[Package guide](README.md) · [Complete source index](../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [example_usage.py](#example_usagepy)
- [i_login_application_service.py](#i_login_application_servicepy)
- [i_qr_scanner.py](#i_qr_scannerpy)
- [login_application_service.py](#login_application_servicepy)
- [login_factory.py](#login_factorypy)
- [stub_login_application_service.py](#stub_login_application_servicepy)

## `__init__.py`

Source: [src/applications/login/__init__.py](../../../src/applications/login/__init__.py).

No top-level functions, classes or public value declarations; inspect the source for imports or entry-point statements.

## `example_usage.py`

Source: [src/applications/login/example_usage.py](../../../src/applications/login/example_usage.py).

Standalone runner for the Login application. Demonstrates three scenarios: 1. Normal login — stub always accepts any numeric ID + password. 2. First-run — is_first_run()=True → first-admin creation form. 3. QR auto-login — try_qr_login() returns credentials after 4 s; fake camera frames are published so the live feed works. Run from the project root: python src/applications/login/example_usage.y_pixels [normal\|first_run\|qr]

Imports (including optional/function-local imports; not a startup dependency list): `PyQt6.QtCore`, `PyQt6.QtWidgets`, `cv2`, `logging`, `numpy`, `os`, `src.applications.login.login_factory`, `src.applications.login.stub_login_application_service`, `src.engine.auth.i_authenticated_user`, `src.engine.core.message_broker`, `src.engine.core.messaging_service`, `src.shared_contracts.events.vision_events`, `sys`, `typing`.

### `_FirstRunStub`

```python
class _FirstRunStub(StubLoginApplicationService):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def is_first_run(self) -> bool
```

### `_QrAutoStub`

```python
class _QrAutoStub(StubLoginApplicationService):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def try_qr_login(self) -> Optional[Tuple[str, str]]
```

```python
def move_to_login_pos(self) -> None
```

### `_FakeCameraPublisher`

```python
class _FakeCameraPublisher:
```

Publishes synthetic BGR frames at ~15 fps so the CameraView has something to show.

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self)
```

```python
def start(self) -> None
```

```python
def stop(self) -> None
```

### `_run`

```python
def _run(service, title: str, with_camera: bool=False) -> None
```

### `run_standalone`

```python
def run_standalone() -> None
```

## `i_login_application_service.py`

Source: [src/applications/login/i_login_application_service.py](../../../src/applications/login/i_login_application_service.py).

Imports (including optional/function-local imports; not a startup dependency list): `abc`, `src.engine.auth.i_authenticated_user`, `typing`.

### `ILoginApplicationService`

```python
class ILoginApplicationService(ABC):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
@abstractmethod
def authenticate(self, user_id: str, password: str) -> Optional[IAuthenticatedUser]
```

Verify credentials. Returns IAuthenticatedUser on success, None on failure.

```python
@abstractmethod
def authenticate_qr(self, qr_payload: str) -> Optional[IAuthenticatedUser]
```

Verify a QR-encoded payload. Returns IAuthenticatedUser on success, None on failure.

```python
@abstractmethod
def try_qr_login(self) -> Optional[Tuple[str, str]]
```

Poll the camera for a QR code. Returns (user_id, password) if a valid payload is detected, None otherwise.

```python
@abstractmethod
def move_to_login_pos(self) -> None
```

Move the robot to the QR scan position. No-op if no robot is configured.

```python
@abstractmethod
def is_first_run(self) -> bool
```

True if the user store is empty — setup wizard should be shown.

```python
@abstractmethod
def create_first_admin(self, user_id: str, first_name: str, last_name: str, password: str) -> Tuple[bool, str]
```

Create the initial admin user on first run. Returns (success, message).

## `i_qr_scanner.py`

Source: [src/applications/login/i_qr_scanner.py](../../../src/applications/login/i_qr_scanner.py).

Imports (including optional/function-local imports; not a startup dependency list): `abc`, `typing`.

### `IQrScanner`

```python
class IQrScanner(ABC):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
@abstractmethod
def scan(self) -> Optional[str]
```

Capture the latest camera frame and return a decoded QR payload, or None if no QR code is detected.

## `login_application_service.py`

Source: [src/applications/login/login_application_service.py](../../../src/applications/login/login_application_service.py).

Imports (including optional/function-local imports; not a startup dependency list): `src.applications.login.i_login_application_service`, `src.applications.login.i_qr_scanner`, `src.applications.user_management.domain.i_user_repository`, `src.applications.user_management.domain.user_schema`, `src.engine.auth.i_authenticated_user`, `src.engine.auth.i_authentication_service`, `src.engine.robot.interfaces.i_robot_service`, `typing`.

### `LoginApplicationService`

```python
class LoginApplicationService(ILoginApplicationService):
```

Application service for the login flow. Delegates auth to IAuthenticationService. Manages first-run detection, admin creation, optional robot positioning, and optional QR scanning. robot_service and qr_scanner are optional — features degrade gracefully when absent (useful in development or non-robot configurations).

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, auth_service: IAuthenticationService, user_repository: IUserRepository, robot_service: Optional[IRobotService]=None, qr_scanner: Optional[IQrScanner]=None, login_position: Optional[List[float]]=None, admin_role_value: str='Admin') -> None
```

```python
def authenticate(self, user_id: str, password: str) -> Optional[IAuthenticatedUser]
```

```python
def authenticate_qr(self, qr_payload: str) -> Optional[IAuthenticatedUser]
```

```python
def try_qr_login(self) -> Optional[Tuple[str, str]]
```

```python
def move_to_login_pos(self) -> None
```

```python
def is_first_run(self) -> bool
```

```python
def create_first_admin(self, user_id: str, first_name: str, last_name: str, password: str) -> Tuple[bool, str]
```

## `login_factory.py`

Source: [src/applications/login/login_factory.py](../../../src/applications/login/login_factory.py).

Imports (including optional/function-local imports; not a startup dependency list): `src.applications.login.controller.login_controller`, `src.applications.login.i_login_application_service`, `src.applications.login.model.login_model`, `src.applications.login.view.login_view`, `src.engine.core.i_messaging_service`, `typing`.

### `LoginFactory`

```python
class LoginFactory:
```

Builds and wires the login MVC triple, returns the dialog.

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
@staticmethod
def build(service: ILoginApplicationService, messaging: Optional[IMessagingService]=None, parent=None) -> LoginView
```

## `stub_login_application_service.py`

Source: [src/applications/login/stub_login_application_service.py](../../../src/applications/login/stub_login_application_service.py).

Imports (including optional/function-local imports; not a startup dependency list): `enum`, `src.applications.login.i_login_application_service`, `src.engine.auth.i_authenticated_user`, `typing`.

### `_StubUser`

```python
class _StubUser(IAuthenticatedUser):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
@property
def user_id(self) -> str
```

```python
@property
def role(self) -> Enum
```

### `StubLoginApplicationService`

```python
class StubLoginApplicationService(ILoginApplicationService):
```

Always authenticates successfully. Used in tests and standalone runners.

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def authenticate(self, user_id: str, password: str) -> Optional[IAuthenticatedUser]
```

```python
def authenticate_qr(self, qr_payload: str) -> Optional[IAuthenticatedUser]
```

```python
def try_qr_login(self) -> Optional[Tuple[str, str]]
```

```python
def move_to_login_pos(self) -> None
```

```python
def is_first_run(self) -> bool
```

```python
def create_first_admin(self, user_id: str, first_name: str, last_name: str, password: str) -> Tuple[bool, str]
```
