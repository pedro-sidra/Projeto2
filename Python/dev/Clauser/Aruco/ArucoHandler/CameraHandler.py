"""This file contains the CameraHandler class, which is responsible for calibrating the used camera so Aruco
can be used."""
import numpy as np

class CameraHandler(object):

    def __init__(self):
        """Instantiates a generic camera with no predefined data regarding camera matrix or distortion coefficients."""

        self.cameraMatrix = None
        self.distCoeff = None

    def getCalibrationData(self) -> list:
        """Returns the calibration data of the camera: [cameraMatrix, distCoeff]
        :rtype: list
        """

        return [self.cameraMatrix, self.distCoeff]

class NotebookCamera(CameraHandler):

    def __init__(self):
        """Defines a specific camera. In this case, the camera from Cláuser's notebook used for testing."""

        super().__init__()

        self.cameraMatrix = np.matrix([[990.21397739, 0., 598.01706421],
                                       [0., 986.2634437, 299.09250586], [0., 0., 1.]])
        self.distCoeff = np.matrix([[-3.73900798e-02, -2.11866768e+00,
                                     -1.24858649e-02, 1.56129987e-03,
                                     1.01775216e+01]])


