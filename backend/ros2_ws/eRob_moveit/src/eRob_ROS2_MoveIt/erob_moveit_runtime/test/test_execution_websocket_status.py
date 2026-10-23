"""Terminal chain evidence must remain visible to WebSocket status consumers."""
from pathlib import Path
import sys
from types import SimpleNamespace
import unittest

SCRIPTS = Path(__file__).resolve().parents[1] / 'scripts'
sys.path.insert(0, str(SCRIPTS))
from runtime_websockets.execution_server import execution_payload


class TestExecutionWebSocketStatus(unittest.TestCase):
    def payload(self, chain):
        robot = SimpleNamespace(get_ordered_motion_chain_status=lambda: chain)
        node = SimpleNamespace(
            is_motion_stack_ready=lambda: True,
            status_publisher=SimpleNamespace(get_status_dict=lambda: {'is_executing': False}),
        )
        return execution_payload(robot, node, 1)

    def test_terminal_chain_keeps_error_and_progress_evidence(self):
        for phase in ('error', 'failed', 'rejected', 'completed'):
            with self.subTest(phase=phase):
                chain = {'active': False, 'phase': phase,
                         'error': 'ordered-chain planning failed: no IK candidates found',
                         'planned_segments_count': 0, 'executed_segments_count': 0}
                payload = self.payload(chain)
                self.assertTrue(payload['success'])
                self.assertEqual(chain, payload['status']['ordered_motion_chain'])

    def test_active_chain_and_partial_progress_remain_visible(self):
        chain = {'active': True, 'phase': 'executing',
                 'planned_segments_count': 3, 'executed_segments_count': 1}
        self.assertEqual(chain, self.payload(chain)['status']['ordered_motion_chain'])

    def test_unavailable_chain_is_omitted(self):
        for chain in (None, False, 'unavailable'):
            with self.subTest(chain=chain):
                self.assertNotIn('ordered_motion_chain', self.payload(chain)['status'])
