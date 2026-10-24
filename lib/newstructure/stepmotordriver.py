import threading
from lib.newstructure.tools import circles_to_pulses,is_dev_mode
from lib.newstructure.constant import *
from lib.newstructure.motionplaner import MotionPlanner
from typing import  List, Tuple


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

    def set_cmd_running(self,action):
        print(f"{action} is ready to execute,setting cmdrunning true>>>>>>>")
        self.cmd_running = True

    def reset_cmd_running(self,action):
        print(f"{action} is ready to execute,setting cmdrunning false>>>>>>>")
        self.cmd_running = False

    def _on_run_done(self,command ,success, resp):
        self._default_done(command, success, resp)

    def _default_done(self, cmd, success, resp):
        self.last_result = (success, resp)
        print(f"{cmd} is executed done ,ready to set cmd_running false<<<<<<<")
        #self.reset_cmd_running("normaldone")
      
        if not success:
            print(f"[{cmd}] 执行失败: {resp}")
            self.bus.publish(
                "command_failed",
                {
                    "cmd": cmd,
                    "resp": resp
                }
            )

        else:
        
            print(f"[{cmd}] ACK成功")
            self.bus.publish(
                "command_ack",
                {
                    "cmd": cmd,
                    "resp": resp
                }
            )
           
    def reset_home(self):
        self.home = False
        
    def get_current_pos(self):
        return self.current_position  

    def update_current_pos(self,pos):
        self.current_position =  pos
        print(f"当前最新位置:{self.current_position}")
    #绝对值坐标运动
    def go_action(self, action, params)-> Tuple[bool, List[str]]:
        print(f"[{self.name}] start {action}")
        target = params["target"]
        anglespeed = params["speed"]

        params = MotionPlanner.plan_abs_move(
            motor=self,
            target=target,
            current_position=self.current_position,
            speed=anglespeed
        )


        if params is None:
            print("no movement needed")
            return False,["NO_MOVE","没有可用参数"]


        # 发送运行命令
        success = self.run(
            params["circles"],
            params["speed"],
            params["direction"]
        )
        if not success:
            print(f"错误: 运行命令失败")
            return False,["RETRY","命令执行失败"]

        if is_dev_mode():  #模拟更新位置
            self.update_current_pos(target)

        print("执行成功")
        return True,["SUBMITTED","提交成功"]  
    
        
    def go(self, target: float, anglespeed: int):  # 回零后进行绝对运动，水平离开0点位置 为正值，翻转离开0点 逆时针为正值 ，顺时值为负值
        """单次运转电机"""  ##绝对运动
        print("####运行电机####")
        print(f"[{self.name}] ID:{self.motor_id} 运行到位置{target}, 角速度 {anglespeed}, 主板类型:{self.board_id}")

        # 计算脉冲数
        params = MotionPlanner.plan_abs_move(
            motor=self,
            target=target,
            current_position=self.current_position,
            speed=anglespeed
        )

        if params is None:
            print("no movement needed")
            return False,["没有参数"]  
         # 发送运行命令
        # 发送运行命令
        success = self.run(
            params["circles"],
            params["speed"],
            params["direction"]
        )
        if not success:
            print(f"错误: 运行命令失败")
            return False,["运行命令失败"]
        
        print("执行成功")
        return True,["执行成功"]    
      
    def run(self, circles: float, anglespeed: int, direction: int):
        """异步运行电机（基于通信队列，无线程）"""
        print("####运行电机####")
        if self.cmd_running :
            print("run命令还在运行中")
            return False

        print(f"[{self.name}] ID:{self.motor_id} 运行 {circles} 圈, 角速度 {anglespeed}")

        # 计算脉冲
        pulses = circles_to_pulses(circles)
        if direction >= 0:
            pulses = abs(pulses)
        else:
            pulses = -abs(pulses)

        # 提交到通信队列（不再开线程）
        self.set_cmd_running("run")
        self.com.execute_command_async(
            "RUN",
            [
                str(self.board_id),
                str(self.motor_id),
                str(pulses),
                str(anglespeed)
            ],
            callback=self._on_run_done,
            priority=PRIORITY_CONTROL
        )

        return True
    
    # dir = in or out
    def go_InOut(self, anglespeed: int, dir: str):
        """长运转电机"""
        if self.cmd_running :
            print("命令还在运行中")
            return False,["命令还在运行"]
        print("####运行电机####")
        print(f"[{self.name}] ID:{self.motor_id} 连续运行, 角速度 {anglespeed}, 主板类型:{self.board_id},")

        params = MotionPlanner.plan_inout_move(
            motor = self,
            directionstr=dir
        )

        if params is None:
            print("no movement needed")
            return False,["没有参数"] 
             
            # 发送运行命令  优先级CONTROL 1
        self.set_cmd_running("go_InOut")
        self.com.execute_command_async(
            "LONG", 
            [str(self.board_id), str(self.motor_id), str(params["direction"]), str(anglespeed)],
            callback=self._on_run_done,
            priority = PRIORITY_CONTROL
        )

        return True,["执行成功"]




    def runlong(self, anglespeed: int, direction: int):
        """长运转电机"""
        if self.cmd_running :
            print("命令还在运行中")
            return False,["命令还在运行"]
        print("####运行电机####")
        print(f"[{self.name}] ID:{self.motor_id} 连续运行, 角速度 {anglespeed}, 主板类型:{self.board_id}")

            # 发送运行命令  优先级CONTROL 1
        self.set_cmd_running("runlong")
        self.com.execute_command_async(
            "LONG", 
            [str(self.board_id), str(self.motor_id), str(direction), str(anglespeed)],
            callback=self._on_run_done,
            priority = PRIORITY_CONTROL
        )

        return True,["执行成功"]
    

    def pause(self):
        """暂停电机"""       
        print("####暂停电机####")   #目前runlong和pause存在 不匹配，因为两个指令加锁不同，暂时不影响 实际运行，如果影响实际运行，考虑改结构解决
        print(f"[{self.name}] ID:{self.motor_id} 暂停中... 主板类型:{self.board_id}")
      
         # 发送运行命令
        self.com.execute_command_async(
            "PAUSE", 
            [str(self.board_id), str(self.motor_id)],
            callback=self._on_run_done,
            priority = PRIORITY_CONTROL
        )

        return True,["执行成功"]    
    
    def stop(self):
        """急停电机"""
        print("####急停电机####")
        print(f"[{self.name}] ID:{self.motor_id} 急停中... 主板类型:{self.board_id}")
      
         # 发送运行命令
        self.com.execute_command_async(
            "STOP", 
            [str(self.board_id), str(self.motor_id)],
            callback=self._on_run_done,
            priority = PRIORITY_EMERGENCY
        )

        return True ,["执行成功"]    


    #   水平垂直复位
    def reset_zero(self)-> Tuple[bool, List[str]]:
        """复位单个电机"""
        if self.cmd_running :
            print("命令还在运行中")
            return False,["命令还在运行中"]
        print("####复位电机####")
        print(f"[{self.name}] ID:{self.motor_id} 运行 复位电机【{self.name}】, 主板类型:{self.board_id}")
        # 计算脉冲数
        params = MotionPlanner.plan_orgset_move(
            motor=self
        )

        if params is None:
            print("no movement needed")
            return False,["没有参数"]   

        if params["direction"] >=0:
            pulses = abs(params["pulses"])
        else:
            pulses = -abs(params["pulses"])   

        #复位速度
        anglespeed = params["speed"]   #生产标准速度360，测试使用90      
         # 发送运行命令
        self.set_cmd_running("reset_zero")
        self.com.execute_command_async(
            "ORGRST", 
            [str(self.board_id), str(self.motor_id), str(pulses), "0",str(anglespeed)],
            callback=self._on_run_done,
            priority = PRIORITY_CONTROL
        )
 
        self.current_position = 0
        self.homed = True
    
        return True,["SUBMITTED",f"电机{self.name}复位成功"]


    #   水平垂直复位
    def reset_zero_byspeed(self,anglespeed)-> Tuple[bool, List[str]]:
        """复位单个电机"""
        if self.cmd_running :
            print("命令还在运行中")
            return False,["命令还在运行中"]
        print("####复位电机####")
        print(f"[{self.name}] ID:{self.motor_id} 运行 复位电机【{self.name}】, 主板类型:{self.board_id}")
        # 计算脉冲数
        params = MotionPlanner.plan_orgset_move(
            motor=self
        )

        if params is None:
            print("no movement needed")
            return False,["NO_MOVE","没有参数"]   

        if params["direction"] >=0:
            pulses = abs(params["pulses"])
        else:
            pulses = -abs(params["pulses"])   

        # 发送运行命令
        self.set_cmd_running("reset_zero_byspeed")
        success = self.com.execute_command_async(
            "ORGRST", 
            [str(self.board_id), str(self.motor_id), str(pulses), "0",str(anglespeed)],
            callback=self._on_run_done,
            priority = PRIORITY_CONTROL
        )

        if not success:
            print(f"错误: 运行命令失败")
            return False,["RETRY","命令执行失败"]
 
        self.current_position = 0
        self.homed = True
    
        return True,[f"电机{self.name}复位成功"]


    #   水平垂直复位
    def reset_zero_both(self,positive: int = 1,speed:int = 90)-> Tuple[bool, List[str]]:
        """复位单个电机"""

        print(f"[{self.name}] ID:{self.motor_id} 运行 复位电机【{self.name}】, 主板类型:{self.board_id}")
        # 复位脉冲数
        pulses = RESET_PULSES if positive == 1 else -RESET_PULSES
       
        #复位速度
        anglespeed = speed   #生产标准速度360，测试使用90      
         # 发送运行命令
        self.set_cmd_running("reset_zero_both")
        self.com.execute_command_async(
            "ORGRST", 
            [str(self.board_id), str(self.motor_id), str(pulses), "0",str(anglespeed)],
            callback=self._on_run_done,
            priority = PRIORITY_CONTROL
        )
 
        self.current_position = 0
        self.homed = True
    
        return True,[f"电机{self.name}复位成功"]
