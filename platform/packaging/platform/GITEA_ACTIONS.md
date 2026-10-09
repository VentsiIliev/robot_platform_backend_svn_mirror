# Platform releases with Gitea Actions

The repository workflow [platform-release.yaml](../../../.gitea/workflows/platform-release.yaml)
is manually dispatched from Gitea and releases the platform for `paint_tray_dry`.
It calls the existing `packaging/platform/build_and_release.py paint_tray_dry`, which
reads `src/robot_systems/paint_tray_dry/VERSION`, builds the platform, runs its
frozen self-test, and packages the installer/update archive. It does not package
or start the ROS backend.

## One-time Gitea setup

1. Enable Actions on the Gitea instance and enable repository Actions in the repository settings.
2. Install and register an Actions runner on an Ubuntu 24.04 build machine, using a repository runner registration token. Give it the label `platform-release:host`; the workflow selects `platform-release`.
3. Provision Python 3.12, `python3-venv`, Git, Node.js 20 for `actions/checkout@v4`, `flock`, and the native libraries required by the platform (including ZBar, XCB cursor support, and Qt's other X11 dependencies). Complete `launch_robot_app.sh --setup-only` once as the runner user; jobs cannot answer an interactive sudo prompt.
4. Add repository Actions secret `ROBOT_RELEASE_TOKEN`: a Gitea access token with repository read/write access. It must belong to an account with write access to this repository. The workflow uses it for private checkout, tags, releases, and attachments.
5. Optionally set repository Actions variable `ROBOT_RELEASE_STORE` to an absolute directory writable by the runner. Otherwise artifacts are cached under the runner user's `~/.local/share/gitea-platform-releases/<owner>/<repository>/<source-commit>/`.

The runner must reach Gitea, the Python package index, and GitHub (checkout action
and the existing contour-editor wheel dependency). Register a runner on a build
machine; it need not be the Gitea server. ROS build prerequisites are not required
for this platform-only job. A running graphical desktop is not required: checks
use Qt offscreen.

Official instructions: [Actions quick start](https://docs.gitea.com/usage/actions/quickstart/),
[runner registration](https://docs.gitea.com/1.25/usage/actions/act-runner/), and
[Actions secrets](https://docs.gitea.com/usage/actions/secrets/).
Use a Gitea version supporting `workflow_dispatch` for the manual Run workflow button.

## Publish a platform version

1. Update `platform/src/robot_systems/paint_tray_dry/VERSION` to an unused version and commit the source and workflow changes.
2. From the development `git svn` checkout, publish to SVN first with `git svn dcommit`, then push the resulting `master` commit to Gitea.
3. Open **Actions → Publish paint tray dry platform → Run workflow**, selecting `master`.
4. Inspect the job logs and the resulting release under **Releases**.

The job checks SVN revision metadata in the selected commit before building. A
normal Actions clone cannot publish to SVN; this job does not call `git svn` or
need SVN credentials. SVN keeps source history, while Gitea hosts the version tag,
release notes, and downloadable build artifacts.

The helper creates/verifies the exact tag `paint_tray_dry/platform/v<VERSION>`.
A tag already pointing at another commit fails before building. The release starts
as a draft and becomes published after all attachments are uploaded:

- platform update archive;
- installer archive;
- `latest.json` update metadata;
- `release-manifest.json` recording source commit, SVN revision, and artifact hashes;
- `SHA256SUMS` for the build artifacts;
- `latest.json.sig` when a signing key was supplied to the helper.

The workflow does not supply a signing key, so its output supports manual
installation but does not enable the existing signed remote-update mechanism.
Gitea release attachments do not automatically become the updater's configured
repository/channel layout. Publishing does not install or activate a release on
any robot.

## Retry and artifact retention

The runner serializes publication with a file lock. Verified artifacts are cached
by source commit, avoiding a different archive on retry. Retry the same selected
commit after an upload failure. Existing attachments are compared by SHA256;
different files and incomplete already-published releases are not overwritten.

If packaging failed before its receipt was written, inspect the partial cached
output before retrying; the existing build script intentionally refuses to replace
an archive. Keep the runner artifact store backed up. Multiple runner hosts should
share the store/lock or use one designated release runner to preserve retry behavior.
Ensure Gitea permits attachments as large as both release archives.

The workflow and publisher have local fixture tests, but the job must still be
validated on the registered runner. Enabling Actions, installing a runner, and
adding the secret are server/machine setup steps, not changes performed by adding
this workflow file.
