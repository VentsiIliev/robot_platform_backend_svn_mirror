# Publish changes to SVN and GitHub

`scripts/publish_changes.py` automates the repository's shared `master` workflow:
stage selected changes → commit → `git svn dcommit` → disposable LFS mirror → LFS upload → fast-forward GitHub `master`.
The GitHub destination is https://github.com/VentsiIliev/robot_platform_backend_svn_mirror.
Gitea and GitLab are no longer default publication destinations.
It uses standard-library Python and your installed Git/git-svn and Git LFS (`sudo apt-get install git-lfs` on Ubuntu). Git/SVN prompts
use your terminal; the script does not store credentials. No deployment or release
tag is created.

Run from the repository root:

```bash
cd /home/ilv/Desktop/25488_ZeroErr_git

# Preview first; does not stage, commit or publish
python3 platform/scripts/publish_changes.py --all -m "Describe changes" --dry-run

# Commit and publish every tracked/untracked change across the repository
python3 platform/scripts/publish_changes.py --all -m "Describe changes"
```

To control the commit scope, stage files yourself and omit `--all`:

```bash
git add -- platform/src/path/to/file.py platform/docs/path/to/README.md
python3 platform/scripts/publish_changes.py -m "Describe staged changes"
```

Alternatively pass file/directory paths after the options; paths are relative to
your current directory. Already staged changes are also included in the commit.
The script requires no unstaged/untracked leftovers before creating a commit,
because SVN publication needs a clean tree. If a partial selection leaves other
changes, it stops without committing and preserves the selected staging.

If run from `platform/`, use `python3 scripts/publish_changes.py` instead.
`--remote NAME` overrides the default destinations (`github-svn-mirror`). Repeat `--remote` to select multiple destinations. Publication is restricted to the shared `master` branch, including
an explicit rejection of the protected `run_main.py` branch.

## Retry an interrupted or failed publication

```bash
python3 platform/scripts/publish_changes.py --resume
```

`--resume` creates no commit and stages nothing. It requires a clean tree, runs
SVN publication and then retries the GitHub push. Use it after fixing credentials,
connectivity or another publication error. A failed Git push after a successful
SVN commit does not mean SVN failed; SVN is already published. Retrying with `--resume`
publishes an LFS projection of SVN history to GitHub without creating another SVN commit. Do not rerun the
commit mode just to retry that push.

SVN publishes **all pending local commits**, not only the newly created commit.
The script prints that list before proceeding. SVN may rewrite Git IDs; the Git
push happens only when `HEAD` matches the SVN tracking commit and has SVN metadata.
For a mirror-only retry after SVN has succeeded:

```bash
python3 platform/scripts/publish_changes.py --resume --github-only
```

This verifies that `master` matches `refs/remotes/git-svn` and has SVN metadata,
but neither stages/commits files nor calls SVN. Unrelated working edits can remain;
the mirror is built only from the committed SVN revision. `--github-only` requires
`--resume` and the default `github-svn-mirror` destination.

Each failed command stops later steps. It never force-pushes, automatically
stashes changes, resolves conflicts or undoes a completed SVN publication.

## Checks and verification

Preflight verifies branch, SVN tracking/configuration, selected Git remotes, installed
git-svn and absence of an active merge/rebase/cherry-pick/revert. Before committing
it checks staged whitespace; before/after SVN it checks the clean tree. These are
publication checks, not application tests: run appropriate project tests before
invoking it.

`tests/scripts/test_publish_changes.py` uses disposable local Git repositories
with simulated SVN/push adapters. It checks ordering, rewritten-head verification,
dry-run immutability, protected branches, leftover changes, SVN failure, missing remotes and retry
after a Git push fails. No real repository publication is performed by those tests.

## Large assets and the GitHub LFS projection

`github_lfs_mirror.py` creates a disposable clone from committed source `master`.
It runs `git lfs migrate import --above=104857600b --include-ref=refs/heads/master`
throughout that branch history, including oversized assets removed in later
revisions. The original Git/SVN checkout, index, branches, working files and SVN
revision map remain unchanged. The disposable clone stores Git LFS pointers and
matching `.gitattributes`; SVN continues to store full STL data.

Before uploading, the helper scans every reachable Git blob to verify the 100 MiB
limit and checks that GitHub's current `master` is an ancestor of the projected
head. It uploads all LFS objects, pushes normally (no force), then verifies the
remote head. Unexpected remote history or concurrent updates stop publication.
Network commands have timeouts. Git LFS uses the existing GitHub credentials;
no credentials are copied into source files or logs.

Rebuilding the projection from the same SVN history produces the same commit IDs.
Subsequent SVN revisions extend that projected history. Original commit IDs are
retained before the first oversized-blob conversion; later GitHub IDs differ from
SVN Git IDs while retaining their original `git-svn-id` lines. Match revisions
using that metadata, not equality between the two master hashes.

A reusable LFS data cache is kept under the source Git common directory at
`github-lfs-objects`; it is never committed. Dispose of failed temporary clones
without losing the source checkout or changing SVN history. LFS objects can be
recreated from the full Git blobs; no force-push or source migration is needed.
Use the same installed Git LFS version when publishing: if a future version
produces different projected history, the ancestry check stops instead of
rewriting GitHub.

For GitHub clones, install Git LFS, run `git lfs install`, and clone normally. For
an existing clone, run `git lfs pull` after updating to materialize assets. Direct
Git pushes from the canonical SVN branch bypass conversion and fail on oversized
STLs. Release tags need their corresponding projected GitHub commits too; this
script publishes `master`, not release tags.

`tests/scripts/test_github_lfs_mirror.py` uses real Git LFS and disposable local
remotes to check asset checksums, removed large blobs, deterministic repeat
publication, later fast-forwards, dirty-source preservation, unpublished SVN
commits and rejection of remote-only history. These tests do not contact GitHub
or SVN.
