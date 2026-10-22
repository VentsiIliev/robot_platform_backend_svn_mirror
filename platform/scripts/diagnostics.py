"""Readable diagnostics for the configured RobotSystem; no application startup."""
from pathlib import Path
import json
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.engine.diagnostics.timeline import main


if __name__ == '__main__':
    arguments = sys.argv[1:]
    # Repository-specific discovery belongs here, never in the engine reader.
    if '--evidence-directory' not in arguments:
        try:
            system = json.loads((ROOT / 'config/platform.json').read_text())['robot_system']
            if type(system) is str and system.replace('_', '').isalnum():
                evidence = ROOT / 'src/robot_systems' / system / 'storage/diagnostics'
                if (evidence / 'failure_register.jsonl').is_file():
                    arguments = ['--evidence-directory', str(evidence), *arguments]
        except (OSError, ValueError, KeyError):
            pass
    main(arguments)
