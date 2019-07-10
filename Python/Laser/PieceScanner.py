import cv2
import pdb
import numpy as np
import cv2
import matplotlib.pyplot as plt
import argparse
import json
import numpy as np
from skimage.morphology import skeletonize, thin

from SLCalculator import SLCalculator


PARAMS = "params.json"
PARAMS_LAB = "paramsLAB.json"

REF_UPPER = np.array([88, 11, 255])
REF_LOWER = np.array([33, 0, 253])
# REF_UPPER = np.array([89, 9, 255])
# REF_LOWER = np.array([37, 0, 207])


def nothing(x):
    pass


def morphCloseThenOpen(mask):
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))

    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)

    # mask = thin(1*(mask>0), max_iter=3)

    mask = cv2.morphologyEx(mask, cv2.MORPH_ERODE, kernel, iterations=1)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)

    return mask


with open(PARAMS_LAB, 'r') as f:
    paramsLAB_init = json.loads(f.read())

with open(PARAMS, 'r') as f:
    params_init = json.loads(f.read())

# params = {
#     "highH": 180,
#     "lowH": 180,
#     "lowS": 255,
#     "highS": 255,
#     "lowV": 255,
#     "highV": 255,
# }

params = {"highH": 180,
          "lowH": 180,
          "lowS": 255,
          "highS": 255,
          "lowV": 255,
          "highV": 255}

paramsLAB = {
    "lowL": 255,
    "highL": 255,
    "lowA": 255,
    "highA": 255,
    "lowB": 255,
    "highB": 255,
}


def get_mask_lab(im, calib=True):
    im_LAB = cv2.cvtColor(im, cv2.COLOR_BGR2LAB)
    if not calib:
        LASER_LOWER = np.array(
            [paramsLAB_init['lowL'], paramsLAB_init['lowA'], paramsLAB_init['lowB']])
        LASER_UPPER = np.array(
            [paramsLAB_init['highL'], paramsLAB_init['highA'], paramsLAB_init['highB']])
        mask = cv2.inRange(im_LAB, LASER_LOWER, LASER_UPPER)
        mask = morphCloseThenOpen(mask)
        return mask

    cv2.namedWindow("Calibrate Mask")
    cv2.namedWindow("Trackbar")
    for paramName, value in paramsLAB.items():
        cv2.createTrackbar(paramName, 'Trackbar',
                           paramsLAB_init[paramName], value, nothing)

    cv2.namedWindow("Pic", cv2.WINDOW_NORMAL)
    k = ''
    while k != ord('q'):
        k = cv2.waitKey(5)

        for key, value in paramsLAB.items():
            paramsLAB[key] = cv2.getTrackbarPos(key, 'Trackbar')

        LASER_LOWER = np.array(
            [paramsLAB['lowL'], paramsLAB['lowA'], paramsLAB['lowB']])
        LASER_UPPER = np.array(
            [paramsLAB['highL'], paramsLAB['highA'], paramsLAB['highB']])

        mask = cv2.inRange(im_LAB, LASER_LOWER, LASER_UPPER)
        mask = morphCloseThenOpen(mask)

        cv2.imshow("Pic", im)
        cv2.imshow("Calibrate Mask", mask)

    with open("paramsLAB.json", 'w')as f:
        f.write(json.dumps(paramsLAB))
    return mask


def get_mask(im, calib=True):
    im_HSV = cv2.cvtColor(im, cv2.COLOR_BGR2HSV)

    if not calib:
        LASER_LOWER = np.array(
            [params_init['lowH'], params_init['lowS'], params_init['lowV']])
        LASER_UPPER = np.array(
            [params_init['highH'], params_init['highS'], params_init['highV']])
        mask = cv2.inRange(im_HSV, LASER_LOWER, LASER_UPPER)
        mask = morphCloseThenOpen(mask)
        return mask

    cv2.namedWindow("Calibrate Mask")
    cv2.namedWindow("Trackbar")
    for paramName, value in params.items():
        cv2.createTrackbar(paramName, 'Trackbar',
                           params_init[paramName], value, nothing)

    cv2.namedWindow("Pic", cv2.WINDOW_NORMAL)
    k = ''
    while k != ord('q'):
        k = cv2.waitKey(5)

        for key, value in params.items():
            params[key] = cv2.getTrackbarPos(key, 'Trackbar')

        LASER_LOWER = np.array(
            [params['lowH'], params['lowS'], params['lowV']])
        LASER_UPPER = np.array(
            [params['highH'], params['highS'], params['highV']])

        mask = cv2.inRange(im_HSV, LASER_LOWER, LASER_UPPER)
        mask = morphCloseThenOpen(mask)

        cv2.imshow("Pic", im)
        cv2.imshow("Calibrate Mask", mask)

    with open(PARAMS, 'w')as f:
        f.write(json.dumps(params))
    return mask


