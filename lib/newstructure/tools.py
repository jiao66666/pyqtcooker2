import crcmod
from lib.newstructure.constant import *
from lib.newstructure.runtime import runtime
from lib.newstructure.websocket_runtime import websocket_server

import sys
import random
import time
import re

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


def parse_all_motor_status(response: str):
    """
    解析所有电机状态响应。

    示例：
        #ALLRunStatus,2,0*11111*B8

    返回：
        "11111"

    其中每一位对应一个电机：
        0 -> STOPING
        1 -> PAUSEING
        2 -> ORGING
        3 -> RUNING
        4 -> ERROR
    """

    parts = response.split('*')

    # 正常格式：
    # [协议内容, 状态数据, CRC]
    if len(parts) != 3:
        return None

    status = parts[1].strip()

    # ALLRunStatus 应该返回5路电机状态
    if len(status) != 5:
        return None

    # 每一位都应该是 0~4
    if not all(char in "01234" for char in status):
        return None

    return status


def parse_all_motor_pulses(response: str):
    """
    解析所有电机脉冲数响应。

    示例：
        #ALLPulse,2,0*-1,-122163,-40762,+141152,+111803*5F

    返回：
        "-1,-122163,-40762,+141152,+111803"
    """

    parts = response.split('*')

    # 正常格式：
    # [协议内容, 脉冲数据, CRC]
    if len(parts) != 3:
        return None

    pulse_data = parts[1].strip()

    if not pulse_data:
        return None

    items = pulse_data.split(',')

    # ALLPulse 应该返回5路电机脉冲
    if len(items) != 5:
        return None

    # 验证每个数据确实是整数
    try:
        for item in items:
            int(item.strip())
    except ValueError:
        return None

    return pulse_data


def circles_to_pulses(circles, step_angle = 1.8, microsteps = MICRO_STEP):
    # 每圈的步数 = 360 / 步距角
    steps_per_revolution = 360 / step_angle
    # 每圈的脉冲数 = 步数 * 细分数
    pulses_per_revolution = steps_per_revolution * microsteps
    # 总脉冲数 = 圈数 * 每圈的脉冲数
    total_pulses = int(circles * pulses_per_revolution)
    return total_pulses     


def pulses_to_circles(
        pulses,
        step_angle=1.8,
        microsteps=MICRO_STEP
):
    """
    脉冲转换为旋转圈数

    pulses:
        电机脉冲数，可正可负

    step_angle:
        步进电机步距角，默认1.8度

    microsteps:
        细分数

    return:
        电机旋转圈数，可正可负
    """

    # 每圈基础步数
    steps_per_revolution = 360 / step_angle

    # 每圈脉冲数
    pulses_per_revolution = (
        steps_per_revolution * microsteps
    )

    circles = pulses / pulses_per_revolution

    return round(circles,2)


def apply_action_params_override(template_name, action_params):
    """
    根据动作模板，动态覆盖指定动作的参数。

    参数:
        template_name : 动作模板名称
        action_params : 动作名称与覆盖参数的映射
    """

    template = ACTION_PARAMS_KEYLIST[template_name]

    stack = [template]

    while stack:
        current_template = stack.pop()

        for item in current_template:
            action_name = item[1]

            override_data = action_params.get(action_name)

            if override_data:
                runtime.set_action_override(
                    action_name,
                    override_data
                )

            # 子动作树
            if len(item) > 3 and item[3]:
                stack.append(item[3])


# 按电机类型批量覆盖参数
def apply_action_params_override_bymotortype(template_name, motor_params):
    template = ACTION_PARAMS_KEYLIST[template_name]
    stack = [template]

    while stack:
        current_template = stack.pop()

        for item in current_template:
            motor_type = item[0]
            action_name = item[1]
            override_data = motor_params.get(motor_type)

            if override_data:
                runtime.set_motor_type_action_override(
                    motor_type, action_name, override_data
                )

            if len(item) > 3 and item[3]:
                stack.append(item[3])


