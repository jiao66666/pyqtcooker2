from lib.newstructure.constant import *
from typing import List, Tuple

class SpinMotorManager:
    def __init__(self, board_id,motors,rs485):
        self.motors = motors
        self.board_id = board_id
        self.com = rs485
        self.last_result = None

    def _on_run_done(self, command,success, resp):
        self._default_done(command, success, resp)

    def _default_done(self, cmd, success, resp):
        self.last_result = (success, resp)

        if not success:
            print(f"[{cmd}] 执行失败: {resp}")
        else:
            print(f"[{cmd}] ACK成功")

    def setspeedall(self,speed):
        """批量设置电机速度"""
        print("####批量设置电机速度####")
        print(f"批量设置feeder电机速度... 主板类型:{self.board_id}")
      
         # 发送运行命令
        self.com.execute_command_async(
            "SPEED", 
            [str(self.board_id), "0",str(speed),str(speed)],
            priority = PRIORITY_CONTROL
        )
      
        return True        

    def stop_all_motors(self):
        """批量停止电机"""
        print("####批量停止电机####")
      
         # 发送运行命令
        self.com.execute_command_async(
            "STOP", 
            [str(self.board_id), "0","11"],
            priority = PRIORITY_CONTROL
        )
      
        return True  