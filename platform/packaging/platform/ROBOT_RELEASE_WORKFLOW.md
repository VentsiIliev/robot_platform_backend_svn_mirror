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

No version bump, commit, SVN upload, tag creation, external publication or real
machine activation is performed automatically. Jenkins can later invoke these
same commands. Broader release usage is in `deployment/README.md` in the combined
checkout root.
