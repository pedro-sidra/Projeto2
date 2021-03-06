import numpy as np 
import cv2

def nothing(x):
    pass

def getAngle(contour):
    rect = cv2.minAreaRect(cnt)
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

    return rect

def rotateImage(image, angle):
  image_center = tuple(np.array(image.shape[1::-1]) / 2)
  image_center = (180, 151)
  rot_mat = cv2.getRotationMatrix2D(image_center, angle, 1.0)
  result = cv2.warpAffine(image, rot_mat, image.shape[1::-1], flags=cv2.INTER_LINEAR)
  return result


cv2.namedWindow('image')
cv2.createTrackbar('Rotation','image',0,360,nothing)

while(1):
    image= cv2.imread('/home/hanel/Projeto2/dev/Hanel/rotation_crop.png',cv2.IMREAD_COLOR)
    k = cv2.waitKey(1) & 0xFF
    
    if k == 27:
        break

    rotation = cv2.getTrackbarPos('Rotation','image')
    image = rotateImage(image, rotation)

    img = cv2.cvtColor(image,cv2.COLOR_BGR2GRAY)
    ret,thresh = cv2.threshold(img,127,255,0)
    _ , contours, _ = cv2.findContours(thresh,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
    cnt = contours[0]

    getAngle(cnt)
    cv2.imshow('image',image)

cv2.destroyAllWindows()

