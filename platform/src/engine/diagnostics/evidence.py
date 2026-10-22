"""Bounded immutable inline evidence; publication is not a durable receipt.

Small, explicitly selected primitive snapshots are encoded into ordinary events.
Readers must verify every part and its digest. Rotation, overflow or a crash may
leave only a manifest or a subset; that is incomplete evidence, never success.
"""
from hashlib import sha256
import json
import logging
from uuid import uuid4

from .events import is_recording, observe
from .validation import PrimitiveSnapshot, identifier

MAX_BYTES = 65536
PART_SIZE = 2048
_logger = logging.getLogger(__name__)


def publish_snapshot(name: str, data, *, unavailable_reason='not_available', expand_dataclasses=False) -> dict:
    """Snapshot now, attempt nonblocking submission, and return a read-only reference.

    Producers own domain selection and redaction. Objects/arrays/geometry are not
    implicitly expanded. No registry, artifact workers or retained object leases.
    """
    if not is_recording():
        return {'name': name, 'availability': 'unavailable', 'schema_version': 1,
                'reason': 'recorder_inactive'}
    reference = {'snapshot_id': uuid4().hex, 'name': name, 'availability': 'unavailable', 'schema_version': 1}
    try:
        identifier(name)
        if data is None:
            observe(_logger, 'evidence.snapshot', **reference, reason=unavailable_reason, parts=0)
            return reference
        snapshot = PrimitiveSnapshot(max_nodes=4096, max_items=128, max_depth=10, max_characters=32768,
                                     expand_dataclasses=expand_dataclasses)
        value = snapshot.copy(data)
        encoded = json.dumps(value, sort_keys=True, ensure_ascii=True, allow_nan=False, separators=(',', ':'))
        if len(encoded) > MAX_BYTES:
            raise ValueError('snapshot_size_limit')
        parts = max(1, (len(encoded) + PART_SIZE - 1) // PART_SIZE)
        reference.update(availability='submitted', sha256=sha256(encoded.encode('ascii')).hexdigest(),
                         parts=parts, snapshot_omitted_fields=snapshot.omitted)
        observe(_logger, 'evidence.snapshot', **reference,
                publication='submitted_without_admission_or_commit_acknowledgement', bytes=len(encoded))
        for index in range(parts):
            observe(_logger, 'evidence.snapshot.part', snapshot_id=reference['snapshot_id'],
                    level=logging.DEBUG, index=index, data=encoded[index * PART_SIZE:(index + 1) * PART_SIZE])
    except Exception:
        reference['availability'] = 'unavailable'
        try:
            observe(_logger, 'evidence.snapshot', **reference, reason='snapshot_capture_failed', parts_expected=None)
        except Exception:
            pass
    return reference
