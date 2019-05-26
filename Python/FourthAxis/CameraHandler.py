"""This file contains the CameraHandler class, which is responsible for calibrating and using a camera."""
import numpy as np
import cv2

class CameraHandler(object):

    def __init__(self):
        """Instantiates a generic camera with no predefined data regarding camera matrix or distortion coefficients."""

        # Calibration data
        self.cameraMatrix = None
        self.distCoeff = None

        # Camera information
        self.device = 0
        self.videoCapture = None

    def getCalibrationData(self) -> list:
        """Returns the calibration data of the camera: [cameraMatrix, distCoeff]
        :rtype: list
        """

        return [self.cameraMatrix, self.distCoeff]

    def takePicture(self):
        """Takes a picture and returns its image."""

        if self.videoCapture is None:
            self.videoCapture = cv2.VideoCapture(self.device)

            # Check success in openning device
            if not self.videoCapture.isOpened():
                raise IOError("Couldn't open video device.")

        # Captures picture
        success, image = self.videoCapture.read()

        if not success:
            raise IOError("Couldn't take picture.")

        return image

    def stopTakingPictures(self):

        # Close device
        self.videoCapture.release()
        self.videoCapture = None

class NotebookCamera(CameraHandler):

    def __init__(self):
        """Defines a specific camera. In this case, the camera from Cláuser's notebook used for testing."""

        super().__init__()

        self.cameraMatrix = np.matrix([[990.21397739, 0., 598.01706421],
                                       [0., 986.2634437, 299.09250586], [0., 0., 1.]])
        self.distCoeff = np.matrix([[-3.73900798e-02, -2.11866768e+00,
                                     -1.24858649e-02, 1.56129987e-03,
                                     1.01775216e+01]])

        self.device = 0
