import paho.mqtt.client as mqtt
import time
from datetime import datetime

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

mqttBroker ="test.mosquitto.org"

client = mqtt.Client("Smartphone")
client.connect(mqttBroker) 

client.loop_start()

while True:
    client.subscribe("Overall Status")
    client.on_message = on_message

client.loop_stop()
