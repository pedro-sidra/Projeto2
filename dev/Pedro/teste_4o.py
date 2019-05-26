import serial
import time
import cv2

def read_ser():
    return "".join(com.readline().decode(encoding='utf-8').split())

def save_picture(frame, angle):
    cv2.imwrite("pic"+angle+".png",frame)


x = cv2.VideoCapture(1)
com = serial.Serial("/dev/ttyACM0", 9600)

time.sleep(1)
com.write(b'b')

while True:
    com.write(b'b')
    c = read_ser()

    ret, frame = x.read()

    print(c)
    if c=='p':
        angle = read_ser()
        save_picture(frame, angle)
