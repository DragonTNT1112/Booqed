import tkinter as tk
from datetime import datetime
import paho.mqtt.client as mqtt
from paho.mqtt import publish
import os
from time import *

class MainWindow():
    def __init__(self, window):
        self.window = window

        self.mqttBroker = "test.mosquitto.org"
        self.topic_list = ["Qubic/Overall Status", "Qubic/File Names", "Qubic/Saved Images"]
        self.client = mqtt.Client("Client_Message")
        self.all_client_status = False

        self.file_name = ""
        self.received_img_log_file_name = "Received_Images.txt"

        self.ID = "Not Connected"
        self.Pod_Status = "Not Connected"
        self.Obj_Status = "Not Connected"
        self.Mot_Status = "Not Connected"

        self.Obj_txt = None
        self.Mot_txt = None
        self.Obj_txt_color = "black"
        self.Mot_txt_color = "black"

        self.create_img_log()

        # Create canvas for image
        self.set_up_window(window)

    def create_img_log(self):
        try:
            img_log_file = open(self.received_img_log_file_name, "x")
            img_log_file.close()
        except:
            pass

    def on_message(self, client, userdata, message):

        if message.topic == "Qubic/Overall Status":
            message_list = str(message.payload.decode("utf-8")).split("|")
            current_time = datetime.now()
            self.ID = message_list[0]
            self.Obj_Status = message_list[1]
            self.Mot_Status = message_list[2]
            self.Pod_Status = message_list[3]

            # print("Time: ", str(current_time)[:-7])
            self.title_ID.config(text="POD ID - {}".format(self.ID))

            if self.Obj_Status == "True":
                self.Obj_txt = "Objet Detected"
                self.Obj_txt_color = "red"
            else:
                self.Obj_txt = "No Object Detected"
                self.Obj_txt_color = "green"

            if self.Mot_Status == "True":
                self.Mot_txt = "Motion Detected"
                self.Mot_txt_color = "red"
            else:
                self.Mot_txt = "No Motion Detected"
                self.Mot_txt_color = "green"

            if self.Pod_Status == "Occupied":
                self.Pod_txt_color = "red"
            else:
                self.Pod_txt_color = "green"

            self.Pod.config(text=self.Pod_Status, fg=self.Pod_txt_color)
            self.Obj.config(text=self.Obj_txt, fg=self.Obj_txt_color)
            self.Mot.config(text=self.Mot_txt, fg=self.Mot_txt_color)

            self.log_box.config(state="normal")
            self.log_box.insert("end", "{} - Pod's status have received from Pod ({})\n".format(str(datetime.now())[:-7],
                                                                                                self.ID))
            self.log_box.config(state="disabled")


        if message.topic == "Qubic/File Names":
            self.file_name = str(message.payload.decode("utf-8"))

        if message.topic == "Qubic/Saved Images":
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

            path = r"C:\Users\zzh84\OneDrive\Documents\GitHub\Booqed\Received_images\{}\{}\{}".format(self.ID,
                                                                                                     date_folder,
                                                                                                     time_period)

            if not os.path.exists(path):
                os.makedirs(path)

            directory = "C:/Users/zzh84/OneDrive/Documents/GitHub/Booqed/Received_images/{}/{}/{}/".format(self.ID, date_folder, time_period)

            f = open(directory + self.file_name + format, "wb")
            f.write(message.payload)

            self.log_box.config(state="normal")
            self.log_box.insert("end", "{} - Image ({}) received from Pod ({})\n".format(str(datetime.now())[:-7],
                                                                                         self.file_name, self.ID))
            self.log_box.config(state="disabled")

            f.close()

            img_log_file = open(self.received_img_log_file_name, "a")
            img_log_file.write("{}|{}|{}|{}\n".format(self.ID,date_folder, time_period, self.file_name))
            img_log_file.close()

    def on_connect(self, client, userdata, flags, rc):
        for i in self.topic_list:
            client.subscribe(i)

    def Start_MQTT(self):
        self.log_box.config(state="normal")
        time = str(datetime.now())[:-7]
        self.log_box.insert("end","{} - Creating new client instance...\n".format(time))



        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message

        self.log_box.insert("end", "{} - Connecting to MQTT broker...\n".format(time).format(time))
        self.log_box.config(state="disabled")

        self.client.connect(self.mqttBroker)

        self.client.loop_start()

    def set_up_window(self, window):

        window.title("Qubic Client")
        # window.geometry("{}x{}".format(window_width, window_height))

        # Menu for the navigation

        menubar = tk.Menu(window)
        window.config(menu=menubar)

        connectMenu = tk.Menu(menubar, tearoff=0)
        connectMenu.add_command(label="Connect to MQTT broker", command=self.Start_MQTT)
        menubar.add_cascade(label="Connect", menu=connectMenu)

        # Title Label

        title = "POD ID - {}".format(self.ID)
        self.title_ID = tk.Label(window, text=title, font="Helvetica 20 bold", bg="yellow", fg="blue", height=2,
                                 width=40)
        self.title_ID.grid(row=0, column=0, columnspan=2, padx=5, pady=5)

        # Labels for the Pod Status
        l1 = tk.Label(window, text="Qubic Status:", font="Helvetica 16 bold", width=20, anchor="w")
        l2 = tk.Label(window, text="Object Detection:", font="Helvetica 16 bold", width=20, anchor="w")
        l3 = tk.Label(window, text="Motion Detection:", font="Helvetica 16 bold", width=20, anchor="w")

        l1.grid(row=1, column=0, padx=5, pady=5, stick="e")
        l2.grid(row=2, column=0, padx=5, pady=5, stick="e")
        l3.grid(row=3, column=0, padx=5, pady=5, stick="e")

        self.Pod = tk.Label(window, text=self.Pod_Status, font="Helvetica 16 bold", width=20, anchor="w")
        self.Pod.grid(row=1, column=1)

        self.Obj = tk.Label(window, text=self.Obj_Status, font="Helvetica 16 bold", width=20, anchor="w")
        self.Obj.grid(row=2, column=1)

        self.Mot = tk.Label(window, text=self.Mot_Status, font="Helvetica 16 bold", width=20, anchor="w")
        self.Mot.grid(row=3, column=1)

        # Create log widget
        self.log_box = tk.Text(root, wrap="word", width=80)
        self.log_box.grid(row=4, column=0, columnspan=2, padx=10, pady=10)
        self.log_box.config(font="Ubuntu 12 italic", state="disabled")


if __name__ == "__main__":
    root = tk.Tk()
    main_window = MainWindow(root)
    root.mainloop()
