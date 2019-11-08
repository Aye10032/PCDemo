import base64
import cv2
import zmq

ip = 'tcp://192.168.2.192:5555'

context = zmq.Context()
footage_socket = context.socket(zmq.PUB)
footage_socket.bind(ip)

camera_hand = cv2.VideoCapture(1)
camera_hand.set(3, 480)
camera_hand.set(4, 360)
while True:
    try:
        success1, frame_hand = camera_hand.read()
        if not success1:
            break
        height, width = frame_hand.shape[:2]
        print(height, width)
        buffer = cv2.imencode('.jpg', frame_hand)[1]
        jpg_as_text = base64.b64encode(buffer)
        footage_socket.send(jpg_as_text)

    except KeyboardInterrupt:
        camera_hand.release()
        cv2.destroyAllWindows()
        break
