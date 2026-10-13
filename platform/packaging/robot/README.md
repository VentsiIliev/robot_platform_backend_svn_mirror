# Local combined release workflow

Run from the combined checkout's `platform/` directory. The target and exact
versions default to `config/platform.json`; no second selection file is needed.

```bash
# Daily hardware-free release tests; works with uncommitted changes.
python3 -B packaging/robot/release_robot.py check

# Check the existing configured robot archive, including a temporary install.
python3 -B packaging/robot/release_robot.py verify

# Test, build missing components, assemble, and verify the installed archive.
python3 -B packaging/robot/release_robot.py build
```

An optional final target argument selects an explicitly configured entry, e.g.
`check paint_tray_dry`. These checks currently cover the configured paint/ZeroErr
release workflow; they do not certify other robot systems or real hardware.

Build requires committed, clean source and unused robot release version. For a
platform-only change, increment `platform_version` and `release_version`, retain
the tested `backend_version`, and commit/upload source before the official build.
Existing components are checksum/identity validated and reused. Corrupt or
incompatible components fail rather than being rebuilt or overwritten.

The workflow stops on failure. JSON stage reports are retained under the ignored
`dist/release-checks/` directory, with commands, durations, status and verified
archive checksum. Terminal output contains detailed test/build errors. A failed
post-build check leaves the archive available for diagnosis, with a failed report;
only a passed report indicates this workflow accepted it. Use `verify` to retry
the configured archive check. Existing versions and tags are never replaced.

Verification extracts the actual combined archive, compares its embedded manifest,
runs its installer into a disposable root, then invokes the installed launcher
with `--self-test` and Qt offscreen. It never installs into the real machine root,
starts the GUI main loop, launches backend nodes, or performs hardware acceptance.
The separate packaging integration suite checks rollback/data preservation,
runtime locks, archive traversal, and exact component matching using fixtures.

The required platform suite covers startup selection, backend launcher contracts,
paint override isolation, release targets, and release orchestration. This is a
curated release gate, not the full application suite. Known stale paint integration
fixtures and `test_paint_packaging_profile` source-layout assertions need repair
before adding them to the gate. ROS package unit tests and lazy-screen construction
checks are not included yet; backend builds retain their existing relocation and
package-discovery checks. Frozen self-tests do not replace machine acceptance.

## Publish to SVN and GitHub

After setting the desired versions in `config/platform.json` and committing the
source changes, run from `platform/`:

```bash
.venv/bin/python -B packaging/robot/release_robot.py publish
```

The target defaults to `robot_system`. `--remote` defaults to `github-svn-mirror`; its
push URL must identify a GitHub repository through HTTPS or the usual GitHub SSH URL. `--notes-file /path/to/notes.md`
optionally supplies release notes. Create a GitHub access token with repository
contents read/write access. The command prompts for it without echoing, or reads
`GITHUB_TOKEN` for unattended runs. The token is used for both API calls and Git
push authentication, and is not written to the stage report or command arguments.
SVN credentials must already be available or entered at its normal prompt.

The publication action:

1. Requires a clean `master` work branch and checks access to the configured GitHub repository.
2. Runs `git svn dcommit` for all pending commits before packaging records source identity.
3. Runs the release tests, builds missing pinned components, and assembles the robot archive, or verifies an existing archive of the selected version.
4. Verifies the archive through the temporary installation and frozen self-test.
5. Creates/verifies exact component and robot tags, then atomically pushes `master` and only those tags to GitHub, without force.
6. Creates a GitHub draft release on the robot tag, uploads the combined archive, SHA256 file, and manifest, and publishes it only after all uploads complete.

Notes include the SVN revision and component versions. This publishes one combined
robot release; component tags are pushed, but separate component release pages
are not created. A release must record an SVN revision. Existing artifacts that
lack one need a new version built after source publication.

If an upload fails, rerun `publish` with the same versions. The existing archive
is verified again; existing remote attachments are downloaded and compared by
SHA256 before being reused. Different artifacts, conflicting tags, or incomplete
already-published releases fail without overwriting them. Uploads stream from
disk rather than loading the entire archive into memory. GitHub's per-asset size limit must accommodate the robot archive. Failed source synchronization, tests, builds,
or pushes stop the workflow; SVN publication cannot be rolled back automatically
if a later stage fails.

`check`, `build`, and `verify` remain local operations. No action automatically
bumps versions, stages or commits source, starts hardware, or activates a release
on a real machine. No SVN release tags are created. A runner can invoke the same
command once provisioned with the build prerequisites and repository credentials.
Broader release usage is in `deployment/README.md` in the combined checkout root.

## Installed system and update service

The combined installer is run as the desktop user after verifying and extracting
the archive:

```bash
python3 -B robot/install.py
```

First installation provisions native dependencies, remote support, GNOME Kiosk
and the per-user updater. Kiosk provisioning automatically installs the shared
exit-password hash embedded during the platform build; repeated installation
preserves the station's existing hash.
Maintenance installation preserves desktop and machine settings. Explicit
`--setup-system --kiosk enabled` retries system provisioning.
Package installation waits for the apt/dpkg lock held by automatic OS updates.

Installed layout:

```text
~/.local/share/robot-releases/paint_tray_dry/
    releases/VERSION/{platform,backend,manifest.json}
    current -> releases/VERSION
    launch.sh
    tools -> versioned updater tools
    data/
    updates.json
    update-state/
```

The separate `robot-update-paint_tray_dry.service` runs in the desktop user's
systemd manager. The Software Update screen sends it check, download and queue
requests. It verifies and stages the complete release, waits until the platform
exits, stops the bundled backend, and switches both components together. The
stable launcher waits for activation and reopens the platform. This service
requires a running user manager; no system-wide daemon or user lingering is
configured by the installer.

Before an existing installation activates a candidate, the updater compares its
remote-support package version with the candidate's `release.conf`. A matching
version skips installation; a required upgrade uses the root-owned restricted
helper. Failure blocks robot activation. Existing machines need one trusted
installer maintenance run to provision that helper and refresh the user service.
See [remote-support configuration and trust](../remote_support/README.md).
Application rollback does not revert this machine-wide package installation.
Automatic kiosk updates are deferred; software updates preserve kiosk settings.

```bash
systemctl --user status robot-update-paint_tray_dry.service
journalctl --user -u robot-update-paint_tray_dry.service -n 80 --no-pager
```

`updates.json` is seeded from the selected system-owned `storage/update_source.json` only on first installation and preserved thereafter. See [per-system sources](../../docs/robot_systems/update_sources.md).
A `repository_type` of `github` or `gitlab` selects complete robot release attachments;
`feed` and `svn` read `stable/latest.json` and the referenced archive. Legacy `gitea` remains supported for existing stations. Private GitHub/GitLab
repositories require a machine-local `token_file`. Never embed credentials in
archives or source. Plain HTTP needs explicit `allow_insecure_http`; use it only
for the trusted LAN/test setup. Signed sources use the configured public key.

The VM test feed uses `http://10.0.2.2:8768/`, served on the host from
`platform/dist/install-tests/complete-updates/`. It is independent of GitHub.
The VM test successfully updated 1.0.6 to 1.0.7; real robot hardware acceptance
remains separate. Mutable settings and update-source configuration are preserved.
