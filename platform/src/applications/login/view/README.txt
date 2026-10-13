Position-fix release

Replace login view module with login_view.py (preserve your original module filename).
Place fluid_assets alongside the module.

Changes:
- Fix image coordinates via mapToGlobal/mapFromGlobal rather than mapTo sibling.
- Keep native Qt layouts and hidden placeholder labels for original positioning.
- Retain smoke composited in front of decorative images inside WebEngine.
- Increase automatic dye visibility modestly.
- Do not change login/QR controller signals.

Caveat: original machine image may itself have an opaque rectangular background;
this requires a truly transparent PNG for complete elimination.

Requires PyQt6-WebEngine. Not visually verified in your full application.
