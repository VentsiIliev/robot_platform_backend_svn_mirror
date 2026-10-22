import contextlib
import io
import json
from pathlib import Path
import tempfile
import unittest

from src.engine.diagnostics.timeline import Follower, decode, main, render


class TimelineTests(unittest.TestCase):
    def record(self, second, **fields):
        return dict(timestamp=f'2026-10-21T07:38:{second:02d}+00:00',
                    level='INFO', message=f'step {second}', **fields)

    def test_orders_rotated_logs_and_failure_index_and_filters_exact_cycle(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / 'events.jsonl.1').write_text(json.dumps(self.record(40, context={'cycle_id': 'a'})) + '\n')
            (root / 'events.jsonl').write_text(json.dumps(self.record(42, context={'cycle_id': 'b'})) + '\n')
            (root / 'failure_register.jsonl').write_text(json.dumps(dict(
                recorded_at_utc='2026-10-21T07:38:41Z', cycle_id='a',
                message='exit failed', failure_bundle=str(root / 'bundle.json'))) + '\n')
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                main(['--directory', tmp, '--evidence-directory', tmp, '--utc', '--cycle-id', 'a'])
            text = output.getvalue()
            self.assertLess(text.index('step 40'), text.index('exit failed'))
            self.assertNotIn('step 42', text)
            self.assertIn('Evidence:', text)
            self.assertIn('uncorrelated', text)

    def test_time_level_selection_and_invalid_record_warning(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'events.jsonl'
            path.write_text('\n'.join(map(json.dumps, [self.record(40),
                dict(self.record(41), level='ERROR'), dict(self.record(42), level='ERROR')])) + '\ninvalid\n')
            out, err = io.StringIO(), io.StringIO()
            with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
                main(['--directory', tmp, '--since', '2026-10-21T07:38:41Z',
                      '--until', '2026-10-21T07:38:41Z', '--level', 'ERROR', '--utc'])
            self.assertIn('step 41', out.getvalue())
            self.assertNotIn('step 40', out.getvalue())
            self.assertNotIn('step 42', out.getvalue())
            self.assertIn('Invalid/incomplete', err.getvalue())

    def test_follow_partial_lines_rename_rotation_and_truncation(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'events.jsonl'
            path.write_bytes(b'')
            follower = Follower(path)
            self.addCleanup(follower.close)
            follower.open(end=True)
            encoded = json.dumps(self.record(40)).encode()
            with path.open('ab') as file:
                file.write(encoded[:20])
            self.assertEqual(follower.poll(), [])
            with path.open('ab') as file:
                file.write(encoded[20:] + b'\n')
            self.assertEqual(follower.poll()[0]['message'], 'step 40')
            path.rename(path.with_suffix('.old'))
            path.write_text(json.dumps(self.record(41)) + '\n')
            follower.poll()  # Detect replacement after draining old inode.
            self.assertEqual(follower.poll()[0]['message'], 'step 41')
            path.write_bytes(b'')
            with contextlib.redirect_stderr(io.StringIO()):
                follower.poll()
            path.write_text(json.dumps(self.record(42)) + '\n')
            self.assertEqual(follower.poll()[0]['message'], 'step 42')

    def test_render_preserves_traceback_and_omission_warning_without_terminal_controls(self):
        record = decode(json.dumps(self.record(40, traceback='first\nsecond',
                            omitted_fields=2, fields={'pressure': -62})))
        record['message'] = '\x1b[31munsafe\nnext'
        text = render(record, details=True, utc=True)
        self.assertNotIn('\x1b', text)
        self.assertIn('pressure', text)
        self.assertIn('Capture omitted 2', text)
        self.assertIn('    second', text)

    def test_missing_files_are_visible_and_no_files_created(self):
        with tempfile.TemporaryDirectory() as tmp:
            out, err = io.StringIO(), io.StringIO()
            with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
                main(['--directory', tmp])
            self.assertIn('No matching', out.getvalue())
            self.assertIn('Cannot read', err.getvalue())
            self.assertEqual(list(Path(tmp).iterdir()), [])
