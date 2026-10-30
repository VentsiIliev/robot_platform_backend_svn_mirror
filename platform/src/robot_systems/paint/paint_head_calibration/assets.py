"""Content-addressed reference images under an injected robot-system storage root."""

from hashlib import sha256
from pathlib import Path
from struct import unpack

from src.engine.core.durable_files import DurabilityError, atomic_write_bytes, sync_directory
from src.robot_systems.paint.contracts.paint_head_calibration.errors import (
    CalibrationFailure,
    CalibrationFailureCode,
    CalibrationPersistenceError,
    PaintHeadCalibrationError,
)
from src.robot_systems.paint.contracts.paint_head_calibration.interfaces import (
    IReferenceAssetRepository,
)
from src.robot_systems.paint.contracts.paint_head_calibration.models import (
    AssetId,
    ImageSize,
    ReferenceAsset,
)

_PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"


def _check_png(data: bytes, size: ImageSize) -> None:
    if (
        not isinstance(data, bytes)
        or len(data) < 33
        or not data.startswith(_PNG_SIGNATURE)
        or data[12:16] != b"IHDR"
        or unpack(">II", data[16:24]) != (size.width, size.height)
    ):
        raise PaintHeadCalibrationError(
            CalibrationFailure(
                CalibrationFailureCode.ASSET_INVALID, "Reference PNG dimensions/format are invalid"
            )
        )


class FileReferenceAssetRepository(IReferenceAssetRepository):
    def __init__(self, root: Path) -> None:
        self._root = root.resolve()

    def _path(self, identity: AssetId) -> Path:
        if not isinstance(identity, AssetId):
            raise PaintHeadCalibrationError(
                CalibrationFailure(
                    CalibrationFailureCode.ASSET_INVALID, "Reference identity is invalid"
                )
            )
        return self._root / f"{identity.value}.png"

    def put_png(self, data: bytes, size: ImageSize) -> ReferenceAsset:
        _check_png(data, size)
        identity = AssetId(sha256(data).hexdigest())
        destination = self._path(identity)
        try:
            if destination.is_symlink():
                raise ValueError("Refusing to use a reference-image symlink")
            if destination.exists():
                if destination.read_bytes() != data:
                    raise ValueError("Stored reference content does not match its identity")
            else:
                atomic_write_bytes(destination, data)
        except (OSError, ValueError) as error:
            raise CalibrationPersistenceError(
                CalibrationFailure(
                    CalibrationFailureCode.STORAGE_SAVE_FAILED,
                    str(error),
                    published=isinstance(error, DurabilityError),
                )
            ) from error
        return ReferenceAsset(identity, size)

    def read_png(self, asset: ReferenceAsset) -> bytes:
        source = self._path(asset.asset_id)
        try:
            if source.is_symlink():
                raise ValueError("Refusing to read a reference-image symlink")
            data = source.read_bytes()
        except FileNotFoundError as error:
            raise CalibrationPersistenceError(
                CalibrationFailure(
                    CalibrationFailureCode.ASSET_NOT_FOUND, "Reference image is missing"
                )
            ) from error
        except (OSError, ValueError) as error:
            raise CalibrationPersistenceError(
                CalibrationFailure(CalibrationFailureCode.STORAGE_LOAD_FAILED, str(error))
            ) from error
        if sha256(data).hexdigest() != asset.asset_id.value:
            raise PaintHeadCalibrationError(
                CalibrationFailure(
                    CalibrationFailureCode.ASSET_INVALID, "Reference image checksum differs"
                )
            )
        _check_png(data, asset.size)
        return data

    def delete(self, identity: AssetId) -> None:
        try:
            self._path(identity).unlink(missing_ok=True)
            if self._root.is_dir():
                sync_directory(self._root)
        except OSError as error:
            raise CalibrationPersistenceError(
                CalibrationFailure(
                    CalibrationFailureCode.ASSET_CLEANUP_FAILED, str(error), published=True
                )
            ) from error
