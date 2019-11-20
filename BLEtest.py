import time
import serial

import serial.tools.list_ports

import wx


class window(wx.Frame):
    def __init__(self, parent, id):
        wx.Frame.__init__(self, parent, id, '蓝牙测试', size=(400, 170),
                          style=wx.CAPTION | wx.MINIMIZE_BOX | wx.CLOSE_BOX | wx.SYSTEM_MENU)
        self.Center()

        self.panel = wx.Panel(self)

        self.portx = "COM6"
        self.bps = 9600
        self.timex = 0.2

        self.portxLabel = wx.StaticText(self.panel, -1, '端口', (10, 20), (70, 25), wx.ALIGN_CENTRE)
        self.portxText = wx.TextCtrl(self.panel, -1, 'COM6', (80, 15), (80, 25))

        self.bpsLabel = wx.StaticText(self.panel, -1, '波特率', (10, 50), (70, 25), wx.ALIGN_CENTRE)
        self.bpsText = wx.TextCtrl(self.panel, -1, '9600', (80, 45), (80, 25))

        self.timexLabel = wx.StaticText(self.panel, -1, '延时', (10, 80), (70, 25), wx.ALIGN_CENTRE)
        self.timexText = wx.TextCtrl(self.panel, -1, '0.2', (80, 75), (80, 25))

        self.msgLabel = wx.StaticText(self.panel, -1, '信息', (170, 20), (60, 25), wx.ALIGN_CENTRE)
        self.msgText = wx.TextCtrl(self.panel, -1, '\x13', (230, 15), (80, 25))

        self.btn = wx.Button(self.panel, -1, 'OK', (230, 70), (80, 25))
        self.btn.Bind(wx.EVT_BUTTON, self.connect)

        port_list = list(serial.tools.list_ports.comports())
        if len(port_list) == 0:
            print('无可用串口')
        else:
            for i in range(0, len(port_list)):
                print(port_list[i])

    def receiveimg1(self, event):
        i = 0

        self.portx = self.portxText.GetValue()
        self.bps = int(self.bpsText.GetValue())
        self.timex = float(self.timexText.GetValue())
        ser = serial.Serial(self.portx, self.bps, timeout=self.timex)
        test = '\x51'

        while True:
            # time.sleep(0.2)
            # i += 1
            try:

                # 写数据
                result = ser.write(test.encode('utf-8'))
                print("写总字节数:", result)

                msg = ser.read().hex()
                if msg == 'ff':
                    msg = ser.read(4).hex()
                    print(msg)
                msg = ''

                # ser.close()  # 关闭串口

            except Exception as e:
                print("---异常---：", e)

    def connect(self, event):
        import _thread
        _thread.start_new_thread(self.receiveimg1, (event,))


if __name__ == '__main__':
    app = wx.App()
    frame = window(parent=None, id=-1)
    frame.Show()
    app.MainLoop()
