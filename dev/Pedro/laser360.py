import cv2
import json
import glob
import numpy as np

REF_PHOTO = "./FOTOS ENSAIO/refgambi.jpg"
PIECE_PHOTO = "./FOTOS ENSAIO/pic241.65.png"
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

    "2highH": 180,
    "2lowH": 180,
    "2lowS": 255,
    "2highS": 255,
    "2lowV": 255,
    "2highV": 255,

    "highH": 180,
    "lowH": 180,
    "lowS": 255,
    "highS": 255,
    "lowV": 255,
    "highV": 255,

}


def nothing(x):
    pass


def get_mask(im, calib=True, roi=False):
    im_HSV = cv2.cvtColor(im, cv2.COLOR_BGR2HSV)

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

        LASER_LOWER2 = np.array(
            [params['2lowH'], params['2lowS'], params['2lowV']])
        LASER_UPPER2 = np.array(
            [params['2highH'], params['2highS'], params['2highV']])

        # mask = cv2.inRange(im_HSV, LASER_LOWER, LASER_UPPER)
        # mask2 = cv2.inRange(im_HSV, LASER_LOWER2, LASER_UPPER2)
        # mask = cv2.bitwise_or(mask,mask2)
        # mask= cv2.adaptiveThreshold(cv2.cvtColor(im,cv2.COLOR_BGR2GRAY), 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 1+2*params['2highH'], -50+params['2lowH'])
        ret,mask = cv2.threshold(cv2.cvtColor(im,cv2.COLOR_BGR2GRAY), 0, 255, cv2.THRESH_TRIANGLE | cv2.THRESH_BINARY)

        if roi:
            gambiarra = np.zeros_like(mask)
            gambiarra[180:475,180:500]=1
            mask = mask*gambiarra

        mask = morphCloseThenOpen(mask)

        cv2.namedWindow("Pic", cv2.WINDOW_NORMAL)
        cv2.imshow("Pic", mask)

    with open(PARAMS, 'w')as f:
        f.write(json.dumps(params))
    return mask


def get_ref_points(mask):

    width, height = mask.shape

    y, x = np.nonzero(mask)

    points = np.vstack((x, y))
    points = points.swapaxes(0, 1)

    (mean,), eig = cv2.PCACompute(points.astype('float32'), mean=None)

    v1, v2 = eig
    dx, dy = v1

    a = dy/dx
    b = mean[1] - a*mean[0]

    def f(x): return a*x+b
    def f_inv(y): return y/a - b/a

    x1 = np.min(x)
    x2 = np.max(x)
    px = np.linspace(x1, x2, 100)
    py = f(px)

    points = np.array((px, py))

    return points.T.astype(np.int32), eig


im = cv2.imread(REF_PHOTO)
mask = get_mask(im, calib=True)
# ret,mask = cv2.threshold(cv2.cvtColor(im,cv2.COLOR_BGR2GRAY), 0, 255, cv2.THRESH_OTSU | cv2.THRESH_BINARY)
mask_points, eig = get_ref_points(mask)

vperp =eig[1]

for PIECE_PHOTO in glob.glob("./FOTOS ENSAIO/pic*.png"):
    im = cv2.imread(PIECE_PHOTO)
    mask_piece = get_mask(im, calib=True, roi=True)
    # mask_piece = cv2.adaptiveThreshold(cv2.cvtColor(im,cv2.COLOR_BGR2GRAY), 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 55, 10)
    gambiarra = np.zeros_like(mask_piece)
    gambiarra[180:475,180:500]=1
    mask_piece = mask_piece*gambiarra

    cv2.line(im, (int(mask_points[0, 0]), int(mask_points[0, 1])), (int(
        mask_points[-1, 0]), int(mask_points[-1, 1])), (0, 0, 255), 8)

    contours, _ = cv2.findContours(mask_piece, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    cv2.drawContours(im, contours, -1, (0, 0, 0), 6)


    k = ''
    cv2.namedWindow("result")
    cv2.waitKey()
    while k != ord('q'):
        cv2.imshow("result", im)
        k = cv2.waitKey(10)

    y,x = np.nonzero(mask_piece)
    piece_points = np.vstack((x, y))
    piece_points = piece_points.swapaxes(0, 1)

    ds = np.zeros(mask_points.shape[0])
    for i, point in enumerate(mask_points):
        dists = np.abs(np.dot(piece_points-point, vperp)/np.linalg.norm(piece_points-point,axis=-1))
        dists = np.nan_to_num(dists)

        if np.isclose(np.max(dists),1):
            idx = np.argmax(dists)
            ds[i] = np.linalg.norm(piece_points[idx] - point)
        else:
            ds[i]=0

    import matplotlib.pyplot as plt
    plt.plot(17.9/36*ds/PIXELS_PER_CM)
    plt.show()
