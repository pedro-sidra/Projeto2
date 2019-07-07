import cv2
import time
import pdb

cap = cv2.VideoCapture(0)
ret = False
#cap.set(cv2.CAP_PROP_FRAME_WIDTH ,1280);
#cap.set(cv2.CAP_PROP_FRAME_HEIGHT,720);
#time.sleep(2)
#cap = cv2.VideoCapture(0)

i = 0

while True:
    _, img = cap.read()
    img = cv2.resize(img,(1280,960))
    # imgflip = cv2.flip(img, 0)
    print(img.shape)
    cv2.imshow("ola", img)
    # cv2.imshow("ola2", imgflip)
    key = cv2.waitKey(10)
    print(key)
    if key == 27:
        break
    elif key == 115:  # 's':
        cv2.imwrite("screenshot " + str(i) + ".png", img)
        i = i + 1
