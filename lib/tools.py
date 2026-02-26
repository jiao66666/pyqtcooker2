import serial
import serial.tools.list_ports
import sys
from lib.boardtype import MICRO_STEP

def is_dev_mode():
    """判断是否是测试环境"""
    return not getattr(sys, 'frozen', False)

def circles_to_pulses(circles, step_angle = 1.8, microsteps = MICRO_STEP):
    # 每圈的步数 = 360 / 步距角
    steps_per_revolution = 360 / step_angle
    # 每圈的脉冲数 = 步数 * 细分数
    pulses_per_revolution = steps_per_revolution * microsteps
    # 总脉冲数 = 圈数 * 每圈的脉冲数
    total_pulses = int(circles * pulses_per_revolution)
    return total_pulses


def list_ports():
    ports = serial.tools.list_ports.comports()
    for port in ports:
        print(f"设备: {port.device}, 描述: {port.description}, PID/VID: {port.pid}/{port.vid}")

def testSendDirectly():
    s= serial.Serial(
        port='COM6',
        baudrate=115200,
        bytesize=serial.EIGHTBITS,
        parity=serial.PARITY_NONE,
        stopbits=serial.STOPBITS_ONE,
        timeout=1.0
    )
    cmd = '#ENABLE,1,0,11111*CE'
    s.write(cmd.encode('utf-8'))
    s.flush()
    res = s.readall().decode()
    print(res)
    s.close()
       


if __name__ == "__main__":
    print("=== RS485通信类接口测试 ===")

    testSendDirectly()


    print("\n=== 测试完成 ===")    
