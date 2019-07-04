# -*- coding: utf-8 -*-
import cv2
from laser import get_mask_lab,get_mask
import imutils
print('hai')
img = cv2.imread("C://Users//Mateus//Desktop//1.jpeg")
img = imutils.resize(img,height=300)
mask = get_mask(img, calib = True)
cv2.imshow('mask',mask)
cv2.waitKey()
cv2.destroyAllWindows()