#file name = Pub2Code.jpynb
import paho.mqtt.publish as publish
import time

count = 0

while( count< 10 ):
    publish.single("Sensors/MyOffice/Indoor/Temp", "23.4", hostname="localhost")
    publish.single("Sensors/MyOffice/Indoor/Humi", "33", hostname="localhost")
    publish.single("Sensors/MyOffice/Indoor/Lamp", "ON", hostname="localhost")

    publish.single("Sensors/MyOffice/Outdoor/Temp", "33.4", hostname="localhost")
    publish.single("Sensors/MyOffice/Outdoor/Humi", "23", hostname="localhost")
    publish.single("Sensors/MyOffice/Outdoor/Lamp", "OFF", hostname="localhost")

    time.sleep(2)
    count+=1
