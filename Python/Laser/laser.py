import cv2
import json
import numpy as np

from SLCalculator import SLCalculator

REF_PHOTO = "/home/estudos/Pictures/Projeto2/TesteLaser/ref.jpg"
PIECE_PHOTO = "/home/estudos/Pictures/Projeto2/TesteLaser/inclinadoBorr.jpg"
PARAMS = "params.json"

PIXELS_PER_CM = 32 # GAMBI


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


def nothing(x):
    pass


def get_mask(im, calib=True):
    im_HSV = cv2.cvtColor(im, cv2.COLOR_BGR2HSV)

    # return cv2.threshold(cv2.cvtColor(im,cv2.COLOR_BGR2GRAY), 0, 255,
    #                      cv2.THRESH_OTSU | cv2.THRESH_BINARY)[1]

    if not calib:
        LASER_LOWER = np.array(
            [params_init['lowH'], params_init['lowS'], params_init['lowV']])
        LASER_UPPER = np.array(
            [params_init['highH'], params_init['highS'], params_init['highV']])
        mask = cv2.inRange(im_HSV, LASER_LOWER, LASER_UPPER)
        mask = morphCloseThenOpen(mask)
        return mask

    cv2.namedWindow("Mask")
    for paramName, value in params.items():
        cv2.createTrackbar(paramName, 'Mask',
                           params_init[paramName], value, nothing)

    k = ''
    while k != ord('q'):
        k = cv2.waitKey(5)

        for key, value in params.items():
            params[key] = cv2.getTrackbarPos(key, 'Mask')

        LASER_LOWER = np.array(
            [params['lowH'], params['lowS'], params['lowV']])
        LASER_UPPER = np.array(
            [params['highH'], params['highS'], params['highV']])

        mask = cv2.inRange(im_HSV, LASER_LOWER, LASER_UPPER)
        mask = morphCloseThenOpen(mask)

        cv2.namedWindow("Pic", cv2.WINDOW_NORMAL)
        cv2.imshow("Pic", mask)

    with open(PARAMS, 'w')as f:
        f.write(json.dumps(params))
    return mask


def get_ref_points(mask):

    y, x = np.nonzero(mask)

    points = np.vstack((x, y)).swapaxes(0, 1)

    (mean,), eig = cv2.PCACompute(points.astype('float32'), mean=None)

    v1, v2 = eig
    dx, dy = v1

    a = dy/dx
    b = mean[1] - a*mean[0]

    def f(x): return a*x+b

    x1 = np.min(x)
    x2 = np.max(x)
    px = np.linspace(x1, x2, 100)
    py = f(px)

    points = np.array((px, py))

    return points.T.astype(np.int32), eig


im = cv2.imread(REF_PHOTO)
mask = get_mask(im, calib=True)
SL = SLCalculator(refMask=mask, ppcm = PIXELS_PER_CM)
SL.draw_refLine(im)

cv2.imshow("Rolou?", im)
cv2.waitKey(-1)


# im = cv2.imread(PIECE_PHOTO)
# mask_piece = get_mask(im, calib=True)


# contours, _ = cv2.findContours(mask_piece, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
# cv2.drawContours(im, contours, -1, (0, 0, 0), 6)


# k = ''
# cv2.namedWindow("result")
# cv2.waitKey()
# while k != ord('q'):
#     cv2.imshow("result", im)
#     k = cv2.waitKey(10)

# y,x = np.nonzero(mask_piece)
# piece_points = np.vstack((x, y))
# piece_points = piece_points.swapaxes(0, 1)

# ds = np.zeros(mask_points.shape[0])
# for i, point in enumerate(mask_points):
#     dists = np.abs(np.dot(piece_points-point, vperp)/np.linalg.norm(piece_points-point,axis=-1))
#     dists = np.nan_to_num(dists)

#     if np.isclose(np.max(dists),1):
#         idx = np.argmax(dists)
#         ds[i] = np.linalg.norm(piece_points[idx] - point)
#     else:
#         ds[i]=0

# import matplotlib.pyplot as plt
# plt.plot(17.9/36*ds/PIXELS_PER_CM)
# plt.show()
