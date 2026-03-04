import serial
import serial.tools.list_ports
import sys
from lib.boardtype import MICRO_STEP
import ast
from typing import List, Dict, Union
import time


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





def generate_linear_speed_params(init_position,target_position, num_nodes, target_speed, initial_speed=90):
    """
    生成速度-位置节点，处理速度线性增长 或者 减少的情况 ，生成线性增加（位置，速度）或线性递减速（位置，速度）的节点列表
    :param init_position: 目标位置（最大位置）
    :param target_position: 目标位置（最大位置）
    :param num_nodes: 节点个数
    :param target_speed: 目标速度（最大速度）
    :param initial_speed: 初始速度，默认从 90 开始
    :return: 生成的[(position, speed)]节点列表
    """
    if target_position > init_position:
        direction = 1
    else:
        direction = -1
      
    start_point = init_position
    start_speed = initial_speed
 
    # 计算每个位置的间隔
    # 计算每个位置的间隔
    distance = abs(target_position - init_position)
    distance_space = distance / (num_nodes - 1)

    speed_diff = abs(target_speed - initial_speed)
    speed_space = speed_diff / (num_nodes - 1)

    # 生成节点列表
    speed_profile = []

    for i in range(num_nodes):
        
        position = start_point + i * distance_space * direction
        speed = start_speed + i * speed_space * direction

        #print("计算过程：",position,speed,direction,start_point,start_speed)
        # 将位置和速度组成元组，添加到节点列表中
        speed_profile.append((round(position,2), int(speed)))
    
    return parse_speed_params(str(speed_profile[:-1]))


def ease_in_out_move_smooth(start_pos, target_pos, max_speed, send_speed_func, interval=0.02):
    """
    平滑 Easy-In-Out 动态调速
    start_pos: 起始位置（度）
    target_pos: 目标位置（度）
    max_speed: 最大速度（度/秒）
    send_speed_func: 发送速度信号的函数
    interval: 每次更新速度的时间间隔（秒）
    """
    # 总位移和方向
    distance = abs(target_pos - start_pos)
    direction = 1 if target_pos > start_pos else -1

    # 粗略估算总时间
    # 假设加速+减速阶段占总位移比例 60%，匀速阶段占 40%
    # total_time = total_distance / (平均速度)
    # 平均速度约取 max_speed * 0.7
    avg_speed = max_speed * 0.7
    total_time = distance / avg_speed

    start_time = time.time()

    while True:
        t = time.time() - start_time
        if t >= total_time:
            break

        # 归一化时间 0~1
        p = t / total_time

        # 使用三次平滑函数 cubic ease-in-out
        if p < 0.5:
            speed_ratio = 4 * p**3  # 加速阶段
        else:
            speed_ratio = 1 - ((-2*p + 2)**3) / 2  # 减速阶段

        speed = max_speed * speed_ratio * direction

        send_speed_func(speed)

        time.sleep(interval)


