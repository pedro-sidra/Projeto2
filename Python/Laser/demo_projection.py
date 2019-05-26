import cv2
import argparse
import json
import numpy as np

from SLCalculator import SLCalculator

PARAMS = "params.json"


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

def parseArgs():
    # Parse arguments
    ap = argparse.ArgumentParser(description="Shows a demo of the projection into the line reference")
    ap.add_argument("picture", help="filepath of the picture to use")
    ap.add_argument("-s", "--show_picture", help="picture to show instead of the ref")
    ap.add_argument("--height", action="store_true", help="calculate and show height")
    ap.add_argument("--ppcm", type=int, help="Pixels per cm on the pictures",
                    default=32)
    return ap.parse_args()



if __name__=="__main__":
    args = parseArgs()

    im = cv2.imread(args.picture)
    mask = get_mask(im, calib=True)
    SL = SLCalculator(refMask=mask, ppcm = args.ppcm)

    if args.show_picture:
        im = cv2.imread(args.show_picture)

    SL.draw_refLine(im)
    imref = im.copy()

    pointa,pointb = 0,0
    k=0
    def click_and_crop(event, x, y, flags, param):
        global point, SL, im, args
        if event == cv2.EVENT_MOUSEMOVE:
            font = cv2.FONT_HERSHEY_SIMPLEX
            # Get the projection points
            perpline = SL.perpLine(x,y)
            pointa = np.array([0, int(perpline(0))])
            pointb= np.array([im.shape[1], int(perpline(im.shape[1]))])
            # pointa, pointb = SL.projectionVector(x,y)

            # Draw the projection line
            im = imref.copy()
            cv2.line(im, (*pointa.astype(np.int32),), (*pointb.astype(np.int32),),
                    (0,0,0), 5)

            cv2.circle(im, (x,y), 10, (0,0,255),2)

            # Calculate the values to print in cm
            dist = SL.dist_to_ref(x,y, signed=True)/args.ppcm

            dist = round(dist,2)
            xcm, ycm = x/args.ppcm, y/args.ppcm
            xcm, ycm = round(xcm,2), round(ycm,2)

            if args.height:
                height = round(17.9/36*dist,2)
                cv2.putText(im,f'height={height}cm',(x,y+25),
                            font, 1,(0,0,255),1,cv2.LINE_AA)

            # Write near the mouse pos
            cv2.putText(im,f'({xcm},{ycm})cm',(x,y),
                        font, 1,(0,0,255),1,cv2.LINE_AA)
            cv2.putText(im,f'dist={dist}cm',(x,y+50),
                        font, 1,(0,0,255),1,cv2.LINE_AA)


    cv2.namedWindow("Demo")
    cv2.setMouseCallback("Demo", click_and_crop)

    while k != ord('q'):
        cv2.imshow("Demo", im)
        k = cv2.waitKey(10)
