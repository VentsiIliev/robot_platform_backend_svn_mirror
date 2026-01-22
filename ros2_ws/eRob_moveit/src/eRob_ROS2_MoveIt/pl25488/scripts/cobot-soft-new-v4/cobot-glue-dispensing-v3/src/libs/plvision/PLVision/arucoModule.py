"""
* File: arucoModule.py
* Author: IlV
* Comments:
* Revision history:
* Date       Author      Description
* -----------------------------------------------------------------
** 140524     IlV         Initial release
* -----------------------------------------------------------------
"""
# TODO update the module in PLVision to use the new ArucoDetector shared
import cv2
from enum import Enum
print(cv2.__version__)

class ArucoDictionary(Enum):
    """
    Enumeration for available ArUco dictionaries in OpenCV.
    """
    DICT_4X4_50 = cv2.aruco.DICT_4X4_50
    DICT_4X4_100 = cv2.aruco.DICT_4X4_100
    DICT_4X4_250 = cv2.aruco.DICT_4X4_250
    DICT_4X4_1000 = cv2.aruco.DICT_4X4_1000
    DICT_5X5_50 = cv2.aruco.DICT_5X5_50
    DICT_5X5_100 = cv2.aruco.DICT_5X5_100
    DICT_5X5_250 = cv2.aruco.DICT_5X5_250
    DICT_5X5_1000 = cv2.aruco.DICT_5X5_1000
    DICT_6X6_50 = cv2.aruco.DICT_6X6_50
    DICT_6X6_100 = cv2.aruco.DICT_6X6_100
    DICT_6X6_250 = cv2.aruco.DICT_6X6_250
    DICT_6X6_1000 = cv2.aruco.DICT_6X6_1000
    DICT_7X7_50 = cv2.aruco.DICT_7X7_50
    DICT_7X7_100 = cv2.aruco.DICT_7X7_100
    DICT_7X7_250 = cv2.aruco.DICT_7X7_250
    DICT_7X7_1000 = cv2.aruco.DICT_7X7_1000

class ArucoDetector:
    """
    Detects ArUco markers in images using OpenCV 4.11+ ArucoDetector shared.
    """
    def __init__(self, arucoDict=ArucoDictionary.DICT_6X6_250):
        self.arucoDict = cv2.aruco.getPredefinedDictionary(arucoDict.value)
        self.parameters = cv2.aruco.DetectorParameters()

        # MAXIMUM RELAXED PARAMETERS - for extremely easy detection
        self.parameters.adaptiveThreshWinSizeMin = 3
        self.parameters.adaptiveThreshWinSizeMax = 53  # Increased from 23
        self.parameters.adaptiveThreshWinSizeStep = 4   # Smaller step for more attempts
        self.parameters.adaptiveThreshConstant = 5      # Reduced from 7

        # Allow even smaller and larger markers
        self.parameters.minMarkerPerimeterRate = 0.005  # Reduced from 0.01
        self.parameters.maxMarkerPerimeterRate = 8.0    # Increased from 4.0

        # Very relaxed corner detection
        self.parameters.polygonalApproxAccuracyRate = 0.08   # Increased from 0.05
        self.parameters.minCornerDistanceRate = 0.005        # Reduced from 0.01
        self.parameters.minDistanceToBorder = 0              # Reduced from 1

        # Maximum error correction tolerance
        self.parameters.errorCorrectionRate = 0.8            # Increased from 0.6
        self.parameters.maxErroneousBitsInBorderRate = 0.5   # Increased from 0.35

        # Corner refinement for better accuracy
        self.parameters.cornerRefinementMethod = cv2.aruco.CORNER_REFINE_SUBPIX
        self.parameters.cornerRefinementWinSize = 5
        self.parameters.cornerRefinementMaxIterations = 50   # Increased from 30
        self.parameters.cornerRefinementMinAccuracy = 0.005  # Reduced from 0.01

        # Additional parameters for difficult detection scenarios
        self.parameters.minMarkerDistanceRate = 0.01  # Allow very close markers
        self.parameters.perspectiveRemoveIgnoredMarginPerCell = 0.1

        self.detector = cv2.aruco.ArucoDetector(self.arucoDict, self.parameters)

    def detectAll(self, image):
        """
        Detects all ArUco markers in the given image.
        """

        if image is None or image.size == 0:
            print("Error: Image is empty or not loaded correctly.")


        corners, ids, _ = self.detector.detectMarkers(image)
        return corners, ids if ids is not None else []

    def detectAreaCorners(self, image, arucoIds, maxAttempts=10):
        """
        Detects four specified ArUco markers in the image and returns their corners.
        """
        if len(arucoIds) != 4:
            print("Error: The number of ArUco markers must be 4.")
            return None, None

        found_markers = 0
        corners = [None, None, None, None]
        attempts = 0

        while attempts < maxAttempts and found_markers < 4:
            corners_detected, ids_detected, _ = self.detector.detectMarkers(image)

            if ids_detected is None:
                attempts += 1
                continue

            for bbox, marker_id in zip(corners_detected, ids_detected):
                if marker_id[0] in arucoIds:
                    found_markers += 1
                    index = arucoIds.index(marker_id[0])
                    corners[index] = bbox[0][0]
                    print(f"Marker {marker_id[0]} found")

            attempts += 1

        if None in corners:
            print("Not all specified markers detected.")
            return None, None

        return corners, arucoIds
