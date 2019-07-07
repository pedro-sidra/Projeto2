import cv2
import os
import matplotlib.pyplot as plt
import argparse
import json
import numpy as np

from PieceScanner import PieceScanner

REF_PHOTO = "/home/estudos/Pictures/Projeto2/TesteLaser/ref.jpg"
PIECE_PHOTO = "/home/estudos/Pictures/Projeto2/TesteLaser/inclinadoBorr.jpg"

# medida de um objeto na vida real e em uma imagem
PIXELS_PER_CM = 29

# tangente do angulo do laser com a superficie de ref.
TAN_LASER_ANGLE = 26.2/23


PLOT_EACH = False

def parseArgs():
    # Parse arguments
    ap = argparse.ArgumentParser(description="Shows the results for images")
    ap.add_argument("reference", help="filepath of the ref. picture to use",
                    )
    ap.add_argument("pieces", nargs='+',
                    help="filepath of the pictures to run calculations on",
                    )
    ap.add_argument("--ppcm", type=float, help="Pixels per cm on the pictures",
                    default=PIXELS_PER_CM)
    return ap.parse_args()


def morphCloseThenOpen(mask):
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
    return mask


with open(PARAMS, 'r') as f:
    params_init = json.loads(f.read())

with open("paramsLAB.json", 'r') as f:
    paramsLAB_init = json.loads(f.read())

params = {
    "highH": 180,
    "lowH": 180,
    "lowS": 255,
    "highS": 255,
    "lowV": 255,
    "highV": 255,
}

paramsLAB = {
    "lowL": 255,
    "highL": 255,
    "lowA": 255,
    "highA": 255,
    "lowB": 255,
    "highB": 255,
        }

def nothing(x):
    pass


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
    for paramName, value in paramsLAB.items():
        cv2.createTrackbar(paramName, 'Calibrate Mask',
                           paramsLAB_init[paramName], value, nothing)

    cv2.namedWindow("Pic", cv2.WINDOW_NORMAL)
    k = ''
    while k != ord('q'):
        k = cv2.waitKey(5)

        for key, value in paramsLAB.items():
            paramsLAB[key] = cv2.getTrackbarPos(key, 'Calibrate Mask')

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


def meanFilter(vec, w=2):
    v = vec
    for i in range(w, v.shape[0]-w):
        block = v[i-w:i+w+1]
        m = np.mean(block, dtype=np.float32)
        v[i] = m
    return v

#Opens a windows that allows the user to select a rectangular ROI
def selectRoi(im):
    r = cv2.selectROI(im,showCrosshair=False)    
    return r

#Filters out everyting out of the specified ROI
def applyRoi(im,r):
    blank = np.zeros(shape=im.shape, dtype=np.uint8) 
    imCrop = im[int(r[1]):int(r[1]+r[3]), int(r[0]):int(r[0]+r[2])]
    blank[int(r[1]):int(r[1]+r[3]), int(r[0]):int(r[0]+r[2])]=imCrop
    return blank


if __name__ == "__main__":
    args = parseArgs()

    ref_im = cv2.imread(args.reference)

    scanner = PieceScanner(ppcm=PIXELS_PER_CM,
                           tanLaserAngle=TAN_LASER_ANGLE,
                           axisCenter=(346, 7.5))
    scanner.init_reference(ref_im)
    scanner.show_reference()

    for piece in args.pieces:
        piece_im = cv2.imread(piece)

        angle = os.path.splitext(piece)[0].split("pic")[-1]
        angle = np.pi*float(angle)/180
        x, heights = scanner.add_view(piece_im, angle)

        if PLOT_EACH:
            fig, axs = plt.subplots(1, 2)
            axs[0].imshow(piece_im)
            axs[0].set_title(angle)
            axs[1].plot(x, heights, 'b+')
            plt.show()

    points = scanner.get_piece()
    plt.figure()
    plt.plot(*points, 'go')
    plt.show()

    angles = (np.arctan2(points[0, :], points[1, :]))

    samples = 720
    dtheta = 2*np.pi/samples

    xp, yp = points
    points_filter = np.empty(points.shape)

    for i, a in enumerate(np.linspace(-np.pi, np.pi, samples)):

        in_range = np.bitwise_and(angles>= a, angles < a+dtheta)
        size = in_range.nonzero()[0].size

        xf = xp[in_range].sum()/size
        yf = yp[in_range].sum()/size
        points_filter[:,i] = np.array([xf,yf])

    plt.figure()
    plt.plot(*points_filter, 'go')
    plt.show()

