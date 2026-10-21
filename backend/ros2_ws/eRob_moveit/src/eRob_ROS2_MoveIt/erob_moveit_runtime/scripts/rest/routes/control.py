"""HTTP routes for control; validation and runtime decisions belong to the API."""
from flask import Blueprint, request
from runtime_api.control.api import ControlApi
from .common import to_http


def control_blueprint(api: ControlApi):
    routes = Blueprint('runtime_control', __name__)

    @routes.route('/collision/calibration/recording/start', methods=['POST'])
    def start_collision_calibration_recording():
        return to_http(api.start_collision_recording())

    @routes.route('/collision/calibration/recording/stop', methods=['POST'])
    def stop_collision_calibration_recording():
        return to_http(api.stop_collision_recording())

    @routes.route('/collision/monitor/suppression', methods=['POST'])
    def set_collision_monitor_suppression():
        return to_http(api.set_collision_suppression(request.get_json()))

    @routes.route('/visualization/rviz', methods=['GET', 'POST'])
    def control_rviz():
        if request.method == 'GET':
            return to_http(api.rviz_status())
        return to_http(api.set_rviz_enabled(request.get_json()))

    @routes.route('/collision/monitor/diagnostics/open', methods=['POST'])
    def open_collision_monitor_diagnostics():
        return to_http(api.open_collision_diagnostics())

    @routes.route('/safety/walls/enabled', methods=['GET'])
    def safety_walls_enabled():
        return to_http(api.safety_walls_enabled())

    @routes.route('/safety/walls/status', methods=['GET'])
    def safety_walls_status():
        return to_http(api.safety_walls_status())

    @routes.route('/safety/walls/enable', methods=['POST'])
    def enable_safety_walls():
        return to_http(api.enable_safety_walls())

    @routes.route('/safety/walls/disable', methods=['POST'])
    def disable_safety_walls():
        return to_http(api.disable_safety_walls())

    @routes.route('/safety/passages', methods=['GET'])
    def motion_passages_status():
        return to_http(api.motion_passage_status())

    @routes.route('/safety/passages/<passage_id>', methods=['GET', 'POST'])
    def motion_passage(passage_id):
        if request.method == 'GET':
            return to_http(api.motion_passage_status(passage_id))
        return to_http(api.set_motion_passage_closed(passage_id, request.json))

    @routes.route('/io/digital_output', methods=['POST'])
    def set_digital_output():
        return to_http(api.set_digital_output(request.json))

    @routes.route('/drive/enable', methods=['POST'])
    def enable_drive_operation():
        return to_http(api.enable_drive_operation())

    @routes.route('/drive/disable', methods=['POST'])
    def disable_drive_operation():
        return to_http(api.disable_drive_operation())

    @routes.route('/drive/status', methods=['GET'])
    def drive_operation_status():
        return to_http(api.drive_operation_status())

    @routes.route('/motion/interlock/status', methods=['GET'])
    def motion_interlock_status():
        return to_http(api.motion_interlock_status())

    @routes.route('/motion/interlock/reset', methods=['POST'])
    def reset_motion_interlock():
        return to_http(api.reset_motion_interlock())
    return routes
