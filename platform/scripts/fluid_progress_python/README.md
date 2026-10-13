# Fluid Progress — native PySide6 port

Three reusable `QWidget` implementations of the attached HTML concepts:

- `InkBar`: rounded ink-filled progress bar with animated wavy edge
- `Vessel`: circular liquid vessel with animated surface and contrast-aware percentage
- `PlumeLine`: thin progress line with a glowing moving head and smoke trail

## Run

```bash
python -m pip install -r requirements.txt
python demo.py
```

All three widgets appear together in one window and share demo controls.

## Embed in your application

```python
from widgets import InkBar, Vessel, PlumeLine

widget = InkBar()  # or Vessel(), PlumeLine()
widget.set_progress(42, speed_mb_s=5.5)
widget.set_running(True)
widget.set_waiting(False)
# widget.reset()
```

Call `set_progress()` from the GUI thread. The demo's download is simulated; connect your actual download signals to the widget in production. The port approximates Canvas radial gradients and particles with QPainter, not WebGL.
