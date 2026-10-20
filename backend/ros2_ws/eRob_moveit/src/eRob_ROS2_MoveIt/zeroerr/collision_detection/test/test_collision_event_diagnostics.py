"""Build and exercise the ROS-independent real-time diagnostic handoff."""
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest


class TestCollisionEventDiagnostics(unittest.TestCase):
    @unittest.skipUnless(shutil.which("g++"), "C++ compiler unavailable")
    def test_snapshot_serialization_and_nonblocking_queue(self):
        root = Path(__file__).resolve().parent
        # Installed in collision_detection/test; staging keeps test/ and include/ beside each other.
        include = root.parent / "runtime" / "include"
        if not include.exists():
            include = root.parent / "include"
        with tempfile.TemporaryDirectory() as temporary:
            binary = Path(temporary) / "collision_event_diagnostics"
            subprocess.run([
                "g++", "-std=c++17", "-O2", "-Wall", "-Wextra", "-Werror", "-pthread",
                "-I" + str(include), str(root / "test_collision_event_diagnostics.cpp"),
                "-o", str(binary),
            ], check=True, timeout=60)
            subprocess.run([str(binary)], check=True, timeout=20)


if __name__ == "__main__":
    unittest.main()
