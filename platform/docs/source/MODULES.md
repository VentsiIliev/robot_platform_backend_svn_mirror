# Module reference: `src`

[Package guide](README.md) · [Complete source index](../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [cam_server.py](#cam_serverpy)

## `__init__.py`

Source: [src/__init__.py](../../src/__init__.py).

No top-level functions, classes or public value declarations; inspect the source for imports or entry-point statements.

## `cam_server.py`

Source: [src/cam_server.py](../../src/cam_server.py).

Imports (including optional/function-local imports; not a startup dependency list): `atexit`, `cv2`, `flask`, `src.engine.vision.implementation.plvision.PLVision.Camera`, `threading`, `time`.

Module declarations (expressions are shown without evaluating them):

```python
cam_lock = threading.Lock()
frame_lock = threading.Lock()
frame_ready = threading.Condition(frame_lock)
cam = Camera(cameraIndex=0, width=1280, height=720, fps=30)
latest_jpeg = None
latest_frame_id = 0
capture_running = True
capture_thread = threading.Thread(target=_camera_loop, daemon=True)
app = Flask(__name__)
```

### `_camera_loop`

```python
def _camera_loop()
```

### `generate_frames`

```python
def generate_frames()
```

### `video_feed`

```python
def video_feed()
```

### `index`

```python
def index()
```

### `set_auto_exposure`

```python
def set_auto_exposure()
```

### `cleanup`

```python
def cleanup()
```
