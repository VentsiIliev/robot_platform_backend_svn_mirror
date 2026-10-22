"""Durable state files and cooperative process locks for Linux installations."""
from contextlib import contextmanager
import fcntl
import os
from pathlib import Path


# Keep updater imports stable while sharing the single durability implementation.
from src.engine.core.durable_files import atomic_write_json as atomic_json, sync_directory


@contextmanager
def lock(path: Path, *, shared: bool = False):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a+") as stream:
        try:
            fcntl.flock(stream, (fcntl.LOCK_SH if shared else fcntl.LOCK_EX) | fcntl.LOCK_NB)
        except BlockingIOError as exc:
            raise RuntimeError("Platform is running or another update is in progress") from exc
        yield


def sync_tree(root: Path) -> None:
    """Persist file contents and directory entries before publishing a tree."""
    for directory, _, files in os.walk(root, topdown=False):
        directory = Path(directory)
        for name in files:
            with (directory / name).open("rb") as stream:
                os.fsync(stream.fileno())
        sync_directory(directory)
