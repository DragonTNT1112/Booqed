from datetime import datetime
import paho.mqtt.client as mqtt
from paho.mqtt import publish
import os

def on_message(client, userdata, message):
    global Pod_id
    message_list = str(message.payload.decode("utf-8")).split("|")
    current_time = datetime.now()
    Pod_id = message_list[0]
    Obj_Status = message_list[1]
    Mot_Status = message_list[2]
    Pod_Status = message_list[3]
    print()
    print("Time: ", str(current_time)[:-7])
    print("Pod ID:", str(Pod_id))
    print("Obj Status:", Obj_Status)
    print("Mot Status:", Mot_Status)
    print("Pod Status:", Pod_Status)
    print()


def on_connect(client, userdata, flags, rc):
    print("Connected to server...")

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.

    # The callback for when a PUBLISH message is received from the server.


def image_message(client, userdata, msg):
    # more callbacks, etc
    # Create a file with write byte permission
    format = ".jpg"

    current_time = datetime.now()
    date_folder = str(current_time.date())

    if current_time.minute < 30:
        Hour = str(current_time.hour)
        next_hour = Hour
        Min = '00'
        next_min = '30'
    else:
        Hour = str(current_time.hour)
        next_hour = str(int(current_time.hour) + 1)
        Min = '30'
        next_min = '00'

    time_period = "{}_{} - {}_{}".format(Hour, Min, next_hour, next_min)

    path = r"C:\Users\zzh84\PycharmProjects\MotionDetection\Received_images\{}\{}\{}".format(Pod_id, date_folder, time_period)

    if not os.path.exists(path):
        os.makedirs(path)

    directory = "Received_images/{}/{}/{}/".format(Pod_id, date_folder, time_period)

    file_name = str(current_time.time())[:-7].replace(":", "_")
    f = open(directory + file_name + format, "wb")
    f.write(msg.payload)
    print("-------------------------------------------------------------")
    print("{}: Image Received from Pod({})".format(current_time, Pod_id))
    print("-------------------------------------------------------------")
    f.close()


mqttBroker = "test.mosquitto.org"

client1 = mqtt.Client("Smartphone")
client3 = mqtt.Client("Image")

client1.connect(mqttBroker)
client3.connect(mqttBroker, 1883, 60)

client1.subscribe("Qubic/Overall Status")
client3.subscribe("Qubic/Saved Images")

client1.loop_start()
client3.loop_start()

while True:

    client1.on_message = on_message
    client3.on_message = image_message
