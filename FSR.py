import RPi.GPIO as GPIO

class ForceSensor():
    def __init__(self):
        self.ForceReading = 0
        GPIO.setmode(GPIO.BCM);
        GPIO.setup(23, GPIO.IN)

    def GetForce(self):
        self.ForceReading = GPIO.input(23)
        return self.ForceReading