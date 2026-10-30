from lib.newstructure.constant import *

class FeederMotorManager:
    def __init__(self, board_id,motors,rs485):
        self.motors = motors
        self.board_id = board_id
        self.com = rs485

    def stop_all_motors(self):
        """停止所有电机"""
        channels = [str(motor.motor_id) for motor in self.motors.values()]

        if not channels:
            return False

        success, _ = self.com._execute_command_sync(
            "MULTI_OUTPUT",
            [str(self.board_id), "0", *channels]
        )

        return True

