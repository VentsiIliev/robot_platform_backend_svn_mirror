"""Local retained-history reader. Never initializes logging, hardware or bootstrap."""
from datetime import datetime, timedelta, timezone
import heapq
import json
import os
from pathlib import Path
import re
import time

from src.engine.diagnostics.runtime import default_directory
from src.engine.diagnostics.timeline import decode, instant, LEVELS, MAX_LINE
from src.engine.diagnostics.incident import export_incident
from .i_diagnostics_service import IDiagnosticsService


class DiagnosticsApplicationService(IDiagnosticsService):
    MAX_FILES = 32
    MAX_BYTES = 64 * 1024 * 1024
    MAX_SECONDS = 2.0
    MAX_EVENTS = 500

    def initial_directory(self) -> str:
        return str(default_directory())

    def query(self, filters: dict) -> dict:
        directory = Path(filters['directory']).expanduser()
        seconds = filters.get('window_seconds')
        since = instant(filters['since']) if filters.get('since') else (
            datetime.now(timezone.utc) - timedelta(seconds=seconds) if seconds else None)
        until = instant(filters['until']) if filters.get('until') else None
        if since and until and since > until:
            raise ValueError('Start time must precede end time')
        minimum = LEVELS.get(filters.get('level'), 10)
        search = filters.get('search', '').casefold().strip()
        warnings, paths, selected = set(), [], []
        deadline, consumed, serial, matched = time.monotonic() + self.MAX_SECONDS, 0, 0, 0
        limited = False
        try:
            with os.scandir(directory) as entries:
                for index, entry in enumerate(entries):
                    if index >= 128:
                        warnings.add('Directory inventory limit reached')
                        limited = True
                        break
                    if re.fullmatch(r'events\.jsonl(?:\.[0-9]+)?|failure_register\.jsonl', entry.name):
                        if entry.is_file(follow_symlinks=False):
                            paths.append(Path(entry.path))
                        else:
                            warnings.add(f'Non-regular file skipped: {entry.name}')
            paths.sort(key=lambda path: int(path.suffix[1:]) if path.suffix[1:].isdigit() else -1)
            if len(paths) > self.MAX_FILES:
                warnings.add('File count limit reached')
                limited = True
            for path in paths[:self.MAX_FILES]:
                oversized = False
                try:
                    with path.open('rb') as stream:
                        while True:
                            if consumed >= self.MAX_BYTES or time.monotonic() >= deadline:
                                warnings.add('Scan budget reached; narrow the time range or inspect fewer files')
                                limited = True
                                break
                            line = stream.readline(min(MAX_LINE + 1, self.MAX_BYTES - consumed))
                            consumed += len(line)
                            if not line:
                                break
                            if oversized or len(line) > MAX_LINE:
                                oversized = not line.endswith(b'\n')
                                warnings.add(f'Oversized record skipped: {path.name}')
                                continue
                            if not line.endswith(b'\n'):
                                warnings.add(f'Incomplete final record skipped: {path.name}')
                                continue
                            record = decode(line)
                            if record is None:
                                warnings.add(f'Invalid record skipped: {path.name}')
                                continue
                            if (not filters.get('include_evidence_parts')
                                    and record.get('event') == 'evidence.snapshot.part'):
                                continue
                            stamp = record['_time']
                            operation = filters.get('operation_id')
                            if operation and (not isinstance(record.get('context'), dict)
                                    or record['context'].get('operation_id') != operation):
                                continue
                            if since and stamp < since or until and stamp > until:
                                continue
                            if LEVELS.get(str(record.get('level')), 20) < minimum:
                                continue
                            if search and search not in json.dumps({key: value for key, value in record.items()
                                    if key != '_time'}, ensure_ascii=False).casefold():
                                continue
                            serial += 1
                            matched += 1
                            item = (stamp, serial, record)
                            if len(selected) < self.MAX_EVENTS:
                                heapq.heappush(selected, item)
                            elif item[:2] > selected[0][:2]:
                                heapq.heapreplace(selected, item)
                except OSError as error:
                    warnings.add(f'Cannot read {path.name}: {error}')
                if consumed >= self.MAX_BYTES or time.monotonic() >= deadline:
                    break
        except OSError as error:
            warnings.add(str(error))
        if not paths:
            warnings.add('No retained event files found in this directory')
        events = []
        for stamp, _, record in sorted(selected):
            record.pop('_time', None)
            record['_display_time'] = stamp.astimezone().isoformat(timespec='milliseconds')
            record['_summary'] = self._summary(record)
            events.append(record)
        return {'events': events, 'warnings': sorted(warnings), 'matched': matched,
                'limited': limited, 'directory': str(directory), 'bytes_read': consumed}

    def export_incident(self, filters: dict, destination: str) -> dict:
        filters = dict(filters)
        selected_operation = filters.pop('selected_operation_id', None)
        filters['include_evidence_parts'] = True
        if selected_operation:
            filters.update(operation_id=selected_operation, window_seconds=None,
                           since=None, until=None, search='', level='DEBUG')
        selection = self.query(filters)
        path = export_incident(selection, destination, filters=filters)
        return {'path': str(path), 'event_count': len(selection['events']),
                'operation_id': selected_operation, 'scan_limited': selection['limited'],
                'selection_truncated': selection['matched'] > len(selection['events'])}

    @staticmethod
    def _summary(record):
        fields = record.get('fields')
        fields = fields if isinstance(fields, dict) else {}
        parts = [str(fields[key]) for key in ('application', 'tab', 'field') if key in fields]
        if 'before' in fields or 'after' in fields:
            parts.append(f"{fields.get('before')} → {fields.get('after')}")
        if fields.get('pending_application') or fields.get('application') == 'pending':
            parts.append('pending application')
        selected = {'application', 'tab', 'field', 'before', 'after', 'outcome'}
        for key, value in fields.items():
            if key not in selected and type(value) in (str, int, float, bool) and len(parts) < 6:
                parts.append(f'{key}={str(value)[:256]}')
        if record.get('omitted_fields'):
            parts.append(f"omitted_fields={record['omitted_fields']}")
        message = record.get('message')
        if message and message != record.get('event'):
            parts.append(str(message))
        return ' · '.join(parts)[:2048]
