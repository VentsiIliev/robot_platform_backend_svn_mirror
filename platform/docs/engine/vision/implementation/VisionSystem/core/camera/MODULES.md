# Module reference: `src/engine/vision/implementation/VisionSystem/core/camera`

[Package guide](README.md) · [Complete source index](../../../../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [frame_grabber.py](#frame_grabberpy)
- [remote_camera.py](#remote_camerapy)

## `frame_grabber.py`

Source: [src/engine/vision/implementation/VisionSystem/core/camera/frame_grabber.py](../../../../../../../src/engine/vision/implementation/VisionSystem/core/camera/frame_grabber.py).

Imports (including optional/function-local imports; not a startup dependency list): `collections`, `dataclasses`, `logging`, `src.engine.vision.frame_orientation`, `threading`, `time`.

### `FrameSnapshot`

```python
@dataclass(frozen=True)
class FrameSnapshot:
```

Declared fields/defaults:

```python
frame: object
timestamp_s: float
sequence: int
```

### `FrameGrabber`

```python
class FrameGrabber:
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, camera, maxlen=5, *, read_timeout_s=0.25, restart_after_failures=4, restart_cooldown_s=1.0, restart_max_cooldown_s=10.0, post_restart_settle_s=0.2, stale_frame_timeout_s=1.0, flip_horizontal=False, flip_vertical=False, rotate_degrees=0)
```

Threaded camera grabber. camera: Camera object with .capture() method maxlen: number of frames to keep in buffer read_timeout_s: timeout passed to camera.capture() for each frame read restart_after_failures: consecutive failed reads before attempting restart restart_cooldown_s: base wait between restart attempts (doubles on each failed restart, capped at restart_max_cooldown_s) restart_max_cooldown_s: upper bound for the restart backoff post_restart_settle_s: short wait after restarting the stream stale_frame_timeout_s: how long the latest buffered frame may be reused before it is considered stale and hidden from callers

```python
def start(self)
```

```python
def set_camera(self, camera) -> None
```

```python
def set_orientation(self, horizontal: bool, vertical: bool, rotate_degrees: int=0) -> None
```

Apply a new capture orientation to every frame acquired from now on. Buffered frames are dropped so no consumer can mix pre- and post-orientation geometry.

```python
def get_orientation(self) -> tuple[bool, bool, int]
```

```python
def is_transposed(self) -> bool
```

True when the applied rotation swaps the frame width and height.

```python
def get_latest(self)
```

```python
def get_latest_snapshot(self)
```

```python
def get_latest_snapshot_since(self, last_sequence: int, timeout_s: float | None=None)
```

```python
def pause(self) -> None
```

Suspend acquisition without closing the camera device.

```python
def resume(self) -> None
```

Resume acquisition and require callers to receive a newly captured frame.

```python
def stop(self)
```

## `remote_camera.py`

Source: [src/engine/vision/implementation/VisionSystem/core/camera/remote_camera.py](../../../../../../../src/engine/vision/implementation/VisionSystem/core/camera/remote_camera.py).

Imports (including optional/function-local imports; not a startup dependency list): `requests`, `src.engine.vision.implementation.plvision.PLVision.Camera`, `traceback`, `urllib.parse`.

### `RemoteCamera`

```python
class RemoteCamera(Camera):
```

Camera subclass for MJPEG HTTP streams. Delegates all capture and exposure control to Camera, which already handles http:// device strings via CAP_FFMPEG.

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, url: str, width=None, height=None, fps=None)
```

```python
def set_auto_exposure(self, enabled: bool)
```

Override Camera.set_auto_exposure — skips the stop/start stream cycle that causes SIGSEGV on FFMPEG HTTP streams. Sends an HTTP request to the camera server instead.
