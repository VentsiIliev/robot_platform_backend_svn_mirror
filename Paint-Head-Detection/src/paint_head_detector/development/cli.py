"""Executable development entry point, separate from the image API."""

import sys

import cv2

from ..errors import PaintHeadError
from .application import DetectorDevelopmentApplication
from .options import parse_options


def main(argv: list[str] | None = None) -> int:
    try:
        options = parse_options(argv)
        cv2.setNumThreads(options.development.runtime.opencv_threads)
        DetectorDevelopmentApplication(options).run()
        return 0
    except PaintHeadError as error:
        print(f"{error.reason.value}: {error.message}", file=sys.stderr)
        return 2
    except KeyboardInterrupt:
        return 130
