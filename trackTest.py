import wx
import cv2
import _thread
import numpy as np
import pygame


class window(wx.Frame):
    def __init__(self, parent, id):
        wx.Frame.__init__(self, parent, id, '抢险车上位机', size=(516, 500),
                          style=wx.CAPTION | wx.MINIMIZE_BOX | wx.CLOSE_BOX | wx.SYSTEM_MENU)
        self.Center()

        icon = wx.Icon('conf/logo.ico', wx.BITMAP_TYPE_ICO)
        self.SetIcon(icon)

        panel = wx.Panel(self)

        img = wx.Image('conf/car.png', wx.BITMAP_TYPE_ANY).ConvertToBitmap()
        self.img_car = wx.StaticBitmap(panel, -1, img, pos=(10, 10), size=(480, 360))

        self.readVideo = True

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
            _thread.start_new_thread(self.xboxInput, ())

        # _thread.start_new_thread(self.videoShow(), ())

    def videoShow(self):
        capture = cv2.VideoCapture(0)
        capture.set(3, 1280)
        capture.set(4, 720)

        while self.readVideo:
            flag, frame = capture.read()
            if not flag:
                break
            frame = cv2.resize(frame, (640, 360))
            height, width = frame.shape[:2]
            print(height, width)
            cv2.imwrite('temp.png',frame)

    def xboxInput(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.JOYBUTTONDOWN:
                    if event.button == 6:
                        print('ok')


if __name__ == '__main__':
    app = wx.App()
    frame = window(parent=None, id=-1)
    frame.Show()
    app.MainLoop()
