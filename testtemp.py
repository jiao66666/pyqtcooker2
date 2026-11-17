import serial
import time

port = serial.Serial(
    "COM19",
    921600,
    timeout=0.1
)

try:
    print("串口打开成功")
    start_time = time.time()

    while time.time() - start_time < 10:
        data = port.read(port.in_waiting or 1)

        if data:
            print(data)

    print("测试结束")

finally:
    port.close()