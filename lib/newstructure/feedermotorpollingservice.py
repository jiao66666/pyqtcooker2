import threading
import time
from lib.newstructure.constant import *
from lib.newstructure.runtime import runtime
import random
from lib.newstructure.tools import is_dev_mode

#此文档为加料电机轮询实现代码
class FeederMotorPollingService:

    def __init__(self, rs485, bus, motors,websocket_server,interval=0.2):
        self.rs485 = rs485
        self.bus = bus
        self.interval = interval
        self.running = False
        self.motors = motors
        self.websocket_server = websocket_server

    # =========================
    # 启动 / 停止
    # =========================
    def start(self):
        self.running = True
        threading.Thread(target=self._loop, daemon=True).start()

    def stop(self):
        self.running = False

    # =========================
    # 主循环
    # =========================
    def _loop(self):

        while self.running:
            self._check_all_motors_status() 

            time.sleep(self.interval)

    # 为最大化查询效率可考虑替换此方法
    def _check_all_motors_status(self):

        self.rs485.execute_command_async(
            "GETFB",
            [str(self.rs485.board_id), "1-24", "0", "1"],
            callback=self._on_motor_status_all
        )


    # =========================
    # 回调：所有加料电机状态
    # =========================
    def _on_motor_status_all(self, command, success, resp):

        print("执行加料板电机状态查询。。。")
        print("加料电机状态回调中>>>>>>>>>>")

        if not success:
            print("查询所有加料电机状态失败")
            return

        print("GETFB返回:", resp)

        try:

            # ==================================================
            # GETFB 返回格式：
            #
            # +GETFB:1,111111111111111111111111
            #
            # resp[0] -> "111111111111111111111111"
            #
            # 每一个字符对应一个通道：
            #
            # index 0  -> 1号电机
            # index 1  -> 2号电机
            # ...
            # index 23 -> 24号电机
            #
            # mode=0：
            # 0 -> 低电平
            # 1 -> 高电平
            # ==================================================

            status_data = resp[0].strip()

            if not status_data:
                print("加料电机状态数据为空")
                return

            if len(status_data) != 24:
                print(
                    f"警告：加料电机状态数量不正确，"
                    f"期望=24，实际={len(status_data)}"
                )

            # ==================================================
            # 遍历24路加料电机状态
            # ==================================================

            for motor_id, status_code in enumerate(status_data, start=1):

                # ------------------------------------------------
                # 0：关闭
                # ------------------------------------------------
                if status_code == "0":

                    print(
                        f"加料电机 {motor_id} 状态：关闭"
                    )

                # ------------------------------------------------
                # 1：开启
                # ------------------------------------------------
                elif status_code == "1":

                    print(
                        f"加料电机 {motor_id} 状态：开启"
                    )

                # ------------------------------------------------
                # 未知状态
                # ------------------------------------------------
                else:

                    print(
                        f"加料电机 {motor_id} 未知状态：{status_code}"
                    )

                # TODO:
                # 后期可以通过 WebSocket 实时推送当前加料电机状态
                #
                # {
                #     "type": "feeder_motor_status",
                #     "motor_id": motor_id,
                #     "status": "开启/关闭"
                # }

        except Exception as e:

            print(
                "处理所有加料电机状态异常:",
                e
            )