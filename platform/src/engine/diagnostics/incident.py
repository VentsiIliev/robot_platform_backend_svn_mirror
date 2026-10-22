"""Reviewable incident exports from retained events, without domain imports."""
from datetime import datetime, timezone
from hashlib import sha256
import json
import os
from pathlib import Path
import re
import tempfile
from zipfile import ZipFile, ZIP_DEFLATED

from .evidence import MAX_BYTES, PART_SIZE
from .timeline import decode, render


def reconstruct_evidence(events, *, warnings=None):
    references, fragments, conflicts = {}, {}, set()
    limited = False
    def visit(value, depth=0):
        nonlocal limited
        if depth > 8:
            limited = True
            return
        if isinstance(value, dict):
            sid = value.get('snapshot_id')
            if isinstance(sid, str) and re.fullmatch(r'[A-Za-z0-9_-]{1,128}', sid):
                if 'availability' in value and (sid in references or len(references) < 128):
                    previous = references.get(sid)
                    if previous and any(previous.get(key) != value.get(key) for key in
                                        ('sha256', 'parts', 'availability')):
                        conflicts.add(sid)
                    references[sid] = dict(value)
                elif 'availability' in value:
                    limited = True
            if len(value) > 64:
                limited = True
            for item in list(value.values())[:64]:
                visit(item, depth + 1)
        elif isinstance(value, list):
            if len(value) > 128:
                limited = True
            for item in value[:128]:
                visit(item, depth + 1)
    for event in events:
        fields = event.get('fields', {})
        visit(fields)
        if event.get('event') == 'evidence.snapshot.part' and isinstance(fields, dict):
            sid, index, data = (fields.get(key) for key in ('snapshot_id', 'index', 'data'))
            if (isinstance(sid, str) and re.fullmatch(r'[A-Za-z0-9_-]{1,128}', sid)
                    and type(index) is int and 0 <= index < MAX_BYTES // PART_SIZE
                    and type(data) is str and len(data) <= PART_SIZE):
                if sid not in fragments and len(fragments) >= 128:
                    limited = True
                    continue
                parts = fragments.setdefault(sid, {})
                if index in parts and parts[index] != data:
                    conflicts.add(sid)
                parts[index] = data
    if limited and warnings is not None:
        warnings.append('Evidence reconstruction limit reached; references may be missing')
    result = []
    for sid in sorted(set(references) | set(fragments)):
        reference = references.get(sid, {})
        count, parts = reference.get('parts'), fragments.get(sid, {})
        item = {'snapshot_id': sid, 'name': reference.get('name'),
                'status': 'incomplete', 'parts_available': len(parts), 'parts_expected': count,
                'snapshot_omitted_fields': reference.get('snapshot_omitted_fields', 0)}
        if reference.get('schema_version', 1) != 1:
            item['reason'] = 'unsupported_snapshot_schema'
        elif reference.get('availability') == 'unavailable':
            item.update(status='unavailable', reason=reference.get('reason', 'capture_unavailable'))
        elif sid in conflicts:
            item['reason'] = 'conflicting_metadata_or_parts'
        elif type(count) is int and 0 < count <= MAX_BYTES // PART_SIZE and set(parts) == set(range(count)):
            encoded = ''.join(parts[index] for index in range(count))
            try:
                if sha256(encoded.encode('ascii')).hexdigest() != reference.get('sha256'):
                    raise ValueError('digest_mismatch')
                payload = json.loads(encoded, parse_constant=_reject_constant)
                item.update(status='partial' if item['snapshot_omitted_fields'] else 'complete',
                            payload=payload, sha256=reference['sha256'])
            except (ValueError, UnicodeError, RecursionError):
                item['reason'] = 'invalid_payload_or_digest'
        else:
            item['reason'] = 'missing_manifest_or_parts'
        result.append(item)
    return result


def _reject_constant(value):
    raise ValueError('Non-finite JSON evidence')


def export_incident(selection: dict, destination: str | Path, *, filters: dict) -> Path:
    """Publish an exclusive ZIP of the actual selection; disclose scan/capture gaps.

    This is a best-effort retained-file read, not an atomic database timeline or
    recorder commit receipt. External artifact paths are never followed/copied.
    """
    destination = Path(destination)
    if destination.exists():
        raise FileExistsError(destination)
    events = selection['events']
    if not isinstance(events, list) or len(events) > 500:
        raise ValueError('Incident selection exceeds 500 events; narrow the filters')
    warnings = list(selection.get('warnings', []))
    evidence = reconstruct_evidence(events, warnings=warnings)
    expected = set()
    for event in events:
        fields = event.get('fields')
        if isinstance(fields, dict) and isinstance(fields.get('expected_evidence'), list):
            expected.update(name for name in fields['expected_evidence'][:64] if isinstance(name, str))
    records, timeline, total = [], [], 0
    for event in events:
        record = {key: value for key, value in event.items() if not key.startswith('_')}
        line = json.dumps(record, ensure_ascii=False, allow_nan=False) + '\n'
        total += len(line.encode('utf-8'))
        if total > 64 * 1024 * 1024:
            raise ValueError('Incident event size limit reached')
        records.append(line)
        parsed = decode(line)
        if parsed is not None and event.get('event') != 'evidence.snapshot.part':
            timeline.append(render(parsed, details=True, utc=True))
    if selection.get('matched', len(events)) > len(events):
        warnings.append('Only the newest 500 matching retained events are included')
    if not events:
        warnings.append('Empty selection does not establish correct machine behavior')
    manifest = {
        'schema_version': 1, 'created_utc': datetime.now(timezone.utc).isoformat(),
        'filters': filters, 'event_count': len(events), 'matched_during_scan': selection.get('matched'),
        'scan_limited': selection.get('limited', False), 'warnings': warnings,
        'history_snapshot': 'best_effort_retained_files',
        'capture_coverage': 'selective; absent records do not prove absence of an issue',
        'loss_accounting': 'selection_only; recorder losses outside selected records are unknown',
        'recorder_commit_acknowledgement': 'not_available',
        'external_artifacts': 'not_copied; image/geometry/backend-log completeness is not established',
        'machine_ids': sorted({str(event.get('machine_id') or '') for event in events}),
        'operation_ids': sorted({str((event.get('context') or {}).get('operation_id')) for event in events
                                 if isinstance(event.get('context'), dict) and event['context'].get('operation_id')}),
        'time_coverage': {'first': events[0].get('timestamp') if events else None,
                          'last': events[-1].get('timestamp') if events else None},
        'events_with_omitted_detail': sum(bool(event.get('omitted_fields')) for event in events),
        'expected_evidence_not_captured': sorted(expected - {item['name'] for item in evidence}),
        'evidence': [{key: value for key, value in item.items() if key != 'payload'} for item in evidence],
    }
    destination.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(dir=destination.parent, suffix='.zip', delete=False) as handle:
        staged = Path(handle.name)
    try:
        with ZipFile(staged, 'w', compression=ZIP_DEFLATED) as archive:
            archive.writestr('events.jsonl', ''.join(records))
            archive.writestr('timeline.txt', '\n\n'.join(timeline))
            archive.writestr('manifest.json', json.dumps(manifest, indent=2, ensure_ascii=False))
            for item in evidence:
                if 'payload' in item:
                    archive.writestr(f"evidence/{item['snapshot_id']}.json",
                                     json.dumps(item['payload'], indent=2, ensure_ascii=False))
        os.link(staged, destination)
    finally:
        staged.unlink(missing_ok=True)
    return destination