def get_pot_pos(potnum,postype):
    if potnum == 1:
        if postype == 'pos_outfood':
            print("移动到外倒料口1")
            flip_pos = POT1_POS_OUTFOOD_FLIP
            level_pos = POT1_POS_OUTFOOD_LEVEL
            msg = "移动到外倒料口1"
        elif postype == 'pos_infood':
            print("移动到内倒料口1")
            flip_pos = POT1_POS_INFOOD_FLIP
            level_pos = POT1_POS_INFOOD_LEVEL
            msg = "移动到内倒料口1"
        elif postype == 'pos_washpot':
            print("移动到洗锅位置1")
            flip_pos = POT1_POS_WASHPOT_FLIP
            level_pos = POT1_POS_WASHPOT_LEVEL
            msg = "移动到洗锅位置1"
        elif postype == 'pos_firepot':
            flip_pos = POT1_POS_FIREPOT_FLIP
            level_pos = POT1_POS_FIREPOT_LEVEL
            print("移动到灶位1") 
            msg = "移动到灶位1"
        else:
            print("未知位置")
            flip_pos = 0
            level_pos = 0
    else:
        if postype == 'pos_outfood':
            print("移动到外倒料口2")
            flip_pos = POT2_POS_OUTFOOD_FLIP
            level_pos = POT2_POS_OUTFOOD_LEVEL
            msg = "移动到外倒料口2"
        elif postype == 'pos_infood':
            print("移动到内倒料口2")
            flip_pos = POT2_POS_INFOOD_FLIP
            level_pos = POT2_POS_INFOOD_LEVEL
            msg = "移动到内倒料口2"
        elif postype == 'pos_washpot':
            print("移动到洗锅位置2")
            flip_pos = POT2_POS_WASHPOT_FLIP
            level_pos = POT2_POS_WASHPOT_LEVEL
            msg = "移动到洗锅位置2"
        elif postype == 'pos_firepot':
            flip_pos = POT2_POS_FIREPOT_FLIP
            level_pos = POT2_POS_FIREPOT_LEVEL
            print("移动到灶位2")        
            msg = "移动到灶位2"
        else:
            print("未知位置")
            flip_pos = 0
            level_pos = 0
            msg = "未知位置"
        
    return {"flip_pos":flip_pos,"level_pos":level_pos,"msg":msg}

def is_dev_mode():
    """判断是否是测试环境"""
    return not getattr(sys, 'frozen', False)    


def get_boardlist():
    if is_dev_mode():
        return [
            {
                "name":"stepmotor",
                "port":DEV_STEP_PORT,
                "baudrate":STEP_BAUT_RATE,
                "timeout":BOARD_TIMEOUT,
                "board_id":BOARDTYPE_STEP
            },
            {
                "name":"feedermotor",
                "port":DEV_FEED_PORT,
                "baudrate":FEED_BAUT_RATE,
                "timeout":BOARD_TIMEOUT,
                "board_id":BOARDTYPE_FEEDER
            },
            {
                "name":"spinmotor",
                "port":DEV_SPIN_PORT,
                "baudrate":STEP_BAUT_RATE,
                "timeout":BOARD_TIMEOUT,
                "board_id":BOARDTYPE_SPIN
            },
            {
                "name":"icemotor",
                "port":DEV_ICE_PORT,
                "baudrate":STEP_BAUT_RATE,
                "timeout":BOARD_TIMEOUT,
                "board_id":BOARDTYPE_ICE
            }
        ]
    else:
        return [
            {
                "name":"stepmotor",
                "port":STEP_PORT,
                "baudrate":STEP_BAUT_RATE,
                "timeout":BOARD_TIMEOUT,
                "board_id":BOARDTYPE_STEP
            },
            {
                "name":"feedermotor",
                "port":FEED_PORT,
                "baudrate":FEED_BAUT_RATE,
                "timeout":BOARD_TIMEOUT,
                "board_id":BOARDTYPE_FEEDER
            },
            {
                "name":"spinmotor",
                "port":SPIN_PORT,
                "baudrate":STEP_BAUT_RATE,
                "timeout":BOARD_TIMEOUT,
                "board_id":BOARDTYPE_SPIN
            },
            {
                "name":"icemotor",
                "port":ICE_PORT,
                "baudrate":STEP_BAUT_RATE,
                "timeout":BOARD_TIMEOUT,
                "board_id":BOARDTYPE_ICE
            }
        ]

