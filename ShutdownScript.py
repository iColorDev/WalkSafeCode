import RPi.GPIO as GPIO
import time
import os
GPIO.setmode(GPIO.BCM)
GPIO.setup(24, GPIO.IN)

while True:
    Reset = GPIO.input(24)
    if Reset == 1:
        time.sleep(5)
        Reset = GPIO.input(24)
        if Reset == 1:
            os.system('sudo shutdown -P now')