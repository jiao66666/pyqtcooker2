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
        self.cmd_running = False
        self.last_result = None

    def _on_run_done(self, success, resp):
        self._default_done("RUN", success, resp)

    def _default_done(self, cmd, success, resp):
        self.last_result = (success, resp)

        if not success:
            print(f"[{cmd}] 执行失败: {resp}")
        else:
            print(f"[{cmd}] ACK成功")

        self.cmd_running = False



    def enable_all_motors(self):

        print("使能所有电机....")

        if self.cmd_running:
            print("命令还在执行中")
            return False

        self.cmd_running = True

        self.com.execute_command_async(
            "ENABLE",
            [str(self.board_id), "0", "11111"],
            callback=self._on_run_done
        )

        return True

    def stop_all_motors(self):

        print("急停所有电机....")

        if self.cmd_running:
            print("命令还在执行中")
            return False

        self.cmd_running = True

        self.com.execute_command_async(
            "STOP",
            [str(self.board_id), "0", "11111"],
            callback=self._on_run_done
        )

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
      
    def run(self, circles: float, anglespeed: int, direction: int):
        """异步运行电机（基于通信队列，无线程）"""

        print("####运行电机####")

        if not self.com or not self.com.connected:
            print("错误: 串口未连接，无法运行电机")
            return False

        if self.cmd_running :
            print("命令还在运行中")
            return False

        self.cmd_running  = True

        print(f"[{self.name}] ID:{self.motor_id} 运行 {circles} 圈, 角速度 {anglespeed}")

        # 计算脉冲
        pulses = circles_to_pulses(circles)
        if direction >= 0:
            pulses = abs(pulses)
        else:
            pulses = -abs(pulses)

        # 提交到通信队列（不再开线程）
        self.com.execute_command_async(
            "RUN",
            [
                str(self.board_id),
                str(self.motor_id),
                str(pulses),
                str(anglespeed)
            ],
            callback=self._on_run_done
        )

        return True
    

    def runlong(self, anglespeed: int, direction: int):
        """长运转电机"""
        print("####运行电机####")
        if not self.com or not self.com.connected:
            print("错误: 串口未连接，无法运行电机")
            return False
        print(f"[{self.name}] ID:{self.motor_id} 连续运行, 角速度 {anglespeed}, 主板类型:{self.board_id}")

            # 发送运行命令  优先级CONTROL 1
        self.com.execute_command_async(
            "LONG", 
            [str(self.board_id), str(self.motor_id), str(direction), str(anglespeed)],
            priority = 1
        )

        return True
    

    def pause(self):
        """暂停电机"""
        print("####暂停电机####")
        if not self.com or not self.com.connected:
            print("错误: 串口未连接，无法运行电机")
            return False
        print(f"[{self.name}] ID:{self.motor_id} 暂停中... 主板类型:{self.board_id}")
      
         # 发送运行命令
        self.com.execute_command_async(
            "PAUSE", 
            [str(self.board_id), str(self.motor_id)],
            priority = 1
        )

        return True    
    
    def stop(self):
        """急停电机"""
        print("####急停电机####")
        if not self.com or not self.com.connected:
            print("错误: 串口未连接，无法运行电机")
            return False
        print(f"[{self.name}] ID:{self.motor_id} 急停中... 主板类型:{self.board_id}")
      
         # 发送运行命令
        self.com.execute_command_async(
            "STOP", 
            [str(self.board_id), str(self.motor_id)],
            priority = 0
        )

        return True      