"""Run the reusable shell with sample widgets and no robot services."""

import sys
from pathlib import Path

# Support direct execution from any working directory, including an extracted
# standalone checkout where this directory is the pl_gui package itself.
if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from PyQt6.QtWidgets import QApplication

from pl_gui.shell.AppShell import AppShell
from pl_gui.shell.app_descriptor import AppDescriptor
from pl_gui.shell.base_app_widget.AppWidget import AppWidget
from pl_gui.shell.shell_config import (
    FOLDER_ADMINISTRATION,
    FOLDER_SERVICE,
    FOLDER_WORK,
    ShellConfig,
)


def build_shell() -> AppShell:
    """Build a demo shell after the caller has created QApplication."""
    ShellConfig.reset_to_defaults()
    shell = AppShell(
        app_descriptors=[
            AppDescriptor("Dashboard", "fa5s.tachometer-alt", FOLDER_WORK),
            AppDescriptor("Device Control", "fa5s.tools", FOLDER_SERVICE),
            AppDescriptor("Settings", "fa5s.cog", FOLDER_ADMINISTRATION),
        ],
        widget_factory=AppWidget,
        languages=[("en", "English")],
    )
    shell.setWindowTitle("pl_gui — Standalone Demo")
    shell.header.userAccountButton.hide()
    shell.header.power_toggle_button.hide()
    return shell


def run_standalone() -> int:
    """Start the standalone demo and return the Qt event loop exit code."""
    app = QApplication(sys.argv)
    shell = build_shell()
    shell.show()
    return app.exec()


if __name__ == "__main__":
    sys.exit(run_standalone())
