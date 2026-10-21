"""HTTP routes for state; validation and runtime decisions belong to the API."""
from flask import Blueprint
from runtime_api.state.api import StateApi
from .common import to_http


def state_blueprint(api: StateApi):
    routes = Blueprint('runtime_state', __name__)

    @routes.route('/health', methods=['GET'])
    def health():
        return to_http(api.health())

    @routes.route('/startup/status', methods=['GET'])
    def startup_status():
        return to_http(api.startup_status())

    @routes.route('/execute/ordered_motion_chain/prepared/<plan_id>', methods=['GET'])
    def prepared_ordered_motion_chain(plan_id):
        return to_http(api.prepared_ordered_motion_chain_status(plan_id))

    @routes.route('/position/current', methods=['GET'])
    def get_position():
        return to_http(api.current_position())

    @routes.route('/position/base_tcp', methods=['GET'])
    def get_base_tcp_position():
        return to_http(api.base_tcp_position())

    @routes.route('/position/flange', methods=['GET'])
    def get_flange_position():
        return to_http(api.flange_position())

    @routes.route('/velocity/current', methods=['GET'])
    def get_velocity():
        return to_http(api.current_velocity())

    @routes.route('/status', methods=['GET'])
    def get_status():
        return to_http(api.status())

    @routes.route('/execute/ordered_motion_chain/status', methods=['GET'])
    def get_ordered_motion_chain_status():
        return to_http(api.ordered_motion_chain_status())

    @routes.route('/state/snapshot', methods=['GET'])
    def get_state_snapshot():
        return to_http(api.state_snapshot())

    @routes.route('/state/kinematics', methods=['GET'])
    def get_state_kinematics():
        return to_http(api.state_kinematics())

    @routes.route('/servojog/until-condition/status', methods=['GET'])
    def conditional_servo_status():
        return to_http(api.conditional_servo_status())
    return routes
