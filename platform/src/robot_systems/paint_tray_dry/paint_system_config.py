"""Optional overrides for this paint robot system.

Shared defaults live in src.robot_systems.paint.paint_system_config.
Declare only values that should differ for this system, using the same names.
Unspecified values inherit the shared defaults. Overrides apply to this system
only; they never modify the shared module or another paint system.
These are source-controlled application/diagnostic switches, not machine settings.

Examples (uncomment to override):
    SHOW_DASHBOARD_CAMERA_PREVIEW = True
    PAINT_ADJUSTMENT_APP = False
    BYPASS_CONTOUR_PREPARATION = False

"""

# Keep image capture available in this profile independently of shared defaults.
IMAGE_CAPTURE_APP = True
IMAGE_CAPTURE_FOLDER_ID = 4  # Tests
