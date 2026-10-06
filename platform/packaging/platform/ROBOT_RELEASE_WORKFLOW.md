# Local combined release workflow

Run from the combined checkout's `platform/` directory. The target and exact
versions default to `config/platform.json`; no second selection file is needed.

```bash
# Daily hardware-free release tests; works with uncommitted changes.
python3 -B packaging/platform/release_robot.py check

# Check the existing configured robot archive, including a temporary install.
python3 -B packaging/platform/release_robot.py verify

# Test, build missing components, assemble, and verify the installed archive.
python3 -B packaging/platform/release_robot.py build
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

## Publish to SVN and Gitea

After setting the desired versions in `config/platform.json` and committing the
source changes, run from `platform/`:

```bash
.venv/bin/python -B packaging/platform/release_robot.py publish
```

The target defaults to `robot_system`. `--remote` defaults to `gitea-test`; its
push URL must identify the Gitea HTTP(S) repository. `--notes-file /path/to/notes.md`
optionally supplies release notes. Create a Gitea access token with repository
write and user-read access. The command prompts for it without echoing, or reads
`GITEA_TOKEN` for unattended runs. The token is used for both API calls and Git
push authentication, and is not written to the stage report or command arguments.
SVN credentials must already be available or entered at its normal prompt.

The publication action:

1. Requires a clean `master` work branch and checks access to the configured Gitea repository.
2. Runs `git svn dcommit` for all pending commits before packaging records source identity.
3. Runs the release tests, builds missing pinned components, and assembles the robot archive, or verifies an existing archive of the selected version.
4. Verifies the archive through the temporary installation and frozen self-test.
5. Creates/verifies exact component and robot tags, then atomically pushes `master` and only those tags to Gitea, without force.
6. Creates a Gitea draft release on the robot tag, uploads the combined archive, SHA256 file, and manifest, and publishes it only after all uploads complete.

Notes include the SVN revision and component versions. This publishes one combined
robot release; component tags are pushed, but separate component release pages
are not created. A release must record an SVN revision. Existing artifacts that
lack one need a new version built after source publication.

If an upload fails, rerun `publish` with the same versions. The existing archive
is verified again; existing remote attachments are downloaded and compared by
SHA256 before being reused. Different artifacts, conflicting tags, or incomplete
already-published releases fail without overwriting them. Uploads stream from
disk rather than loading the entire archive into memory. Gitea's attachment limits
must accommodate the robot archive. Failed source synchronization, tests, builds,
or pushes stop the workflow; SVN publication cannot be rolled back automatically
if a later stage fails.

`check`, `build`, and `verify` remain local operations. No action automatically
bumps versions, stages or commits source, starts hardware, or activates a release
on a real machine. No SVN release tags are created. A runner can invoke the same
command once provisioned with the build prerequisites and repository credentials.
Broader release usage is in `deployment/README.md` in the combined checkout root.
