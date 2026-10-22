"""Read-only human timeline over retained JSONL and optional failure indexes."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import sys
import time

from .runtime import default_directory

MAX_LINE = 262144
LEVELS = {'DEBUG': 10, 'INFO': 20, 'WARNING': 30, 'ERROR': 40, 'CRITICAL': 50}


def instant(value):
    """Explicit offsets or machine-local timestamps; normalize comparisons to UTC."""
    if not isinstance(value, str):
        raise ValueError('Expected an ISO timestamp string')
    parsed = datetime.fromisoformat(value.replace('Z', '+00:00'))
    return parsed.astimezone(timezone.utc)


def clean(value):
    # Evidence is untrusted terminal input: remove control/escape sequences.
    return ''.join(c if c.isprintable() else ' ' for c in str(value))


def decode(line):
    try:
        def invalid_constant(value):
            raise ValueError(f'Non-finite JSON value: {value}')
        record = json.loads(line, parse_constant=invalid_constant)
        if not isinstance(record, dict):
            return None
        record['_time'] = instant(record.get('timestamp') or record['recorded_at_utc'])
        if 'recorded_at_utc' in record and 'level' not in record:
            record['level'] = 'ERROR'
            record['event'] = 'operation.failed'
        return record
    except (ValueError, KeyError, TypeError, OverflowError, RecursionError):
        return None


def records(path, warnings):
    try:
        with path.open('rb') as stream:
            while line := stream.readline(MAX_LINE + 1):
                if len(line) > MAX_LINE:
                    while line and not line.endswith(b'\n'):
                        line = stream.readline(MAX_LINE + 1)
                    warnings.add(f'Oversized records skipped: {path}')
                    continue
                record = decode(line)
                if record is None:
                    warnings.add(f'Invalid/incomplete records skipped: {path}')
                else:
                    yield record
    except OSError as error:
        warnings.add(f'Cannot read {path}: {error}')


def matches(record, args):
    if args.since and record['_time'] < args.since:
        return False
    if args.until and record['_time'] > args.until:
        return False
    if LEVELS.get(record.get('level'), 20) < LEVELS[args.level]:
        return False
    context = record.get('context') or {}
    if not isinstance(context, dict):
        context = {}
    for key in ('cycle_id', 'run_id'):
        requested = getattr(args, key)
        if requested and requested != (record.get(key) or context.get(key)):
            return False
    return not args.source or args.source.lower() in str(record.get('logger', '')).lower()


def render(record, *, details=False, utc=False):
    stamp = record['_time'] if utc else record['_time'].astimezone()
    level = clean(record.get('level', 'INFO'))
    message = clean(record.get('message') or record.get('event') or '(no message)')
    source = clean(record.get('logger', 'failure index'))
    source = source.rsplit('.', 1)[-1]
    lines = [f'{stamp:%Y-%m-%d %H:%M:%S.%f}'[:-3] + f' {level:<8} {source}: {message}']
    context = record.get('context') or {}
    if not isinstance(context, dict):
        context = {}
    ids = {key: record.get(key) or context.get(key) for key in ('cycle_id', 'run_id', 'operation_id', 'action_id')}
    fields = record.get('fields') or {}
    summary = {**{k: v for k, v in ids.items() if v}, **({'output': record['output']} if record.get('output') else {})}
    if context.get('actor'):
        summary['actor'] = context['actor']
    if fields:
        summary['fields'] = fields
    if record.get('metrics'):
        summary['metrics'] = record['metrics']
    if summary:
        text = clean(json.dumps(summary, ensure_ascii=False))
        lines.append('    ' + (text if details else text[:260] + (' … (--details)' if len(text) > 260 else '')))
    if type(record.get('failure_bundle')) is str:
        bundle = Path(record['failure_bundle'])
        lines.append('    Evidence: ' + clean(bundle) + (' [present]' if bundle.is_file() else ' [missing]'))
        image = bundle.parent / 'capture.png'
        lines.append('    Image: ' + clean(image) + (' [present]' if image.is_file() else ' [missing/not captured]'))
        if details:
            try:
                with bundle.open('rb') as stream:
                    data = stream.read(MAX_LINE + 1)
                if len(data) > MAX_LINE:
                    lines.append('    Bundle summary omitted: exceeds preview size limit.')
                else:
                    content = json.loads(data)
                    if isinstance(content, dict):
                        sections = [key for key, value in content.items() if value is not None]
                        lines.append('    Bundle sections: ' + clean(', '.join(sections)))
            except (OSError, ValueError, TypeError):
                lines.append('    Bundle summary unavailable: unreadable or invalid JSON.')
    if record.get('omitted_fields'):
        lines.append(f'    Capture omitted {record["omitted_fields"]} field(s); original detail is unavailable.')
    if details and record.get('traceback'):
        lines.extend('    ' + clean(line) for line in str(record['traceback']).splitlines())
    return '\n'.join(lines)


class Follower:
    """Track open inode through rename rotation; retain incomplete append lines."""
    def __init__(self, path):
        self.path = path
        self.stream = None
        self.pending = b''
        self.oversized = False

    def open(self, *, end=False):
        try:
            self.stream = self.path.open('rb')
            if end:
                self.stream.seek(0, 2)
        except FileNotFoundError:
            self.stream = None

    def poll(self):
        if self.stream is None:
            self.open()
        if self.stream is None:
            return []
        output = []
        for _ in range(1000):
            chunk = self.stream.readline(MAX_LINE + 1)
            if not chunk:
                break
            if len(self.pending) + len(chunk) > MAX_LINE:
                self.oversized = True
                self.pending = b''
            elif not self.oversized:
                self.pending += chunk
            if chunk.endswith(b'\n'):
                if self.oversized:
                    print('Timeline: oversized live record skipped', file=sys.stderr)
                elif (record := decode(self.pending)) is not None:
                    output.append(record)
                else:
                    print('Timeline: invalid live record skipped', file=sys.stderr)
                self.pending = b''
                self.oversized = False
        # Drain renamed file before switching to its replacement.
        try:
            current = self.path.stat()
            opened = self.stream.fileno()
            import os
            previous = os.fstat(opened)
            if (current.st_dev, current.st_ino) != (previous.st_dev, previous.st_ino):
                if self.stream.tell() >= previous.st_size:
                    if self.pending:
                        print('Timeline: incomplete record at rotation', file=sys.stderr)
                    self.close()
                    self.open()
            elif current.st_size < self.stream.tell():
                self.stream.seek(0)
                self.pending = b''
                print('Timeline: log truncated; continuity may be incomplete', file=sys.stderr)
        except FileNotFoundError:
            pass
        return output

    def close(self):
        if self.stream is not None:
            self.stream.close()
        self.stream = None
        self.pending = b''
        self.oversized = False


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--directory', type=Path, default=default_directory())
    parser.add_argument('--evidence-directory', type=Path, action='append', default=[],
                        help='Additional directory containing failure_register.jsonl (repeatable)')
    parser.add_argument('--since', type=instant, help='ISO timestamp; without offset uses local timezone')
    parser.add_argument('--until', type=instant)
    parser.add_argument('--cycle-id')
    parser.add_argument('--run-id')
    parser.add_argument('--source')
    parser.add_argument('--level', choices=LEVELS, default='INFO')
    parser.add_argument('--last', type=int, default=50)
    parser.add_argument('--details', action='store_true')
    parser.add_argument('--utc', action='store_true')
    parser.add_argument('--follow', '-f', action='store_true')
    args = parser.parse_args(argv)
    if not 1 <= args.last <= 10000:
        parser.error('--last must be between 1 and 10000')
    if args.since and args.until and args.since > args.until:
        parser.error('--since must be before --until')
    warnings = set()
    evidence = [p / 'failure_register.jsonl' for p in args.evidence_directory]
    followers = [Follower(p) for p in [args.directory / 'events.jsonl', *evidence]]
    # Open before history scan, so appends during the scan remain available.
    if args.follow:
        for follower in followers:
            follower.open(end=True)
    try:
        paths = sorted(args.directory.glob('events.jsonl.[0-9]*'),
                       key=lambda p: int(p.suffix[1:]) if p.suffix[1:].isdigit() else 0,
                       reverse=True) + [args.directory / 'events.jsonl', *evidence]
        # Bounded selection by timestamp even when multiple source files interleave.
        import heapq
        selected = heapq.nlargest(args.last, (r for p in paths for r in records(p, warnings) if matches(r, args)),
                                 key=lambda r: r['_time'])
        print('Timeline — ' + ('UTC' if args.utc else 'local time') + f' — {args.directory}', flush=True)
        print('Retained evidence only; missing records do not prove correct machine behavior.', flush=True)
        if args.cycle_id or args.run_id:
            print('ID filters exclude uncorrelated records; use a time range to include them.', flush=True)
        for record in reversed(selected):
            print(render(record, details=args.details, utc=args.utc), flush=True)
        for warning in sorted(warnings):
            print('Timeline: ' + warning, file=sys.stderr)
        if not selected:
            print('No matching retained records.', flush=True)
        if args.follow:
            print('Following new records (Ctrl+C to stop). Live/history overlap is best effort.', flush=True)
            while True:
                live = [r for follower in followers for r in follower.poll() if matches(r, args)]
                for record in sorted(live, key=lambda r: r['_time']):
                    print(render(record, details=args.details, utc=args.utc), flush=True)
                time.sleep(0.2)
    except KeyboardInterrupt:
        pass
    except BrokenPipeError:
        pass
    finally:
        for follower in followers:
            follower.close()


if __name__ == '__main__':
    main()
