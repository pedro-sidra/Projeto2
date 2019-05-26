from proj2.GCodeGenerator import GCodeGenerator
from proj2.dev.Hanel.shapedetect_gambiarrento import *
import numpy as np
import cv2
def nothing(x):
    pass

def getAngle(contour):
    rect = cv2.minAreaRect(contour)
    #print(rect[2])
    dim1=rect[1][0]
    dim2=rect[1][1]
    if(dim1>dim2):
        angle = -rect[2]
    else:
        angle = 90-rect[2]

    if angle >=90 and angle <180:
        angle = angle - 90
    elif angle >=180:
        angle -= 180
    angle = abs(angle)

    print (angle)

    return angle

def rotateImage(image, angle):
  image_center = (180, 151)
  rot_mat = cv2.getRotationMatrix2D(image_center, angle, 1.0)
  result = cv2.warpAffine(image, rot_mat, image.shape[1::-1], flags=cv2.INTER_LINEAR)
  return result

while(True):
    cv2.namedWindow('image')
    cv2.createTrackbar('Rotation','image',0,360,nothing)


    image= cv2.imread('/home/hanel/Projeto2/dev/Hanel/img_small_crop.jpeg',cv2.IMREAD_COLOR)

    rotation = cv2.getTrackbarPos('Rotation','image')
    

    piece = callibAndGetPiece(image, {"type": "hsv", "block": 3})

    angle = getAngle(piece)

    font                   = cv2.FONT_HERSHEY_SIMPLEX
    bottomLeftCornerOfText = (10,50)
    fontScale              = 1
    fontColor              = (255,255,255)
    lineType               = 2
    image = rotateImage(image, rotation)
    text = "Angle: {:2f}".format(angle)
    cv2.putText(image,text, 
        bottomLeftCornerOfText, 
        font, 
        fontScale,
        fontColor,
        lineType)

    cv2.imshow('image',image)
    key = cv2.waitKey(1) & 0xFF
    if key == 27:
        break

