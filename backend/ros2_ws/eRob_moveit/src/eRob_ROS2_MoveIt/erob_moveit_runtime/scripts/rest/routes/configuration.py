"""HTTP routes for configuration; validation and runtime decisions belong to the API."""
from flask import Blueprint, request
from runtime_api.configuration.api import ConfigurationApi
from .common import to_http


def configuration_blueprint(api: ConfigurationApi):
    routes = Blueprint('backend_configuration', __name__)

    @routes.route('/collision/monitor/config', methods=['GET'])
    def get_collision_monitor_config():
        return to_http(api.get_collision_monitor())

    @routes.route('/collision/monitor/config', methods=['POST'])
    def update_collision_monitor_config():
        return to_http(api.update_collision_monitor(request.get_json()))

    @routes.route('/tool/registry', methods=['GET'])
    def get_tool_registry():
        return to_http(api.tool_registry())

    @routes.route('/tool/registry/<int:tool_id>', methods=['POST'])
    def update_tool_registry(tool_id):
        return to_http(api.update_tool_registry(tool_id, request.json))

    @routes.route('/workobject/registry', methods=['GET'])
    def get_workobject_registry():
        return to_http(api.workobject_registry())

    @routes.route('/workobject/registry/<int:user_id>', methods=['POST'])
    def update_workobject_registry(user_id):
        return to_http(api.update_workobject_registry(user_id, request.json))

    @routes.get('/configuration')
    def configuration_catalog():
        return to_http(api.catalog())

    @routes.route('/configuration/<section>', methods=['GET', 'PATCH'])
    def configuration_section(section):
        if request.method == 'GET':
            return to_http(api.get(section))
        return to_http(api.update(section, request.get_json()))

    @routes.post('/configuration/<section>/apply')
    def configuration_apply(section):
        return to_http(api.apply(section, request.get_json()))

    @routes.patch('/configuration/calibration/tools/<int:tool_id>')
    def configuration_tool(tool_id):
        return to_http(api.update('calibration', request.get_json(), tool_id=tool_id))

    @routes.patch('/configuration/calibration/workobjects/<int:user_id>')
    def configuration_workobject(user_id):
        return to_http(api.update('calibration', request.get_json(), user_id=user_id))

    return routes
