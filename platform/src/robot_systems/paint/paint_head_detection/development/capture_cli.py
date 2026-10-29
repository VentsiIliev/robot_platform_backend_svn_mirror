"""Thin CLI for the reusable development capture runner."""

import json
import sys

import cv2

from ..errors import PaintHeadError
from .capture_application import CaptureApplication
from .options import parse_options


def main(argv: list[str] | None = None) -> int:
    try:
        options = parse_options(argv, capture_mode=True)
        cv2.setNumThreads(options.development.runtime.opencv_threads)
        app = CaptureApplication(options)
        if options.benchmark:
            result = app.benchmark()
            print(
                json.dumps(
                    {
                        "processing_fps": result.processing_fps,
                        "milliseconds_per_frame": result.milliseconds_per_frame,
                        "frames": result.frames,
                        "opencv_threads": cv2.getNumThreads(),
                    }
                )
            )
        else:
            app.run()
        return 0
    except PaintHeadError as error:
        print(f"{error.reason.value}: {error.message}", file=sys.stderr)
        return 2
    except KeyboardInterrupt:
        return 130
