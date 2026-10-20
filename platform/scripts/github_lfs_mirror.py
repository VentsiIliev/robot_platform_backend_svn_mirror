"""Publish an LFS projection of SVN history without rewriting the git-svn checkout."""
from __future__ import annotations

from dataclasses import dataclass
import os
from pathlib import Path
import shlex
import subprocess
import tempfile

GITHUB_BLOB_LIMIT = 100 * 1024 * 1024


class MirrorError(RuntimeError):
    pass


@dataclass(frozen=True)
class MirrorResult:
    source_head: str
    mirror_head: str


def command(root: Path, *args: str, capture: bool = False,
            allowed: tuple[int, ...] = (0,)) -> str:
    if not capture:
        print(f"\n$ git {shlex.join(args)}", flush=True)
    environment = dict(os.environ, GIT_LFS_SKIP_SMUDGE="1", GIT_TERMINAL_PROMPT="0")
    # Bound failed network/authentication attempts; never wait indefinitely on SSH.
    environment.setdefault("GIT_SSH_COMMAND", "ssh -o BatchMode=yes -o ConnectTimeout=15 "
                           "-o ConnectionAttempts=1 -o ServerAliveInterval=15 -o ServerAliveCountMax=2")
    try:
        result = subprocess.run(["git", *args], cwd=root, env=environment, text=True,
                                stdout=subprocess.PIPE if capture else None,
                                stderr=subprocess.PIPE if capture else None, timeout=300)
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise MirrorError(f"git {shlex.join(args)}: {exc}") from exc
    if result.returncode not in allowed:
        detail = result.stderr.strip() if capture else f"exit {result.returncode}"
        raise MirrorError(f"git {shlex.join(args)} failed: {detail}")
    return result.stdout.strip() if capture else ""


def oversized_blobs(root: Path, ref: str, limit: int = GITHUB_BLOB_LIMIT) -> list[tuple[str, int]]:
    """Check all reachable blobs, including assets removed from the latest tree."""
    objects = command(root, "rev-list", "--objects", "--no-object-names", ref, capture=True)
    if not objects:
        return []
    result = subprocess.run(["git", "cat-file", "--batch-check=%(objectname) %(objecttype) %(objectsize)"],
                            cwd=root, input=objects+"\n", text=True, capture_output=True, check=True)
    oversized = []
    for line in result.stdout.splitlines():
        oid, kind, size = line.split()
        if kind == "blob" and int(size) > limit:
            oversized.append((oid, int(size)))
    return oversized


def publish_github_mirror(source: Path, remote: str, *, limit: int = GITHUB_BLOB_LIMIT) -> MirrorResult:
    """Build a deterministic projection, upload LFS objects, then fast-forward master.

    All rewrites and hooks live in a disposable clone. Its LFS object cache lives
    under the source Git directory, so retrying does not discard the asset data.
    Neither the source index, working files, branches nor SVN metadata are changed.
    """
    source = source.resolve()
    head = command(source, "rev-parse", "refs/heads/master", capture=True)
    svn_head = command(source, "rev-parse", "refs/remotes/git-svn", capture=True)
    if head != svn_head or "git-svn-id:" not in command(source, "log", "-1", "--format=%B", head, capture=True):
        raise MirrorError("Publish to SVN first: master must match the SVN-generated commit")
    # Fail before cloning or uploading if LFS is unavailable.
    command(source, "lfs", "version", capture=True)
    url = command(source, "remote", "get-url", "--push", remote, capture=True)
    common = Path(command(source, "rev-parse", "--git-common-dir", capture=True))
    if not common.is_absolute():
        common = source / common
    cache = common.resolve() / "github-lfs-objects"
    cache.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="svn-github-lfs-") as directory:
        mirror = Path(directory) / "mirror"
        command(source, "clone", "--shared", "--no-checkout", "--single-branch", "--branch", "master",
                "--", str(source), str(mirror))
        command(mirror, "config", "lfs.storage", str(cache))
        command(mirror, "config", "lfs.dialtimeout", "15")
        command(mirror, "config", "lfs.activitytimeout", "60")
        command(mirror, "remote", "add", "github", url)
        command(mirror, "checkout", "master")
        command(mirror, "lfs", "install", "--local")
        command(mirror, "lfs", "migrate", "import", f"--above={limit}b",
                "--include-ref=refs/heads/master", "--skip-fetch")
        projected = command(mirror, "rev-parse", "HEAD", capture=True)
        oversized = oversized_blobs(mirror, "master", limit)
        if oversized:
            raise MirrorError(f"Migration left oversized Git blobs: {oversized}")
        # Validate fast-forward ancestry BEFORE transferring large LFS payloads.
        refs = command(mirror, "ls-remote", "github", "refs/heads/master", capture=True)
        if refs:
            expected = refs.split()[0]
            command(mirror, "fetch", "--no-tags", "github", "refs/heads/master")
            fetched = command(mirror, "rev-parse", "FETCH_HEAD", capture=True)
            if fetched != expected:
                raise MirrorError("GitHub master changed during preparation; retry publication")
            ancestor = subprocess.run(["git", "merge-base", "--is-ancestor", expected, projected], cwd=mirror)
            if ancestor.returncode:
                raise MirrorError("GitHub history is not an ancestor of the LFS projection; "
                                  "no force-push was attempted. Inspect both histories before retrying.")
        print(f"\nSVN source: {head}\nGitHub LFS projection: {projected}", flush=True)
        command(mirror, "lfs", "push", "--all", "github", "master")
        # No --force. A concurrent update is rejected by ordinary push semantics.
        command(mirror, "push", "github", "master:refs/heads/master")
        actual = command(mirror, "ls-remote", "github", "refs/heads/master", capture=True).split()
        if not actual or actual[0] != projected:
            raise MirrorError("GitHub branch verification failed after push")
        if command(source, "rev-parse", "refs/heads/master", capture=True) != head:
            raise MirrorError("Source master changed during publication; the captured SVN revision was published")
    return MirrorResult(head, projected)
