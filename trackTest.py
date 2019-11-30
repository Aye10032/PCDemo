import wx
import cv2
import _thread
import numpy as np


class window(wx.Frame):
    def __init__(self, parent, id):
        wx.Frame.__init__(self, parent, id, '抢险车上位机', size=(1010, 600),
                          style=wx.CAPTION | wx.MINIMIZE_BOX | wx.CLOSE_BOX | wx.SYSTEM_MENU)
        self.Center()

        icon = wx.Icon('conf/logo.ico', wx.BITMAP_TYPE_ICO)
        self.SetIcon(icon)

        panel = wx.Panel(self)

        self.readVideo = True

        _thread.start_new_thread(self.videoShow(), ())

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


if __name__ == '__main__':
    app = wx.App()
    frame = window(parent=None, id=-1)
    frame.Show()
    app.MainLoop()
