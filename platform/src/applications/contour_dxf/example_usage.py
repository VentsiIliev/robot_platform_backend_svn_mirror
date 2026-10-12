"""Launch the tray-dryer camera studio; pass --demo for a synthetic preview."""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

def run_standalone():
    from scripts.paint_tray_capture_dxf import main
    return main()

if __name__ == '__main__':
    raise SystemExit(run_standalone())
