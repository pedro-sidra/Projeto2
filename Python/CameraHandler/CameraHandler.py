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

    def setResolution(self, res):
        width, height = res
        self.videoCapture.set(cv2.CAP_PROP_FRAME_WIDTH ,width);
        self.videoCapture.set(cv2.CAP_PROP_FRAME_HEIGHT,height);

    def stopTakingPictures(self):

        # Close device
        self.videoCapture.release()
        self.videoCapture = None


class CameraHandlerFromFile(CameraHandler):
    def __init__(self, file, device=0):
        """Defines a specific camera from a .npz file containing camera coefs."""

        super().__init__()

        contents = np.load(file)
        self.cameraMatrix = contents['mtx']
        self.distCoeff = contents['dist']

        self.device = device

        img = self.takePicture()

        self.setResolution((1280, 960))

        img = self.takePicture()

        h,  w = img.shape[:2]
        self.optCameraMtx, self.roi = cv2.getOptimalNewCameraMatrix(
            self.cameraMatrix, self.distCoeff,
            (w, h), 0, (w, h))

    def getMatrix(self):
        return self.optCameraMtx

    def read(self):
        image = self.takePicture()

        ret = cv2.undistort(image,
                           self.cameraMatrix,
                           self.distCoeff, None,
                           self.optCameraMtx,
                           )
        # crop the image
        x, y, w, h = self.roi
        ret = ret[y:y+h, x:x+w]
        return ret


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
