import tkinter as tk
from PIL import Image, ImageTk
import cv2
import numpy as np

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
    def __init__(self, window, cap):
        self.window = window

        self.Pod_Status = None
        self.Obj_Status = None
        self.Mot_Status = None

        self.cap = cap
        self.interval = int(1000/FPS)  # Interval in ms to get the latest frame

        # Create canvas for image
        self.set_up_window(window)

        self.get_base_image()
        self.real_frame = None
        # Update image on canvas
        self.update_image()

    def get_base_image(self):
        self.base_image = self.cap.read()[1]
        self.base_image = cv2.cvtColor(self.base_image, cv2.COLOR_BGR2GRAY)
        self.base_image = cv2.GaussianBlur(self.base_image, (25, 25), 0)

    def convert2tk(self, img):
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)  # to RGB
        img = Image.fromarray(img)  # to PIL format
        img = ImageTk.PhotoImage(img)  # to ImageTk format
        return img

    def get_current_frame(self, real_frame):
        self.current_frame = cv2.cvtColor(real_frame, cv2.COLOR_BGR2GRAY)
        self.current_frame = cv2.GaussianBlur(self.current_frame, (25, 25), 0)

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

        l1 = tk.Label(window, text="Qubic Status", font=("Helvetica 16 bold"), width=20, anchor="w")
        l2 = tk.Label(window, text="Object Detection", font=("Helvetica 16 bold"), width=20, anchor="w")
        l3 = tk.Label(window, text="Motion Detection", font=("Helvetica 16 bold"), width=20, anchor="w")

        l1.grid(row=0, column=1, padx=5, pady=5)
        l2.grid(row=3, column=1, padx=5, pady=5)
        l3.grid(row=6, column=1, padx=5, pady=5)

        self.Pod = tk.Label(window, text=self.Pod_Status, font=("Helvetica 16 bold"), width=20, anchor="w")
        self.Pod.grid(row=1, column=1, padx=5, pady=5)

        self.Obj = tk.Label(window, text=self.Obj_Status, font=("Helvetica 16 bold"), width=20, anchor="w")
        self.Obj.grid(row=4, column=1, padx=5, pady=5)

        self.Mot = tk.Label(window, text=self.Mot_Status, font=("Helvetica 16 bold"), width=20, anchor="w")
        self.Mot.grid(row=7, column=1, padx=5, pady=5)

        self.canvas_ori = tk.Canvas(self.window, width=camera_width, height=camera_height)
        self.canvas_ori.grid(row=0, column=0, rowspan=9, padx=5, pady=5)

        self.canvas_capture = tk.Canvas(self.window, width=camera_width, height=camera_height)
        self.canvas_capture.grid(row=9, column=0, rowspan=3, padx=5, pady=5)


if __name__ == "__main__":
    root = tk.Tk()
    main_window = MainWindow(root, cv2.VideoCapture(0))
    root.mainloop()
