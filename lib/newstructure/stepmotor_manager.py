from lib.newstructure.constant import *

class StepMotorManager:
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

    def enable_all_motors(self):

        print("使能所有电机....")

        if self.cmd_running:
            print("命令还在执行中")
            return False

        self.cmd_running = True

        self.com.execute_command_async(
            "ENABLE",
            [str(self.board_id), "0", "11111"],
            callback=self._on_run_done,
            priority=PRIORITY_CONTROL
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
            callback=self._on_run_done,
            priority=PRIORITY_CONTROL
        )

        return True  
    
    def reset_home_all(self):
        for motor in self.motors.values():
            motor.reset_home()

        return True    
    

    def speed_all(self,speedval):
        print("加速所有电机....")

        if self.cmd_running:
            print("命令还在执行中")
            return False

        self.cmd_running = True
        cmdstr =f"{speedval},{speedval},{speedval},{speedval},{speedval}"
        self.com.execute_command_async(
            "SPEED",
            [str(self.board_id), "0", cmdstr],
            callback=self._on_run_done,
            priority=PRIORITY_CONTROL
        )

        return True