#不在前端显示的命令（频率太高，没有必要）    
BLACK_CMDS_LIST = {
    "#ALLRUNSTATUS",#步进电机轮询
    "#ALLPULSE",    #步进电机轮询
    "#RUNSTATUS",   #旋转电机轮询
    "YT+GETFB=1"    #加料电机轮询
}

# 两个锅各自维护自己的当前位置
current_positions = {

    1: {
        "x": 0,
        "y": 0
    },

    2: {
        "x": 0,
        "y": 0
    }

}


def trace_info(info):

       # 新锁控板二进制指令：只打印，不进入旧协议解析
    if isinstance(info, (bytes, bytearray)):
        print(f"[RS485二进制数据] {bytes(info).hex(' ').upper()}")
        data = []
        data.append({
            "type": "command",
            "info": bytes(info).hex(' ').upper(),
            "potid":0
        })
        return

    parts = info.split(",")
    cmd = parts[0].upper()
    board_id= int(parts[1])

    print(f"trace cmd is:{cmd}")
    if cmd in BLACK_CMDS_LIST:
        return

    if cmd == "#RUN" and board_id == BOARDTYPE_STEP:
        pulses = int(parts[3])
        motorid = int(parts[2])
        # 当前属于哪个锅
        potid = get_pot_id(motorid,BOARDTYPE_STEP)
    elif cmd == "#RUN" and board_id == BOARDTYPE_SPIN:
        motorid = int(parts[2])
        potid = get_pot_id(motorid,BOARDTYPE_SPIN)
    else:
        potid = 0    

    data = []
    data.append({
        "type": "command",
        "info": info,
        "potid":potid
    })

    websocket_server.send(data)

    if cmd == "#RUN" and board_id == BOARDTYPE_STEP:

        cordinfo = []

        # 当前锅的位置
        pos = current_positions[potid]

        # 本次移动量
        delta = pulses_to_circles(pulses)

        # -----------------------------
        # Y轴（翻锅）
        # -----------------------------
        if motorid in [
            POT1_FLIP_MOTOR,
            POT2_FLIP_MOTOR
        ]:

            if motorid == POT2_FLIP_MOTOR:
                pos["y"] -= delta
            else:
                pos["y"] += delta

        # -----------------------------
        # X轴（移动）
        # -----------------------------
        elif motorid in [
            POT1_MOVE_MOTOR,
            POT2_MOVE_MOTOR
        ]:

            # 目前两个锅方向一致
            pos["x"] -= delta

        # 发送当前锅轨迹
        corddata = {

            "type": "trajectory",

            "potid": potid,

            "x": round(pos["x"], 2),

            "y": round(pos["y"], 2)

        }

        cordinfo.append(corddata)

        print(
            "发送轨迹:",
            cordinfo
        )

        websocket_server.send(cordinfo)

    # print("ws:executing info", data)


def get_pot_id(motorid,board_id = BOARDTYPE_STEP):
    print(f"get motorid is:{motorid},ready to transform")
    if board_id == BOARDTYPE_STEP:
        if motorid in [POT1_MOVE_MOTOR,POT1_FLIP_MOTOR]:
            return POT1
        else:
            return POT2    
    elif board_id == BOARDTYPE_SPIN:
        if motorid in [POT1_SPIN_MOTOR]:
            return POT1
        else:
            return POT2  
    elif board_id == BOARDTYPE_FEEDER:
        if motorid in [POT1_FLAVORMOTOR1,POT1_FLAVORMOTOR2,POT1_FLAVORMOTOR3,POT1_FLAVORMOTOR4,POT1_FLAVORMOTOR5,POT1_FLAVORMOTOR6,POT1_FLAVORMOTOR7,POT1_FLAVORMOTOR8]:
            return POT1
        else:
            return POT2       
    else:
        return 0       

