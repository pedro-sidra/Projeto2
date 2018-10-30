import cv2

cap = cv2.VideoCapture(1)
ret = cap.set(3,1280 );
ret = cap.set(4,720);


while True:
    _,img = cap.read()
    imgflip = cv2.flip(img,0)
    print(img.shape)
    cv2.imshow("ola",img)
    cv2.imshow("ola2",imgflip)
    key = cv2.waitKey(10)
    if key == 27:
        break

    