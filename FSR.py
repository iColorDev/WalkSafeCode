import RPi.GPIO as GPIO

class ForceSensor():
    def __init__(self):
        self.ForceReading = 0
        GPIO.setmode(GPIO.BCM);
        GPIO.setup(23, GPIO.IN)

    def GetForce(self):
        self.ForceReading = GPIO.input(23)
<<<<<<< HEAD
        return self.ForceReading
=======
        return self.ForceReading
>>>>>>> 156c3064e36a9c088fb68bfaaac2632a99913196
