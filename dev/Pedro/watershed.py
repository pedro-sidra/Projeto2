import sys
sys.path.append("../..")
import argparse
import numpy as np
import cv2

def parseArgs():
    # Parse arguments
    ap = argparse.ArgumentParser()
    ap.add_argument("-i", "--image", required=True, 
                    help="Image to apply hatershed on")
    args = vars(ap.parse_args())
    return args

def main():
    args = parseArgs()

    img = cv2.imread(args["image"])
    shifted = cv2.pyrMeanShiftFiltering(img, 21, 51)
    cv2.imshow("Input", img)

    # convert the mean shift image to grayscale, then apply
    # Otsu's thresholding
    gray = cv2.cvtColor(shifted, cv2.COLOR_BGR2GRAY)
    thresh = cv2.threshold(gray, 0, 255,
        cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
    cv2.imshow("Thresh", thresh)

    # noise removal
    kernel = np.ones((3,3),np.uint8)
    opening = cv2.morphologyEx(thresh,cv2.MORPH_OPEN,kernel, iterations = 3)

    # sure background area
    sure_bg = cv2.dilate(opening,kernel,iterations=1)

    # Finding sure foreground area
    dist_transform = cv2.distanceTransform(opening,cv2.DIST_L2,3)
    ret, sure_fg = cv2.threshold(dist_transform,0.8*dist_transform.max(),255,0)

    # Finding unknown region
    sure_fg = np.uint8(sure_fg)
    unknown = cv2.subtract(sure_bg,sure_fg)

    # Marker labelling
    ret, markers = cv2.connectedComponents(sure_fg)

    # Add one to all labels so that sure background is not 0, but 1
    markers = markers+1

    # Now, mark the region of unknown with zero
    markers[unknown==255] = 0

    markers = cv2.watershed(img,markers)
    img[markers == -1] = [255,0,0]

    cv2.imshow("result", img)
    cv2.imshow("markers", markers)

    cv2.waitKey(0)



if __name__ == "__main__":
    main()
