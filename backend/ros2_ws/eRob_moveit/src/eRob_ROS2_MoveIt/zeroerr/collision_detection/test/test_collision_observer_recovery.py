"""Exercise the exact baseline/rearm policy used by the real-time controller."""
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest


class TestCollisionObserverRecovery(unittest.TestCase):
    @unittest.skipUnless(shutil.which("g++"), "C++ compiler unavailable")
    def test_stationary_calibration_and_baseline_preserving_rearm(self):
        root = Path(__file__).resolve().parent
        include = root.parent / "runtime" / "include"
        if not include.exists():
            include = root.parent / "include"
        with tempfile.TemporaryDirectory() as temporary:
            binary = Path(temporary) / "observer_recovery"
            subprocess.run([
                "g++", "-std=c++17", "-O2", "-Wall", "-Wextra", "-Werror",
                "-I" + str(include), str(root / "test_collision_observer_recovery.cpp"),
                "-o", str(binary),
            ], check=True, timeout=30)
            subprocess.run([str(binary)], check=True, timeout=10)


if __name__ == "__main__":
    unittest.main()