def build_dc_action(command, direction, dc_speed, dc_time):
    if command == "longrun":
        return "spin_longrun", {
            "direction": direction,
            "speed": dc_speed
        }

    if command == "run":
        return "spin_run", {
            "direction": direction,
            "time": dc_time,
            "speed": dc_speed
        }
    if command == "speed":
        return "spin_speed", {
            "speed": dc_speed
        }

    if command == "speedall":
        return "spin_speedall", {
            "speed": dc_speed
        }
    
    return "dc_stop", {}   


def getTestDCMsg(pot,action,direction):
    
    if action == "spin_longrun":
        astr="长转"
    elif action == "spin_run":
        astr="正常转"
    elif action == "spin_stop":
        astr="停止"  
    elif action == "spin_speed":
        astr="速度"  
    elif action == "spin_speedall":
        astr="批量速度"
        pot="1-2"
    else:
        astr="执行"

    if direction > 0:
        dstr="正向"
    else:
        dstr="负向"

    return f"{pot}号锅{dstr} {astr}"        
            









def validate_board_command(boardtype: str, command: str) -> bool:
    """
    判断主板命令是否符合对应主板的命令格式。

    参数:
        boardtype: 主板类型
            - stepmotor
            - feedermotor

        command: 实际准备发送的命令字符串

    返回:
        True  -> 命令格式合法
        False -> 命令格式不合法
    """

    if not isinstance(boardtype, str):
        return False

    if not isinstance(command, str):
        return False

    boardtype = boardtype.strip().lower()
    command = command.strip()

    if not command:
        return False

    if boardtype == "stepmotor":
        return _validate_stepmotor_command(command)

    elif boardtype == "feedermotor" or boardtype == "spinmotor":
        return _validate_feedermotor_command(command)

    return False


# ============================================================
# StepMotor
# ============================================================

