import base64
import cv2
import zmq
import time
import numpy as np
import smbus  # smbus
import math
from socket import *
import _thread
import _thread
import serial


class Run():
    def __init__(self):
        ip = 'tcp://192.168.2.19:5555'

        self.context = zmq.Context()
        self.footage_socket = self.context.socket(zmq.PUB)
        self.footage_socket.bind(ip)

        # self.power_mgmt_1 = 0x6b
        # self.bus = smbus.SMBus(1)  # or bus = smbus2.SMBus(1) for Revision 2 boards
        # self.address = 0x68  # This is the address value read via the i2cdetect command
        # self.bus.write_byte_data(self.address, self.power_mgmt_1, 0)  # Now wake the 6050 up as it starts in sleep mode

        self.ser = serial.Serial('/dev/ttyAMA0', 9600)

        self.isnomal = True
        self.bbox = None
        self.count = 0

        self.capture1 = cv2.VideoCapture(2)
        self.capture2 = cv2.VideoCapture(0)
        self.capture1.set(3, 640)
        self.capture1.set(4, 360)
        self.capture2.set(3, 640)
        self.capture2.set(4, 360)
        self.capture1.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'))
        self.capture2.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'))
        self.capture1.set(cv2.CAP_PROP_FPS, 15)
        self.capture2.set(cv2.CAP_PROP_FPS, 15)

        self.frame_hand_temp = None

        _thread.start_new_thread(self.pc_socket, ())
        # _thread.start_new_thread(self.ser_thread, ())

        while True:
            self.nomal_send()
            self.track_frame()

    def pc_socket(self):
        HOST = ''
        PORT = 6655
        BUFSIZ = 1024
        ADDR = (HOST, PORT)

        tcpSerSock = socket(AF_INET, SOCK_STREAM)
        tcpSerSock.bind(ADDR)
        tcpSerSock.listen(5)

        while True:
            print('waiting for connection...')
            tcpCliSock, addr = tcpSerSock.accept()
            print('...connnecting from:', addr)

            while True:
                data = tcpCliSock.recv(BUFSIZ)
                if data:
                    strmsg = data.decode('utf-8')
                    strlist = strmsg.split()
                    self.bbox = (int(strlist[0]), int(strlist[1]), int(strlist[2]), int(strlist[3]))
                    print(self.bbox)
                    self.isnomal = False
                # tcpCliSock.send('[%s] %s' %(bytes(ctime(),'utf-8'),data))
            tcpCliSock.close()

    def ser_thread(self):
        while True:
            size = self.ser.inWaiting()
            if size != 0:
                response = self.ser.read(size).hex()  # 读取内容并显示
                print(response)
                self.ser.flushInput()  # 清空接收缓存区

    def read_word(self, adr):
        high = self.bus.read_byte_data(self.address, adr)
        low = self.bus.read_byte_data(self.address, adr + 1)
        val = (high << 8) + low
        return val

    def read_word_2c(self, adr):
        val = self.read_word(adr)
        if (val >= 0x8000):
            return -((65535 - val) + 1)
        else:
            return val

    def dist(self, a, b):
        return math.sqrt((a * a) + (b * b))

    def get_y_rotation(self, x, y, z):
        radians = math.atan2(x, self.dist(y, z))
        return -math.degrees(radians)

    def get_x_rotation(self, x, y, z):
        radians = math.atan2(y, self.dist(x, z))
        return math.degrees(radians)

    def nomal_send(self):
        while self.isnomal:
            # accel_xout = self.read_word_2c(0x3b)
            # accel_yout = self.read_word_2c(0x3d)
            # accel_zout = self.read_word_2c(0x3f)
            #
            # accel_xout_scaled = accel_xout / 16384.0
            # accel_yout_scaled = accel_yout / 16384.0
            # accel_zout_scaled = accel_zout / 16384.0
            #
            # x_rotation = self.get_x_rotation(accel_xout_scaled, accel_yout_scaled, accel_zout_scaled)
            # y_rotation = self.get_y_rotation(accel_xout_scaled, accel_yout_scaled, accel_zout_scaled)
            x_rotation = 90
            y_rotation = 80
            x_text = 'x: ' + str(format(x_rotation, '.2f'))
            y_text = 'y: ' + str(format(y_rotation, '.2f'))

            success1, frame_hand = self.capture1.read()
            success2, frame_car = self.capture2.read()
            if not success1 or not success2:
                break
            frame_hand = cv2.resize(frame_hand, (640, 360))
            frame_car = cv2.resize(frame_car, (640, 360))
            frame_hand = frame_hand[0:360, 80:560]
            frame_car = frame_car[0:360, 80:560]
            frame_car = cv2.flip(frame_car, 180)
            self.frame_hand_temp = frame_hand.copy()
            frame = np.hstack((frame_hand, frame_car))
            localtime = time.strftime("%H:%M:%S", time.localtime())
            cv2.putText(frame, localtime, (350, 340), cv2.FONT_ITALIC, 0.75, (10, 10, 10), 2)
            cv2.putText(frame, localtime, (350, 340), cv2.FONT_ITALIC, 0.75, (255, 255, 255), 1)
            cv2.putText(frame, x_text, (490, 50), cv2.FONT_ITALIC, 0.75, (10, 10, 10), 2)
            cv2.putText(frame, x_text, (490, 50), cv2.FONT_ITALIC, 0.75, (255, 255, 255), 1)
            cv2.putText(frame, y_text, (490, 20), cv2.FONT_ITALIC, 0.75, (10, 10, 10), 2)
            cv2.putText(frame, y_text, (490, 20), cv2.FONT_ITALIC, 0.75, (255, 255, 255), 1)
            # height, width = frame.shape[:2]
            # print(str(format(x_rotation, '.2f')))
            buffer = cv2.imencode('.jpg', frame)[1]
            jpg_as_text = base64.b64encode(buffer)
            self.footage_socket.send(jpg_as_text)

    def track_frame(self):
        if not self.isnomal:
            tracker = cv2.TrackerMedianFlow_create()
            tracker.init(self.frame_hand_temp, self.bbox)

            while not self.isnomal:
                success1, frame_hand = self.capture1.read()
                # success2, frame_car = self.capture2.read()
                if not success1:
                    break
                frame_hand = cv2.resize(frame_hand, (640, 360))
                # frame_car = cv2.resize(frame_car, (640, 360))
                frame_hand = frame_hand[0:360, 80:560]
                # frame_car = frame_car[0:360, 80:560]
                # frame_car = cv2.flip(frame_car, 180)
                flag, self.bbox = tracker.update(frame_hand)

                # print(self.bbox)
                timer = cv2.getTickCount()
                fps = int(cv2.getTickFrequency() / (cv2.getTickCount() - timer))

                height, width = frame_hand.shape[:2]

                p_x = int(self.bbox[0])
                p_y = int(self.bbox[1])
                p_w = int(self.bbox[2])
                p_h = int(self.bbox[3])
                p1 = (p_x, p_y)
                p2 = (p_x + p_w, p_y + p_h)
                c_x = int(self.bbox[0] + self.bbox[2] / 2)
                c_y = int(self.bbox[1] + self.bbox[3] / 2)
                proportion_x = -(0.5 - c_x / width)
                proportion_y = -(0.5 - c_y / height)

                if flag:
                    cv2.rectangle(frame_hand, p1, p2, (255, 255, 255), 2, 1)
                    cv2.rectangle(frame_hand, p1, p2, (0, 0, 0), 1, 1)

                    cv2.circle(frame_hand, (c_x, c_y), 1, (0, 0, 255), 2, 0)

                    cv2.line(frame_hand, (0, c_y), (c_x - int(p_w / 2), c_y), (255, 255, 255), 2, 0)
                    cv2.line(frame_hand, (0, c_y), (c_x - int(p_w / 2), c_y), (0, 0, 0), 1, 0)
                    cv2.line(frame_hand, (c_x, 0), (c_x, c_y - int(p_h / 2)), (255, 255, 255), 2, 0)
                    cv2.line(frame_hand, (c_x, 0), (c_x, c_y - int(p_h / 2)), (0, 0, 0), 1, 0)
                    cv2.line(frame_hand, (c_x + int(p_w / 2), c_y), (width, c_y), (255, 255, 255), 2, 0)
                    cv2.line(frame_hand, (c_x + int(p_w / 2), c_y), (width, c_y), (0, 0, 0), 1, 0)
                    cv2.line(frame_hand, (c_x, c_y + int(p_h / 2)), (c_x, height), (255, 255, 255), 2, 0)
                    cv2.line(frame_hand, (c_x, c_y + int(p_h / 2)), (c_x, height), (0, 0, 0), 1, 0)

                    cv2.putText(frame_hand, "[%.2f, %.2f]" % (proportion_x, proportion_y),
                                (int(c_x + 5), int(p_y - 8)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)

                    if proportion_y <= -0.1:
                        self.ser.write(b'\x56')
                    elif proportion_y >= 0.1:
                        self.ser.write(b'\x55')

                    # if proportion_x <= -0.1:
                    #     self.ser.write(b'\x46')
                    #     time.sleep(1)
                    #     self.ser.write(47)
                    # elif proportion_x >= 0.1:
                    #     self.ser.write(b'\x45')
                    #     time.sleep(1)
                    #     self.ser.write(47)
                    # else:
                    if p_w * p_h >= 0.8 * width * 0.9 * height:
                        self.ser.write(b'\x47')
                    else:
                        self.ser.write(b'\x43')

                    self.count = 0
                else:
                    cv2.putText(frame_hand, "Tracking failure detected", (50, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.75,
                                (0, 0, 255),
                                2)
                    self.count += 1
                    if self.count >= 5:
                        self.isnomal = True

                cv2.putText(frame_hand, "FPS : " + str(fps),
                            (10, 15), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)
                cv2.putText(frame_hand, "FPS : " + str(fps),
                            (10, 15), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)

                cv2.putText(frame_hand,
                            "Center : (" + str(c_x) + ',' + str(c_y) + ")",
                            (10, 35), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)
                cv2.putText(frame_hand,
                            "Center : (" + str(c_x) + ',' + str(c_y) + ")",
                            (10, 35), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)

                cv2.putText(frame_hand, "Size : " + str(p_w * p_h),
                            (10, 55), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)
                cv2.putText(frame_hand, "Size : " + str(p_w * p_h),
                            (10, 55), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
                # frame = np.hstack((frame_hand, frame_car))
                localtime = time.strftime("%H:%M:%S", time.localtime())
                cv2.putText(frame_hand, localtime, (350, 340), cv2.FONT_ITALIC, 0.75, (10, 10, 10), 2)
                cv2.putText(frame_hand, localtime, (350, 340), cv2.FONT_ITALIC, 0.75, (255, 255, 255), 1)
                buffer = cv2.imencode('.jpg', frame_hand)[1]
                jpg_as_text = base64.b64encode(buffer)
                self.footage_socket.send(jpg_as_text)


if __name__ == '__main__':
    Run()
