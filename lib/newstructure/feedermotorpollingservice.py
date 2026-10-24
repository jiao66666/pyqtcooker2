import threading
import time

from lib.newstructure.constant import *
from lib.newstructure.runtime import runtime
from lib.newstructure.tools import is_dev_mode


# 此文档为新锁控板状态轮询实现代码
class FeederMotorPollingService:

    def __init__(self, rs485, bus, motors, websocket_server, interval=0.2):
        self.rs485 = rs485
        self.bus = bus
        self.interval = interval
        self.running = False
        self.motors = motors
        self.websocket_server = websocket_server

        self._thread = None

    # =========================
    # 启动 / 停止
    # =========================
    def start(self):
        if self.running:
            return

        self.running = True
        self._thread = threading.Thread(
            target=self._loop,
            daemon=True
        )
        self._thread.start()

    def stop(self):
        self.running = False

    # =========================
    # 主循环
    # =========================
    def _loop(self):
        while self.running:
            self._check_all_motors_status()
            time.sleep(self.interval)

    # =========================
    # 查询所有锁通道状态
    # =========================
    def _check_all_motors_status(self):
        self.rs485.execute_command_async(
            "GETALLFB",
            [str(self.rs485.board_id)],
            callback=self._on_motor_status_all,
            priority=PRIORITY_CONTROL
        )

    # =========================
    # 回调：所有锁通道状态
    # =========================
    def _on_motor_status_all(self, command, success, resp):
        print("锁控板状态回调中>>>>>>>>>>")

        if not success:
            print("查询锁控板所有通道状态失败")
            return

        print("GETALLFB 返回:", resp)

        try:
            if not resp:
                print("锁控板状态数据为空")
                return

            # 新版 FeederProtocol.parse_response() 返回：
            # (True, "GETALLFB", [通道数量, 通道1状态, 通道2状态, ...])
            #
            # 此处 resp 是 execute_command_async 回调传入的
            # 已解析参数列表，不是原始二进制帧。

            if len(resp) < 2:
                print(f"锁控板状态数据长度不正确：{resp}")
                return

            channel_count = int(resp[0])
            status_data = resp[1:]

            if len(status_data) != channel_count:
                print(
                    f"锁控板状态数量不匹配："
                    f"协议数量={channel_count}，"
                    f"实际数量={len(status_data)}"
                )
                return

            # 遍历所有通道
            for motor_id, status_code in enumerate(status_data, start=1):
                status_code = int(status_code)

                if status_code == 0:
                    status_text = "关闭"
                elif status_code == 1:
                    status_text = "开启"
                else:
                    status_text = f"未知状态({status_code})"

                print(f"锁通道 {motor_id} 状态：{status_text}")

                # TODO：如需实时推送，可在此处发送 WebSocket 消息
                #
                # self.websocket_server.send_message({
                #     "type": "feeder_motor_status",
                #     "motor_id": motor_id,
                #     "status": status_text
                # })

        except (TypeError, ValueError, IndexError) as e:
            print("解析锁控板状态数据异常:", e)

        except Exception as e:
            print("处理锁控板状态异常:", e)