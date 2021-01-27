import numpy as np
import cv2
import cv2.aruco as aruco
from datetime import datetime


def resolution(width, height):
    cap.set(3, width)
    cap.set(4, height)


cap = cv2.VideoCapture(0)

resolution(1280, 720)
Font_Org = (5, 35)
Font_scale = 1.5
Font = cv2.FONT_HERSHEY_SIMPLEX
Font_thickness = 2

previousMarkers = 9
thread_switch = True

while True:
    ret, frame = cap.read()
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    aruco_dict = aruco.Dictionary_get(aruco.DICT_4X4_50)

    arucoParameters = aruco.DetectorParameters_create()

    corners, ids, rejectedImgPoints = aruco.detectMarkers(
        gray, aruco_dict, parameters=arucoParameters)

    frame = aruco.drawDetectedMarkers(frame, corners, ids)

    currentMarkers = len(corners)
    cv2.putText(frame, str(currentMarkers), (1220, 50), Font,
                Font_scale, (0, 0, 255), Font_thickness, cv2.LINE_AA)

    if currentMarkers < 9 and previousMarkers == 9:
        mark_time = datetime.now()
    if currentMarkers == 9:
        mark_time = datetime.now()

    previousMarkers = len(corners)

    current_time = datetime.now()
    difference = current_time - mark_time

    if difference.seconds >= 10 and thread_switch == True:
        thread_switch = False

    if not thread_switch:
        cv2.putText(frame, 'User has Checked-In!', Font_Org, Font,
                    Font_scale, (0, 255, 0), Font_thickness, cv2.LINE_AA)

    cv2.imshow('Display', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
