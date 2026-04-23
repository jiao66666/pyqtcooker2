# motionplanner.py

from lib.newstructure.boardtype import *

class MotionPlanner:

    def __init__(self):
        pass
    @staticmethod
    def plan_abs_move(motor, target, current_position, speed):
        """
        把业务目标转换为电机执行参数
        """

        # 1️⃣ 计算位移
        delta = target - current_position

        if delta == 0:
            return None  # 不需要动
        
        if motor.motor_id in [POT1_MOVE_MOTOR,POT2_MOVE_MOTOR] and target < 0:
            return None        

        # 2️⃣ 圈数（你的系统单位）
        circles = abs(delta)

        # 3️⃣ 方向（保持你原逻辑）
        if motor.motor_id in [POT1_MOVE_MOTOR, POT1_FLIP_MOTOR]:
            direction = -1 if delta >= 0 else 1
        else:
            direction = 1 if delta >= 0 else -1

        # 4️⃣ 转 pulses
        circles = abs(delta)

        return {
            "circles": circles,
            "speed": speed,
            "direction": direction
        }