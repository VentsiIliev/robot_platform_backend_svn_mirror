"""Paint-owned selection of settings and workpiece evidence, for every outcome."""
import logging

from src.engine.diagnostics.evidence import publish_snapshot
from src.engine.diagnostics.events import is_recording, observe

_logger = logging.getLogger(__name__)


def publish_cycle_settings(context) -> dict:
    if not is_recording():
        return {}
    references = {}
    for name, config in (('raw_process_settings', context.raw_process_config),
                         ('effective_process_settings', context.process_config)):
        references[name] = publish_snapshot('paint.' + name, config, expand_dataclasses=True,
                                            unavailable_reason='configuration_not_captured')
    return references


def publish_workpiece(context) -> None:
    if not is_recording():
        return
    try:
        raw = context.raw_workpiece if isinstance(context.raw_workpiece, dict) else getattr(context.execution_plan, 'workpiece', {})
        raw = raw if isinstance(raw, dict) else {}
        metadata = {key: raw[key] for key in ('workpieceId', 'id', 'name', 'storage_id', 'settings',
                     'velocity', 'acceleration', 'offset', 'height_mm') if key in raw}
        # Large geometry remains separately managed evidence; never expand it here.
        metadata.update(description=context.workpiece_description,
                        dry_run_placement=context.dry_run_metadata,
                        geometry_capture='not_included', image_capture='not_included')
        context.diagnostic_evidence['workpiece'] = publish_snapshot('paint.workpiece', metadata if raw else None,
            unavailable_reason='no_prepared_workpiece')
        observe(_logger, 'paint.workpiece.prepared' if raw else 'paint.workpiece.unavailable',
                workpiece_id=raw.get('workpieceId') or raw.get('id'), name=raw.get('name'),
                description=context.workpiece_description,
                evidence=context.diagnostic_evidence['workpiece'])
    except Exception:
        # Optional evidence cannot mask preparation or prevent cycle cleanup.
        pass


def publish_execution_plan(context) -> None:
    if not is_recording():
        return
    try:
        if 'workpiece' not in context.diagnostic_evidence:
            publish_workpiece(context)
        plan = context.execution_plan
        jobs = plan.execution_jobs
        metadata = []
        for job in jobs[:64]:
            metadata.append({key: value for key, value in list(job.items())[:64]
                if type(value) in (str, int, float, bool, type(None)) or key in ('settings', 'pickup_xy')})
        context.diagnostic_evidence['execution_plan'] = publish_snapshot('paint.execution_plan', {
            'job_count': len(jobs), 'job_metadata': metadata, 'jobs_omitted': max(0, len(jobs) - 64),
            'planned_waypoints': plan.total_spline_pts, 'geometry_capture': 'not_included',
        })
    except Exception:
        pass
