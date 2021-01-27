import cv2
import numpy as np


def resolution(width, height):
    cap.set(3, width)
    cap.set(4, height)


# Motion_Sensor = False  # True if activity detected

cap = cv2.VideoCapture(0)
resolution(1280, 720)
Font_Org = (5, 35)
Font_scale = 1.5
Font = cv2.FONT_HERSHEY_SIMPLEX
Font_thickness = 2

ret, base_img = cap.read()
base_img = cv2.cvtColor(base_img, cv2.COLOR_BGR2GRAY)
base_img = cv2.GaussianBlur(base_img, (25, 25), 0)

while True:
    ret, real_frame = cap.read()
    current_frame = cv2.cvtColor(real_frame, cv2.COLOR_BGR2GRAY)
    current_frame = cv2.GaussianBlur(current_frame, (25, 25), 0)

    # Calculating the difference and image thresholding
    delta = cv2.absdiff(base_img, current_frame)
    threshold = cv2.threshold(delta, 50, 255, cv2.THRESH_BINARY)[1]

    # Finding all the contours
    (contours, _) = cv2.findContours(threshold, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Drawing rectangles bounding the contours
    if len(contours) > 0:
        areas = [cv2.contourArea(contour) for contour in contours]
        max_index = np.argmax(areas)
        cnt = contours[max_index]
        if cv2.contourArea(cnt) < 500:
            continue
        else:
            (x, y, w, h) = cv2.boundingRect(cnt)
            cv2.rectangle(real_frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

        cv2.putText(real_frame, 'Pod Status: Occupied', Font_Org, Font,
                    Font_scale, (0, 0, 255), Font_thickness, cv2.LINE_AA)
    else:
        cv2.putText(real_frame, 'Pod Status: Vacant', Font_Org, Font,
                    Font_scale, (0, 255, 0), Font_thickness, cv2.LINE_AA)


    cv2.imshow('Threshold', threshold)
    cv2.imshow('Display', real_frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
