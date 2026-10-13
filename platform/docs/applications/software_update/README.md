# Software Update

Shared MVC application using `ISoftwareUpdateService`. Its model has no Qt or
platform imports. Signed release checks and downloads run through BackgroundWorker;
the controller stops workers on cleanup. The screen supports English/Bulgarian
initial translation and runtime language switching.

Paint, Glue, Welding and Twin wire it into Administration with an administrator permission
policy and a process-state gate. Installation is queued only when the main process
is idle/stopped. Complete robot updates are applied outside the GUI after normal
shutdown by the independent per-user update service; the launcher waits and reopens
the application. Each target uses its own config and source. Twin refuses scheduling
with an attached runtime until it exposes an idle-state contract; offline CLI installation remains available.

See [complete robot installation and operation](../../../packaging/robot/README.md)
and [platform-only operation](../../../packaging/platform/README.md).

Check for updates remains available when updates are disabled or configuration
is missing. Clicking it reports the configuration problem in the screen status.
Checks run in the background and the button is disabled while an operation runs.
Download remains disabled until updates are enabled; installation requires a
staged release and the existing production-state gate.

While downloading and verifying, the view displays the shared fluid progress
widget in indeterminate mode because the updater service does not currently
publish byte-level progress. `SoftwareUpdateView.PROGRESS_WIDGET_STYLE` selects
the visual in one place and defaults to `"plume"`; `"ink"` and `"vessel"` are
drop-in alternatives. A successful download leaves the indicator at 100%, while
a failed download hides and resets it.

The same screen supports absolute local release directories for trusted testing,
or signed HTTPS feeds for remote updates. Both paths preserve machine data and
validate release identity/checksums before staging. See the local-feed example in
the packaging guide.

Every explicitly requested check presents its completed result in an information
dialog (new version or up to date), or a critical dialog when the check fails.
The status line retains the same result. Request/completion/failure logs help
diagnose signal or worker issues. Frozen self-tests exercise the Check button,
background result callback, selected update indicator, and every packaged fluid
progress variant without hardware or interactive dialogs.

<!-- source-navigation:start -->
## Source navigation

[Module reference](MODULES.md) — signatures, fields, imports and source links for every Python file in this directory.

| Source subdirectory | Guide |
|---|---|
| `controller/` | [controller](controller/README.md) |
| `localization/` | [localization](localization/README.md) |
| `model/` | [model](model/README.md) |
| `service/` | [service](service/README.md) |
| `view/` | [view](view/README.md) |

[Complete source index](../../SOURCE_INDEX.md).
<!-- source-navigation:end -->
