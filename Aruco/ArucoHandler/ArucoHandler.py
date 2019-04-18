"""This file contains the ArucoHandler class, which is responsible for interfacing OpenCV aruco methods."""

import cv2
from cv2 import aruco
import numpy as np
import xml.etree.ElementTree as ET

ID = 0
OUTPUT_MARKER = f'marker_{ID}.jpg'
RED = (0, 0, 255)
GREEN = (0, 255, 0)
SIDE_PIXELS = 100

class ArucoHandler(object):

    def __init__(self):

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

    def __showImage(self, title, img):

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
                print(f'p1: {pList[0]}')
                print(f'p2: {pList[1]}')
                print(f'p3: {pList[2]}')
                print(f'p4: {pList[3]}')

        except:
            print("Couldn't get 4 points from corners.")

        return pList

    def generateMarker(self, marker_id=ID, side_pixels=SIDE_PIXELS, output_file=OUTPUT_MARKER):

        image = cv2.imread(output_file)

        # To draw a marker, the following structure is used:
        # 1: dictionary
        # 2: id in the selected dictionary, in this case, ranges from 0 to 249
        # 3: size of the output image, in this case, 200x200 px
        # 4: output image
        # 5: border size
        img_with_marker = aruco.drawMarker(self.dictionary, marker_id, side_pixels, image, 1)

        if self.window_mode:
            self.__showImage('Marker', img_with_marker)

        cv2.imwrite(OUTPUT_MARKER, img_with_marker)

    def detectMarkersInImage(self, img, ids = ID):

        corners, ids, rejectedImgPoints = aruco.detectMarkers(img, self.dictionary, )

        if self.verbose_mode:
            print(f'polygon corners: {corners[0][0]}')
            print(f'ids[0]: {ids[0]}')
            print(f'rejectedImgPoints[0]: {rejectedImgPoints[0]}')

        if self.verbose_mode:
            self.__get4PointsFromCorners(corners)

        if self.window_mode:
            imgPoly = aruco.drawDetectedMarkers(img, corners, ids, GREEN)
            self.__showImage('Detected Marker', imgPoly)

        return [corners, ids, rejectedImgPoints]

    def estimateArucoAngles(self, corners, cameraMatrix, distCoeffs, markerLength=0.01, rvecs=None, tvecs=None, _objPoints=None):

        rvecs, tvecs, _objPoints = aruco.estimatePoseSingleMarkers(corners, markerLength, cameraMatrix, distCoeffs, rvecs, tvecs, _objPoints)

arc_handler = ArucoHandler()
# arc_handler.generateMarker()
arc_handler.detectMarkersInImage(cv2.imread("cloudsMarker.jpg"))
