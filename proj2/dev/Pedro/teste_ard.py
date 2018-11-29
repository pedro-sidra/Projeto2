import serial
import time

ser = serial.Serial('COM6')
time.sleep(3)

ser.write(b'r')
ser.write(b'd')
ser.write(b'k')
time.sleep(1)

print(serial)
