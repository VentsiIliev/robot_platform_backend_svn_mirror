"""Install an authorized navigation snapshot while preserving the active screen."""
import logging

from src.bootstrap.application_loader import ApplicationLoader


def replace_shell_applications(shell, robot_system, messaging_service, visible_specs,
                               access_guard, *, show_folders=False):
    showing_folders = shell.stacked_widget.currentWidget() is shell.folders_page
    loader = ApplicationLoader(messaging_service)
    for spec in visible_specs:
        if spec.factory is None:
            logging.getLogger(__name__).warning("ApplicationSpec '%s' has no factory — skipping", spec.name)
            continue
        loader.register_spec(spec, builder=lambda spec=spec: spec.factory(robot_system))
    descriptors, widget_factory = loader.build_registry()
    shell._app_descriptors = descriptors
    shell._widget_factory = access_guard.guard_factory(widget_factory)
    shell.create_folders_page()
    if show_folders or showing_folders:
        shell.stacked_widget.setCurrentWidget(shell.folders_page)
