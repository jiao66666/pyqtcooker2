import threading
import time
from lib.newstructure.constant import *
from lib.newstructure.runtime import runtime
import random
from lib.newstructure.tools import is_dev_mode

#此文档为DC旋转电机轮询实现代码
class SpinMotorPollingService:

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


    #为最大化查询效率可考虑替换此方法
    def _check_all_motors_status(self):

        self.rs485.execute_command_async(
            "RunStatus",
            [str(self.rs485.board_id),"0"],
            callback=self._on_motor_status_all
        )

    # =========================
    # 回调：所有电机状态
    # =========================
    def _on_motor_status_all(self, command, success, resp):

        print("执行生产环境电机状态查询。。。")
        print("电机状态回调中>>>>>>>>>>")

        if not success:
            print("查询所有电机状态失败")
            return

        print("ALLRunStatus返回:", resp)

        try:

            # ==================================================
            # 例如：
            #
            # #ALLRunStatus,2,0304*00000*B3
            #
            # resp[0] -> "0304"
            #
            # 每一个字符对应一路电机：
            #
            # 0 -> 停止
            # 3 -> 运行
            # 4 -> 故障
            # ==================================================

            status_data = resp[0].strip()

            if not status_data:
                print("电机状态数据为空")
                return

            if len(status_data) != len(self.motors):
                print(
                    f"警告：电机数量与返回状态数量不一致，"
                    f"电机数量={len(self.motors)}，"
                    f"返回状态数量={len(status_data)}"
                )

            # ==================================================
            # 遍历所有电机状态
            # ==================================================

            for motor_id, status_code in enumerate(status_data):

                # 只处理当前系统存在的电机
                if motor_id not in self.motors:
                    continue

                status_code = status_code.strip()

                # ------------------------------------------------
                # 0：停止
                # ------------------------------------------------
                if status_code == "0":

                    print(
                        f"电机 {motor_id} 状态：停止"
                    )

                # ------------------------------------------------
                # 3：运行
                # ------------------------------------------------
                elif status_code == "3":

                    print(
                        f"电机 {motor_id} 状态：运行"
                    )

                # ------------------------------------------------
                # 4：故障
                # ------------------------------------------------
                elif status_code == "4":

                    print(
                        f"电机 {motor_id} 状态：故障"
                    )

                # ------------------------------------------------
                # 未知状态
                # ------------------------------------------------
                else:

                    print(
                        f"电机 {motor_id} 未知状态：{status_code}"
                    )

                # TODO:
                # 后期可以在这里通过 WebSocket
                # 实时推送当前电机状态到前端，
                # 例如：
                #
                # {
                #     "type": "motor_status",
                #     "motor_id": motor_id,
                #     "status": "停止/运行/故障"
                # }

        except Exception as e:

            print(
                "处理所有电机状态异常:",
                e
            )