def _validate_stepmotor_command(command: str) -> bool:
    """
    stepmotor ASCII 协议命令格式检查。

    例如：

        #RUN,1,0,2560000,360*49
        #ALLRUN,1,0,32000,1080,32000,1080,-32000,1080,0,0,32000,1080*11
        #ENABLE,1,2*AF
        #SETBaudRate,115200*3C
    """

    # --------------------------------------------------------
    # 基础格式：
    #
    # #COMMAND,...*CHECKSUM
    #
    # StepMotor 校验码为 2 位十六进制
    # --------------------------------------------------------

    match = re.fullmatch(
        r"#([A-Za-z_]+)(?:,([^*]*))?\*([0-9A-Fa-f]{2})",
        command
    )

    if not match:
        return False

    cmd_name = match.group(1)
    param_string = match.group(2)
    checksum = match.group(3)

    params = []

    if param_string is not None:
        params = param_string.split(",")

    # ========================================================
    # 1. RUN
    #
    # #RUN,1,0,2560000,360*49
    #
    # 地址, 电机号, 脉冲数, 速度
    # ========================================================

    if cmd_name == "RUN":
        if len(params) != 4:
            return False

        address, motor, pulse, speed = params

        return (
            _is_uint(address) and
            _is_motor_id(motor) and
            _is_int(pulse) and
            _is_uint(speed)
        )

    # ========================================================
    # 2. ALLRUN
    #
    # #ALLRUN,1,0,
    #   pulse,speed,
    #   pulse,speed,
    #   pulse,speed,
    #   pulse,speed,
    #   pulse,speed
    # ========================================================

    elif cmd_name == "ALLRUN":
        if len(params) != 12:
            return False

        address = params[0]
        reserved = params[1]

        if not _is_uint(address):
            return False

        if not _is_uint(reserved):
            return False

        # 5 个电机，每个 pulse + speed
        for i in range(2, 12, 2):

            pulse = params[i]
            speed = params[i + 1]

            if not _is_int(pulse):
                return False

            if not _is_uint(speed):
                return False

        return True

    # ========================================================
    # 3. LONG
    #
    # #LONG,1,0,-1,360*85
    # ========================================================

    elif cmd_name == "LONG":
        if len(params) != 4:
            return False

        address, motor, value, speed = params

        return (
            _is_uint(address) and
            _is_motor_id(motor) and
            _is_int(value) and
            _is_uint(speed)
        )

    # ========================================================
    # 4. ORGRST
    #
    # #ORGRST,1,1,-2560000,100,720*20
    # ========================================================

    elif cmd_name == "ORGRST":
        if len(params) != 5:
            return False

        address, motor, pulse, limit_pulse, speed = params

        return (
            _is_uint(address) and
            _is_motor_id(motor) and
            _is_int(pulse) and
            _is_uint(limit_pulse) and
            _is_uint(speed)
        )

    # ========================================================
    # 5. ALLORGRST
    #
    # 地址,任意值,
    # pulse,xxx,speed × 5
    # ========================================================

    elif cmd_name == "ALLORGRST":

        if len(params) != 17:
            return False

        address = params[0]
        reserved = params[1]

        if not _is_uint(address):
            return False

        if not _is_uint(reserved):
            return False

        # 5 个电机
        for i in range(2, 17, 3):

            pulse = params[i]
            reserved_value = params[i + 1]
            speed = params[i + 2]

            if not _is_int(pulse):
                return False

            if not _is_uint(reserved_value):
                return False

            if not _is_uint(speed):
                return False

        return True

    # ========================================================
    # 6. SPEED
    #
    # 单电机：
    # #SPEED,1,0,720*3C
    #
    # 全电机：
    # #SPEED,1,0,360,360,360,0,360*E7
    #
    # 根据参数数量区分
    # ========================================================

    elif cmd_name == "SPEED":

        # 单电机
        if len(params) == 3:

            address, motor, speed = params

            return (
                _is_uint(address) and
                _is_motor_id(motor) and
                _is_uint(speed)
            )

        # 所有电机
        elif len(params) == 7:

            address = params[0]
            reserved = params[1]

            if not _is_uint(address):
                return False

            if not _is_uint(reserved):
                return False

            for speed in params[2:]:
                if not _is_uint(speed):
                    return False

            return True

        return False

    # ========================================================
    # 7. ENABLE
    #
    # 单个：
    # #ENABLE,1,2*AF
    #
    # 所有：
    # #ENABLE,1,0,10111*CD
    # ========================================================

    elif cmd_name == "ENABLE":

        if len(params) == 2:

            address, motor = params

            return (
                _is_uint(address) and
                _is_motor_id(motor)
            )

        elif len(params) == 3:

            address, reserved, value = params

            return (
                _is_uint(address) and
                _is_uint(reserved) and
                _is_binary_string(value)
            )

        return False

    # ========================================================
    # STOP / PAUSE
    # ========================================================

    elif cmd_name in ("STOP", "PAUSE"):

        # 单电机
        if len(params) == 2:

            address, motor = params

            return (
                _is_uint(address) and
                _is_motor_id(motor)
            )

        # 所有电机
        elif len(params) == 3:

            address, reserved, value = params

            return (
                _is_uint(address) and
                _is_uint(reserved) and
                _is_binary_string(value)
            )

        return False

    # ========================================================
    # SETAddr
    #
    # #SETAddr,1,2*6F
    # ========================================================

    elif cmd_name == "SETAddr":

        if len(params) != 2:
            return False

        address, new_address = params

        return (
            _is_uint(address) and
            _is_uint(new_address) and
            0 <= int(new_address) <= 65534
        )

    # ========================================================
    # SETBaudRate
    # ========================================================

    elif cmd_name == "SETBaudRate":

        if len(params) != 1:
            return False

        baudrate = params[0]

        return baudrate in {
            "4800",
            "9600",
            "19200",
            "38400",
            "57600",
            "115200",
        }

    # ========================================================
    # SETMotor
    #
    # #SETMotor,1,2,1.8,32,1200,500*09
    # ========================================================

    elif cmd_name == "SETMotor":

        if len(params) != 6:
            return False

        address, motor, step_angle, subdivision, run_current, pause_current = params

        return (
            _is_uint(address) and
            _is_motor_id(motor) and
            _is_float(step_angle) and
            _is_uint(subdivision) and
            _is_uint(run_current) and
            _is_uint(pause_current)
        )

    # ========================================================
    # SETSwitchMode
    # SETRunMode
    # SETEncoderMode
    # SETPulseSave
    # ========================================================

    elif cmd_name in (
        "SETSwitchMode",
        "SETRunMode",
        "SETEncoderMode",
        "SETPulseSave",
    ):

        if len(params) != 3:
            return False

        address, reserved, value = params

        if not _is_uint(address):
            return False

        if not _is_uint(reserved):
            return False

        if not _is_uint(value):
            return False

        # 这些命令实际允许的值不同
        if cmd_name == "SETSwitchMode":
            return int(value) in (0, 1, 2)

        if cmd_name == "SETRunMode":
            return int(value) in (0, 1)

        if cmd_name == "SETEncoderMode":
            return int(value) in (0, 1, 2)

        if cmd_name == "SETPulseSave":
            return int(value) in (0, 1)

    # ========================================================
    # SETEncoderLine
    #
    # #SETEncoderLine,1,0,1000,1000,1000,1000,1000*DB
    # ========================================================

    elif cmd_name == "SETEncoderLine":

        if len(params) != 7:
            return False

        address, reserved = params[:2]

        if not _is_uint(address):
            return False

        if not _is_uint(reserved):
            return False

        for value in params[2:]:
            if not _is_uint(value):
                return False

            if not 100 <= int(value) <= 3000:
                return False

        return True

    # ========================================================
    # SETAccele
    #
    # #SETAccele,1,0,100,100,100,100,100*E0
    # ========================================================

    elif cmd_name == "SETAccele":

        if len(params) != 7:
            return False

        address, reserved = params[:2]

        if not _is_uint(address):
            return False

        if not _is_uint(reserved):
            return False

        for value in params[2:]:

            if not _is_uint(value):
                return False

            if not 50 <= int(value) <= 2000:
                return False

        return True

    # ========================================================
    # Pulse
    # INNum
    # PULSEZero
    # INZero
    #
    # 单电机版本
    # ========================================================

    elif cmd_name in (
        "Pulse",
        "INNum",
        "INZero",
        "PULSEZero",
    ):

        if len(params) != 2:
            return False

        address, motor = params

        return (
            _is_uint(address) and
            _is_motor_id(motor)
        )

    # ========================================================
    # ALLPulse
    # ALLINNum
    #
    # #ALLPulse,1,0*E8
    # ========================================================

    elif cmd_name in (
        "ALLPulse",
        "ALLINNum",
    ):

        if len(params) != 2:
            return False

        address, reserved = params

        return (
            _is_uint(address) and
            _is_uint(reserved)
        )

    # ========================================================
    # ALL INZero / PULSEZero
    #
    # #INZero,1,0,11101*5D
    # #PULSEZero,1,0,11001*4E
    # ========================================================

    elif cmd_name in (
        "ALLINZero",
        "ALLPULSEZero",
    ):
        if len(params) != 3:
            return False

        address, reserved, value = params

        return (
            _is_uint(address) and
            _is_uint(reserved) and
            _is_binary_string(value)
        )

    # ========================================================
    # RunStatus
    # ========================================================

    elif cmd_name == "RunStatus":

        if len(params) != 2:
            return False

        address, motor = params

        return (
            _is_uint(address) and
            _is_motor_id(motor)
        )

    # ========================================================
    # ALLRunStatus
    # Error_Value
    # SwitchStatus
    # ========================================================

    elif cmd_name in (
        "ALLRunStatus",
        "Error_Value",
        "SwitchStatus",
    ):

        if len(params) != 2:
            return False

        address, reserved = params

        return (
            _is_uint(address) and
            _is_uint(reserved)
        )

    # --------------------------------------------------------
    # 未知命令
    # --------------------------------------------------------

    return False


