import threading
from lib.newstructure.tools import circles_to_pulses
from lib.newstructure.constant import *
from lib.newstructure.motionplaner import MotionPlanner

class StepMotor:
    def __init__(self, name,motor_id, bus, rs485):
        self.name = name
        self.com = rs485
        self.motor_id = motor_id
        self.board_id = self.com.board_id
        self.bus = bus
        self.homed = False  # 是否已回零位
        self.current_position = 0
        self.is_running = False
        self.last_result = None


    def enable_all_motors(self):
        print("使能所有电机....")
        success, resp = self.com.execute_command(
            "ENABLE", 
            [str(self.board_id),"0",str("11111")]
        )
        if not success:
            print(f"错误: {resp}")
            return False
        return True        

    def stop_all_motors(self):
        print("急停所有电机....")
        success, resp = self.com.execute_command(
            "STOP", 
            [str(self.board_id),"0",str("11111")]
        )
        if not success:
            print(f"错误: {resp}")
            return False
        
        return True        

    #绝对值坐标运动
    def go(self, action, params):
        print(f"[{self.name}] start {action}")
        target = params["target"]
        anglespeed = params["speed"]

        #if not self.homed:
        #    print("not zero ,can't go move")
        #    return False

        params = MotionPlanner.plan_abs_move(
            motor=self,
            target=target,
            current_position=self.current_position,
            speed=anglespeed
        )

        if params is None:
            print("no movement needed")
            return False
  
         # 发送运行命令
        success = self.run(
            params["circles"],
            params["speed"],
            params["direction"]
        )
        if not success:
            print(f"错误: 运行命令失败")
            return False
        
        print("执行成功")
        print(f"执行完后当前位置:{self.current_position}")
        return True  
      
    """      
    #步进电机转动
    def run(self, circles: float, anglespeed: int, direction: int):
        #单次运转电机#  ##相对运动
        print("####运行电机####")
        if not self.com or not self.com.connected:
            print("错误: 串口未连接，无法运行电机")
            return False
        print(f"[{self.name}] ID:{self.motor_id} 运行 {circles} 圈, 角速度 {anglespeed}")
        # 计算脉冲数
        pulses = circles_to_pulses(circles)
        if direction >=0:
            pulses = abs(pulses)
        else:
            pulses = -abs(pulses)    
         # 发送运行命令
        success, resp = self.com.execute_command(
            "RUN", 
            [str(self.board_id), str(self.motor_id), str(pulses), str(anglespeed)]
        )
        if not success:
            print(f"错误: {resp}")
            return False
        return True
    """    

    def run(self, circles: float, anglespeed: int, direction: int):
        """异步运行电机（只隔离IO，不改状态机）"""

        print("####运行电机####")

        if not self.com or not self.com.connected:
            print("错误: 串口未连接，无法运行电机")
            return False

        if self.is_running:
            print("电机仍在运行中")
            return False

        self.is_running = True

        print(f"[{self.name}] ID:{self.motor_id} 运行 {circles} 圈, 角速度 {anglespeed}")

        def task():
            try:
                # 计算脉冲
                pulses = circles_to_pulses(circles)
                if direction >= 0:
                    pulses = abs(pulses)
                else:
                    pulses = -abs(pulses)

                # ✔ 这里只做 IO（阻塞放线程）
                success, resp = self.com.execute_command(
                    "RUN",
                    [
                        str(self.board_id),
                        str(self.motor_id),
                        str(pulses),
                        str(anglespeed)
                    ]
                )

                self.last_result = (success, resp)

                if not success:
                    print(f"电机执行失败: {resp}")

            finally:
                # ❗只清 IO状态，不做控制决策
                self.is_running = False

        threading.Thread(target=task, daemon=True).start()

        return True