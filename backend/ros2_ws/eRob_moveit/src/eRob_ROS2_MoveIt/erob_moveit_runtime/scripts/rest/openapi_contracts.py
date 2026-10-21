"""Generate shared OpenAPI schemas from the Python response/DTO contracts."""
from dataclasses import MISSING, fields, is_dataclass
from enum import Enum
import types
from typing import Any, Literal, NotRequired, Required, Union, get_args, get_origin, get_type_hints, is_typeddict

from runtime_api.contracts import ErrorInfo, ResponseBody
from runtime_api.configuration.requests import ConfigurationUpdateRequest
from runtime_api.configuration.responses import ConfigurationResponse, RegistryResponse
from runtime_api.motion.responses import MotionResponse
from runtime_api.state.responses import StateResponse
from runtime_api.control.requests import DigitalOutputRequest
from runtime_api.control.responses import ControlResponse


MODELS = (ErrorInfo, ResponseBody, ConfigurationResponse, RegistryResponse, MotionResponse, StateResponse,
          ControlResponse, ConfigurationUpdateRequest, DigitalOutputRequest)


def schema_for(annotation):
    origin, arguments = get_origin(annotation), get_args(annotation)
    if origin in (Required, NotRequired):
        return schema_for(arguments[0])
    if annotation is Any:
        return {}
    if origin in (Union, types.UnionType):
        non_null = [item for item in arguments if item is not type(None)]
        result = schema_for(non_null[0]) if len(non_null) == 1 else {'oneOf': [schema_for(item) for item in non_null]}
        if len(non_null) != len(arguments):
            # OpenAPI 3.0 expresses nullability separately from JSON Schema's null type.
            result = {**result, 'nullable': True}
        return result
    if origin is Literal:
        return {'type': 'string', 'enum': list(arguments)}
    if origin in (list, tuple):
        return {'type': 'array', 'items': schema_for(arguments[0]) if arguments else {}}
    if origin is dict:
        return {'type': 'object', 'additionalProperties': schema_for(arguments[1]) if arguments else {}}
    if annotation in MODELS:
        return {'$ref': '#/components/schemas/' + annotation.__name__}
    if isinstance(annotation, type) and issubclass(annotation, Enum):
        return {'type': 'string', 'enum': [member.value for member in annotation]}
    return {str: {'type': 'string'}, bool: {'type': 'boolean'}, int: {'type': 'integer'},
            float: {'type': 'number'}}.get(annotation, {})


def model_schema(model):
    annotations = get_type_hints(model, include_extras=True)
    required = set(getattr(model, '__required_keys__', ()))
    if is_dataclass(model):
        required = {field.name for field in fields(model) if field.default is MISSING and field.default_factory is MISSING}
    for key, value in annotations.items():
        if get_origin(value) is NotRequired:
            required.discard(key)
        elif get_origin(value) is Required:
            required.add(key)
    schema = {'type': 'object', 'properties': {key: schema_for(value) for key, value in annotations.items()},
              'additionalProperties': not is_dataclass(model)}
    if required:
        schema['required'] = sorted(required)
    return schema


def api_group(path, method):
    if (path.startswith('/configuration') or path.startswith('/tool/registry')
            or path.startswith('/workobject/registry') or path == '/collision/monitor/config'):
        return 'configuration'
    if (path.startswith(('/position/', '/velocity/', '/state/', '/startup/')) or path in ('/health', '/status')
            or path == '/execute/ordered_motion_chain/status'
            or path == '/servojog/until-condition/status'
            or path == '/execute/ordered_motion_chain/prepared/{plan_id}' and method == 'get'):
        return 'state'
    if (path.startswith(('/drive/', '/io/', '/safety/', '/visualization/', '/collision/'))
            or path.startswith('/motion/interlock/')):
        return 'control'
    return 'motion'


