from datetime import datetime
import paho.mqtt.client as mqtt
from paho.mqtt import publish
import os


def id_message(client, userdata, message):
    global Pod_id
    Pod_id = message.payload.decode("utf-8")
    print("*****************************************")
    print("Receiving data from Pod:", str(Pod_id))
    print("*****************************************")


def on_message(client, userdata, message):
    message_list = str(message.payload.decode("utf-8")).split("|")
    current_time = datetime.now()
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
    client.subscribe("Qubic/Saved_Images")
    # The callback for when a PUBLISH message is received from the server.


def image_message(client, userdata, msg):
    # more callbacks, etc
    # Create a file with write byte permission
    format = ".jpg"

    current_time = datetime.now()
    date_folder = str(current_time.date())

    path = r"C:\Users\zzhu827\PycharmProjects\Booqed-updated\Received_images\{}\{}".format(Pod_id, date_folder)

    if not os.path.exists(path):
        os.makedirs(path)

    directory = "Received_images/{}/{}/".format(Pod_id, date_folder)

    file_name = str(current_time.time())[:-7].replace(":", "_")
    f = open(directory + file_name + format, "wb")
    f.write(msg.payload)
    print("-----------------------------------------")
    print("Image Received from Pod({})".format(Pod_id))
    print("-----------------------------------------")
    f.close()


mqttBroker = "test.mosquitto.org"

client1 = mqtt.Client("Smartphone")
client2 = mqtt.Client("ID tracker")
client3 = mqtt.Client("Image")

client1.connect(mqttBroker)
client2.connect(mqttBroker)
client3.connect(mqttBroker, 1883, 60)

client1.loop_start()
client2.loop_start()
client3.loop_start()


client3.on_connect = on_connect

client2.subscribe("Qubic/Pod ID")
client2.on_message = id_message

while True:
    client1.subscribe("Qubic/Overall Status")
    client1.on_message = on_message
    client3.on_message = image_message

client.loop_stop()
