"""This file contains the ArucoHandler class, which is responsible for interfacing OpenCV aruco methods."""

import cv2
from cv2 import aruco
import numpy as np
import xml.etree.ElementTree as ET
from CameraHandler import *

ID = 0
OUTPUT_MARKER = f'marker_{ID}.jpg'
RED = (0, 0, 255)
GREEN = (0, 255, 0)
SIDE_PIXELS = 100

class ArucoHandler(object):

    def __init__(self):
        """Defines an ArucoHandler instance, responsible for getting aruco corners and pose from images."""

        window_mode = True
        verbose_mode = True

        # Loads configuration
        tree = ET.parse('config.xml')
        root = tree.getroot()

        for config in root.iter('window'):
            window_mode = window_mode and bool(int(config.attrib['status']))
        for config in root.iter('verbose'):
            verbose_mode = verbose_mode and bool(int(config.attrib['status']))

        self.window_mode = window_mode
        self.verbose_mode = verbose_mode

        # The predefined dictionary contains the following structure:
        # 1: AXA means AxA bits
        # 2: _250 means the dictionary is composed of 250 markers
        self.dictionary = aruco.getPredefinedDictionary(aruco.DICT_6X6_50)

    def _showImage(self, title, img):
        """Shows images, so while testing it's possible to see the result."""

        if self.window_mode:

            cv2.imshow(title, img)
            cv2.waitKey(0)
            cv2.destroyAllWindows()

    def __get4PointsFromCorners(self, corners):

        pList = []

        try:

            polygon = corners[0][0]
            for p in polygon:
                pList.append((p[0], p[1]))

            if self.verbose_mode:
                print(f'\np1: {pList[0]}')
                print(f'p2: {pList[1]}')
                print(f'p3: {pList[2]}')
                print(f'p4: {pList[3]}')

        except:
            print("Couldn't get 4 points from corners.")

        return pList

    def generateMarker(self, marker_id=ID, side_pixels=SIDE_PIXELS, output_file=OUTPUT_MARKER):
        """Generate image with marker."""

        image = cv2.imread(output_file)

        # To draw a marker, the following structure is used:
        # 1: dictionary
        # 2: id in the selected dictionary, in this case, ranges from 0 to 249
        # 3: size of the output image, in this case, 200x200 px
        # 4: output image
        # 5: border size
        img_with_marker = aruco.drawMarker(self.dictionary, marker_id, side_pixels, image, 1)

        if self.window_mode:
            self._showImage('Marker', img_with_marker)

        cv2.imwrite(OUTPUT_MARKER, img_with_marker)

    def detectMarkersInImage(self, img, ids = ID):

        corners, ids, rejectedImgPoints = aruco.detectMarkers(img, self.dictionary, ids=ids)

        if self.verbose_mode:

            print(f'\n--- Detecting Markers in Image ---')
            try:
                print(f'Polygon corners: {corners[0][0]}')
            except:
                print(f'\nNo corner found.\n')
            try:
                print(f'Ids[0]: {ids[0]}')
            except:
                print(f'\nNo id found.\n')
            try:
                print(f'RejectedImgPoints[0]: {rejectedImgPoints[0]}')
            except:
                print(f'\nNo point rejected.\n')

        if self.verbose_mode:
            self.__get4PointsFromCorners(corners)

        if self.window_mode:
            imgPoly = aruco.drawDetectedMarkers(img, corners, ids, GREEN)
            self._showImage('Detected Marker', imgPoly)

        return [corners, ids, rejectedImgPoints]

    def estimateArucoPose(self, img, corners, camera: CameraHandler, markerLength=0.01):
        """
        Returns rotation and translation vectors as well as position of aruco markers.

        :param img: image to draw.
        :param corners: vector of marker corners returned by the 'detectMarkersInImage' function
        :param cameraMatrix: camera matrix obtained after calibration using cv::calibrateCamera
        :param distCoeffs: camera distortion coefficients after calibration using cv::calibrateCamera
        :param markerLength: size of length of marker in a distance unit (meters, for instance). Output vectors will be in the same unit.

        """

        # rvecs: rotation vectors for each marker in 'corners'.
        rvecs = None
        # tvecs: translation vectors for each marker in 'corners'.
        tvecs = None

        cameraMatrix, distCoeffs = camera.getCalibrationData()

        rvecs, tvecs, _objPoints = aruco.estimatePoseSingleMarkers(corners, markerLength,     # Marker information
                                                                   cameraMatrix, distCoeffs,  # Camera information
                                                                   rvecs, tvecs)              # R&T Vectors

        imgWithAxes = aruco.drawAxis(img, cameraMatrix, distCoeffs, rvecs, tvecs, 2*markerLength)
        self._showImage('Image with Axes', imgWithAxes)
        cv2.waitKey(0)

        if self.verbose_mode:

            print(f'\n--- Estimating Pose in Image ---')
            print(f'rvecs: {rvecs}')
            print(f'tvecs: {tvecs}')
            print(f'_objPoints: {_objPoints}')

        return [rvecs, tvecs, _objPoints]

