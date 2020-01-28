import RPi.GPIO as GPIO
import time

GPIO.setwarnings(False)

class UltraSonic():
    def __init__(self):
        self.TRIG = 21
        self.ECHO1 = 17
        self.ECHO2 = 27
        self.ECHO3 = 22
        self.TimeOut = 0.4
        
    def GetSensorReading(self, Sensor):
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.TRIG, GPIO.OUT)
        GPIO.setup(Sensor, GPIO.IN)
        GPIO.output(self.TRIG, True)
        time.sleep(.00001)
        GPIO.output(self.TRIG, False)
        pulse_start = time.time()
        TO = pulse_start + self.TimeOut
        while GPIO.input(Sensor) == 0 and pulse_start < TO:
            pulse_start = time.time()
        pulse_end = time.time()
        TO = pulse_end + self.TimeOut
        while GPIO.input(Sensor) == 1 and pulse_end < TO:
            pulse_end = time.time()
        pulse_dura = pulse_end - pulse_start
        distance = pulse_dura * 13503
        distance = round(distance, 2)
        return distance

        
    def PersonDetected(self, Distance):
        Distances = []
        SensorChecks = 0
        #sensorR = self.GetSensorReading(self.ECHO2)
        sensorL = self.GetSensorReading(self.ECHO1)
        #print(sensorR, sensorL)
        #Distances.append(sensorR)
        Distances.append(sensorL)
        for distance in Distances:
            if distance <= Distance:
                SensorChecks += 1
        if SensorChecks >= 1:
            return True
        return False