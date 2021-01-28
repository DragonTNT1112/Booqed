import numpy as np
import cv2
import cv2.aruco as aruco
from datetime import datetime


camera_width = 800
camera_height = 400
Font_Org = (5, 35)
Obj_Font_Org = (5, 35)
Mot_Font_Org = (5, 70)
Font_scale = 1
Font = cv2.FONT_HERSHEY_SIMPLEX
Font_thickness = 2

aruco_dict = aruco.Dictionary_get(aruco.DICT_4X4_50)
arucoParameters = aruco.DetectorParameters_create()

class Qubic:
    def __init__(self, id, in_time, out_time):
        self.qubic_id = str(id)
        self.check_in_time = datetime.strptime(in_time, '%Y-%m-%d %H:%M:%S').time()
        self.check_out_time = datetime.strptime(out_time, '%Y-%m-%d %H:%M:%S').time()

    def Check_In(self, time_now):
        previousMarkers = 9
        thread_switch = True

        if time_now >= self.check_in_time:
            cap = cv2.VideoCapture(0)
            cap.set(3, camera_width)
            cap.set(4, camera_height)
            while True:
                ret, frame = cap.read()
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

                corners, ids, rejectedImgPoints = aruco.detectMarkers(
                    gray, aruco_dict, parameters=arucoParameters)

                frame = aruco.drawDetectedMarkers(frame, corners, ids)

                currentMarkers = len(corners)
                cv2.putText(frame, str(currentMarkers), (750, 50), Font,
                            Font_scale, (0, 0, 255), Font_thickness, cv2.LINE_AA)

                if currentMarkers < 9 and previousMarkers == 9:
                    mark_time = datetime.now()
                if currentMarkers == 9:
                    mark_time = datetime.now()

                previousMarkers = len(corners)

                current_time = datetime.now()
                difference = current_time - mark_time

                if difference.seconds >= 3 and thread_switch == True:
                    thread_switch = False

                if not thread_switch:
                    cv2.putText(frame, 'User has Checked-In!', Font_Org, Font,
                                Font_scale, (0, 255, 0), Font_thickness, cv2.LINE_AA)

                cv2.imshow('Display', frame)
                if cv2.waitKey(1) & (not thread_switch):
                    print("User has checked in!")
                    break

            cap.release()
            cv2.destroyAllWindows()
        else:
            pass

    def Check_Out(self, time_now):
        previousMarkers = 0
        thread_switch = True

        if time_now >= self.check_out_time:
            cap = cv2.VideoCapture(0)
            cap.set(3, camera_width)
            cap.set(4, camera_height)
            while True:
                ret, frame = cap.read()
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

                corners, ids, rejectedImgPoints = aruco.detectMarkers(
                    gray, aruco_dict, parameters=arucoParameters)

                frame = aruco.drawDetectedMarkers(frame, corners, ids)

                currentMarkers = len(corners)
                cv2.putText(frame, str(currentMarkers), (750, 50), Font,
                            Font_scale, (0, 0, 255), Font_thickness, cv2.LINE_AA)

                if currentMarkers == 9 and previousMarkers < 9:
                    mark_time = datetime.now()
                if currentMarkers < 9:
                    mark_time = datetime.now()

                previousMarkers = len(corners)

                current_time = datetime.now()
                difference = current_time - mark_time

                if difference.seconds >= 3 and thread_switch == True:
                    thread_switch = False

                if not thread_switch:
                    cv2.putText(frame, 'User has Checked-Out!', Font_Org, Font,
                                Font_scale, (0, 255, 0), Font_thickness, cv2.LINE_AA)

                cv2.imshow('Display', frame)
                if cv2.waitKey(1) & (not thread_switch):
                    print("User has checked out!")
                    break

            cap.release()
            cv2.destroyAllWindows()
        else:
            pass

    def User_Detection(self):
        avg = None
        cap = cv2.VideoCapture(0)
        cap.set(3, camera_width)
        cap.set(4, camera_height)

        ret, base_img = cap.read()
        base_img = cv2.cvtColor(base_img, cv2.COLOR_BGR2GRAY)
        base_img = cv2.GaussianBlur(base_img, (25, 25), 0)

        while True:
            ret, real_frame = cap.read()
            current_frame = cv2.cvtColor(real_frame, cv2.COLOR_BGR2GRAY)
            current_frame = cv2.GaussianBlur(current_frame, (25, 25), 0)

            # Calculating the difference and image thresholding
            Obj_delta = cv2.absdiff(base_img, current_frame)
            Obj_threshold = cv2.threshold(Obj_delta, 50, 255, cv2.THRESH_BINARY)[1]

            # Finding all the contours
            (Obj_contours, _) = cv2.findContours(Obj_threshold, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            # Drawing rectangles bounding the contours
            if len(Obj_contours) > 0:
                areas = [cv2.contourArea(contour) for contour in Obj_contours]
                max_index = np.argmax(areas)
                cnt = Obj_contours[max_index]
                if cv2.contourArea(cnt) < 500:
                    pass
                else:
                    (x, y, w, h) = cv2.boundingRect(cnt)
                    cv2.rectangle(real_frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

                cv2.putText(real_frame, 'Pod Status: Occupied', Obj_Font_Org, Font,
                            Font_scale, (0, 0, 255), Font_thickness, cv2.LINE_AA)
                Obj_Status = True
            else:
                cv2.putText(real_frame, 'Pod Status: Empty', Obj_Font_Org, Font,
                            Font_scale, (0, 255, 0), Font_thickness, cv2.LINE_AA)
                Obj_Status = False

            if avg is None:
                avg = current_frame.copy().astype("float")

            cv2.accumulateWeighted(current_frame, avg, 0.01)

            # Calculating the difference and image thresholding
            Mot_delta = cv2.absdiff(current_frame, cv2.convertScaleAbs(avg))
            Mot_threshold = cv2.threshold(Mot_delta, 50, 255, cv2.THRESH_BINARY)[1]

            (Mot_contours, _) = cv2.findContours(Mot_threshold, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            # Drawing rectangles bounding the contours
            if len(Mot_contours) > 0:
                areas = [cv2.contourArea(contour) for contour in Mot_contours]
                max_index = np.argmax(areas)
                cnt = Mot_contours[max_index]

                cv2.putText(real_frame, 'Motion Detected', Mot_Font_Org, Font,
                            Font_scale, (0, 0, 255), Font_thickness, cv2.LINE_AA)
                Mot_Status = True
            else:
                cv2.putText(real_frame, 'No Motion Detected', Mot_Font_Org, Font,
                            Font_scale, (0, 255, 0), Font_thickness, cv2.LINE_AA)
                Mot_Status = False

            cv2.imshow('Obj_Threshold', Obj_threshold)
            cv2.imshow('Mot_Threshold', Mot_threshold)
            cv2.imshow('Display', real_frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        cap.release()
        cv2.destroyAllWindows()


Pod = Qubic(205, "2021-01-26 10:00:00", "2021-01-26 11:00:00")
current_time = datetime.now().time()
# Pod.Check_In(current_time)
# Pod.Check_Out(current_time)
Pod.User_Detection()
