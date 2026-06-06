# faultmanager.py

import threading
from lib.newstructure.runtime import runtime


class FaultManager:

    def __init__(self, bus):
        self.bus = bus

        bus.subscribe("command_ack", self.on_command_ack)
        bus.subscribe("command_failed", self.on_command_failed)

    def on_command_ack(self, data):
        """
        命令收到ACK
        目前仅记录日志
        """
        print(
            f"[ACK] motor={data['motor']} "
            f"cmd={data['cmd']}"
        )

    def on_command_failed(self, data):
        """
        命令执行失败
        """

        print(
            f"[ERROR] motor={data['motor']} "
            f"cmd={data['cmd']} "
            f"reason={data['reason']}"
        )

        runtime.set_dirty(True)

        # 后续可以扩展
        # self.stop_all_tasks()
        # self.disable_all_motor()
        # self.notify_frontend()