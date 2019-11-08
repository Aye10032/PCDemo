import time

import serial  # 导入模块

i = 0

while not (i == 20):
    time.sleep(0.2)
    i += 1
    try:
        portx = "COM6"
        bps = '9600'
        timex = 0.2
        ser = serial.Serial(portx, bps, timeout=timex)
        test = '\x31'

        # 写数据
        result = ser.write(test.encode('utf-8'))
        print("写总字节数:", result)

        ser.close()  # 关闭串口

    except Exception as e:
        print("---异常---：", e)
