import time
import board
#import RPi.GPIO as GPIO
import digitalio
import busio
import adafruit_lis3dh

class Accelerometer():
    def __init__(self):
        self.i2c = busio.I2C(board.SCL, board.SDA)
        self.int1 = digitalio.DigitalInOut(board.D6)  # Set this to the correct pin for the interrupt!
        self.lis3dh = adafruit_lis3dh.LIS3DH_I2C(self.i2c, int1=self.int1)
        self.accel = (0,0,0)
        
    def GetAcceleration(self):
        self.accel = self.lis3dh.acceleration
        return self.accel
        return self.accel