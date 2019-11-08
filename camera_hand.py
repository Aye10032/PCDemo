import base64
import cv2
import zmq
import time
import numpy as np

ip = 'tcp://192.168.2.192:5555'

context = zmq.Context()
footage_socket = context.socket(zmq.PUB)
footage_socket.bind(ip)

capture1 = cv2.VideoCapture(0)
capture2 = cv2.VideoCapture(2)
capture1.set(3, 1280)
capture1.set(4, 720)
capture2.set(3, 1280)
capture2.set(4, 720)
while True:
    try:
        success1, frame_hand = capture1.read()
        success2, frame_car = capture2.read()
        if not success1 or not success2:
            break
        frame_hand = cv2.resize(frame_hand, (640, 360))
        frame_car = cv2.resize(frame_car, (640, 360))
        frame_hand = frame_hand[0:360, 80:560]
        frame_car = frame_car[0:360, 80:560]
        frame = np.hstack((frame_hand, frame_car))
        localtime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        cv2.putText(frame, localtime, (20, 20), cv2.FONT_HERSHEY_COMPLEX, 0.75, (0, 0, 255), 2)
        height, width = frame.shape[:2]
        print(height, width)
        buffer = cv2.imencode('.jpg', frame)[1]
        jpg_as_text = base64.b64encode(buffer)
        footage_socket.send(jpg_as_text)

    except KeyboardInterrupt:
        capture1.release()
        capture2.release()
        cv2.destroyAllWindows()
        break
