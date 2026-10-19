# Platform Settings

`PlatformSettings` is the shared administrator-facing application for
platform-wide user-interface preferences. Paint and its variants, Glue,
Welding, and Twin Robot register it in the Administration folder and restrict
it to the Admin role.

The initial Appearance section exposes `ui.custom_virtual_keyboard_enabled`.
The packaged `platform.json` value remains the factory default. On installed
systems, operator changes are persisted to
`$ROBOT_PLATFORM_DATA_ROOT/platform/ui.json`; source-tree development runs
persist to `config/platform.json`.

Virtual-keyboard changes take effect immediately. Shared keyboard-capable
fields query the process-wide policy whenever they are focused, and disabling
the setting closes an open keyboard and restores any temporary scroll/layout
adjustments. `VirtualKeyboardWidgetFactory` always creates the shared
keyboard-capable field types so screens built while the feature is disabled
can respond when it is enabled later.

The application follows the standard MVC boundary: the view emits the toggle,
the controller delegates through the model, and `PlatformSettingsService`
atomically persists the preference before updating the live policy. English
and Bulgarian strings are owned by the application-local localization
catalogs. Language selection remains in its existing shell location and is not
part of this application yet.
