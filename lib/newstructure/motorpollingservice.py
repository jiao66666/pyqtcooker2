import threading
import time
from lib.newstructure.constant import *
from lib.newstructure.runtime import runtime


class MotorPollingService:

    def __init__(self, rs485, bus, motors, interval=0.2):
        self.rs485 = rs485
        self.bus = bus
        self.interval = interval
        self.running = False
        self.motors = motors

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
            self._check_all_motors()
            self._check_all_position()
            time.sleep(self.interval)

    # =========================
    # 电机状态查询（异步化）
    # =========================
    def _check_all_motors(self):

        for motor_id in self.motors:

            self.rs485.execute_command_async(
                "RunStatus",
                [str(motor_id)],
                callback=lambda s, r, mid=motor_id: self._on_motor_status(mid, s, r)
            )

    # =========================
    # 回调：电机状态
    # =========================
    def _on_motor_status(self, motor_id, success, response):

        if not success:
            return

        status = response[1]
        print(f"[Polling] motor {motor_id} status: {status}")

        if status == "PAUSEING":
            runtime.set_done(motor_id)
            self.bus.publish("MOTOR_DONE", {"motor_id": motor_id})

        elif status == "ERROR":
            self.bus.publish("MOTOR_ERROR", {"motor_id": motor_id})

    # =========================
    # 位置查询（异步化）
    # =========================
    def _check_all_position(self):

        self.rs485.execute_command_async(
            "ALLPulse",
            [str(self.rs485.board_id), "0"],
            callback=self._on_all_position
        )

    # =========================
    # 回调：位置更新
    # =========================
    def _on_all_position(self, success, resp):

        if not success:
            print(f"错误: {resp}")
            return

        items = resp[1].split(",")

        if len(items) != 5:
            print("错误：电机数量有误！！！")
            return

        pos_all = [
            self.convert_pulses_to_position(int(x), idx)
            for idx, x in enumerate(items)
        ]

        for idx, pos in enumerate(pos_all):
            runtime.set_position({
                "motor_id": self.motors[idx].motor_id,
                "position": pos
            })

        print(f"反馈成功，返回数据为: {pos_all}")

    # =========================
    # 脉冲转位置
    # =========================
    def convert_pulses_to_position(self, pulses: int, motor_id: int) -> float:

        if motor_id in [1, 2]:
            if pulses < 0:
                circles = abs(pulses / (MICRO_STEP * 200))
            else:
                circles = -abs(pulses / (MICRO_STEP * 200))
        else:
            circles = pulses / (MICRO_STEP * 200)

        return round(circles, 2)