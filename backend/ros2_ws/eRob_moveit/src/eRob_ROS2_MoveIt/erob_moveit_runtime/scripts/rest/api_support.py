"""Compatibility imports for callers predating the transport-neutral motion API."""
from flask import jsonify
from runtime_api.motion.requests import (
    parse_jog_request,
    parse_joint_jog_request,
    parse_servo_jog_start_request,
    parse_servo_jog_to_z_request,
    parse_move_linear_request,
    parse_execute_path_request,
    parse_execute_sequence_request,
    parse_execute_ordered_motion_chain_request,
    parse_prepare_ordered_motion_chain_request,
    parse_cartesian_servo_start_request,
    parse_cartesian_servo_update_request,
    _state_validity_contact_pairs,
    _coerce_pose6,
)
from runtime_api.motion.responses import MOTION_ERROR_DESCRIPTIONS, motion_error
from motion.planning.reachability import validate_pose_from_start


def motion_error_response(result: int, **extra):
    response = motion_error(result, **extra)
    return jsonify(response.body), response.status
