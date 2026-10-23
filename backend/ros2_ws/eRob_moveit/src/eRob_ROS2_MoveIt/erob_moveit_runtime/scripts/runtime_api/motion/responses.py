"""Motion acknowledgement/completion contracts and backend failure mapping."""
from typing import Any
from runtime_api.contracts import ApiResponse, ResponseBody, response_error

class MotionResponse(ResponseBody, total=False):
    result: int | str
    task_id: int | str | None
    accepted: bool
    final: bool
    queued: bool
    queue_position: int
    state: str
    reason: str
    detail: str
    message: str
    reachable: bool
    servo: dict[str, Any] | None
    conditional_servo: dict[str, Any]
    plan_id: str
    status_ws: str
    status_ws_port: int
    origin: list[float]
    user_id: int
    tool_name: str
    timing_trace_id: str
    timing: dict[str, int]

MOTION_ERROR_DESCRIPTIONS = {
    -1:  "Busy / invalid input / generic error",
    -2:  "MoveIt service unavailable",
    -3:  "Safety violation: target outside workspace",
    -4:  "No current robot position available",
    -5:  "Motion queue full",
    -6:  "Path planning failed: MoveIt returned no trajectory",
    -7:  "Time parameterization failed (TOTG/Ruckig)",
    -8:  "Jacobian fallback path planning failed",
    -9:  "Near-singularity detected",
    -10: "Collision detected during Jacobian check",
    -11: "Cartesian path planning failed: target unreachable, collision, or joint-limit constraint",
    -12: "Hardware not ready for motion",
    -13: "Drive operation is not enabled; call POST /drive/enable before motion",
    -14: "Controller execution failed: trajectory tolerance or controller action error",
}


def motion_error(result: int, **extra) -> ApiResponse[MotionResponse]:
    description = extra.get('detail') or MOTION_ERROR_DESCRIPTIONS.get(result, f'Unknown motion result {result}')
    status = 503 if result in (-2, -5, -12) else 409 if result in (-13, -14) else 400 if result in (-3, -11) else 500
    return response_error(description, status, code=f'motion_error_{abs(result)}', source='controller' if result == -14 else 'runtime',
                          details={'result': result, **extra}, result=result, **extra)
