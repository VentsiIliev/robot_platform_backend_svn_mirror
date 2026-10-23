"""Revision-checked backend configuration client; no Qt or ROS dependencies."""
import json
import os
import re
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit
from urllib.request import Request, urlopen


def cell_fixture_identifier(scene_object_id):
    match = re.fullmatch(r'world/(cell_fixture_[A-Za-z0-9_]+)/0', scene_object_id or '')
    return match.group(1) if match else None


def default_backend_url():
    explicit = os.environ.get('ROBOT_BACKEND_NETWORK_CONFIG')
    path = Path(explicit) if explicit else Path(__file__).resolve().parents[3]/'config/backend_network.json'
    if not path.exists() and not explicit:
        return 'http://127.0.0.1:5000'
    values = json.loads(path.read_text())
    host = values['client_host']
    host = f'[{host}]' if ':' in host else host
    return f'http://{host}:{values["http_port"]}'


class BackendConfigurationClient:
    def __init__(self, url):
        parts = urlsplit(url)
        if parts.scheme not in ('http', 'https') or not parts.hostname or parts.username or parts.password or parts.query or parts.fragment:
            raise ValueError('Enter an HTTP(S) backend URL without credentials, query or fragment.')
        self.url = url.rstrip('/')

    def _request(self, method, suffix='', body=None):
        data = None if body is None else json.dumps(body, allow_nan=False).encode()
        request = Request(self.url+'/configuration/cell_scene'+suffix, data=data, method=method,
                          headers={'Content-Type':'application/json'})
        try:
            with urlopen(request, timeout=12) as response:
                result = json.load(response)
        except HTTPError as error:
            try:
                result = json.load(error)
            except (ValueError, OSError):
                raise RuntimeError(f'Backend returned HTTP {error.code}') from error
            raise RuntimeError(result.get('error') or f'Backend returned HTTP {error.code}') from error
        except URLError as error:
            raise RuntimeError(f'Cannot reach backend: {error.reason}') from error
        if not isinstance(result, dict) or not result.get('success'):
            raise RuntimeError(result.get('error', 'Backend configuration request failed') if isinstance(result,dict) else 'Invalid backend response')
        if not isinstance(result.get('revision'),str) or not isinstance(result.get('saved',{}).get('CELL_COLLISION_OBJECTS'),dict):
            raise RuntimeError('Backend returned an invalid cell scene configuration')
        return result

    def get(self):
        return self._request('GET')

    def save(self, revision, enabled):
        if not enabled or any(type(value) is not bool for value in enabled.values()):
            raise ValueError('Choose boolean enabled states before saving.')
        return self._request('PATCH', body={'expected_revision':revision, 'changes':{
            'CELL_COLLISION_OBJECTS':{key:{'enabled':value} for key,value in enabled.items()}}})

    def apply(self, revision):
        return self._request('POST', '/apply', {'expected_revision':revision})

    def set_enabled(self, identifier, enabled):
        """Read a fresh revision, then change only the explicitly selected fixture."""
        if type(enabled) is not bool:
            raise ValueError('Collision enabled state must be boolean.')
        view = self.get()
        definitions = view['saved']['CELL_COLLISION_OBJECTS']
        if identifier not in definitions or 'merged_into' in definitions[identifier]:
            raise ValueError('The selected object is not configured in this backend profile.')
        if definitions[identifier]['enabled'] == enabled:
            return self.apply(view['revision']) if view.get('pending_application') else view
        return self.save(view['revision'], {identifier:enabled})

    def merge_fixtures(self, identifiers, name):
        view = self.get()
        result = self._request('PATCH', body={'expected_revision':view['revision'],
                             'changes':{'merge':{'ids':list(identifiers), 'name':name}}})
        merged_id = result.get('merged_object_id')
        if not isinstance(merged_id, str) or merged_id not in result['saved']['CELL_COLLISION_OBJECTS']:
            raise RuntimeError('The backend did not identify the saved merged object. Reload configuration.')
        return result
