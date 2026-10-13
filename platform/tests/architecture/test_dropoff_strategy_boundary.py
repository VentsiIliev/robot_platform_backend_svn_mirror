"""Keep destination-specific implementation out of generic phase coordination."""
import ast
from pathlib import Path
import unittest


class TestDropoffStrategyBoundary(unittest.TestCase):
    def test_workflow_and_other_operations_use_the_dropoff_contract(self):
        root = Path(__file__).resolve().parents[2] / 'src/robot_systems/paint/processes/paint'
        consumers = (
            'workflow/handlers/workflow/pickup_handler.py',
            'workflow/handlers/lifecycle/terminal_common.py',
            'operations/painting/executor.py',
            'operations/edge_cleanup/executor.py',
        )
        forbidden_state = {'_plate_layout_service', '_plate_entry_completed_in_paint_chain',
                           '_dropoff_unwind_prepared'}
        for relative in consumers:
            with self.subTest(module=relative):
                for node in ast.walk(ast.parse((root / relative).read_text())):
                    if isinstance(node, ast.ImportFrom):
                        self.assertNotIn('dropoff.strategies', node.module or '')
                    elif isinstance(node, ast.Name):
                        self.assertNotEqual('DropoffStrategy', node.id)
                    elif isinstance(node, ast.Attribute):
                        self.assertNotIn(node.attr, forbidden_state)
