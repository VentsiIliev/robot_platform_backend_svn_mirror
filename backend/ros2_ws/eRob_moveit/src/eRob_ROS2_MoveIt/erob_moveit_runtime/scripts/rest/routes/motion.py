"""HTTP routes for motion; validation and runtime decisions belong to the API."""
import time
from flask import Blueprint, request
from runtime_api.motion.api import MotionApi
from .common import to_http


def motion_blueprint(api: MotionApi):
    routes = Blueprint('runtime_motion', __name__)

    @routes.route('/move/linear', methods=['POST'])
    def move_linear():
        return to_http(api.move_linear(request.json))

    @routes.route('/move/fast_lin', methods=['POST'])
    def move_fast_lin():
        return to_http(api.move_fast_lin(request.json))

    @routes.route('/move/ptp', methods=['POST'])
    def move_ptp():
        return to_http(api.move_ptp(request.json))

    @routes.route('/execute/path', methods=['POST'])
    def execute_path():
        return to_http(api.execute_path(request.json))

    @routes.route('/execute/sequence', methods=['POST'])
    def execute_sequence():
        return to_http(api.execute_sequence(request.json))

    @routes.route('/execute/ordered_motion_chain', methods=['POST'])
    def execute_ordered_motion_chain():
        return to_http(api.execute_ordered_motion_chain(request.json))

    @routes.route('/execute/ordered_motion_chain/prepare', methods=['POST'])
    def prepare_ordered_motion_chain():
        return to_http(api.prepare_ordered_motion_chain(request.json))

    @routes.route('/execute/ordered_motion_chain/prepared/<plan_id>/execute', methods=['POST'])
    def execute_prepared_ordered_motion_chain(plan_id):
        return to_http(api.execute_prepared_ordered_motion_chain(plan_id))

    @routes.route('/unwind/joint6', methods=['POST'])
    def unwind_joint6():
        return to_http(api.unwind_joint6(request.json))

    @routes.route('/tool/active', methods=['GET'])
    def get_active_tool():
        return to_http(api.active_tool())

    @routes.route('/tool/active', methods=['POST'])
    def set_active_tool():
        return to_http(api.set_active_tool(request.json))

    @routes.route('/reachability/pose', methods=['POST'])
    def validate_pose():
        return to_http(api.validate_pose(request.json))

    @routes.route('/stop', methods=['POST'])
    def stop_motion():
        return to_http(api.stop_motion())

    @routes.route('/motion/controlled-stop', methods=['POST'])
    def controlled_stop():
        return to_http(api.controlled_stop(request.json))

    @routes.route('/workobject/set', methods=['POST'])
    def set_workobject():
        return to_http(api.set_workobject(request.json))

    @routes.route('/workobject/active', methods=['GET'])
    def get_active_workobject():
        return to_http(api.active_workobject())

    @routes.route('/workobject/active', methods=['POST'])
    def set_active_workobject():
        return to_http(api.set_active_workobject(request.json))

    @routes.route('/servo/cartesian/start', methods=['POST'])
    def cartesian_servo_start():
        return to_http(api.cartesian_servo_start(request.get_json(silent=True)))

    @routes.route('/servo/cartesian/update', methods=['POST'])
    def cartesian_servo_update():
        return to_http(api.cartesian_servo_update(request.get_json(silent=True)))

    @routes.route('/servo/cartesian/stop', methods=['POST'])
    def cartesian_servo_stop():
        return to_http(api.cartesian_servo_stop())

    @routes.route('/jog', methods=['POST'])
    def jog():
        return to_http(api.jog(request.get_json(silent=True)))

    @routes.route('/jog/joint', methods=['POST'])
    def joint_jog():
        return to_http(api.joint_jog(request.get_json(silent=True)))

    @routes.route('/servojog/start', methods=['POST'])
    def servo_jog_start():
        return to_http(api.servo_jog_start(request.get_json(silent=True)))

    @routes.route('/servojog/stop', methods=['POST'])
    def servo_jog_stop():
        payload = request.get_json(silent=True) or {}
        payload['_ros_http_route_enter_ns'] = time.monotonic_ns()
        return to_http(api.servo_jog_stop(payload))

    @routes.route('/servojog/until-condition/start', methods=['POST'])
    def conditional_servo_start():
        return to_http(api.conditional_servo_start(request.get_json(silent=True)))

    @routes.route('/servojog/until-condition/cancel', methods=['POST'])
    def conditional_servo_cancel():
        return to_http(api.conditional_servo_cancel())

    @routes.route('/servojog/to-z', methods=['POST'])
    def servo_jog_to_z():
        return to_http(api.servo_jog_to_z(request.get_json(silent=True)))
    @routes.route('/execute/ordered_motion_chain/prepared/<plan_id>', methods=['DELETE'])
    def discard_prepared_ordered_motion_chain(plan_id):
        return to_http(api.discard_prepared_ordered_motion_chain(plan_id))

    return routes
