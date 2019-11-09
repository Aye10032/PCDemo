import threading
import time

import pygame
import wx
import cv2
import zmq
import base64
import numpy as np


class window(wx.Frame):
    def __init__(self, parent, id):
        wx.Frame.__init__(self, parent, id, '抢险车上位机', size=(1080, 480),
                          style=wx.CAPTION | wx.MINIMIZE_BOX | wx.CLOSE_BOX | wx.SYSTEM_MENU)
        self.Center()

        panel = wx.Panel(self)

        img1 = wx.Image('receive.bmp', wx.BITMAP_TYPE_ANY).ConvertToBitmap()
        self.img_hand = wx.StaticBitmap(panel, -1, img1, pos=(10, 10), size=(480, 360))
        self.img_car = wx.StaticBitmap(panel, -1, img1, pos=(500, 10), size=(480, 360))

        self.startbtn = wx.Button(panel, -1, '连接', pos=(200, 400), size=(70, 25))
        self.Bind(wx.EVT_BUTTON, self.start, self.startbtn)

        # 相关数据
        self.light_status = 0
        self.moment_mode = 0

        # 初始化手柄
        pygame.init()
        pygame.joystick.init()

        self.JoyKit = pygame.joystick.Joystick(0)
        self.JoyKit_name = self.JoyKit.get_name()
        print(self.JoyKit_name)
        self.JoyKit.init()

        self.axe_count = self.JoyKit.get_numaxes()
        print(self.axe_count)

        if self.JoyKit_name == 'XInput Controller #1':
            import _thread
            _thread.start_new_thread(self.xbox_input, ())

    def receiveimg1(self, event):
        context = zmq.Context()

        hand_socket = context.socket(zmq.SUB)
        hand_socket.connect('tcp://192.168.2.192:5555')
        hand_socket.setsockopt_string(zmq.SUBSCRIBE, np.unicode(''))

        while True:
            source_hand = hand_socket.recv_string()
            img = base64.b64decode(source_hand)
            npimg = np.fromstring(img, dtype=np.uint8)
            frame = cv2.imdecode(npimg, 1)

            frame_hand = frame[0:360, 0:480]
            frame_car = frame[0:360, 480:960]
            height1, width1 = frame_hand.shape[:2]
            height2, width2 = frame_car.shape[:2]
            print(height2, width2)
            frame_hand = cv2.cvtColor(frame_hand, cv2.COLOR_BGR2RGB)
            pic_hand = wx.Bitmap.FromBuffer(width1, height1, frame_hand)
            frame_car = cv2.cvtColor(frame_car, cv2.COLOR_BGR2RGB)
            pic_car = wx.Bitmap.FromBuffer(width2, height2, frame_car)
            self.img_hand.SetBitmap(pic_hand)
            self.img_car.SetBitmap(pic_car)
            cv2.imwrite('conf/receive.bmp', frame_car)

    def start(self, event):
        import _thread
        _thread.start_new_thread(self.receiveimg1, (event,))

    def xbox_input(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.JOYHATMOTION:
                    # 车灯
                    if event.value == (0, 1):
                        if self.light_status == 0:
                            print(50)
                            self.light_status = 1
                        elif self.light_status == 1:
                            print(51)
                            self.light_status = 0
                elif event.type == pygame.JOYBUTTONDOWN:
                    if event.button == 7:
                        # 切换至抓取模式
                        if self.moment_mode == 0:
                            self.moment_mode = 1
                            print(47)
                        elif self.moment_mode == 1:
                            self.moment_mode = 0
                    elif event.button == 5:
                        # 刹车
                        if self.moment_mode == 0:
                            print(47)
                elif event.type == pygame.JOYAXISMOTION:
                    if self.moment_mode == 0:
                        # 变速
                        if event.axis == 5:
                            speed_level = (event.value + 1) * 50
                            if speed_level >= 66.66:
                                print(48)
                            elif 33.33 <= speed_level < 66.66:
                                print(49)
                            elif speed_level < 33.33:
                                print(52)
                            print('------')
                        else:
                            if event.axis == 0:
                                print(event.value)


if __name__ == '__main__':
    app = wx.App()
    frame = window(parent=None, id=-1)
    frame.Show()
    app.MainLoop()
