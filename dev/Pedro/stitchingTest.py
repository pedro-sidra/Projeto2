import cv2
import numpy as np

img1 = cv2.imread('..\..\screenshot 0.png')
img2 = cv2.imread('..\..\screenshot 1.png')
img3 = cv2.imread('..\..\screenshot 2.png')
img4 = cv2.imread('..\..\screenshot 3.png')

img1R = cv2.resize(img1, (640, 360))
img2R = cv2.resize(img2, (640, 360))
img3R = cv2.resize(img3, (640, 360))
img4R = cv2.resize(img4, (640, 360))

stitcher = cv2.createStitcher(False)
arr = [img1R, img2R, img3R]
result = stitcher.stitch(arr)

print(result)
resultGambiarra = np.concatenate(arr, axis=0)

cv2.imshow("gambi", resultGambiarra)

cv2.waitKey()

cv2.imshow("img1", result[1])
cv2.imshow("img1 orig", img1)

cv2.waitKey()
