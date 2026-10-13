from __future__ import annotations

from PyQt6.QtCore import QCoreApplication

from src.applications.base.onboarding import OnboardingStep, OnboardingTour


def build_paint_dashboard_tour(view) -> OnboardingTour:
    """Build the paint-owned tour on top of the reusable onboarding UI."""

    steps = (
        OnboardingStep(
            target=lambda: view.onboarding_target("dashboard"),
            title="Welcome to the Paint Dashboard",
            body=(
                "This short tour introduces the main areas used to prepare, monitor, "
                "and run a paint job."
            ),
            spotlight=False,
        ),
        OnboardingStep(
            target=lambda: view.onboarding_target("tray"),
            title="Tray and camera view",
            body=(
                "Use this area to inspect the workpiece layout and, when configured, "
                "switch to a live camera view."
            ),
        ),
        OnboardingStep(
            target=lambda: view.onboarding_target("drying_duration"),
            title="Drying Duration",
            body=(
                "Set how long each painted workpiece must remain on the tray before "
                "it is considered dry. Use the minus and plus buttons or enter a value."
            ),
        ),
        OnboardingStep(
            target=lambda: view.onboarding_target("drying_time"),
            title="Drying Time",
            body=(
                "Select a painted workpiece on the tray to see how long it has been "
                "drying. A dash is shown when no painted workpiece is selected."
            ),
        ),
        OnboardingStep(
            target=lambda: view.onboarding_target("pass_count"),
            title="Number of Passes",
            body=(
                "Choose how many times the robot repeats the paint path. A second "
                "pass can use its own settings or inherit the first pass settings."
            ),
        ),
        OnboardingStep(
            target=lambda: view.onboarding_target("process_scaling"),
            title="Process Scaling",
            body=(
                "Scale the configured process acceleration for the complete paint "
                "cycle. Lower values make all process movements less aggressive."
            ),
        ),
        OnboardingStep(
            target=lambda: view.onboarding_target("speed"),
            title="Pass Speed",
            body=(
                "Set the speed for the selected paint pass. Use the minus and plus "
                "buttons for touch-friendly adjustments."
            ),
        ),
        OnboardingStep(
            target=lambda: view.onboarding_target("resolved_speed"),
            title="Velocity and Acceleration",
            body=(
                "These values show the velocity and acceleration that will actually "
                "be used after the pass speed and process scaling are applied."
            ),
        ),
        OnboardingStep(
            target=lambda: view.onboarding_target("press_offset"),
            title="Press Offset",
            body=(
                "Adjust the pass-specific press offset in millimeters. Positive and "
                "negative values move the paint path relative to its taught position."
            ),
        ),
        OnboardingStep(
            target=lambda: view.onboarding_target("apply_all"),
            title="Apply All",
            body=(
                "Apply the current pass settings together. Review the values above "
                "before confirming them."
            ),
        ),
        OnboardingStep(
            target=lambda: view.onboarding_target("paint_control"),
            title="Paint Control",
            body=(
                "Choose the adjustment step, then use minus or plus to reduce or add "
                "paint. These controls command the configured paint head."
            ),
        ),
        OnboardingStep(
            target=lambda: view.onboarding_target("machine_controls"),
            title="Machine controls",
            body=(
                "Control configured auxiliary devices, cable relief, drying mode, "
                "and tray actions from this panel."
            ),
        ),
        OnboardingStep(
            target=lambda: view.onboarding_target("process_controls"),
            title="Run the paint process",
            body=(
                "Start, pause, resume, or stop the paint process here. Button "
                "availability follows the current process state."
            ),
        ),
        OnboardingStep(
            target=lambda: view.onboarding_target("status"),
            title="Status and messages",
            body=(
                "Review robot, vision, and process status here. Open messages when "
                "you need more detail about the latest event."
            ),
        ),
    )

    return OnboardingTour(
        host_provider=view.window,
        steps=steps,
        translator=_translate,
        parent=view,
    )


def _translate(source: str) -> str:
    return QCoreApplication.translate("PaintDashboardOnboarding", source) or source
