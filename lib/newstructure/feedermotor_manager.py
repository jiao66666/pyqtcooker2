from lib.newstructure.constant import *
from typing import List, Tuple

class FeederMotorManager:
    def __init__(self, board_id,motors,rs485):
        self.motors = motors
        self.board_id = board_id
        self.com = rs485
        self.cmd_running = False
        self.last_result = None

    def _on_run_done(self, command,success, resp):
        self._default_done(command, success, resp)

    def _default_done(self, cmd, success, resp):
        self.last_result = (success, resp)

        if not success:
            print(f"[{cmd}] 执行失败: {resp}")
        else:
            print(f"[{cmd}] ACK成功")

        self.cmd_running = False

    def reboot(self):
        """重启加料电机"""  ##相对运动
        print("####重启加料电机####")
        self.com.execute_command_async(
            "REBOOT", 
            [str(self.board_id)],
            priority = PRIORITY_CONTROL
        )

        return True

    def getfball(self)-> Tuple[bool, List[str]]:
        """获取加料电机反馈""" 
        print("获取所有加料电机反馈")
        motors = "1-24"

        self.com.execute_command_async(
            "GETFB", 
            [str(self.board_id), motors,"0","1"],
            priority = PRIORITY_CONTROL
        )

        return True