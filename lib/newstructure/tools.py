import crcmod
from lib.newstructure.constant import *
from lib.newstructure.runtime import runtime
import sys
import random
import time

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




def apply_action_speed_override(
    template_name,
    move_speed=None,
    flip_speed=None,
    move_target=None,
    flip_target=None
):
    """
    根据动作模板，动态覆盖动作参数

    参数:
        move_speed   : move动作 speed
        flip_speed   : flip动作 speed
        move_target  : move动作 target
        flip_target  : flip动作 target
    """

    template = ACTION_PARAMS_KEYLIST[template_name]

    stack = [template]

    while stack:
        current_template = stack.pop()

        for item in current_template:
            action_name = item[1]

            override_data = None

            # move 开头动作
            if action_name.startswith("move"):

                override_data = {}

                if move_speed is not None:
                    override_data["speed"] = move_speed

                if move_target is not None:
                    override_data["target"] = move_target

            # flip 开头动作
            elif action_name.startswith("flip"):

                override_data = {}

                if flip_speed is not None:
                    override_data["speed"] = flip_speed

                if flip_target is not None:
                    override_data["target"] = flip_target

            # 存在有效覆盖数据才更新
            if override_data:
                runtime.set_action_override(
                    action_name,
                    override_data
                )

            # 子动作树
            if len(item) > 2:
                stack.append(item[2])


def get_pot_pos(potnum,postype):
    if potnum == 1:
        if postype == 'pos_outfood':
            print("移动到外倒料口1")
            flip_pos = POT1_POS_OUTFOOD_FLIP
            level_pos = POT1_POS_OUTFOOD_LEVEL
        elif postype == 'pos_infood':
            print("移动到内倒料口1")
            flip_pos = POT1_POS_INFOOD_FLIP
            level_pos = POT1_POS_INFOOD_LEVEL
        elif postype == 'pos_washpot':
            print("移动到洗锅位置1")
            flip_pos = POT1_POS_WASHPOT_FLIP
            level_pos = POT1_POS_WASHPOT_LEVEL
        elif postype == 'pos_firepot':
            flip_pos = POT1_POS_FIREPOT_FLIP
            level_pos = POT1_POS_FIREPOT_LEVEL
            print("移动到灶位1")        
        else:
            print("未知位置")
            flip_pos = 0
            level_pos = 0
    else:
        if postype == 'pos_outfood':
            print("移动到外倒料口2")
            flip_pos = POT2_POS_OUTFOOD_FLIP
            level_pos = POT2_POS_OUTFOOD_LEVEL
        elif postype == 'pos_infood':
            print("移动到内倒料口2")
            flip_pos = POT2_POS_INFOOD_FLIP
            level_pos = POT2_POS_INFOOD_LEVEL
        elif postype == 'pos_washpot':
            print("移动到洗锅位置2")
            flip_pos = POT2_POS_WASHPOT_FLIP
            level_pos = POT2_POS_WASHPOT_LEVEL
        elif postype == 'pos_firepot':
            flip_pos = POT2_POS_FIREPOT_FLIP
            level_pos = POT2_POS_FIREPOT_LEVEL
            print("移动到灶位2")        
        else:
            print("未知位置")
            flip_pos = 0
            level_pos = 0
        
    return {"flip_pos":flip_pos,"level_pos":level_pos}

def is_dev_mode():
    """判断是否是测试环境"""
    return not getattr(sys, 'frozen', False)    


def get_boardlist():
    if is_dev_mode():
        return [
            {
                "name":"stepmotor",
                "port":"COM2",
                "baudrate":19200,
                "timeout":1.0,
                "board_id":BOARDTYPE_FIVE_AXIS
            },
            {
                "name":"feedermotor",
                "port":"COM3",
                "baudrate":19200,
                "timeout":1.0,
                "board_id":BOARDTYPE_FEEDER
            },
            {
                "name":"spinmotor",
                "port":"COM4",
                "baudrate":19200,
                "timeout":1.0,
                "board_id":BOARDTYPE_DC
            }
        ]
    else:
        return [
            {
                "name":"stepmotor",
                "port":"COM6",
                "baudrate":19200,
                "timeout":1.0,
                "board_id":BOARDTYPE_FIVE_AXIS
            },
            {
                "name":"feedermotor",
                "port":"COM7",
                "baudrate":19200,
                "timeout":1.0,
                "board_id":BOARDTYPE_FEEDER
            },
            {
                "name":"spinmotor",
                "port":"COM10",
                "baudrate":19200,
                "timeout":1.0,
                "board_id":BOARDTYPE_DC
            }
        ]
    

def mock_motor_loop(ws_server):
    print("moni data sending.....")
    positions = {1: 0, 2: 0, 3: 0, 4: 0}

    while True:

        data = []

        for motor_id in positions:

            positions[motor_id] += random.randint(5, 30)

            data.append({
                "motor_id": motor_id,
                "position": positions[motor_id]
            })

        ws_server.send(data)

        print("mock send:", data)

        time.sleep(0.2)    

def get_pot_id(motorid):
    if motorid in [POT1_MOVE_MOTOR,POT1_SPIN_MOTOR]:
        return POT1
    else:
        return POT2        