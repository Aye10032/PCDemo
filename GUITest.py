import time

import serial.tools.list_ports

import pygame
import serial
import wx
import cv2
import zmq
import base64
import numpy as np

(major_ver, minor_ver, subminor_ver) = cv2.__version__.split('.')


class window(wx.Frame):
    def __init__(self, parent, id):
        wx.Frame.__init__(self, parent, id, '抢险车上位机', size=(1010, 600),
                          style=wx.CAPTION | wx.MINIMIZE_BOX | wx.CLOSE_BOX | wx.SYSTEM_MENU)
        self.Center()

        panel = wx.Panel(self)

        img1 = wx.Image('conf/car.png', wx.BITMAP_TYPE_ANY).ConvertToBitmap()
        img2 = wx.Image('conf/hand.png', wx.BITMAP_TYPE_ANY).ConvertToBitmap()

        self.img_car = wx.StaticBitmap(panel, -1, img1, pos=(10, 10), size=(480, 360))
        self.img_hand = wx.StaticBitmap(panel, -1, img2, pos=(500, 10), size=(480, 360))

        self.ipLable = wx.StaticText(panel, -1, 'IP', (20, 405), (30, 20))
        self.ipText = wx.TextCtrl(panel, -1, 'tcp://192.168.2.192:5555', (55, 400), (230, 25))
        self.startbtn = wx.Button(panel, -1, '连接', pos=(300, 400), size=(70, 25))
        self.Bind(wx.EVT_BUTTON, self.start, self.startbtn)

        self.portLable = wx.StaticText(panel, -1, 'prot', (20, 445), (30, 20))
        self.portText = wx.TextCtrl(panel, -1, 'COM9', (55, 440), (60, 25))
        self.bpsLable = wx.StaticText(panel, -1, 'pbs', (160, 445), (30, 20))
        self.list = ['300', '600', '1200', '2400', '4800', '9600', '19200', '38400', '43000', '56000', '57600',
                     '115200']
        self.bpsText = wx.ComboBox(panel, -1, value='9600', choices=self.list, pos=(190, 440), size=(70, 25))
        self.BLEbtn = wx.Button(panel, -1, '连接', pos=(300, 440), size=(70, 25))
        self.Bind(wx.EVT_BUTTON, self.connble, self.BLEbtn)

        wx.StaticText(panel,-1,'温度：',(500,405),(40,20))

        # 相关数据
        self.light_status = 0
        self.moment_mode = 0
        self.bleFlag = False
        self.CCTV_flag = True

        self.frame_car = None
        self.frame_hand = None

        self.RT_temp = 0

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

        # 蓝牙部分
        port_list = list(serial.tools.list_ports.comports())
        if len(port_list) == 0:
            print('无可用串口')
            self.bleFlag = False
        else:
            for i in range(0, len(port_list)):
                print(port_list[i])

        self.portx = "COM9"
        self.bps = '9600'
        self.timex = 0.2
        self.ser = None

    def receiveimg1(self, event):
        context = zmq.Context()

        hand_socket = context.socket(zmq.SUB)
        hand_socket.connect('tcp://192.168.2.192:5555')
        hand_socket.setsockopt_string(zmq.SUBSCRIBE, np.unicode(''))

        while self.CCTV_flag:
            source_hand = hand_socket.recv_string()
            img = base64.b64decode(source_hand)
            npimg = np.fromstring(img, dtype=np.uint8)
            frame = cv2.imdecode(npimg, 1)

            self.frame_car = frame[0:360, 0:480]
            self.frame_hand = frame[0:360, 480:960]
            height1, width1 = self.frame_hand.shape[:2]
            height2, width2 = self.frame_car.shape[:2]
            print(height2, width2)
            self.frame_hand = cv2.cvtColor(self.frame_hand, cv2.COLOR_BGR2RGB)
            pic_hand = wx.Bitmap.FromBuffer(width1, height1, self.frame_hand)
            self.frame_car = cv2.cvtColor(self.frame_car, cv2.COLOR_BGR2RGB)
            pic_car = wx.Bitmap.FromBuffer(width2, height2, self.frame_car)
            self.img_hand.SetBitmap(pic_hand)
            self.img_car.SetBitmap(pic_car)

    def receiveimg2(self, event):
        context = zmq.Context()

        hand_socket = context.socket(zmq.SUB)
        hand_socket.connect('tcp://192.168.2.192:5555')
        hand_socket.setsockopt_string(zmq.SUBSCRIBE, np.unicode(''))

        # cv追踪部分
        tracker_types = ['BOOSTING', 'MIL', 'KCF', 'TLD', 'MEDIANFLOW', 'GOTURN']
        tracker_type = tracker_types[4]

        if int(minor_ver) < 3:
            tracker = cv2.Tracker_create(tracker_type)
        else:
            if tracker_type == 'BOOSTING':
                tracker = cv2.TrackerBoosting_create()
            if tracker_type == 'MIL':
                tracker = cv2.TrackerMIL_create()
            if tracker_type == 'KCF':
                tracker = cv2.TrackerKCF_create()
            if tracker_type == 'TLD':
                tracker = cv2.TrackerTLD_create()
            if tracker_type == 'MEDIANFLOW':
                tracker = cv2.TrackerMedianFlow_create()
            if tracker_type == 'GOTURN':
                tracker = cv2.TrackerGOTURN_create()

        x = 100
        y = 100
        a = 10
        b = 10

        while not self.CCTV_flag:
            source_hand = hand_socket.recv_string()
            img = base64.b64decode(source_hand)
            npimg = np.fromstring(img, dtype=np.uint8)
            frame = cv2.imdecode(npimg, 1)
            self.frame_hand = frame[0:360, 480:960]
            self.frame_hand = cv2.flip(self.frame_hand, 0)
            height1, width1 = self.frame_hand.shape[:2]

            for event in pygame.event.get():
                if event.type == pygame.JOYHATMOTION:
                    if event.value == (0, 1):
                        y += 1
                    elif event.value == (0, -1):
                        y -= 1
                    elif event.value == (1, 0):
                        x += 1
                    elif event.value == (-1, 0):
                        x -= 1
                elif event.type == pygame.JOYBUTTONDOWN:
                    if event.value == 4:
                        if self.JoyKit.get_axis(5) > -0.6:
                            a += 1
                        elif self.JoyKit.get_axis(2) > -0.6:
                            a -= 1
                    elif event.value == 5:
                        if self.JoyKit.get_axis(5) > -0.6:
                            b += 1
                        elif self.JoyKit.get_axis(2) > -0.6:
                            b -= 1

            bbox = (x, y, a, b)  # 横，纵，宽，高
            p1 = (int(bbox[0]), int(bbox[1]))
            p2 = (int(bbox[0] + bbox[2]), int(bbox[1] + bbox[3]))
            cv2.rectangle(self.frame_hand, p1, p2, (0, 255, 0), 2, 1)
            height1, width1 = self.frame_hand.shape[:2]
            self.frame_hand = cv2.cvtColor(self.frame_hand, cv2.COLOR_BGR2RGB)
            pic_hand = wx.Bitmap.FromBuffer(width1, height1, self.frame_hand)

    def start(self, event):
        import _thread
        _thread.start_new_thread(self.receiveimg1, (event,))

    def connble(self, event):
        self.portx = self.portText.GetValue()
        self.bps = self.bpsText.GetValue()
        self.ser = serial.Serial(self.portx, self.bps, timeout=self.timex)
        self.bleFlag = True

    def sendMSG(self, msg, msgx):
        print(msg)
        if self.bleFlag:
            self.ser.write(msgx.encode('utf-8'))

    def xbox_input(self):
        cut_off = 0.2
        while True:
            time.sleep(0.02)
            if self.bleFlag:
                msg = self.ser.read().hex()
                if msg == 'ff':
                    msg = self.ser.read(4).hex()
                    print(msg)
                msg = ''
            for event in pygame.event.get():
                if event.type == pygame.JOYHATMOTION:
                    if self.moment_mode == 0:
                        # 车灯
                        if event.value == (0, 1):
                            if self.light_status == 0:
                                self.sendMSG(50, '\x50')
                                self.light_status = 1
                            elif self.light_status == 1:
                                self.sendMSG(51, '\x51')
                                self.light_status = 0
                elif event.type == pygame.JOYBUTTONDOWN:
                    if event.button == 7:
                        # 切换至抓取模式
                        if self.moment_mode == 0:
                            self.moment_mode = 1
                            self.sendMSG(47, '\x47')
                        elif self.moment_mode == 1:
                            self.moment_mode = 0
                    elif event.button == 4:
                        # 刹车
                        if self.moment_mode == 0:
                            self.sendMSG(47, '\x47')
                    elif event.button == 5:
                        # 精准模式
                        cut_off = 0.7
                    elif event.button == 1:
                        # 保存当前摄像头图像
                        frame_hand = cv2.cvtColor(self.frame_hand, cv2.COLOR_BGR2RGB)
                        frame_car = cv2.cvtColor(self.frame_car, cv2.COLOR_BGR2RGB)
                        cv2.imwrite('conf/car.png', frame_car)
                        cv2.imwrite('conf/hand.png', frame_hand)
                    elif event.button == 6:
                        # 自动追踪开启
                        if self.moment_mode == 1:
                            self.CCTV_flag = False
                            import _thread
                            _thread.start_new_thread(self.receiveimg2, (event,))
                elif event.type == pygame.JOYBUTTONUP:
                    if event.button == 5:
                        # 退出精准模式
                        cut_off = 0.2

            # 行车模式
            if self.moment_mode == 0:
                # 变速
                speed_level = (self.JoyKit.get_axis(5) + 1) * 50
                if speed_level >= 66.66:
                    self.sendMSG(48, '\x48')
                elif 33.33 <= speed_level < 66.66:
                    self.sendMSG(49, '\x49')
                elif 5 < speed_level < 33.33:
                    self.sendMSG(52, '\x52')
                # 前进后退
                elif self.JoyKit.get_axis(1) > cut_off:
                    self.sendMSG(44, '\x44')
                elif self.JoyKit.get_axis(1) < -cut_off:
                    self.sendMSG(43, '\x43')
                # 左右转
                elif self.JoyKit.get_axis(0) > cut_off:
                    self.sendMSG(45, '\x45')
                elif self.JoyKit.get_axis(0) < -cut_off:
                    self.sendMSG(46, '\x46')
                # 手部上下
                elif self.JoyKit.get_axis(4) > cut_off:
                    self.sendMSG(56, '\x56')
                elif self.JoyKit.get_axis(4) < -cut_off:
                    self.sendMSG(55, '\x55')
                # 手部左右
                elif self.JoyKit.get_axis(3) > cut_off:
                    self.sendMSG(54, '\x54')
                elif self.JoyKit.get_axis(3) < -cut_off:
                    self.sendMSG(53, '\x53')
            # 抓取模式
            elif self.moment_mode == 1:
                if self.CCTV_flag:
                    # 抓握
                    if self.JoyKit.get_axis(5) > -0.6:
                        self.sendMSG(31, '\x31')
                    elif self.JoyKit.get_axis(2) > -0.6:
                        self.sendMSG(32, '\x32')
                    # 整体前后
                    elif self.JoyKit.get_axis(1) > cut_off:
                        self.sendMSG(37, '\x37')
                        time.sleep(1)
                    elif self.JoyKit.get_axis(1) < -cut_off:
                        self.sendMSG(38, '\x38')
                        time.sleep(1)
                    # 整体左右
                    elif self.JoyKit.get_axis(0) > cut_off:
                        self.sendMSG(42, '\x42')
                        time.sleep(1)
                    elif self.JoyKit.get_axis(0) < -cut_off:
                        self.sendMSG(41, '\x41')
                        time.sleep(1)
                    # 手部上下
                    elif self.JoyKit.get_axis(4) > cut_off:
                        self.sendMSG(35, '\x35')
                    elif self.JoyKit.get_axis(4) < -cut_off:
                        self.sendMSG(36, '\x36')
                    # 手部左右
                    elif self.JoyKit.get_axis(3) > cut_off:
                        self.sendMSG(34, '\x34')
                    elif self.JoyKit.get_axis(3) < -cut_off:
                        self.sendMSG(33, '\x33')


if __name__ == '__main__':
    app = wx.App()
    frame = window(parent=None, id=-1)
    frame.Show()
    app.MainLoop()
