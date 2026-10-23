
# motor_driver.py

from lib.newstructure.constant import *
from typing import List, Tuple
import threading

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
        self._output_timer = None
        self._output_lock = threading.Lock()

    def ping(self):
        """新版协议没有独立 PING，读取全部锁状态以检测通信。"""
        self.com.execute_command_async(
            "GETALLFB",
            [str(self.board_id)],
            priority=PRIORITY_CONTROL
        )
        return True

    def run(self, overtime: int = 1000):
        """持续输出指定时间，overtime 单位为毫秒。"""

        overtime = int(overtime)

        if overtime <= 0:
            raise ValueError("overtime 必须大于 0 毫秒")

        with self._output_lock:
            # 已有定时输出任务，不允许重复启动
            if self._output_timer is not None:
                if self._output_timer.is_alive():
                    print(f"{self.name} 正在输出中，拒绝重复启动")
                    return False

                self._output_timer = None

            self.overtime = overtime

            # 开启输出
            self.output_on()

            # 创建定时关闭任务
            self._output_timer = threading.Timer(
                overtime / 1000,
                self._timer_output_off
            )
            self._output_timer.daemon = True
            self._output_timer.start()

        return True


    def _timer_output_off(self):
        """定时关闭输出。"""
        try:
            self.output_off()
        finally:
            with self._output_lock:
                self._output_timer = None

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


