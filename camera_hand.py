import base64
import cv2
import zmq
import time
import numpy as np
import smbus
import math

ip = 'tcp://192.168.2.192:5555'

context = zmq.Context()
footage_socket = context.socket(zmq.PUB)
footage_socket.bind(ip)

power_mgmt_1 = 0x6b
bus = smbus.SMBus(1)  # or bus = smbus.SMBus(1) for Revision 2 boards
address = 0x68  # This is the address value read via the i2cdetect command
bus.write_byte_data(address, power_mgmt_1, 0)  # Now wake the 6050 up as it starts in sleep mode


def read_word(adr):
    high = bus.read_byte_data(address, adr)
    low = bus.read_byte_data(address, adr + 1)
    val = (high << 8) + low
    return val


def read_word_2c(adr):
    val = read_word(adr)
    if (val >= 0x8000):
        return -((65535 - val) + 1)
    else:
        return val


def dist(a, b):
    return math.sqrt((a * a) + (b * b))


def get_y_rotation(x, y, z):
    radians = math.atan2(x, dist(y, z))
    return -math.degrees(radians)


def get_x_rotation(x, y, z):
    radians = math.atan2(y, dist(x, z))
    return math.degrees(radians)


capture1 = cv2.VideoCapture(0)
capture2 = cv2.VideoCapture(2)
capture1.set(3, 1280)
capture1.set(4, 720)
capture2.set(3, 1280)
capture2.set(4, 720)
while True:
    try:
        # gyro_xout = read_word_2c(0x43)
        # gyro_yout = read_word_2c(0x45)
        # gyro_zout = read_word_2c(0x47)
        #
        # gyro_xout_scaled = gyro_xout / 131
        # gyro_yout_scaled = gyro_yout / 131
        # gyro_zout_scaled = gyro_zout / 131
        #
        # # x_rotation = get_x_rotation(gyro_xout_scaled, gyro_yout_scaled, gyro_zout_scaled)
        # # y_rotation = get_y_rotation(gyro_xout_scaled, gyro_yout_scaled, gyro_zout_scaled)

        accel_xout = read_word_2c(0x3b)
        accel_yout = read_word_2c(0x3d)
        accel_zout = read_word_2c(0x3f)

        accel_xout_scaled = accel_xout / 16384.0
        accel_yout_scaled = accel_yout / 16384.0
        accel_zout_scaled = accel_zout / 16384.0

        x_rotation=get_x_rotation(accel_xout_scaled, accel_yout_scaled, accel_zout_scaled)
        y_rotation=get_y_rotation(accel_xout_scaled, accel_yout_scaled, accel_zout_scaled)

        success1, frame_hand = capture1.read()
        success2, frame_car = capture2.read()
        if not success1 or not success2:
            break
        frame_hand = cv2.resize(frame_hand, (640, 360))
        frame_car = cv2.resize(frame_car, (640, 360))
        frame_hand = frame_hand[0:360, 80:560]
        frame_car = frame_car[0:360, 80:560]
        frame_car = cv2.flip(frame_car,0)
        frame = np.hstack((frame_hand, frame_car))
        localtime = time.strftime("%H:%M:%S", time.localtime())
        cv2.putText(frame, localtime, (350, 340), cv2.FONT_ITALIC, 0.75, (10, 10, 10), 2)
        cv2.putText(frame, str(format(x_rotation,'.2f')), (820, 350), cv2.FONT_ITALIC, 0.75, (10, 10, 255), 2)
        cv2.putText(frame, str(format(y_rotation, '.2f')), (820, 300), cv2.FONT_ITALIC, 0.75, (10, 10, 255), 2)
        height, width = frame.shape[:2]
        print(str(format(x_rotation,'.2f')))
        buffer = cv2.imencode('.jpg', frame)[1]
        jpg_as_text = base64.b64encode(buffer)
        footage_socket.send(jpg_as_text)

    except KeyboardInterrupt:
        capture1.release()
        capture2.release()
        cv2.destroyAllWindows()
        break
