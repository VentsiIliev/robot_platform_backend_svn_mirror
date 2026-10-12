#!/usr/bin/env python3
"""Commit selected changes, publish through SVN, then push to Gitea and GitLab.

Run from this checkout (paths are relative to your current directory):
  python3 platform/scripts/publish_changes.py --all -m "Describe the change"
  python3 platform/scripts/publish_changes.py -m "Describe staged changes"
  python3 platform/scripts/publish_changes.py --resume

Add --dry-run to inspect the plan without staging, committing or publishing.
"""
from __future__ import annotations

import argparse
from pathlib import Path
import shlex
import subprocess
import sys


class PublicationError(RuntimeError):
    """A precondition or publication step failed."""


class Git:
    def __init__(self, root: Path) -> None:
        self.root = root

    def read(self, *args: str, allowed: tuple[int, ...] = (0,)) -> str:
        result = subprocess.run(
            ["git", *args], cwd=self.root, text=True,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        )
        if result.returncode not in allowed:
            raise PublicationError(result.stderr.strip() or f"git {shlex.join(args)} failed")
        return result.stdout.strip()

    def run(self, *args: str) -> None:
        print(f"\n$ git {shlex.join(args)}", flush=True)
        # Inherit terminal IO so normal Git/SVN credential prompts work. Never
        # read/store credentials or hide a failing command's diagnostics.
        result = subprocess.run(["git", *args], cwd=self.root)
        if result.returncode:
            raise PublicationError(f"git {shlex.join(args)} failed (exit {result.returncode})")


def resolve_paths(root: Path, paths: list[str]) -> list[str]:
    result = []
    for raw in paths:
        path = (Path.cwd() / raw).resolve()
        try:
            result.append(path.relative_to(root).as_posix())
        except ValueError as exc:
            raise PublicationError(f"Path is outside this repository: {raw}") from exc
    return result


def ensure_clean(git: Git) -> None:
    if git.read("status", "--porcelain", "--untracked-files=all"):
        raise PublicationError(
            "SVN publication requires a clean working tree. Commit all intended changes "
            "or preserve unrelated changes separately, then retry with --resume."
        )


def publish(git: Git, args: argparse.Namespace, paths: list[str]) -> None:
    branch = git.read("symbolic-ref", "--quiet", "--short", "HEAD", allowed=(0, 1))
    if branch != "master":
        raise PublicationError(
            f"Publish from the shared master work branch; current branch: {branch or 'detached HEAD'}. "
            "The run_main.py branch is protected."
        )
    git.read("rev-parse", "--verify", "refs/remotes/git-svn")
    git.read("config", "--get", "svn-remote.svn.url")
    for remote in args.remote:
        git.read("remote", "get-url", "--push", remote)
    git.read("svn", "--version")
    for state in ("MERGE_HEAD", "CHERRY_PICK_HEAD", "REVERT_HEAD", "rebase-merge", "rebase-apply"):
        state_path = Path(git.read("rev-parse", "--git-path", state))
        if not state_path.is_absolute():
            state_path = git.root / state_path
        if state_path.exists():
            raise PublicationError("Finish the active merge/rebase/cherry-pick/revert before publishing.")

    status = git.read("status", "--short", "--untracked-files=all")
    pending = git.read("log", "--oneline", "refs/remotes/git-svn..HEAD")
    print(f"Repository: {git.root}\nBranch: {branch}\nGit remotes: {', '.join(args.remote)}", flush=True)
    print("\nCurrent changes:\n" + (status or "(clean)"), flush=True)
    print("\nPending SVN commits (all will be published):\n" + (pending or "(none)"), flush=True)

    if args.resume:
        ensure_clean(git)
        commit_args = None
        stage_args = None
    else:
        stage_args = ["add", "--all"] if args.all else (["add", "--", *paths] if paths else None)
        commit_args = ["commit", "-m", args.message]
        # Detect unstaged/untracked leftovers before creating the commit. A
        # selected-path/staged-only commit cannot be dcommitted with leftovers.
        if stage_args is None:
            dirty = git.read("diff", "--name-only")
            untracked = git.read("ls-files", "--others", "--exclude-standard")
            if dirty or untracked:
                raise PublicationError(
                    "Unstaged/untracked changes remain. Stage all intended files or use --all; "
                    "preserve unrelated changes separately before publishing."
                )

    if args.dry_run:
        print("\nDry run: no files or repositories changed.")
        for command in (stage_args, commit_args, ["svn", "dcommit"],
                        *(["push", remote, "master"] for remote in args.remote)):
            if command:
                print("git " + shlex.join(command))
        return

    if stage_args:
        git.run(*stage_args)
    if commit_args:
        # A partial-path selection may leave unrelated changes. Stop before
        # committing; the user's selected staging remains available for review.
        if git.read("diff", "--name-only") or git.read("ls-files", "--others", "--exclude-standard"):
            raise PublicationError("Unstaged/untracked changes remain after staging; no commit was created.")
        if not git.read("diff", "--cached", "--name-only"):
            raise PublicationError("Nothing staged to commit. Use --resume to publish an existing commit.")
        git.run("diff", "--cached", "--check")
        git.run(*commit_args)
    ensure_clean(git)
    git.run("svn", "dcommit")
    ensure_clean(git)
    if git.read("rev-list", "--count", "refs/remotes/git-svn..HEAD") != "0":
        raise PublicationError("Local commits remain unpublished to SVN; Git push was skipped.")
    head = git.read("rev-parse", "HEAD")
    svn_head = git.read("rev-parse", "refs/remotes/git-svn")
    if head != svn_head or "git-svn-id:" not in git.read("log", "-1", "--format=%B"):
        raise PublicationError("HEAD does not match the SVN-generated commit; Git push was skipped.")
    for remote in args.remote:
        git.run("push", remote, "master")
    print(f"\nPublished to SVN and {', '.join(args.remote)}: {head}")


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("-m", "--message", help="Commit message; required unless --resume")
    parser.add_argument("--all", action="store_true", help="Stage all tracked/untracked changes across the repository")
    parser.add_argument("--resume", action="store_true", help="Publish existing commits; do not stage or create a commit")
    parser.add_argument("--dry-run", action="store_true", help="Display changes/commands without modifying any repository")
    parser.add_argument("--remote", action="append", help="Git push remote; repeat for multiple (default: gitea-test and gitlab-test)")
    parser.add_argument("paths", nargs="*", help="Files/directories to stage, relative to the current directory")
    args = parser.parse_args(argv)
    if args.resume and (args.message or args.all or args.paths):
        parser.error("--resume cannot be combined with a message, --all or paths")
    if not args.resume and (not args.message or not args.message.strip()):
        parser.error("provide a nonempty -m message, or use --resume")
    if args.all and args.paths:
        parser.error("choose --all or explicit paths")
    if args.remote is None:
        args.remote = ["gitea-test", "gitlab-test"]
    if any(not remote or remote.startswith("-") for remote in args.remote):
        parser.error("provide a valid remote name")
    return args


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        discovery = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"], text=True,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        )
        if discovery.returncode:
            raise PublicationError("Run this script from inside the git-svn checkout.")
        root = Path(discovery.stdout.strip()).resolve()
        publish(Git(root), args, resolve_paths(root, args.paths))
    except (OSError, PublicationError) as exc:
        print(f"\nPublication stopped: {exc}\nNo later publication steps were run.", file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        print("\nInterrupted. Check git status/SVN before retrying with --resume.", file=sys.stderr)
        return 130
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
