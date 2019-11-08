import threading
import time

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
            cv2.imwrite('receive.bmp', frame_car)

    def start(self, event):
        import _thread
        _thread.start_new_thread(self.receiveimg1, (event,))


if __name__ == '__main__':
    app = wx.App()
    frame = window(parent=None, id=-1)
    frame.Show()
    app.MainLoop()
