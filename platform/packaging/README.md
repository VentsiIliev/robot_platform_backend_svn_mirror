# Build and release entry points

For the complete robot system (platform and backend together), run from `platform/`:

```bash
source .venv/bin/activate
python3 -B packaging/robot/release_robot.py check paint_tray_dry
python3 -B packaging/robot/release_robot.py build paint_tray_dry
```

Set exact versions in `config/platform.json` and commit before building.
Use `verify` to check an existing archive and `publish` for the official SVN/Gitea
release workflow. See [complete robot releases](robot/README.md).

## Directory ownership

| Location | Purpose |
| --- | --- |
| `packaging/robot/release_robot.py` | Main complete-system release command |
| `packaging/robot/` | Complete-system orchestration, component archives, assembly and installer |
| `packaging/platform/` | Platform-only builder, installer kits and publication |
| `packaging/runtime/` | Installed launcher and update-service command entry point |
| `packaging/shared/` | Shared archive validation and Gitea publication helpers |
| `tests/packaging/` | Hardware-free combined packaging integration tests |
| `packaging/kiosk/` | Desktop kiosk and automatic login setup |
| `packaging/remote_support/` | Bundled remote support installation payload |
| `scripts/` | Development and hardware diagnostics, plus source publication helper |
| `build/` | Disposable build intermediates (ignored by Git) |
| `dist/` | Bundles, verification reports and local VM test feed (ignored by Git) |
| `../releases/TARGET/` | Immutable platform/backend/robot version archives (ignored by Git) |

Build outputs stay outside source history. Do not move or modify an existing
version archive; create a new version when software changes. The VM test feed
under `dist/install-tests/` contains local copies and is not the official publisher.

## Component-only development

`./packaging/platform/build.sh TARGET` builds a raw platform bundle without the
backend. [Platform-only tools](platform/README.md) and the
[platform-only Actions job](platform/GITEA_ACTIONS.md) remain available for that
specific use. Their installers should not replace a complete robot installation.
Per-system build/install/run wrappers have been removed.

The raw PyInstaller bundle includes Python dependencies; native OS libraries are
provisioned by the installer. [Remote support](remote_support/README.md) and
[kiosk setup](kiosk/README.md) describe the installation payloads.

## Publish source changes only

From `platform/`, after reviewing changes:

```bash
python3 -B scripts/publish_changes.py --all -m "Describe changes"
```

This commits, publishes to SVN, then pushes SVN-generated history to Gitea.
Use `--resume` to publish existing commits. It does not build or publish archives.
