from PyQt6.QtCore import QCoreApplication

from src.applications.base.onboarding import OnboardingStep, OnboardingTour


def build_workpiece_editor_tour(view) -> OnboardingTour:
    """Describe the editor using the shared onboarding overlay."""
    steps = (
        OnboardingStep(
            target=lambda: view.onboarding_target('editor'),
            title='Welcome to the Workpiece Editor',
            body='This tour introduces the controls used to prepare a workpiece and its paths.',
            spotlight=False,
        ),
        OnboardingStep(
            target=lambda: view.onboarding_target('capture'),
            title='Capture contours',
            body='Capture workpiece contours from the configured vision system.',
        ),
        OnboardingStep(
            target=lambda: view.onboarding_target('canvas'),
            title='Contour canvas',
            body='Inspect and edit the workpiece geometry here. Use the editing controls to select and adjust points.',
        ),
        OnboardingStep(
            target=lambda: view.onboarding_target('point_visibility'),
            title='Show or hide points',
            body='Toggle the point markers on the canvas.',
        ),
        OnboardingStep(
            target=lambda: view.onboarding_target('zoom_out'),
            title='Zoom out',
            body='Zoom out to see more of the workpiece.',
        ),
        OnboardingStep(
            target=lambda: view.onboarding_target('reset_zoom'),
            title='Reset zoom',
            body='Reset the canvas zoom.',
        ),
        OnboardingStep(
            target=lambda: view.onboarding_target('zoom_in'),
            title='Zoom in',
            body='Zoom in to inspect points and curves more closely.',
        ),
        OnboardingStep(
            target=lambda: view.onboarding_target('pan'),
            title='Pan or select',
            body='Switch between dragging the canvas and selecting geometry.',
        ),
        OnboardingStep(
            target=lambda: view.onboarding_target('layer_expand'),
            title='Expand a layer',
            body='Use the chevron to show or hide the segments in this layer.',
        ),
        OnboardingStep(
            target=lambda: view.onboarding_target('layer_visibility'),
            title='Layer visibility',
            body='Show or hide all segments in this layer.',
        ),
        OnboardingStep(
            target=lambda: view.onboarding_target('layer_add'),
            title='Add a segment',
            body='Add a new segment to this layer.',
        ),
        OnboardingStep(
            target=lambda: view.onboarding_target('layer_lock'),
            title='Lock a layer',
            body='Lock or unlock this layer to control whether its geometry can be edited.',
        ),
        OnboardingStep(
            target=lambda: view.onboarding_target('segment_expand'),
            title='Expand a segment',
            body='Use the chevron to show or hide the anchor and control points of this segment.',
        ),
        OnboardingStep(
            target=lambda: view.onboarding_target('segment_activate'),
            title='Activate a segment',
            body='Tap the segment number to activate it. Press and hold the same button to choose its layer.',
        ),
        OnboardingStep(
            target=lambda: view.onboarding_target('segment_visibility'),
            title='Segment visibility',
            body='Show or hide this segment on the canvas.',
        ),
        OnboardingStep(
            target=lambda: view.onboarding_target('segment_delete'),
            title='Delete a segment',
            body='Delete this segment and its points.',
        ),
        OnboardingStep(
            target=lambda: view.onboarding_target('segment_settings'),
            title='Segment settings',
            body='Open the settings for this individual segment.',
        ),
        OnboardingStep(
            target=lambda: view.onboarding_target('point_select'),
            title='Select a point',
            body='Tap a point row to select it. P labels identify anchor points; C labels identify curve control points. Select one point to enable Nudge.',
        ),
        OnboardingStep(
            target=lambda: view.onboarding_target('nudge'),
            title='Nudge a selected point',
            body='Select a single point, then tap Nudge to expand its controls. Choose a step of 0.1, 1, or 10 units and use the arrows to move the point up, down, left, or right. Tap Nudge again to collapse the controls.',
        ),
        OnboardingStep(
            target=lambda: view.onboarding_target('tools'),
            title='Editing tools',
            body='Open the tools menu for the available geometry operations.',
        ),
        OnboardingStep(
            target=lambda: view.onboarding_target('settings'),
            title='Path settings',
            body='Open settings to review the available segment and path options.',
        ),
        OnboardingStep(
            target=lambda: view.onboarding_target('undo'),
            title='Undo changes',
            body='Undo the last edit. Use the adjacent redo control to restore an undone change.',
        ),
        OnboardingStep(
            target=lambda: view.onboarding_target('redo'),
            title='Redo changes',
            body='Restore the last edit that was undone.',
        ),
        OnboardingStep(
            target=lambda: view.onboarding_target('preview'),
            title='Preview the workpiece',
            body='Preview the workpiece before saving or executing its paths.',
        ),
        OnboardingStep(
            target=lambda: view.onboarding_target('save'),
            title='Save the workpiece',
            body='Open the workpiece form, review its details, and confirm to save.',
        ),
        OnboardingStep(
            target=lambda: view.onboarding_target('execute'),
            title='Execute paths',
            body='This control requests execution of the current workpiece paths. Review the geometry and settings before using it.',
        ),
    )
    return OnboardingTour(view.window, steps, _translate, parent=view)


def _translate(source: str) -> str:
    return QCoreApplication.translate("WorkpieceEditorOnboarding", source) or source
