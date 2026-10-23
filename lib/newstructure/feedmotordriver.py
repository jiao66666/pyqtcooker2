
# motor_driver.py

from lib.newstructure.constant import *
from typing import List, Tuple


class FeederMotor:
    """
    新版锁控板驱动
    RS485: 9600, 8N1
    """

    def __init__(self, name, motor_id, bus, rs485):
        self.com = rs485
        self.motor_id = int(motor_id)       # 锁通道号
        self.name = name
        self.board_id = int(self.com.board_id)  # 锁控板地址
        self.bus = bus
        self.overtime = 1000

    def ping(self):
        """新版协议没有独立 PING，读取全部锁状态以检测通信。"""
        self.com.execute_command_async(
            "GETALLFB",
            [str(self.board_id)],
            priority=PRIORITY_CONTROL
        )
        return True

    def run(self, overtime: int = 1000):
        """按指定持续时间开锁，overtime 单位为毫秒。"""
        overtime = int(overtime)

        if not 1 <= overtime <= 65535:
            raise ValueError("overtime 必须在 1～65535 毫秒之间")

        self.overtime = overtime

        self.com.execute_command_async(
            "OPENLOCK_TIME",
            [
                str(self.board_id),
                str(overtime),
                str(self.motor_id)
            ],
            priority=PRIORITY_CONTROL
        )

        return True

    def output_on(self):
        """锁通道持续输出（0x88）。

        注意：该功能用于继电器、照明灯等持续通电设备。
        电控锁使用此功能可能导致烧坏。
        """
        self.com.execute_command_async(
            "OUTPUT_ON",
            [str(self.board_id), str(self.motor_id)],
            priority=PRIORITY_CONTROL
        )
        return True

    def output_off(self):
        """关闭锁通道输出（0x89）。"""
        self.com.execute_command_async(
            "OUTPUT_OFF",
            [str(self.board_id), str(self.motor_id)],
            priority=PRIORITY_CONTROL
        )
        return True

    
    def getfb(self) -> Tuple[bool, List[str]]:
        """读取指定通道的锁状态。"""
        self.com.execute_command_async(
            "GETFB",
            [str(self.board_id), str(self.motor_id)],
            priority=PRIORITY_CONTROL
        )

        # 保留原有异步调用方式；这里只表示命令已提交，
        # 不代表锁状态查询已经成功。
        return True, []


