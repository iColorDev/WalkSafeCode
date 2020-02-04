from Accel import Accelerometer
from FSR import ForceSensor
from UltraS import UltraSonic
import time
import asyncio
import datetime
import json
import paho.mqtt.client as mqtt
import firebase_admin
from firebase_admin import messaging
from firebase_admin import credentials
import RPi.GPIO as GPIO
import os
GPIO.setmode(GPIO.BCM)
GPIO.setup(24, GPIO.IN)
cred = credentials.Certificate("/home/pi/Desktop/WalkerCode/walksafe-cdc69-firebase-adminsdk-8833d-5de36f7cf6.json")
firebase_admin.initialize_app(cred)
Fsr = ForceSensor()
US = UltraSonic()
Accele = Accelerometer()

broker = "tailor.cloudmqtt.com"
port = 13576
user = "qhpzmcqr"
passw = "Z6izWLSG6xw8"
clientName = "RPi"

mqttClient = mqtt.Client(clientName, clean_session=True)
mqttClient.will_set("WalkerStatus", "Offline", 1, True)
mqttClient.username_pw_set(user, passw)

mqttClient.connect(broker, port)

def PublishOnline(client, userdata, flags, rc):
    if rc == 0:
        mqttClient.publish("WalkerStatus", "Online")
    
def Decode(client, userdata, msg):
    message = msg.payload.decode(encoding='UTF-8')
    print(message)

mqttClient.on_connect = PublishOnline
mqttClient.on_message = Decode
  
mqttClient.loop_start()

class Walker():
    def __init__(self):
        self.LastForce = Fsr.GetForce()
        self.Force = Fsr.GetForce()
        self.LastAcceleration = Accele.GetAcceleration()
        self.Acceleration = Accele.GetAcceleration()
        self.PersonDetected = US.PersonDetected(50)
        self.LastMotionTime = time.time()
        self.LastFallTime = time.time()
        self.MotionNotif = True
        
    def PublishData(self):
        mqttClient.publish("ForceData", self.Force)
        mqttClient.publish("PersonData", self.PersonDetected)
        #mqttClient.publish("AccelData", self.Acceleration[0] + self.Acceleration[1] + self.Acceleration[3])
        
    def SendNotification(self, Topic, Title, Body):
        print("sending notif")
        NotifAmount = 1
        message = messaging.Message(
            apns = messaging.APNSConfig(
                payload = messaging.APNSPayload(
                    aps = messaging.Aps(
                        alert=messaging.ApsAlert(
                            title=Title,
                            body=Body,
                        ),
                        sound="default",
                        badge=NotifAmount + 1
                    ),
                ),
            ),
            topic=Topic,
        )
        messaging.send(message)

    def LogEvent(self, Type, Title, Body):
        Time = datetime.datetime.now().strftime("%m/%d/%y %H:%M")
        data = {
            "type": Type,
            "title": Title,
            "body": Body,
            "time": Time
        }
        jsondata = json.dumps(data)
        mqttClient.publish("LogEvent", jsondata)

    def SendFallNotif(self):
      self.SendNotification("userId_iosDevice","Fall Detected!", "A fall was detected on a walker you are monitoring!")

    def LogFall(self):
        self.LogEvent("Fall", "Fall Detected", "A fall was detected!")

    def LogMotion(self):
        self.LogEvent("Motion", "Motion Detected", "Walker moved by person!")

    def SendMotionNotif(self):
      self.SendNotification("userId_iosDevice","Motion Detected!", "Motion was detected on a walker you are monitoring!")
        
    def Mainloop(self):
        while True:
            self.Force = Fsr.GetForce()
            self.Acceleration = Accele.GetAcceleration()
            #Reset = GPIO.input(24)
            #if Reset == 1:
            #os.system('sudo shutdown -r now')
            if self.Force == 1:
                #Active = False
                #if abs(self.Acceleration[1]) >= 1.27 or abs(self.Acceleration[2]) >= 1.27:
                Active = True
                mqttClient.publish("WalkerActive", "True")
                if time.time() - self.LastMotionTime >= 2700:
                    self.MotionNotif = True
                if self.MotionNotif:
                    self.MotionNotif = False
                    self.LogMotion()
                    self.SendMotionNotif()
                    self.LastMotionTime = time.time()
                if not Active:
                    mqttClient.publish("WalkerActive", "False")
            else:   
                mqttClient.publish("WalkerActive", "False")
            if self.LastForce == 1 and self.Force == 0:
                for i in range(len(self.LastAcceleration)):
                    AccelDiff = abs(self.LastAcceleration[i] - self.Acceleration[i])
                    if  AccelDiff >= 4 and (time.time() - self.LastFallTime) >= 10:
                        print("Quickly accelerated, no one holding on, most likely fell!")
                        self.LastFallTime = time.time()
                        self.LogFall()
                        self.SendFallNotif()
                    elif AccelDiff  < 4 and AccelDiff >= 2.75 :
                        self.PersonDetected = US.PersonDetected(50)
                        print("Acceleration change, unsure, using Ultra Sonic Sensors...")
                        if not self.PersonDetected and (time.time() - self.LastFallTime) >= 10:
                            self.LastFallTime = time.time()
                            self.LogFall()
                            self.SendFallNotif()
            self.PersonDetected = US.PersonDetected(50)
            self.PublishData()
            self.LastForce = self.Force
            self.LastAcceleration = self.Acceleration
            time.sleep(.2)
            

walker = Walker()
walker.Mainloop()
