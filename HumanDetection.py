import numpy as np
import cv2

def change_res(width, height):
    cap.set(3, width)
    cap.set(4, height)

width = 640
height = 480
cv2.startWindowThread()
cap = cv2.VideoCapture(0)
change_res(width, height)
#
# while(True):
#     # reading the frame
#     ret, frame = cap.read()
#     # turn to greyscale:
#     gray_frame = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
#     # apply threshold. all pixels with a level larger than 80 are shown in white. the others are shown in black:
#     ret, threshold_frame = cv2.threshold(gray_frame,80,255,cv2.THRESH_BINARY)
#     # displaying the frame
#     cv2.imshow('frame', frame)
#     cv2.imshow('gray_frame', gray_frame)
#     cv2.imshow('threshold_frame', threshold_frame)
#     if cv2.waitKey(1) & 0xFF == ord('q'):
#         # breaking the loop if the user types q
#         # note that the video window must be highlighted!
#         break
#
# cap.release()
# cv2.destroyAllWindows()
# # the following is necessary on the mac,
# # maybe not on other platforms:
# cv2.waitKey(1)


# Load the cascade
face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_alt.xml')
# Read the input image
while(True):
    # reading the frame
    ret, frame = cap.read()
    # turn to greyscale:
    gray_frame = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)

    faces = face_cascade.detectMultiScale(gray_frame, 1.2, 3)
    if len(faces) != 0:
        # Draw rectangle around the faces
        for (x, y, w, h) in faces:
            cv2.rectangle(frame, (x,y), (x+w, y+h), (255,0,0),2)
            cv2.rectangle(gray_frame, (x, y), (x + w, y + h), (255, 0, 0), 2)

    cv2.imshow('frame', frame)
    cv2.imshow('gray_frame', gray_frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        # breaking the loop if the user types q
        # note that the video window must be highlighted!
        break


cap.release()
cv2.destroyAllWindows()
# the following is necessary on the mac,
# maybe not on other platforms:
cv2.waitKey(1)