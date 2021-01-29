import paho.mqtt.client as mqtt
import time
from datetime import datetime

def id_message(client, userdata, message):
    print("*****************************************")
    print("Receiving data from Pod:", str(message.payload.decode("utf-8")))
    print("*****************************************")

def on_message(client, userdata, message):
    message_list = str(message.payload.decode("utf-8")).split("|")
    current_time = datetime.now()
    Pod_id = message_list[0]
    Obj_Status = message_list[1]
    Mot_Status = message_list[2]
    Pod_Status = message_list[3]
    print("-----------------------------------------")
    print("Time: ", current_time)
    print("ID:", Pod_id)
    print("Obj Status:", Obj_Status)
    print("Mot Status:", Mot_Status)
    print("Pod Status:", Pod_Status)
    print()

mqttBroker ="test.mosquitto.org"

client1 = mqtt.Client("Smartphone")
client2 = mqtt.Client("ID tracker")
client1.connect(mqttBroker)
client2.connect(mqttBroker)

client1.loop_start()
client2.loop_start()

client2.subscribe("Pod ID")
client2.on_message = id_message

while True:
    client1.subscribe("Overall Status")
    client1.on_message = on_message

client.loop_stop()