# ============================================================
# Feedermotor
# ============================================================

def _validate_feedermotor_command(command: str) -> bool:
    """
    当前按照用户上传的 YT_LOCKER24 协议进行格式检查。

    注意：
    用户上传的文件实际是 YT_LOCKER24 路锁控板协议，
    如果真正的 feedermotor 协议与此不同，需要替换本方法。
    """

    # 该协议的指令格式为：
    #
    # YT+COMMAND=PARAMS
    #
    # 文档说明章节中的 CRC16 被省略，
    # 实际示例中可能带 *XXXX。
    #
    # 因此这里同时允许：
    #
    # YT+PING=1
    # YT+PING=1*XXXX

    match = re.fullmatch(
        r"YT\+([A-Z]+)(?:\?=|=)([^*]*)(?:\*([0-9A-Fa-f]{4}))?",
        command
    )

    if not match:
        return False

    cmd_name = match.group(1)
    param_string = match.group(2)

    params = param_string.split(",") if param_string else []

    # ========================================================
    # PING
    #
    # YT+PING=1
    # ========================================================

    if cmd_name == "PING":
        return (
            len(params) == 1 and
            _is_uint(params[0])
        )

    # ========================================================
    # REBOOT
    #
    # YT+REBOOT=1
    # ========================================================

    elif cmd_name == "REBOOT":
        return (
            len(params) == 1 and
            _is_uint(params[0])
        )

    # ========================================================
    # OPENLOCK
    #
    # YT+OPENLOCK=board_id,channel
    #
    # 或：
    #
    # YT+OPENLOCK=board_id,channel,overtime,mode,level,interval
    # ========================================================

    elif cmd_name == "OPENLOCK":

        if len(params) not in (2, 3, 4, 5, 6):
            return False

        if not _is_uint(params[0]):
            return False

        if not _is_channel(params[1]):
            return False

        # 后面的参数允许省略，但如果出现必须合法
        if len(params) >= 3:
            if not _is_uint(params[2]):
                return False

        if len(params) >= 4:
            if params[3] not in ("0", "1"):
                return False

        if len(params) >= 5:
            if params[4] not in ("0", "1"):
                return False

        if len(params) >= 6:
            if not _is_uint(params[5]):
                return False

        return True

    # ========================================================
    # GETFB
    #
    # YT+GETFB=board_id,channel
    # YT+GETFB=board_id,channel,mode
    # YT+GETFB=board_id,channel,mode,level
    # ========================================================

    elif cmd_name == "GETFB":

        if len(params) not in (2, 3, 4):
            return False

        if not _is_uint(params[0]):
            return False

        if not _is_channel(params[1]):
            return False

        if len(params) >= 3 and params[2] not in ("0", "1"):
            return False

        if len(params) >= 4 and params[3] not in ("0", "1"):
            return False

        return True

    # ========================================================
    # OUTPUT
    #
    # YT+OUTPUT=board,channel,enable
    # YT+OUTPUT=board,channel,enable,overtime
    # ========================================================

    elif cmd_name == "OUTPUT":

        if len(params) not in (3, 4):
            return False

        if not _is_uint(params[0]):
            return False

        if not _is_channel(params[1]):
            return False

        if params[2] not in ("0", "1"):
            return False

        if len(params) == 4 and not _is_uint(params[3]):
            return False

        return True

    # ========================================================
    # GETOUT
    # ========================================================

    elif cmd_name == "GETOUT":

        return (
            len(params) == 2 and
            _is_uint(params[0]) and
            _is_channel(params[1])
        )

    # ========================================================
    # PWM
    #
    # YT+PWM=board,channel,high,low
    # YT+PWM=board,channel,high,low,polarity,times
    # ========================================================

    elif cmd_name == "PWM":

        if len(params) not in (4, 6):
            return False

        if not _is_uint(params[0]):
            return False

        if not _is_channel(params[1]):
            return False

        if not _is_uint(params[2]):
            return False

        if not _is_uint(params[3]):
            return False

        if len(params) == 6:

            if params[4] not in ("0", "1"):
                return False

            if not _is_uint(params[5]):
                return False

        return True

    # ========================================================
    # CHECKSUM
    #
    # YT+CHECKSUM=board,enable
    #
    # 查询：
    #
    # YT+CHECKSUM?=board
    # ========================================================

    elif cmd_name == "CHECKSUM":

        if len(params) == 2:

            return (
                _is_uint(params[0]) and
                params[1] in ("0", "1")
            )

        elif len(params) == 1:

            return _is_uint(params[0])

        return False

    # ========================================================
    # BAUDRATE
    # ========================================================

    elif cmd_name == "BAUDRATE":

        if len(params) != 2:
            return False

        if not _is_uint(params[0]):
            return False

        # 文档给出的范围 9600 - 115200
        try:
            baudrate = int(params[1])
        except ValueError:
            return False

        return 9600 <= baudrate <= 115200

    # ========================================================
    # DEFLOCK
    #
    # 设置：
    # board,overtime,mode,level,interval
    #
    # 查询：
    # board
    # ========================================================

    elif cmd_name == "DEFLOCK":

        if len(params) == 1:
            return _is_uint(params[0])

        if len(params) != 5:
            return False

        board, overtime, mode, level, interval = params

        return (
            _is_uint(board) and
            _is_uint(overtime) and
            int(overtime) > 0 and
            mode in ("0", "1") and
            level in ("0", "1") and
            _is_uint(interval)
        )

    # ========================================================
    # LKREPORT
    #
    # 设置：
    # YT+LKREPORT=board,enable
    #
    # 查询：
    # YT+LKREPORT?=board
    # ========================================================

    elif cmd_name == "LKREPORT":

        if len(params) == 1:
            return _is_uint(params[0])

        if len(params) == 2:
            return (
                _is_uint(params[0]) and
                params[1] in ("0", "1")
            )

        return False

    return False


