import crcmod
from lib.newstructure.constant import *
class CRCUtil:
    crc16_func = crcmod.mkCrcFun(
        0x18005,
        rev=True,
        initCrc=0xFFFF,
        xorOut=0x0000
    )

    @staticmethod
    def crc16(data: str) -> str:
        return f"{CRCUtil.crc16_func(data.encode('utf-8')):04X}"

    @staticmethod
    def lrc(data: str) -> str:
        total = 0

        start_idx = data.find('#')
        end_idx = data.find('*')

        if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
            for char in data[start_idx:end_idx + 1]:
                total += ord(char)

        checksum = total % 256
        return f"{checksum:02X}"
    

def parse_motor_status(status_str: str):
    """从电机状态字符串中提取状态信息"""
    # 按 * 分隔字符串
    parts = status_str.split('*')
    if len(parts) > 1:
        return parts[1]  # 返回第二个元素
    else:
        return None  # 如果没有 *，返回 None

def parse_motor_pulses(response: str):
    """从电机状态字符串中提取状态信息"""
    # 按 * 分隔字符串
    if response.count('*') == 2:
        # 提取两个 * 之间的部分作为参数
        start_index = response.index('*') + 1  # 第一个 * 后的开始位置
        end_index = response.rindex('*')  # 最后一个 * 的位置
        content = response[start_index:end_index]  # 获取 * 之间的内容

        return content
    else:
        return None   

def circles_to_pulses(circles, step_angle = 1.8, microsteps = MICRO_STEP):
    # 每圈的步数 = 360 / 步距角
    steps_per_revolution = 360 / step_angle
    # 每圈的脉冲数 = 步数 * 细分数
    pulses_per_revolution = steps_per_revolution * microsteps
    # 总脉冲数 = 圈数 * 每圈的脉冲数
    total_pulses = int(circles * pulses_per_revolution)
    return total_pulses     