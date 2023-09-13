import paho.mqtt.publish as publish
import time
import struct
import paho.mqtt.client as mqtt

client = mqtt.Client( )
client.username_pw_set('hyunsu', '0223')
client.connect("localhost", 1883, 60)

count = 0
Rasp_length = 30
Rasp_length_b = struct.pack("B", Rasp_length)

Rasp_width = 120
Rasp_width_b = struct.pack("B", Rasp_width)

while( count< 3 ):
    publish.single("Smart/Myhome/Rasp/length", Rasp_length_b, hostname="localhost")
    publish.single("Smart/Myhome/Rasp/width", Rasp_width_b, hostname="localhost")

    time.sleep(1)
    count+=1
