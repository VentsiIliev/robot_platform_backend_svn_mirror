"""Atomic, revision-checked YAML storage for one explicitly selected backend profile."""
from contextlib import contextmanager
import fcntl
import os
from pathlib import Path
import tempfile
from threading import RLock

import yaml

from .domain import ConfigurationError, Conflict, Unavailable
from .documents import differences, merge, revision


class YamlProfileRepository:
    def __init__(self, profile, paths, *, root):
        self.profile = str(profile)
        self.root = Path(root).resolve()
        self.paths = {key: Path(value).resolve() for key, value in paths.items()}
        if not self.profile or any(not path.is_relative_to(self.root) for path in self.paths.values()):
            raise ConfigurationError('Configuration paths must belong to the selected profile')
        self._lock = RLock()

    @property
    def sections(self):
        return tuple(self.paths)

    def _path(self, section):
        if section not in self.paths:
            raise ConfigurationError(f'Unknown configuration section: {section}')
        return self.paths[section]

    def _raw(self, path):
        try:
            data = yaml.safe_load(path.read_text(encoding='utf-8'))
        except (OSError, yaml.YAMLError) as exc:
            raise Unavailable(f'Cannot read configuration: {path.name}') from exc
        if not isinstance(data, dict):
            raise ConfigurationError(f'{path.name} must contain a mapping')
        return data

    def _load(self, path, stack=()):
        path = path.resolve()
        if not path.is_relative_to(self.root.parent):
            raise ConfigurationError('Configuration include escapes the configuration directory')
        if path in stack:
            raise ConfigurationError('Configuration include cycle')
        raw = self._raw(path)
        includes = raw.pop('RUNTIME_INCLUDES', [])
        if not isinstance(includes, list) or any(not isinstance(p, str) or not p for p in includes):
            raise ConfigurationError('Invalid configuration includes')
        value = {}
        for include in includes:
            value = merge(value, self._load(path.parent / include, (*stack, path)))
        return merge(value, raw)

    @contextmanager
    def transaction(self, section):
        path = self._path(section)
        with self._lock:
            try:
                descriptor = os.open(path.parent / '.configuration.lock', os.O_CREAT | os.O_RDWR, 0o600)
            except OSError as exc:
                raise Unavailable('Configuration storage is not writable') from exc
            try:
                fcntl.flock(descriptor, fcntl.LOCK_EX)
                yield
            finally:
                os.close(descriptor)

    def read(self, section):
        return self._load(self._path(section))

    def write(self, section, value, expected_revision):
        path = self._path(section)
        if revision(self.read(section)) != expected_revision:
            raise Conflict('Configuration changed; reload it before saving')
        raw = self._raw(path)
        includes = raw.get('RUNTIME_INCLUDES', [])
        inherited = {}
        for include in includes:
            inherited = merge(inherited, self._load(path.parent / include))
        # A removed inherited key cannot be expressed as an override. Reject rather than resurrect it.
        def removed_keys(base, candidate):
            for key, item in base.items():
                if key not in candidate:
                    raise ConfigurationError(f'Cannot remove inherited configuration key {key}')
                if isinstance(item, dict) and isinstance(candidate[key], dict):
                    removed_keys(item, candidate[key])
        removed_keys(inherited, value)
        output = differences(value, inherited)
        if includes:
            output = {'RUNTIME_INCLUDES': includes, **output}
        temporary = None
        try:
            descriptor, temporary = tempfile.mkstemp(prefix='.' + path.name + '.', dir=path.parent)
            with os.fdopen(descriptor, 'w', encoding='utf-8') as stream:
                yaml.safe_dump(output, stream, sort_keys=False, allow_unicode=True)
                stream.flush()
                os.fsync(stream.fileno())
            os.chmod(temporary, path.stat().st_mode & 0o777)
            os.replace(temporary, path)
            temporary = None
            directory = os.open(path.parent, os.O_RDONLY | os.O_DIRECTORY)
            try:
                os.fsync(directory)
            finally:
                os.close(directory)
        except OSError as exc:
            raise Unavailable('Configuration save failed; reload to check the saved revision') from exc
        finally:
            if temporary is not None:
                Path(temporary).unlink(missing_ok=True)
