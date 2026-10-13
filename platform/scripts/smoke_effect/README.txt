PyQt6 WebGL Fluid Smoke Demo
============================

Install:
    python -m pip install PyQt6 PyQt6-WebEngine

Run:
    python main.py

The file fluid.js is copied from your supplied original simulation.
It runs inside QWebEngineView and is not rewritten as PyQt painting code.

The demo form is HTML layered above the WebGL canvas. It is not connected to a login backend.

Configuration: edit the 'config' object near the top of fluid.js.
For more frequent automatic smoke: change IDLE_DELAY from 2.0 to 1.0.
For tighter curls: increase CURL from 30 to 40 (GPU cost may increase).
For stronger initial color: increase IDLE_INTENSITY from 4.0 to 5.0.

If the screen is blank, verify that GPU acceleration / WebGL is available
in your Qt WebEngine environment and check the WebEngine console.
