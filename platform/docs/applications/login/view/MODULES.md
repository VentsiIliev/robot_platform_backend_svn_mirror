# Module reference: `src/applications/login/view`

[Package guide](README.md) · [Complete source index](../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [login_view.py](#login_viewpy)

## `__init__.py`

Source: [src/applications/login/view/__init__.py](../../../../src/applications/login/view/__init__.py).

No top-level functions, classes or public value declarations; inspect the source for imports or entry-point statements.

## `login_view.py`

Source: [src/applications/login/view/login_view.py](../../../../src/applications/login/view/login_view.py).

Imports (including optional/function-local imports; not a startup dependency list): `PyQt6.QtCore`, `PyQt6.QtGui`, `PyQt6.QtWidgets`, `cv2`, `pathlib`, `pl_gui.utils.utils_widgets.camera_view`, `src.engine.auth.i_authenticated_user`, `typing`.

### `_FeedOnlyCameraView`

```python
class _FeedOnlyCameraView(CameraView):
```

CameraView with zoom, pan, and toolbar disabled — feed display only.

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, parent=None)
```

```python
def wheelEvent(self, event) -> None
```

```python
def mousePressEvent(self, event) -> None
```

```python
def mouseMoveEvent(self, event) -> None
```

```python
def mouseReleaseEvent(self, event) -> None
```

### `LoginView`

```python
class LoginView(QDialog):
```

Login dialog layout: ┌──────────────┬──────────────────────────────────────┐ │ │ Page 0: Setup steps │ │ Logo panel │ Page 1: First-admin creation │ │ (gradient) │ Page 2: [Login tab \| QR login tab] │ └──────────────┴──────────────────────────────────────┘ Signals ------- setup_confirmed() — user clicked "Next" on setup page login_submitted(user_id, password) — normal login button / Enter qr_scan_requested() — fired by QTimer while QR tab active qr_tab_activated() — user confirmed QR tab switch first_admin_submitted(id, fn, ln, pw) — first-run form submit

Declared fields/defaults:

```python
setup_confirmed = pyqtSignal()
login_submitted = pyqtSignal(str, str)
qr_scan_requested = pyqtSignal()
qr_tab_activated = pyqtSignal()
first_admin_submitted = pyqtSignal(str, str, str, str)
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, parent=None)
```

```python
def show_setup(self) -> None
```

```python
def show_login(self) -> None
```

```python
def show_first_run(self) -> None
```

```python
def show_error(self, message: str) -> None
```

```python
def accept_login(self, user: IAuthenticatedUser) -> None
```

```python
def result_user(self) -> Optional[IAuthenticatedUser]
```

```python
def start_qr_scanning(self) -> None
```

```python
def stop_qr_scanning(self) -> None
```

```python
def update_camera_frame(self, frame) -> None
```

Push a BGR numpy frame to the camera view. Called from the controller.

```python
def retranslateUi(self, *_) -> None
```

```python
def changeEvent(self, event) -> None
```

```python
def keyPressEvent(self, event) -> None
```

```python
def closeEvent(self, event) -> None
```

```python
def resizeEvent(self, event) -> None
```
