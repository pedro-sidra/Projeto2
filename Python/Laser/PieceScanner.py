import cv2
import numpy as np
import cv2
import matplotlib.pyplot as plt
import argparse
import json
import numpy as np

from SLCalculator import SLCalculator


PARAMS = "params.json"

REF_UPPER = np.array([88, 11, 255])
REF_LOWER = np.array([33, 0, 253])


def nothing(x):
    pass


def morphCloseThenOpen(mask):
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
    return mask


with open(PARAMS, 'r') as f:
    params_init = json.loads(f.read())

params = {
    "highH": 180,
    "lowH": 180,
    "lowS": 255,
    "highS": 255,
    "lowV": 255,
    "highV": 255,
}


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
    for paramName, value in params.items():
        cv2.createTrackbar(paramName, 'Calibrate Mask',
                           params_init[paramName], value, nothing)

    cv2.namedWindow("Pic", cv2.WINDOW_NORMAL)
    k = ''
    while k != ord('q'):
        k = cv2.waitKey(5)

        for key, value in params.items():
            params[key] = cv2.getTrackbarPos(key, 'Calibrate Mask')

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
    def __init__(self, ppcm, tanLaserAngle, axisCenter=(0, 0)):
        self.ppcm = ppcm
        self.axisCenter = axisCenter
        self.tanLaserAngle = tanLaserAngle

        self.views = []
        self.view_points = []
        self.angles = []

    def show_reference(self):
        cv2.imshow("ref", self.ref_im)
        cv2.waitKey(-1)

    def init_reference(self, ref_im):
        self.ref_im = ref_im
        mask = cv2.inRange(cv2.cvtColor(
            ref_im, cv2.COLOR_BGR2HSV), REF_LOWER, REF_UPPER)
        mask = morphCloseThenOpen(mask)

        self.SL = SLCalculator(refMask=mask, ppcm=self.ppcm,
                               tanLaserAngle=self.tanLaserAngle,
                               axisCenter=self.axisCenter)
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

            piece = np.concatenate((piece, points_rot), axis=-1)

        return piece

    def add_view(self, view_img, view_angle):

        view_mask = get_mask(view_img, calib=False)

        # gray = cv2.cvtColor(view_img, cv2.COLOR_BGR2GRAY)
        # view_mask = np.zeros(gray.shape)
        # locations = (slice(230, None, None), slice(213,468, None))
        # mask_partial = cv2.threshold(gray[locations], 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
        # view_mask[locations] = mask_partial

        gambi = np.zeros(view_mask.shape)
        gambi[230:, 213:468] = 1
        view_mask = view_mask * gambi

        x, heights = self.SL.calc_heights(view_mask,
                                          filter=True)

        points = np.bitwise_and(x>-5, x<5)
        x = x[points]
        heights = heights[points]
        self.views.append(view_img)
        self.view_points.append((x, heights))
        self.angles.append(view_angle)

        return x, heights
