"""Flask adapter; the configuration application has no HTTP dependencies."""
from flask import Blueprint, jsonify, request
from werkzeug.exceptions import BadRequest

from .domain import ConfigurationError


def configuration_blueprint(service_getter):
    routes = Blueprint('backend_configuration', __name__, url_prefix='/configuration')

    @routes.errorhandler(ConfigurationError)
    def invalid_configuration(error):
        return jsonify(success=False, error=str(error), code=error.code), error.status

    def payload():
        try:
            value = request.get_json()
        except BadRequest:
            raise ConfigurationError('Request body must be valid JSON') from None
        if not isinstance(value, dict):
            raise ConfigurationError('Request body must be an object')
        if set(value) - {'expected_revision', 'changes'}:
            raise ConfigurationError('Unsupported request fields')
        return value

    @routes.get('')
    def index():
        return jsonify(success=True, schema_version=1, active_profile=service_getter().repository.profile,
                       sections=list(service_getter().repository.sections), authority='backend_profile')

    @routes.route('/<section>', methods=['GET', 'PATCH'])
    def section_configuration(section):
        if request.method == 'GET':
            result = service_getter().get(section)
        else:
            body = payload()
            result = service_getter().update(section, body.get('changes'), body.get('expected_revision'))
        return jsonify(result)

    @routes.post('/<section>/apply')
    def apply_configuration(section):
        body = payload()
        return jsonify(service_getter().retry_application(section, body.get('expected_revision')))

    @routes.patch('/calibration/tools/<int:tool_id>')
    def update_tool(tool_id):
        body = payload()
        return jsonify(service_getter().update('calibration', body.get('changes'), body.get('expected_revision'), tool_id=tool_id))

    @routes.patch('/calibration/workobjects/<int:user_id>')
    def update_workobject(user_id):
        body = payload()
        return jsonify(service_getter().update('calibration', body.get('changes'), body.get('expected_revision'), user_id=user_id))

    return routes
