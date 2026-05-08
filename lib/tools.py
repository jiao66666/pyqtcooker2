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


def test_ease_in_out_move_smooth_curve_bytime(start_pos, target_pos, max_speed, interval=0.1):

    distance = abs(target_pos - start_pos)
    distance_deg = distance * 360

    avg_speed = max_speed * 2/3   # 因为这个曲线平均值是 2/3
    total_time = distance_deg / avg_speed

    direction = 1 if target_pos > start_pos else -1
    start_time = time.time()

    while True:
        t = time.time() - start_time
        if t >= total_time:
            break

        p = t / total_time

        # 真正的速度比例函数
        speed_ratio = 4 * p * (1 - p)

        speed = max_speed * speed_ratio * direction

        print(f"p={p:.3f}, speed_ratio={speed_ratio:.3f}, speed={speed:.1f}")

        time.sleep(interval)

    print("finished")


# 初始化位置

_current_pos = None

def get_current_position(start_pos, target_pos, max_speed=1, interval=0.05,acc_bound=0.4,dec_bound=0.8):
    """
    模拟实时位置输出，基于 S 曲线加速-减速规律
    start_pos, target_pos: 圈数
    max_speed: 最大速度，角度/秒（单位：度）
    interval: 时间步长
    返回当前位置（圈数）
    """
    global _current_pos

    # 第一次调用初始化
    if _current_pos is None:
        _current_pos = start_pos  # 初始化位置为起点

    direction = 1 if target_pos > start_pos else -1
    total_distance = abs(target_pos - start_pos)  # 计算总的圈数差

    # 剩余距离
    remaining_distance = target_pos - _current_pos
    if direction * remaining_distance <= 0:
        _current_pos = target_pos  # 达到目标位置，退出
        return _current_pos

   # 根据起始位置和目标位置计算进度比例
    if direction > 0:
        # 正向运动：start_pos < target_pos
        ratio = (_current_pos - start_pos) / total_distance
    else:
        # 反向运动：start_pos > target_pos
        ratio = (start_pos - _current_pos) / total_distance

    ratio = max(0, min(1, ratio))  # 限制在0~1

    # 根据比例来控制运动曲线
    if ratio < acc_bound:
        # 起步快
        speed_ratio = 0.5 + 0.5 * (ratio / 0.4)  # 线性快速上升到 1
    elif ratio < dec_bound:
        # 中段保持接近最大速度
        speed_ratio = 1.0
    else:
    # 后段缓慢减速
        deceleration_range = 1.0 - dec_bound  # 调整减速区间的长度
        speed_ratio = (1.0 - ratio) / deceleration_range
        speed_ratio = max(speed_ratio, 0.05)  # 防止减速太慢
# --------------------------

    # 当前速度（根据S曲线公式）
    # max_speed是角度/秒，将其转换为圈/秒 (即 max_speed / 360)
    current_speed = (max_speed / 360) * speed_ratio  # 当前速度（圈/秒）

    # 最大速度限制
    current_speed = min(current_speed, max_speed / 360)

    # 最小速度保护
    min_speed = 360 / 360  # 最小速度也要转换为圈/秒
    if current_speed < min_speed:
        current_speed = min_speed

    # 更新位置
    _current_pos += current_speed * interval * direction  # 更新位置

    # 避免超出目标
    if direction > 0 and _current_pos > target_pos:
        _current_pos = target_pos
    elif direction < 0 and _current_pos < target_pos:
        _current_pos = target_pos

    # 输出当前位置信息（调试用）
    print(f"当前比例{ratio},当前速度比{speed_ratio}当前位置: {_current_pos:.2f} 圈, 当前速度: {current_speed*360:.2f} 度/秒")

    return _current_pos

# 测试代码：调用 get_current_position 方法来模拟位置的变化
def test_get_current_position(start_pos, target_pos, max_speed=1, interval=0.1,acc_bound=0.4,dec_bound=0.8):
    """
    测试 get_current_position 函数，观察位置如何变化
    :param start_pos: 起点位置（圈数）
    :param target_pos: 目标位置（圈数）
    :param max_speed: 最大速度（角度/秒）
    :param interval: 循环更新时间（秒）
    """
    print("开始测试：")
    while True:
        # 获取当前位置
        current_pos = get_current_position(start_pos, target_pos, max_speed, interval,acc_bound,dec_bound)
        # print(f"当前位置: {current_pos:.2f} ")

        # 判断是否到达目标
        if (target_pos > start_pos and current_pos >= target_pos) or (target_pos < start_pos and current_pos <= target_pos):
            print("到达目标位置！")
            break

        time.sleep(interval)



def test_ease_in_out_move_smooth_curve_bypos(start_pos, target_pos, max_speed, interval=0.05): 
    """
    基于当前位置的加速-减速平滑运动（带最小速度保护）
    """
    total_distance = abs(target_pos - start_pos)  # 直接用圈单位
    direction = 1 if target_pos > start_pos else -1

    while True:
        # 获取当前位置（圈单位）

        current_pos = get_current_position(start_pos, target_pos, max_speed, interval)

        # 判断是否到达目标
        remaining_distance = target_pos - current_pos  # 保持圈单位
        if direction * remaining_distance <= 0:
            print("到达目标位置，速度设0")
            break

        # 计算当前位置比例
        # 根据起始位置和目标位置计算进度比例
        if direction > 0:
            # 正向运动：start_pos < target_pos
            ratio = (_current_pos - start_pos) / total_distance
        else:
            # 反向运动：start_pos > target_pos
            ratio = (start_pos - _current_pos) / total_distance

        ratio = max(0, min(1, ratio))  # 限制在0~1

        # 根据比例来控制运动曲线
        if ratio < 0.4:
            # 起步快
            speed_ratio = 0.5 + 0.5 * (ratio / 0.4)  # 线性快速上升到 1
        elif ratio < 0.8:
            # 中段保持接近最大速度
            speed_ratio = 1.0
        else:
            # 后段缓慢减速
            speed_ratio = (1.0 - ratio) / 0.2
            speed_ratio = max(speed_ratio, 0.05)  # 防止减速太慢

            # max_speed是角度/秒，将其转换为圈/秒 (即 max_speed / 360)
        current_speed = (max_speed / 360) * speed_ratio  # 当前速度（圈/秒）

        # 最大速度限制
        current_speed = min(current_speed, max_speed / 360)

        # 最小速度保护
        min_speed = 1 / 360  # 最小速度也要转换为圈/秒
        if current_speed < min_speed:
            current_speed = min_speed

        if current_speed > 0:
           # self.adjust_speed(int(current_speed))
           print(f"当前比例: {ratio:.3f}, 速度比例: {speed_ratio:.3f}, 当前角速度: {current_speed * 360:.2f},当前位置:{current_pos:.2f}")
        time.sleep(interval)

    print("finished")

# 运行测试
#test_ease_in_out_move_smooth_curve_bypos(20, -10, 2520, 0.05)  # 测试大速度情况
#test_get_current_position(0, 4.16, 2160, 0.05,0.1,0.9)  # 测试低速度情况