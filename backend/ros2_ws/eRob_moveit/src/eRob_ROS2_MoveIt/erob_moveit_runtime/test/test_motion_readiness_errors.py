"""Readiness failures must report the runtime reason, not infer EtherCAT state."""
from pathlib import Path
import sys
from unittest.mock import Mock
import pytest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from runtime_api.motion.api import MotionApi


@pytest.mark.parametrize('reason', ['Cell collision configuration has not been confirmed by MoveIt',
    'collision detected; operator acknowledgement required', 'EtherCAT slaves not OP: slave 3 SAFEOP'])
@pytest.mark.parametrize('fast', [False,True])
def test_minus_twelve_reports_actual_hardware_readiness_reason(reason,fast):
    gateway=Mock()
    gateway.last_submitted_task_id.return_value=None
    gateway.last_motion_error.return_value='stale planning error: eventual outcome is unknown'
    gateway.runtime_state_snapshot.return_value={'hardware_ready':False,'hardware_fault':reason}
    api=MotionApi(gateway)
    result=api._fast_lin_result(-12,blocking=True) if fast else api._motion_result(-12)
    assert result.status==503
    assert result.body['error']==reason
    assert result.body['error_info']['message']==reason
    if fast:
        assert result.body['accepted'] is False
        assert result.body['final'] is True


def test_missing_readiness_reason_uses_neutral_error():
    gateway=Mock()
    gateway.last_submitted_task_id.return_value=None
    gateway.last_motion_error.return_value=None
    gateway.runtime_state_snapshot.side_effect=RuntimeError('unavailable')
    result=MotionApi(gateway)._motion_result(-12)
    assert result.body['error']=='Hardware not ready for motion'
    assert 'EtherCAT' not in result.body['error']
