"""Read lifetime summaries and export a consistent support archive.

Usage: python -m src.engine.diagnostics.report [--directory DIR] [--export FILE.zip]
"""
from __future__ import annotations

import argparse
import json
import sqlite3
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED

from .runtime import default_directory


def read_summary(directory: str | Path) -> dict:
    """Read committed counters; active measurements lag by one checkpoint."""
    source = Path(directory) / 'statistics.sqlite3'
    db = sqlite3.connect(source.resolve().as_uri() + '?mode=ro', uri=True, timeout=2)
    try:
        with db:
            db.execute('BEGIN')
            metrics = {name: {'samples': samples, 'total': total, 'maximum': maximum}
                       for name, samples, total, maximum in db.execute(
                           'SELECT name,samples,total,maximum FROM metrics ORDER BY name')}
            sessions = [{'id': sid, 'started': started, 'ended': ended, 'interrupted': bool(interrupted)}
                        for sid, started, ended, interrupted in db.execute(
                            'SELECT id,started,ended,interrupted FROM sessions ORDER BY started DESC LIMIT 10')]
        metadata = dict(db.execute('SELECT name,value FROM metadata'))
        return {'schema_version': 1, 'metadata': metadata, 'metrics': metrics, 'recent_sessions': sessions}
    finally:
        db.close()


def export_support_bundle(directory: str | Path, destination: str | Path) -> Path:
    """Snapshot SQLite and bounded log files without touching machine settings.

    Live logs are best-effort: rotation during export can leave a file absent.
    The manifest lists captured files and records that limitation explicitly.
    """
    directory, destination = Path(directory), Path(destination)
    destination.parent.mkdir(parents=True, exist_ok=True)
    if destination.exists():
        raise FileExistsError(destination)
    source = sqlite3.connect((directory / 'statistics.sqlite3').resolve().as_uri() + '?mode=ro', uri=True, timeout=2)
    try:
        with tempfile.TemporaryDirectory() as temp:
            snapshot = Path(temp) / 'statistics.sqlite3'
            target = sqlite3.connect(snapshot)
            try:
                source.backup(target)
            finally:
                target.close()
            summary = read_summary(temp)
            captured = []
            # Build in the destination directory, then publish only a complete ZIP.
            with tempfile.NamedTemporaryFile(dir=destination.parent, suffix='.zip', delete=False) as temporary:
                staged = Path(temporary.name)
            try:
                with ZipFile(staged, 'w', compression=ZIP_DEFLATED) as archive:
                    archive.write(snapshot, 'statistics.sqlite3')
                    archive.writestr('summary.json', json.dumps(summary, indent=2))
                    for path in sorted(directory.glob('events.jsonl*')):
                        if path.is_file() and not path.is_symlink():
                            try:
                                # Cap live reads at the size observed before export.
                                with path.open('rb') as handle:
                                    data = handle.read(path.stat().st_size)
                                archive.writestr('logs/' + path.name, data)
                                captured.append(path.name)
                            except FileNotFoundError:
                                continue
                    archive.writestr('manifest.json', json.dumps({
                        'created_utc': datetime.now(timezone.utc).isoformat(),
                        'schema_version': 1, 'log_files': captured,
                        'logs_snapshot': 'best_effort_live_files',
                        'statistics_snapshot': 'consistent_sqlite_backup',
                    }, indent=2))
                # Exclusive creation prevents replacing an existing support file.
                import os
                os.link(staged, destination)
            finally:
                staged.unlink(missing_ok=True)
    finally:
        source.close()
    return destination


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--directory', type=Path, default=default_directory())
    parser.add_argument('--export', type=Path)
    args = parser.parse_args()
    try:
        if args.export:
            print(export_support_bundle(args.directory, args.export))
        else:
            print(json.dumps(read_summary(args.directory), indent=2))
    except (OSError, sqlite3.Error) as exc:
        parser.exit(1, f"Diagnostics report failed: {exc}\n")


if __name__ == '__main__':
    main()
