"""Configuration use cases. Persistence and runtime application are separate ports."""
from copy import deepcopy
import logging

from .domain import LIVE_MONITOR_FIELDS, ConfigurationError, Conflict, canonical_calibration, edit_tool, edit_workobject, tool_snapshot, validate_sensorless
from .documents import merge, revision
from .ports import ApplicationFailure, ConfigurationRepository, RuntimeConfiguration
from dataclasses import asdict

logger = logging.getLogger(__name__)


class ConfigurationService:
    def __init__(self, repository: ConfigurationRepository, runtime: RuntimeConfiguration, *, collision_profiles=()):
        self.repository = repository
        self.runtime = runtime
        self.collision_profiles = frozenset(collision_profiles)
        self._application_errors = {}

    def _view(self, section, saved, *, reason=None):
        try:
            applied = self.runtime.snapshot(section)
        except Exception as error:
            logger.exception('Configuration runtime state is unavailable')
            applied = None
            reason = reason or ApplicationFailure.from_exception(error, prefix='Saved configuration is available; runtime state could not be verified')
        expected = canonical_calibration(saved) if section == 'calibration' else saved
        applied_normalized = canonical_calibration(applied) if section == 'calibration' and applied is not None else applied
        reason = reason or self._application_errors.get(section)
        if isinstance(reason, str):
            reason = ApplicationFailure('configuration_application_pending', reason)
        comparison_expected = deepcopy(expected)
        comparison_applied = deepcopy(applied_normalized)
        if section == 'sensorless_collision':
            comparison_expected['monitor'].pop('collision_detection_suppressed', None)
            if comparison_applied is not None:
                comparison_applied['monitor'].pop('collision_detection_suppressed', None)
        pending = bool(reason) or comparison_applied != comparison_expected
        restart_required = None if applied is None else False
        if applied is not None and section == 'sensorless_collision':
            restart_required = any(saved[group] != applied[group] for group in ('controller', 'runtime'))
            restart_required = restart_required or any(
                value != applied['monitor'].get(key) for key, value in saved['monitor'].items()
                if key not in LIVE_MONITOR_FIELDS and key != 'collision_detection_suppressed')
        return {'success': True, 'profile': self.repository.profile, 'section': section,
                'revision': self._revision(section, saved), 'saved': deepcopy(saved), 'applied': deepcopy(applied),
                'pending_application': pending, 'application_error': reason.message if reason else None,
                'application_error_info': asdict(reason) if reason else None,
                'restart_required': restart_required,
                **({'tools': tool_snapshot(saved)} if section == 'calibration' else {})}

    def _revision(self, section, document):
        return revision({'profile': self.repository.profile, 'section': section, 'values': document})

    def _apply(self, section, document):
        try:
            reason = self.runtime.apply(section, document)
        except Exception as error:
            logger.exception('Saved configuration application failed')
            reason = ApplicationFailure.from_exception(error)
        if reason:
            self._application_errors[section] = reason
        else:
            self._application_errors.pop(section, None)
        return reason

    def get(self, section):
        with self.repository.transaction(section):
            return self._view(section, self.repository.read(section))

    def _validate(self, section, candidate, previous):
        if section == 'calibration':
            candidate = canonical_calibration(candidate)
            for item in candidate['TOOL_DEFINITIONS'].values():
                profile = item.get('collision_profile', '')
                if profile and profile not in self.collision_profiles:
                    raise ConfigurationError(f'Unknown tool collision profile: {profile}')
            return candidate
        if section == 'sensorless_collision':
            validate_sensorless(candidate, previous)
            return candidate
        raise ConfigurationError('Unknown configuration section')

    def update(self, section, changes, expected_revision, *, tool_id=None, user_id=None):
        if not isinstance(expected_revision, str) or not expected_revision:
            raise ConfigurationError('expected_revision is required; read the configuration before editing')
        if not isinstance(changes, dict) or not changes:
            raise ConfigurationError('A non-empty changes object is required')
        with self.repository.transaction(section):
            previous = self.repository.read(section)
            if self._revision(section, previous) != expected_revision:
                raise Conflict('Configuration changed; reload it before saving')
            if tool_id is not None:
                candidate = edit_tool(previous, tool_id, changes)
            elif user_id is not None:
                candidate = edit_workobject(previous, user_id, changes)
            else:
                if section == 'calibration':
                    allowed = {'TOOL_DEFINITIONS', 'TOOL_ID_MAP', 'REFERENCE_TOOL_ID',
                               'WORKOBJECT_REGISTRY', 'WORKOBJECT_ID_MAP', 'DEFAULT_WORKOBJECT_ID'}
                    if set(changes) - allowed:
                        raise ConfigurationError('Unsupported calibration fields')
                    candidate = merge(canonical_calibration(previous), changes)
                    if 'TOOL_DEFINITIONS' in changes:
                        definitions = changes['TOOL_DEFINITIONS']
                        if not isinstance(definitions, dict):
                            raise ConfigurationError('Tool definitions must be a mapping')
                        candidate['TOOL_DEFINITIONS'].update(deepcopy(definitions))
                else:
                    candidate = merge(previous, changes)
            candidate = self._validate(section, candidate, previous)
            # Never alter runtime state until the entire candidate is durable.
            self.repository.write(section, candidate, revision(previous))
            reason = self._apply(section, candidate)
            return self._view(section, candidate, reason=reason)

    def retry_application(self, section, expected_revision):
        with self.repository.transaction(section):
            saved = self.repository.read(section)
            if self._revision(section, saved) != expected_revision:
                raise Conflict('Configuration changed; reload it before applying')
            reason = self._apply(section, saved)
            return self._view(section, saved, reason=reason)
