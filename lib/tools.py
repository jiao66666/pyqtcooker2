import serial
import serial.tools.list_ports
import sys
from lib.boardtype import MICRO_STEP
import ast
from typing import List, Dict, Union


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
       
def parse_speed_params(speed_params_str: str) -> List[Dict[str, Union[float, int]]]:
    """
    将类似 "[(1,360),(2,720),(3,1080)]" 的字符串转换为
    [{"pos": 1.0, "speed": 360}, ...] 的列表字典格式

    参数:
        speed_params_str: 前端传来的字符串

    返回:
        list[dict]: [{"pos": float, "speed": int}, ...]
    
    抛出:
        ValueError: 如果字符串为空或格式不正确
    """
    if not speed_params_str or not speed_params_str.strip():
        raise ValueError("输入不能为空")

    try:
        # 使用 ast.literal_eval 安全解析
        parsed_list = ast.literal_eval(speed_params_str)

        # 检查解析后的数据类型
        if not isinstance(parsed_list, (list, tuple)):
            raise ValueError("格式必须是列表或元组")

        result = []
        for item in parsed_list:
            if not isinstance(item, (list, tuple)) or len(item) != 2:
                raise ValueError(f"每个元素必须是长度为2的元组或列表: {item}")
            
            pos, speed = item
            # 转换数据类型
            pos = float(pos)
            speed = int(speed)
            result.append({"pos": pos, "speed": speed})

        return result

    except (SyntaxError, ValueError, TypeError) as e:
        raise ValueError(f"格式错误: {e}")

if __name__ == "__main__":
    print("=== RS485通信类接口测试 ===")

    testSendDirectly()


    print("\n=== 测试完成 ===")    
