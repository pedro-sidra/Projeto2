import cv2
import numpy as np
from ..CameraHandler.CameraHandler import CameraHandlerFromFile
import pdb

pdb.set_trace()
cap = CameraHandlerFromFile(file="/home/estudos/code/Projeto2/Python/CameraHandler/camera_params.npz",
                            device=1)
i = 0

while True:
    _, img = cap.read()
    imgflip = cv2.flip(img, 0)
    print(img.shape)
    cv2.imshow("ola", img)
    cv2.imshow("ola2", imgflip)
    key = cv2.waitKey(10)
    print(key)
    if key == 27:
        break
    elif key == 115:  # 's':
        cv2.imwrite("screenshot " + str(i) + ".png", img)
        i = i + 1

mtx = cap.getMatrix()
np.save("mtx.np", mtx)
