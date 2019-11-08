import cv2
import numpy as np

capture1 = cv2.VideoCapture(2)
capture2 = cv2.VideoCapture(3)
capture1.set(3, 1280)
capture1.set(4, 720)
capture2.set(3, 1280)
capture2.set(4, 720)

while True:
    ret1, frame1 = capture1.read()
    ret2, frame2 = capture2.read()
    frame1 = cv2.resize(frame1, (640, 360))
    frame2 = cv2.resize(frame2, (640, 360))
    frame = np.vstack((frame1, frame2))
    height, width = frame1.shape[:2]
    print(height, width)
    cv2.imshow('frame', frame)
    if cv2.waitKey(1) == ord('q'):
        break
