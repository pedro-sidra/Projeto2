import cv2

cap = cv2.VideoCapture(1)
ret = cap.set(3,1280 );
ret = cap.set(4,720);

i=0

while True:
    _,img = cap.read()
    imgflip = cv2.flip(img,0)
    print(img.shape)
    cv2.imshow("ola",img)
    cv2.imshow("ola2",imgflip)
    key = cv2.waitKey(10)
    print(key)
    if key == 27:
        break
    elif key == 115: #'s':
        cv2.imwrite("screenshot " + str(i) + ".png", img)
        i=i+1

    