# ============================================================
# 通用参数检查
# ============================================================

def _is_uint(value: str) -> bool:
    """非负整数"""
    return bool(re.fullmatch(r"\d+", value))


def _is_int(value: str) -> bool:
    """整数，可正可负"""
    return bool(re.fullmatch(r"-?\d+", value))


def _is_float(value: str) -> bool:
    """浮点数，例如 1.8 / 2 / 0.5"""
    return bool(re.fullmatch(r"-?\d+(?:\.\d+)?", value))


def _is_motor_id(value: str) -> bool:
    """
    电机号。

    你的 stepmotor 是 5 路电机，
    所以电机号应该是 0~4。
    """

    if not _is_uint(value):
        return False

    motor_id = int(value)

    return 0 <= motor_id <= 4


def _is_binary_string(value: str) -> bool:
    """
    检查类似：
        10111
        10011
        00100
    """

    return bool(re.fullmatch(r"[01]+", value))


def _is_channel(value: str) -> bool:
    """
    锁控板通道格式：

        1
        1&3&5
        1-5
    """

    # 单通道
    if re.fullmatch(r"\d+", value):
        channel = int(value)
        return 1 <= channel <= 24

    # 多通道：1&3&5
    if re.fullmatch(r"\d+(?:&\d+)+", value):

        channels = value.split("&")

        return all(
            1 <= int(channel) <= 24
            for channel in channels
        )

    # 范围：1-5
    match = re.fullmatch(r"(\d+)-(\d+)", value)

    if match:

        start = int(match.group(1))
        end = int(match.group(2))

        return (
            1 <= start <= 24 and
            1 <= end <= 24 and
            start <= end
        )

    return False



def get_task_resources(task_name, pot_id=None):
    """
    根据动作组名称获取需要占用的全部电机资源。

    pot_id:
        1 或 2：锅动作组
        None：冰柜动作组
    """
    template = ACTION_PARAMS_KEYLIST.get(task_name)

    if template is None:
        raise ValueError(f"未知的动作组：{task_name}")

    if pot_id is not None:
        motor_resource_map = POT_MOTOR_RESOURCE_MAP.get(pot_id)

        if motor_resource_map is None:
            raise ValueError(f"无效的锅编号：{pot_id}")
    else:
        motor_resource_map = ICE_MOTOR_RESOURCE_MAP

    resources = set()

    def collect_resources(items):
        for item in items:
            motor_key = item[0]

            if motor_key not in motor_resource_map:
                raise ValueError(
                    f"动作组 {task_name} 中的电机标识 "
                    f"{motor_key} 没有对应的资源映射"
                )

            resources.add(motor_resource_map[motor_key])

            if len(item) > 3 and isinstance(item[3], list):
                collect_resources(item[3])

    collect_resources(template)

    return resources