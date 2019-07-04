import cv2
import argparse
import json
import numpy as np

from SLCalculator import SLCalculator

REF_PHOTO = "/home/estudos/Pictures/Projeto2/TesteLaser/ref.jpg"
PIECE_PHOTO = "/home/estudos/Pictures/Projeto2/TesteLaser/inclinadoBorr.jpg"
PARAMS = "params.json"

PIXELS_PER_CM = 32  # GAMBI


def parseArgs():
    # Parse arguments
    ap = argparse.ArgumentParser(description="Shows the results for one image")
    ap.add_argument("reference", help="filepath of the ref. picture to use",
                    )
    ap.add_argument("piece", help="filepath of the picture to run calculations on",
                    )
    ap.add_argument("--ppcm", type=int, help="Pixels per cm on the pictures",
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
    for i in range(w,v.shape[0]-w):
        block = v[i-w:i+w+1]
        m = np.mean(block,dtype=np.float32)
        v[i] = m
    return v

if __name__=="__main__":
    args = parseArgs()

    ref_im = cv2.imread(args.reference)
    mask = get_mask(ref_im, calib=False)
    SL = SLCalculator(refMask=mask, ppcm=PIXELS_PER_CM,
                      tanLaserAngle=17.9/36)
    SL.draw_refLine(ref_im)

    k = 0

    cv2.imshow("Rolou?", ref_im)
    cv2.waitKey(-1)

    piece_im = cv2.imread(args.piece)
    piece_mask = get_mask(piece_im, calib=False)
    contours, _ = cv2.findContours(piece_mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    cv2.drawContours(piece_im, contours, -1, (0, 0, 0), 6)

    cv2.imshow("Rolou?", piece_im)
    cv2.waitKey(-1)

    x, heights = SL.calc_heights(piece_mask, filter=False)

    ypic, xpic = np.nonzero(piece_mask)
    for xim, yim, height in zip(xpic, ypic, heights):
        piece_im[yim,xim] = (0,0,abs(int(255*height/max(heights))))
        # return 17.9/36*ds/self.ppcm

    import matplotlib.pyplot as plt

    cv2.imshow("Rolou?", piece_im)
    cv2.waitKey(-1)


    plt.plot(x,heights, 'bo')
    plt.show()
    print(x.shape)