class PieceScanner():
    def __init__(self, ppcm, tanLaserAngle, axisCenter=(0, 0), CM=None, ref_height=300):
        self.ppcm = ppcm
        self.axisCenter = axisCenter
        self.tanLaserAngle = tanLaserAngle
        self.ref_height = ref_height
        self.CM = CM

        self.views = []
        self.view_points = []
        self.angles = []

    def show_reference(self):
        cv2.imshow("ref", self.ref_im)
        cv2.waitKey(-1)

    def init_reference(self, ref_im):
        self.ref_im = ref_im
        # mask = cv2.inRange(cv2.cvtColor(
        mask = get_mask(ref_im, calib=True)
        # mask = cv2.inRange(cv2.cvtColor(
        #     ref_im, cv2.COLOR_BGR2HSV), REF_LOWER, REF_UPPER)
        mask = morphCloseThenOpen(mask)

        self.SL = SLCalculator(refMask=mask, ppcm=self.ppcm,
                               tanLaserAngle=self.tanLaserAngle,
                               axisCenter=self.axisCenter,
                               CM=self.CM,
                               ref_height=self.ref_height,
                              )
        self.SL.draw_refLine(self.ref_im)

    def get_piece(self):

        # first pic is the basepoint
        center_angle = self.angles[0]
        x, y = self.view_points[0]
        piece = np.array([x, y])

        for (x, y), theta in zip(self.view_points[1:],
                                 self.angles[1:]):

            points = np.array([x, y])

            dtheta = (theta-center_angle)
            c, s = np.cos(dtheta), np.sin(dtheta)
            R = np.array([[c, -s], [s, c]])

            points_rot = R@points
            # points_rot = points

            piece = np.concatenate((piece, points_rot), axis=-1)

        return piece

    def _applyRoi(self, im):
        """
        Filters out everyting out of the specified ROI
        """
        r = self.roi

        blank = np.zeros(shape=im.shape, dtype=np.uint8)
        imCrop = im[int(r[1]):int(r[1]+r[3]), int(r[0]):int(r[0]+r[2])]
        blank[int(r[1]):int(r[1]+r[3]), int(r[0]):int(r[0]+r[2])] = imCrop
        return blank

    def _selectRoi(self, im):
        """
        Opens a windows that allows the user to select a rectangular ROI
        """
        r = cv2.selectROI(im, showCrosshair=False)
        return r

    def get_roi(self, sample_img):
        self.roi = self._selectRoi(sample_img)

    def add_view(self, view_img, view_angle, return_mask=False):

        view_img = self._applyRoi(view_img)
        view_mask = get_mask(view_img, calib=True)

        # gray = cv2.cvtColor(view_img, cv2.COLOR_BGR2GRAY)
        # view_mask = np.zeros(gray.shape)
        # locations = (slice(230, None, None), slice(213,468, None))
        # mask_partial = cv2.threshold(gray[locations], 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
        # view_mask[locations] = mask_partial

        # gambi = np.zeros(view_mask.shape)
        # gambi[2*230:, 2*213:2*468] = 1
        # gambi = np.ones(view_mask.shape)
        # view_mask = view_mask * gambi

        x, heights = self.SL.calc_heights(view_mask,
                                          filter=False)

        # points = np.bitwise_and(x>-5, x<5)
        # x = x[points]
        # heights = heights[points]
        self.views.append(view_img)
        self.view_points.append((x, heights))
        self.angles.append(view_angle)

        if return_mask:
            return x, heights, view_mask
        else:
            return x, heights
