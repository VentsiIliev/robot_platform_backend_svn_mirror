# Publish changes to SVN, Gitea and GitLab

`scripts/publish_changes.py` automates the repository's shared `master` workflow:
stage selected changes → commit → `git svn dcommit` → `git push gitea-test master`
→ `git push gitlab-test master`.
Both Git servers receive the SVN-generated `master` history. GitLab’s existing
`main` and any earlier `gitea-test` branch are unchanged.
It uses standard-library Python and your installed Git/git-svn. Git/SVN prompts
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
`--remote NAME` overrides the default destinations (`gitea-test` and
`gitlab-test`). Repeat `--remote` to select multiple destinations. Publication is restricted to the shared `master` branch, including
an explicit rejection of the protected `run_main.py` branch.

## Retry an interrupted or failed publication

```bash
python3 platform/scripts/publish_changes.py --resume
```

`--resume` creates no commit and stages nothing. It requires a clean tree, runs
SVN publication and then retries both Git pushes. Use it after fixing credentials,
connectivity or another publication error. A failed Git push after a successful
SVN commit does not mean SVN failed; SVN is already published. If GitLab fails
after Gitea succeeds, Gitea is already published too. Retrying with `--resume`
safely pushes the same history to both servers. Do not rerun the
commit mode just to retry that push.

SVN publishes **all pending local commits**, not only the newly created commit.
The script prints that list before proceeding. SVN may rewrite Git IDs; the Git
push happens only when `HEAD` matches the SVN tracking commit and has SVN metadata.
Each failed command stops later steps. It never force-pushes, automatically
stashes changes, resolves conflicts or undoes a completed SVN publication.

## Checks and verification

Preflight verifies branch, SVN tracking/configuration, both Git remotes, installed
git-svn and absence of an active merge/rebase/cherry-pick/revert. Before committing
it checks staged whitespace; before/after SVN it checks the clean tree. These are
publication checks, not application tests: run appropriate project tests before
invoking it.

`tests/scripts/test_publish_changes.py` uses disposable local Git repositories
with simulated SVN/push adapters. It checks ordering, rewritten-head verification,
dry-run immutability, protected branches, leftover changes, SVN failure, missing remotes and retry
after either Git push fails. No real repository publication is performed by those tests.
