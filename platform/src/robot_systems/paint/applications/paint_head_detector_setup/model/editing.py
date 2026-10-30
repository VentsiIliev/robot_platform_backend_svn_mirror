"""Pure editing commands preserving every unrelated profile property."""

from dataclasses import replace

from src.robot_systems.paint.contracts.paint_head_calibration.errors import (
    CalibrationValidationError,
)
from src.robot_systems.paint.contracts.paint_head_calibration.models import (
    CalibrationDefinition,
    ExcludedRegion,
    Landmark,
    LandmarkSupport,
    ObjectId,
)

from ..editor_contracts import EditorKind, EditorObject, EditorTarget, GeometryEdit


def objects(definition: CalibrationDefinition) -> tuple[EditorObject, ...]:
    values: list[EditorObject] = []
    if definition.inspection_region is not None:
        values.append(
            EditorObject(
                EditorTarget(EditorKind.INSPECTION, None),
                "",
                definition.inspection_region,
                LandmarkSupport.RECTANGLE,
            )
        )
    if definition.empty_mount_region is not None:
        values.append(
            EditorObject(
                EditorTarget(EditorKind.EMPTY_MOUNT, None),
                "",
                definition.empty_mount_region,
                LandmarkSupport.RECTANGLE,
            )
        )
    values.extend(
        EditorObject(
            EditorTarget(EditorKind.EXCLUDED, item.object_id),
            item.name,
            item.region,
            LandmarkSupport.RECTANGLE,
        )
        for item in definition.excluded_regions
    )
    values.extend(
        EditorObject(
            EditorTarget(EditorKind.LANDMARK, item.object_id),
            item.name,
            item.region,
            item.support,
            item.role,
        )
        for item in definition.landmarks
    )
    return tuple(values)


def change_geometry(
    definition: CalibrationDefinition,
    edit: GeometryEdit,
) -> tuple[CalibrationDefinition, EditorTarget]:
    target = edit.target
    match target.kind:
        case EditorKind.INSPECTION:
            return replace(definition, inspection_region=edit.region), target
        case EditorKind.EMPTY_MOUNT:
            return replace(definition, empty_mount_region=edit.region), target
        case EditorKind.EXCLUDED:
            if target.object_id is None:
                identity = ObjectId.new()
                item = ExcludedRegion(
                    identity, f"Excluded region {len(definition.excluded_regions) + 1}", edit.region
                )
                return replace(
                    definition, excluded_regions=(*definition.excluded_regions, item)
                ), EditorTarget(target.kind, identity)
            if not any(item.object_id == target.object_id for item in definition.excluded_regions):
                raise CalibrationValidationError("Excluded region no longer exists")
            return replace(
                definition,
                excluded_regions=tuple(
                    replace(item, region=edit.region)
                    if item.object_id == target.object_id
                    else item
                    for item in definition.excluded_regions
                ),
            ), target
        case EditorKind.LANDMARK:
            if target.object_id is None:
                identity = ObjectId.new()
                names = {item.name for item in definition.landmarks}
                index = len(names) + 1
                while f"Landmark {index}" in names:
                    index += 1
                landmark = Landmark(
                    identity,
                    f"Landmark {index}",
                    edit.region,
                    definition.tuning.matching.default_feature_threshold,
                    edit.role,
                    False,
                    False,
                    edit.support,
                    None,
                )
                return replace(
                    definition, landmarks=(*definition.landmarks, landmark)
                ), EditorTarget(target.kind, identity)
            if not any(item.object_id == target.object_id for item in definition.landmarks):
                raise CalibrationValidationError("Landmark no longer exists")
            return replace(
                definition,
                landmarks=tuple(
                    replace(item, region=edit.region)
                    if item.object_id == target.object_id
                    else item
                    for item in definition.landmarks
                ),
            ), target
    raise CalibrationValidationError("Unsupported editor target")


def remove_object(definition: CalibrationDefinition, target: EditorTarget) -> CalibrationDefinition:
    match target.kind:
        case EditorKind.INSPECTION:
            return replace(definition, inspection_region=None)
        case EditorKind.EMPTY_MOUNT:
            return replace(definition, empty_mount_region=None)
        case EditorKind.EXCLUDED:
            return replace(
                definition,
                excluded_regions=tuple(
                    item
                    for item in definition.excluded_regions
                    if item.object_id != target.object_id
                ),
            )
        case EditorKind.LANDMARK:
            return replace(
                definition,
                landmarks=tuple(
                    item for item in definition.landmarks if item.object_id != target.object_id
                ),
            )
    raise CalibrationValidationError("Unsupported editor target")


def replace_landmark(definition: CalibrationDefinition, updated: Landmark) -> CalibrationDefinition:
    if not any(item.object_id == updated.object_id for item in definition.landmarks):
        raise CalibrationValidationError("Landmark no longer exists")
    return replace(
        definition,
        landmarks=tuple(
            updated if item.object_id == updated.object_id else item
            for item in definition.landmarks
        ),
    )
