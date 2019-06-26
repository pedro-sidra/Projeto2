import numpy as np
import cv2 as cv
import glob
import argparse

def parseArgs():
    # Parse arguments
    ap = argparse.ArgumentParser() 
    ap.add_argument("images", nargs='+')
    ap.add_argument("--test_images", required=False,
                    default=None, nargs='+')
    return ap.parse_args()

def calib_cam(images, test = False):
    for fname in images:
        img = cv.imread(fname)
        gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)

        # Find the chess board corners
        ret, corners = cv.findChessboardCorners(gray, (7,7), None)

        # If found, add object points, image points (after refining them)
        if ret == True:

            objpoints.append(objp)
            corners2 = cv.cornerSubPix(gray,corners, (11,11), (-1,-1), criteria)
            imgpoints.append(corners)

            print("Found on " + fname)
            # Draw and display the corners
            cv.drawChessboardCorners(img, (7,7), corners2, ret)
            cv.imshow('img', img)
            cv.waitKey(100)

    ret, mtx, dist, rvecs, tvecs = cv.calibrateCamera(objpoints, imgpoints, gray.shape[::-1], None, None)
    if not test:
        print(f'\n{mtx}\n\n{dist}\n')
    cv.destroyAllWindows()

    mean_error = 0
    for i in range(len(objpoints)):
        imgpoints2, _ = cv.projectPoints(objpoints[i], rvecs[i], tvecs[i], mtx, dist)
        error = cv.norm(imgpoints[i], imgpoints2, cv.NORM_L2)/len(imgpoints2)
        mean_error += error
    if test:
        print( "Error on Test set: {}".format(mean_error/len(objpoints)) )
    else:
        print( "total error: {}".format(mean_error/len(objpoints)) )

    return mtx, dist

# termination criteria
criteria = (cv.TERM_CRITERIA_EPS + cv.TERM_CRITERIA_MAX_ITER, 30, 0.001)

# prepare object points, like (0,0,0), (1,0,0), (2,0,0) ....,(6,5,0)
objp = np.zeros((7*7,3), np.float32)
objp[:,:2] = 25*np.mgrid[0:7,0:7].T.reshape(-1,2)

# Arrays to store object points and image points from all the images.
objpoints = [] # 3d point in real world space
imgpoints = [] # 2d points in image plane.

args = parseArgs()

mtx, dist = calib_cam(args.images)
np.savez("camera_params.npz", mtx = mtx, dist = dist)

if args.test_images:
    mtx, dist = calib_cam(args.test_images, test = True)
