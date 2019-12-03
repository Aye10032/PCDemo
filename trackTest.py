import wx
import cv2
import _thread
import numpy as np
import pygame


class window(wx.Frame):
    def __init__(self, parent, id):
        wx.Frame.__init__(self, parent, id, '抢险车上位机', size=(680, 500),
                          style=wx.CAPTION | wx.MINIMIZE_BOX | wx.CLOSE_BOX | wx.SYSTEM_MENU)
        self.Center()

        icon = wx.Icon('conf/logo.ico', wx.BITMAP_TYPE_ICO)
        self.SetIcon(icon)

        panel = wx.Panel(self)

        img = wx.Image('conf/car.png', wx.BITMAP_TYPE_ANY).ConvertToBitmap()
        self.img_car = wx.StaticBitmap(panel, -1, img, pos=(10, 10), size=(640, 360))

        self.readVideo = False
        self.frame = None
        self.TempFrame = None
        self.x = 100
        self.y = 100
        self.a = 10
        self.b = 10
        self.track_bbox = (self.x, self.y, self.a, self.b)  # 横,纵,宽,高
        self.bbox_start = False
        self.track_start = False

        self.capture = cv2.VideoCapture(0)
        self.capture.set(3, 1280)
        self.capture.set(4, 720)

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
            _thread.start_new_thread(self.xboxInput, ())

        # _thread.start_new_thread(self.videoShow(), ())

    def videoShow(self):
        while self.readVideo:
            flag, self.frame = self.capture.read()
            if not flag:
                break
            self.frame = cv2.resize(self.frame, (640, 360))
            height, width = self.frame.shape[:2]
            print(height, width)
            self.TempFrame = cv2.cvtColor(self.frame, cv2.COLOR_BGR2RGB)
            pic = wx.Bitmap.FromBuffer(width, height, self.TempFrame)
            self.img_car.SetBitmap(pic)

    def drawBbox(self):
        while self.bbox_start:
            frame_1 = self.frame.copy()

            p1 = (int(self.track_bbox[0]), int(self.track_bbox[1]))
            p2 = (int(self.track_bbox[0] + self.track_bbox[2]), int(self.track_bbox[1] + self.track_bbox[3]))
            cv2.rectangle(frame_1, p1, p2, (0, 255, 0), 2, 1)
            height, width = frame_1.shape[:2]
            TempFrame = cv2.cvtColor(frame_1, cv2.COLOR_BGR2RGB)
            pic = wx.Bitmap.FromBuffer(width, height, TempFrame)
            self.img_car.SetBitmap(pic)

    def track_frame(self):
        tracker = cv2.TrackerMedianFlow_create()
        tracker.init(self.frame, self.track_bbox)

        while self.readVideo:
            flag, self.frame = self.capture.read()
            if not flag:
                break
            self.frame = cv2.resize(self.frame, (640, 360))
            flag, self.track_bbox = tracker.update(self.frame)
            if flag:
                p1 = (int(self.track_bbox[0]), int(self.track_bbox[1]))
                p2 = (int(self.track_bbox[0] + self.track_bbox[2]), int(self.track_bbox[1] + self.track_bbox[3]))
                cv2.rectangle(self.frame, p1, p2, (0, 255, 0), 2, 1)
            else:
                cv2.putText(self.frame, "Tracking failure detected", (50, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 0, 255),
                            2)

            cv2.putText(self.frame, "Center : (" + str(int(self.track_bbox[0])) + ',' + str(int(self.track_bbox[1])) + ")",
                        (10, 20),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 0, 255), 2)

            cv2.putText(self.frame, "Size : " + str(int(self.track_bbox[2] * self.track_bbox[3])), (10, 50),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.75,
                        (0, 0, 255), 2)
            height, width = self.frame.shape[:2]
            self.TempFrame = cv2.cvtColor(self.frame, cv2.COLOR_BGR2RGB)
            pic = wx.Bitmap.FromBuffer(width, height, self.TempFrame)
            self.img_car.SetBitmap(pic)

    def xboxInput(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.JOYBUTTONDOWN:
                    if event.button == 0:
                        if self.readVideo:
                            self.readVideo = False
                            print('stop video')
                        else:
                            self.readVideo = True
                            _thread.start_new_thread(self.videoShow, ())
                            print('start video')
                    elif event.button == 6:
                        if not self.bbox_start and not self.track_start:
                            self.readVideo = False
                            self.bbox_start = True
                            print('stop video')
                            _thread.start_new_thread(self.drawBbox, ())
                            print('start bbox')

                if self.bbox_start:
                    if self.JoyKit.get_button(4):
                        change = 10
                    elif self.JoyKit.get_button(5):
                        change = 100
                    else:
                        change = 1

                    if event.type == pygame.JOYHATMOTION:
                        if event.value == (0, 1):
                            self.y -= change
                        elif event.value == (0, -1):
                            self.y += change
                        elif event.value == (1, 0):
                            self.x += change
                        elif event.value == (-1, 0):
                            self.x -= change
                    elif event.type == pygame.JOYAXISMOTION:
                        if event.axis == 3 and event.value < -0.6:
                            self.a -= change
                        if event.axis == 3 and event.value > 0.6:
                            self.a += change
                        if event.axis == 4 and event.value < -0.6:
                            self.b += change
                        if event.axis == 4 and event.value > 0.6:
                            self.b -= change
                    elif event.type == pygame.JOYBUTTONDOWN:
                        if event.button == 0:
                            self.bbox_start = False
                            self.track_start = True
                            _thread.start_new_thread(self.track_frame, ())
                    self.track_bbox = (self.x, self.y, self.a, self.b)


if __name__ == '__main__':
    app = wx.App()
    frame = window(parent=None, id=-1)
    frame.Show()
    app.MainLoop()
