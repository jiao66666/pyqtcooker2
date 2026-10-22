# motionplanner.py

from lib.newstructure.constant import *

class MotionPlanner:

    def __init__(self):
        pass
    @staticmethod
    def plan_abs_move(motor, target, current_position, speed):
        """
        电机绝对值目标为移动
        """
        # 0 预处理
        #if not motor.homed:
        #    print("没有归零")
        #    return False

        print(f"当前位置:{current_position},目标位置:{target}")
        # 1 计算位移
        delta = target - current_position

        if motor.board_id == BOARDTYPE_STEP and motor.motor_id in [POT1_MOVE_MOTOR,POT2_MOVE_MOTOR] and target < 0:
            print("计算位移出错！！！！》》》")
            return None        

        if motor.board_id == BOARDTYPE_ICE and target < 0:
            print("目标值非法")
            return None
        
        # 2️ 圈数
        circles = abs(delta)

        # 3️方向
        if motor.board_id == BOARDTYPE_STEP:
            if motor.motor_id in [POT1_MOVE_MOTOR, POT1_FLIP_MOTOR]:
                direction = -1 if delta >= 0 else 1
            else:
                direction = 1 if delta >= 0 else -1
        elif motor.board_id == BOARDTYPE_ICE:
            if motor.motor_id in [ICE_MOTOR_X,ICE_MOTOR_Z]:
                direction = 1 if delta >=0 else 1
            else:
                direction = -1 if delta >=0 else 1    
        else:
            print("方向异常")
            return None            

        # 4️ 转 pulses
        circles = abs(delta)

        if circles == 0:
            print("转动圈数为0")
            return None
        
        return {
            "circles": circles,
            "speed": speed,
            "direction": direction
        }


    @staticmethod
    def plan_orgset_move(motor):
        """
        电机回零运动
        """
        pulses = RESET_PULSES 
        speed = 90
        if motor.board_id == BOARDTYPE_STEP:
            if motor.motor_id in [POT1_MOVE_MOTOR,POT1_FLIP_MOTOR]:
                direction = 1 
            else:
                direction = -1 
        elif motor.board_id == BOARDTYPE_ICE:
            if motor.motor_id in [ICE_MOTOR_X,ICE_MOTOR_Z]:
                direction = -1 
            else:
                direction = 1  

            if motor.motor_id == ICE_MOTOR_Z:  #由于移动慢，可加速回零
                speed = 360     
        else:
            print("方向异常")
            return None 

        return {
            "pulses": pulses,
            "speed": speed,
            "direction": direction
        }

    @staticmethod
    def plan_inout_move(motor,directionstr):
        """
        电机回零运动
        """

        if motor.board_id == BOARDTYPE_STEP:
            if directionstr == "out":
                if motor.motor_id in [POT1_MOVE_MOTOR,POT1_FLIP_MOTOR]:
                    direction = -1 
                else:
                    direction = 1 
            else:        
                if motor.motor_id in [POT1_MOVE_MOTOR,POT1_FLIP_MOTOR]:
                    direction = 1 
                else:
                    direction = -1 
        elif motor.board_id == BOARDTYPE_ICE:
            if directionstr == "out":
                if motor.motor_id in [ICE_MOTOR_X,ICE_MOTOR_Z]:
                    direction = 1 
                else:
                    direction = -1 
            else:
                if motor.motor_id in [ICE_MOTOR_X,ICE_MOTOR_Z]:
                    direction = -1 
                else:
                    direction = 1         
        else:
            print("方向异常")
            return None 

        return {
            "direction": direction
        }
    