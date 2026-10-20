# Platform Settings

`PlatformSettings` is the shared administrator-facing application for platform
UI preferences. Its Appearance section provides a language selector, the virtual
keyboard switch, Light/Dark theme presets, and editable shared colors with color pickers, Apply colors,
and Restore defaults. Moving the color picker or editing a valid hex value
previews the colors immediately without writing preferences. Picker OK keeps
the preview; Cancel restores its previous color. Apply colors saves the palette
atomically, preserving unrelated settings. Leaving the page discards unsaved
previews. Restore defaults also previews until Apply is pressed. Invalid colors
do not change the preview; a failed save retains the draft without modifying
the saved palette. Virtual-keyboard changes are still saved immediately.

Light uses the original palette. Dark keeps the purple accent and uses dark
page/card surfaces, light text, and subdued borders. The shared runtime also
adapts muted text, secondary backgrounds, native table rows, tooltips, disabled
controls, and accent foregrounds for readability. Selecting a theme previews
it; Apply colors saves it. Editing a preset color changes the selector to
Custom. Returning to a preset replaces the draft with that preset. The selected
preset is inferred from its colors, so existing customized preferences remain
compatible without a second theme-mode setting.

Colors are stored in `ui.colors` using six roles: `primary`, `primary_dark`,
`background`, `surface`, `text`, and `border`. Each value must use `#RRGGBB`.
Installed systems save UI overrides to
`$ROBOT_PLATFORM_DATA_ROOT/platform/ui.json`; development uses
`config/platform.json`. Bootstrap loads saved colors before creating the shell.
Restore defaults restores the original shared styles, including historical
shell/application shade differences. Status colors and image assets retain
their own meaning and appearance.

Language uses the existing `ILocalizationService`, injected by bootstrap on the
robot system after QApplication exists. It keeps the existing per-system
`localization.json` persistence and layered catalogs. The header selector remains
available; changing either control synchronizes the other without another
language-change request. App-owned chrome is translated on initial rendering
and runtime language changes.

The view emits user intent; the controller delegates through the model to
`IPlatformSettingsService`. The production service owns persistence and delegates
to the shared appearance/localization APIs. `StubPlatformSettingsService` supports
standalone development without writing host preferences.

## Shared theme API

`pl_gui.theme` has no platform imports and ships with the standalone shell:

- `palette.py`: Qt-free defaults, validation, source color roles, live state,
  preset definitions, derived light/dark colors, and `ThemePreview` for reversible previews. Call `accept()` only after a
  successful durable save; call `discard()` when the editing session ends.
- `runtime.py`: one QObject per QApplication, installed with `install_theme(app)`.
  It updates the application palette and existing widget styles and handles new
  widgets and subsequent StyleChange events. Palette notifications repaint on
  the next GUI event-loop turn to avoid re-entering picker updates or widget
  teardown. The shell scopes its background to its root widget so child
  controls inherit their own themed surfaces. Original QSS is retained on each
  widget so changes and resets do not accumulate color substitutions.
- `icon.py`: an icon engine that resolves its tint when painted. The shared icon
  loader uses it for accent/text-tinted QtAwesome icons, including cached icons.
- `color_field.py`: a reusable picker accepting an injected line-edit widget.

Continue using shared style constants. For code that edits an existing widget
stylesheet, read `source_stylesheet(widget)` rather than its rendered QSS. Code
that only appends rules is also supported by the compatibility adapter. A widget
whose colors represent literal user data (such as a swatch) can opt out of QSS
mapping with `widget.setProperty("themeLiteralColors", True)`.

Custom-painted widgets must read `theme_palette.colors()` and connect a named
bound method to `install_theme(app).colors_changed`; Qt disconnects the receiver
when it is destroyed. Keep all widget mutation in the GUI thread. The shared
`QToggle` demonstrates this pattern. Raster assets, third-party plots, and
arbitrary colors outside the shared palette are not recolored automatically.

The shared virtual keyboard remains the single touch-input policy. The page is
scrollable, and color fields use `KeyboardLineEdit`; both top and bottom fields
remain accessible while the keyboard is open.
