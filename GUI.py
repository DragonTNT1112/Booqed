import tkinter as tk
from PIL import Image, ImageTk
import cv2
import numpy as np
import paho.mqtt.client as mqtt
from paho.mqtt import publish
from datetime import datetime
import os

window_width = 1600
window_height = 1000

camera_width = 640
camera_height = 480
FPS = 60

avg = None

Font_Org = (5, 35)
Obj_Font_Org = (5, 35)
Mot_Font_Org = (5, 70)
Font_scale = 1
Font = cv2.FONT_HERSHEY_SIMPLEX
Font_thickness = 2


class MainWindow():
    def __init__(self, window, cap, Pod_ID):
        self.ID = Pod_ID
        self.window = window

        self.mqttBroker = "test.mosquitto.org"
        self.client = mqtt.Client("Qubic_{}".format(self.ID))
        self.server_status = False

        self.Pod_Status = None
        self.Obj_Status = None
        self.Mot_Status = None

        self.check_in_time = datetime.now()
        self.check_out_time = datetime.now()

        self.in_switch = False
        self.out_switch = False

        self.cap = cap
        self.interval = int(1000 / FPS)  # Interval in ms to get the latest frame

        # Create canvas for image
        self.set_up_window(window)

        self.real_frame = None
        # Update image on canvas
        self.get_base_image()
        self.update_image()

    def get_base_image(self):
        self.base_image_unchanged = self.cap.read()[1]
        self.base_image = cv2.cvtColor(self.base_image_unchanged, cv2.COLOR_BGR2GRAY)
        self.base_image = cv2.GaussianBlur(self.base_image, (25, 25), 0)

    def convert2tk(self, img):
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)  # to RGB
        img = Image.fromarray(img)  # to PIL format
        img = ImageTk.PhotoImage(img)  # to ImageTk format
        return img

    def get_current_frame(self, real_frame):
        self.current_frame = cv2.cvtColor(real_frame, cv2.COLOR_BGR2GRAY)
        self.current_frame = cv2.GaussianBlur(self.current_frame, (25, 25), 0)

    def CheckInCallBack(self):
        self.in_switch = True
        self.check_in_time = datetime.now()
        self.get_base_image()
        print("Start to check in...")
        self.check_in.config(state="disabled")

    def CheckOutCallBack(self):
        self.out_switch = True
        self.check_out_time = datetime.now()
        print("Start to check out...")
        self.check_out.config(state="disabled")

    def Connect2Mqtt(self):
        time = datetime.now()
        try:
            if not self.server_status:
                self.client.connect(self.mqttBroker)
                self.client.publish("Current ID", self.ID)
                print("{}: Connected to MQTT server...".format(time))
                self.send_status.config(state="normal")
                self.take_img.config(state="normal")
                self.server_status = True
            else:
                print("{}: It's already connected to server...".format(time))
                self.client.publish("Qubic/Pod ID", self.ID)
        except:
            print("Unable to connect to MQTT server...")


    def send_captured_img(self, img):
        time = datetime.now().time()
        MQTT_PATH = "Qubic/Saved_Images"
        f = open(img, "rb")
        fileContent = f.read()
        byteArr = bytearray(fileContent)

        publish.single(MQTT_PATH, byteArr, hostname=self.mqttBroker)

        print("{}: Saved image has been successfully sent to clients!".format(time))

    def send_Qubic_status(self):
        time = datetime.now()
        msgs = "{}|{}|{}|{}".format(self.ID, self.Obj_Status, self.Mot_Status, self.Pod_Status)
        self.client.publish("Qubic/Overall Status", msgs)
        print("{}: Pod's Status have Successfully Sent to Server...".format(time))

    def capture_image(self):
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
        file_name = str(current_time.time())[:-7].replace(":", "_")

        format = ".jpg"
        path = r"C:\Users\zzh84\PycharmProjects\MotionDetection\Check_in_out_images\{}\{}\{}".format(self.ID,
                                                                                                     date_folder,
                                                                                                     time_period)

        if not os.path.exists(path):
            os.makedirs(path)

        directory = "Check_in_out_images/{}/{}/{}/".format(self.ID, date_folder, time_period)
        cv2.imwrite(directory + file_name + format, self.real_frame)

        self.send_captured_img(directory + file_name + format)

        if self.Obj_Status == True:
            file_name = str(current_time.time())[:-7].replace(":", "_") + "_Reference"
            cv2.imwrite(directory + file_name + format, self.base_image_unchanged)

    def get_object(self):
        # Calculating the difference and image thresholding
        delta = cv2.absdiff(self.base_image, self.current_frame)
        threshold = cv2.threshold(delta, 25, 255, cv2.THRESH_BINARY)[1]

        # Finding all the contours
        (contours, _) = cv2.findContours(threshold, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # Drawing rectangles bounding the contours
        if len(contours) > 0:
            areas = [cv2.contourArea(contour) for contour in contours]
            max_index = np.argmax(areas)
            cnt = contours[max_index]
            if cv2.contourArea(cnt) < 200:
                pass
            else:
                (x, y, w, h) = cv2.boundingRect(cnt)
                cv2.rectangle(self.real_frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

            self.Obj_Status = True
            self.Obj_txt = "Object Detected"
            self.Obj_txt_color = "red"
        else:
            self.Obj_Status = False
            self.Obj_txt = "No Object Detected"
            self.Obj_txt_color = "green"

    def get_motion(self):
        global avg
        if avg is None:
            avg = self.current_frame.copy().astype("float")

        cv2.accumulateWeighted(self.current_frame, avg, 0.01)

        # Calculating the difference and image thresholding
        delta = cv2.absdiff(self.current_frame, cv2.convertScaleAbs(avg))
        threshold = cv2.threshold(delta, 25, 255, cv2.THRESH_BINARY)[1]

        (contours, _) = cv2.findContours(threshold, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # Drawing rectangles bounding the contours
        if len(contours) > 0:
            areas = [cv2.contourArea(contour) for contour in contours]
            max_index = np.argmax(areas)
            cnt = contours[max_index]

            if cv2.contourArea(cnt) < 200:
                pass
            else:
                (x, y, w, h) = cv2.boundingRect(cnt)
                cv2.rectangle(self.real_frame, (x, y), (x + w, y + h), (0, 0, 255), 2)

            self.Mot_Status = True
            self.Mot_txt = "Motion Detected"
            self.Mot_txt_color = "red"
        else:
            self.Mot_Status = False
            self.Mot_txt = "No Motion Detected"
            self.Mot_txt_color = "green"

    def get_pod_status(self):

        if self.Mot_Status and self.Obj_Status:
            self.Pod_Status = "Occupied"
            self.Pod_txt_color = "red"

        if (not self.Mot_Status) and (not self.Obj_Status):
            self.Pod_Status = "Empty"
            self.Pod_txt_color = "Green"

        if self.Obj_Status == True and self.out_switch == True:
            self.Pod_Status == "Occupied"
            self.Pod_txt_color = "red"

        if self.Mot_Status:
            self.check_out_time = datetime.now()

        if not self.Obj_Status:
            self.check_in_time = datetime.now()

        current_time = datetime.now()
        in_difference = current_time - self.check_in_time
        out_difference = current_time - self.check_out_time

        if in_difference.seconds >= 15 and self.in_switch == True:
            self.in_switch = False
            print("User has checked in!")
            self.check_in.config(state="normal")

        if out_difference.seconds >= 15 and self.out_switch == True:
            self.out_switch = False
            print("User has checked out!")
            self.check_out.config(state="normal")

    def update_image(self):
        # Get the latest frame and convert image format
        unchange_img = self.cap.read()[1]
        self.real_frame = self.cap.read()[1]
        self.get_current_frame(self.real_frame)
        self.get_object()
        self.get_motion()

        self.tk_img = self.convert2tk(self.real_frame)
        self.tk_unchange_img = self.convert2tk(unchange_img)

        # Update Pod
        self.get_pod_status()
        self.Pod.config(text=self.Pod_Status, fg=self.Pod_txt_color)
        self.Obj.config(text=self.Obj_txt, fg=self.Obj_txt_color)
        self.Mot.config(text=self.Mot_txt, fg=self.Mot_txt_color)

        # Update image
        self.canvas_ori.create_image(0, 0, anchor=tk.NW, image=self.tk_img)
        self.canvas_capture.create_image(0, 0, anchor=tk.NW, image=self.tk_unchange_img)

        # Repeat every 'interval' ms
        self.window.after(self.interval, self.update_image)

    def set_up_window(self, window):

        window.title("Qubic Management")
        # window.geometry("{}x{}".format(window_width, window_height))

        # Menu for the navigation

        menubar = tk.Menu(window)
        window.config(menu=menubar)

        connectMenu = tk.Menu(menubar, tearoff=0)
        connectMenu.add_command(label="Connect to MQTT broker", command=self.Connect2Mqtt)
        menubar.add_cascade(label="Connect", menu=connectMenu)

        # Title Label

        title = "POD ID - {}".format(self.ID)
        title_ID = tk.Label(window, text=title, font="Helvetica 20 bold", bg="#42a4f5", fg="white", height=2,
                            width=30)
        title_ID.grid(row=0, column=1, columnspan=2, padx=5, pady=5)

        # Labels for the Pod Status
        l1 = tk.Label(window, text="Qubic Status:", font="Helvetica 16 bold", width=15, anchor="w")
        l2 = tk.Label(window, text="Object Detection:", font="Helvetica 16 bold", width=15, anchor="w")
        l3 = tk.Label(window, text="Motion Detection:", font="Helvetica 16 bold", width=15, anchor="w")

        l1.grid(row=1, column=1, stick="w")
        l2.grid(row=3, column=1, stick="w")
        l3.grid(row=4, column=1, stick="w")

        self.Pod = tk.Label(window, text=self.Pod_Status, font="Helvetica 16 bold", width=15, anchor="w")
        self.Pod.grid(row=1, column=2, stick="w")

        self.Obj = tk.Label(window, text=self.Obj_Status, font="Helvetica 16 bold", width=15, anchor="w")
        self.Obj.grid(row=3, column=2, stick="w")

        self.Mot = tk.Label(window, text=self.Mot_Status, font="Helvetica 16 bold", width=15, anchor="w")
        self.Mot.grid(row=4, column=2, stick="w")

        # Buttons
        self.check_in = tk.Button(window, text="Start to Check In", command=self.CheckInCallBack,
                             font="Helvetica 16 bold", width=15, bg='green', fg='white')
        self.check_in.grid(row=6, column=1, padx=5, pady=5, stick="w")

        self.check_out = tk.Button(window, text="Start to Check Out", command=self.CheckOutCallBack,
                              font="Helvetica 16 bold", width=15, bg='red', fg='white')
        self.check_out.grid(row=7, column=1, padx=5, pady=5, stick="w")

        self.take_img = tk.Button(window, text="Capture Image", command=self.capture_image,
                             font="Helvetica 16 bold", width=15, state="disabled")
        self.take_img.grid(row=8, column=1, padx=5, pady=5, stick="w")

        self.send_status = tk.Button(window, text="Send Pod Status", command=self.send_Qubic_status,
                             font="Helvetica 16 bold", width=15, state="disabled")
        self.send_status.grid(row=9, column=1, padx=5, pady=5, stick="w")

        # Image Canvas
        self.canvas_ori = tk.Canvas(self.window, width=camera_width, height=camera_height)
        self.canvas_ori.grid(row=0, column=0, rowspan=12, padx=5, pady=5)

        self.canvas_capture = tk.Canvas(self.window, width=camera_width, height=camera_height)
        self.canvas_capture.grid(row=12, column=0, rowspan=12, padx=5, pady=5)


if __name__ == "__main__":
    root = tk.Tk()
    main_window = MainWindow(root, cv2.VideoCapture(0), 44565)
    root.mainloop()