def add_runtime_contracts(spec):
    additions = {
        '/motion/controlled-stop': {'post': {'summary': 'Decelerate the expected task while preserving queued work',
            'requestBody': {'required': True, 'content': {'application/json': {'schema': {
                'type': 'object', 'required': ['expected_task_id'], 'properties': {
                    'expected_task_id': {'oneOf': [{'type': 'integer'}, {'type': 'string'}]},
                    'stop_duration_s': {'type': 'number', 'minimum': 0.05, 'maximum': 2.0}}}}}}}},
        '/servojog/until-condition/start': {'post': {'summary': 'Start conditional Servo or fast LIN motion'}},
        '/servojog/until-condition/cancel': {'post': {'summary': 'Cancel conditional motion'}},
        '/servojog/until-condition/status': {'get': {'summary': 'Observe conditional motion state'}},
        '/safety/passages': {'get': {'summary': 'Read motion passages'}},
        '/safety/passages/{passage_id}': {
            'parameters': [{'name': 'passage_id', 'in': 'path', 'required': True, 'schema': {'type': 'string'}}],
            'get': {'summary': 'Read a motion passage'},
            'post': {'summary': 'Set passage closed state', 'requestBody': {'required': True, 'content': {
                'application/json': {'schema': {'type': 'object', 'required': ['closed'],
                                               'properties': {'closed': {'type': 'boolean'}}}}}}}},
    }
    for path, operations in additions.items():
        spec['paths'].setdefault(path, operations)
        for method, operation in operations.items():
            if method in ('get', 'post'):
                operation.setdefault('responses', {})['200'] = {'description': 'Operation result'}
    schemas = spec.setdefault('components', {}).setdefault('schemas', {})
    schemas.update({model.__name__: model_schema(model) for model in MODELS})
    schemas['ErrorInfo']['description'] = (
        'Stable machine-readable code, original cause and operation. outcome_unknown means a timeout '
        'does not establish whether a command was applied. No implicit retries are performed.')
    schemas['ConfigurationResponse']['description'] = (
        'success confirms persistence. pending_application and application_error_info separately describe '
        'runtime application; restart_required is null when observed state is unavailable.')
    spec['tags'] = [{'name': name, 'description': description} for name, description in (
        ('configuration', 'Backend-owned profile definitions and revision-checked persistence'),
        ('motion', 'Moves, paths, jogging/Servo, stopping and frame selection'),
        ('state', 'Read-only robot state, startup and operation status'),
        ('control', 'Drive state, interlocks, general-purpose I/O and diagnostics'))]
    for path, methods in spec['paths'].items():
        for method, operation in methods.items():
            if method not in ('get', 'post', 'patch', 'put', 'delete'):
                continue
            group = api_group(path, method)
            operation['tags'] = [group]
            operation.setdefault('parameters', []).append({
                'name': 'X-Request-ID', 'in': 'header', 'required': False,
                'description': 'Optional correlation identifier echoed in the response header/body.',
                'schema': {'type': 'string', 'maxLength': 128, 'pattern': '^[A-Za-z0-9._-]+$'},
            })
            responses = operation.setdefault('responses', {})
            for code in ('400', '404', '409', '415', '500', '501', '503', '504'):
                responses.setdefault(code, {'description': {
                    '400': 'Invalid request or malformed JSON', '404': 'Resource not found',
                    '409': 'State conflict or stale configuration revision', '415': 'JSON media type required',
                    '500': 'Runtime or backend response failure', '501': 'Unsupported operation',
                    '503': 'Runtime, hardware or storage unavailable',
                    '504': 'Gateway confirmation timed out; inspect outcome_unknown',
                }[code]})
            for code, response in responses.items():
                if not str(code).isdigit():
                    continue
                model = 'ResponseBody' if int(code) >= 400 else group.capitalize() + 'Response'
                if int(code) < 400 and path.startswith(('/tool/registry', '/workobject/registry')):
                    model = 'RegistryResponse'
                response.setdefault('content', {}).setdefault('application/json', {})['schema'] = {
                    '$ref': '#/components/schemas/' + model}
                response.setdefault('headers', {})['X-Request-ID'] = {'schema': {'type': 'string'}, 'description': 'Request correlation ID'}
            if path == '/configuration/{section}' and method == 'patch' or path.startswith('/configuration/calibration/') and method == 'patch':
                operation['requestBody']['content']['application/json']['schema'] = schema_for(ConfigurationUpdateRequest)
            if path == '/io/digital_output' and method == 'post':
                operation['requestBody']['content']['application/json']['schema'] = schema_for(DigitalOutputRequest)
