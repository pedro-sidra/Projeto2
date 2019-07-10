import cv2
import numpy as np
from CameraHandler.CameraHandler import CameraHandlerFromFile
import pdb

CROSSHAIR_WIDTH=5
CROSSHAIR_COLOR=(255,0,0)

CAM_PARAMS_FILE = "../CameraHandler/camera_params.npz"
CAM_DEVICE = 0
HEIGHT, WIDTH = 960, 1280
cap = CameraHandlerFromFile(file=CAM_PARAMS_FILE,
                            device=CAM_DEVICE,
                            resize=(WIDTH,HEIGHT))
cap.setExposure(-6)

i = 0

x_mouse = 0
y_mouse = 0
def draw_crosshair(event, x, y, flags, param):
    global x_mouse, y_mouse
    if event == cv2.EVENT_MOUSEMOVE:
        x_mouse = x
        y_mouse = y


cv2.namedWindow("Webcam")
cv2.setMouseCallback("Webcam", draw_crosshair)

while True:
    _, img = cap.read()
    imgflip = cv2.flip(img, 0)
    cv2.line(imgflip, (x_mouse,0) , (x_mouse,HEIGHT),
             CROSSHAIR_COLOR, CROSSHAIR_WIDTH)
    cv2.line(imgflip, (0,y_mouse) , (WIDTH,y_mouse),
             CROSSHAIR_COLOR, CROSSHAIR_WIDTH)

    cv2.line(img, (x_mouse,0) , (x_mouse,HEIGHT),
             CROSSHAIR_COLOR, CROSSHAIR_WIDTH)
    cv2.line(img, (0,y_mouse) , (WIDTH,y_mouse),
             CROSSHAIR_COLOR, CROSSHAIR_WIDTH)
    cv2.imshow("Webcam", img)
    cv2.imshow("ola2", imgflip)
    key = cv2.waitKey(10)
    if key == 27:
        break
    elif key == 115:  # 's':
        cv2.imwrite("screenshot " + str(i) + ".png", img)
        i = i + 1

mtx = cap.getMatrix()
np.save("mtx.np", mtx)
