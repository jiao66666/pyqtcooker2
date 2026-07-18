import threading
import time
from lib.newstructure.constant import *
from lib.newstructure.runtime import runtime
import random


class MotorPollingService:

    def __init__(self, rs485, bus, motors, mockmotor,interval=0.2):
        self.rs485 = rs485
        self.bus = bus
        self.interval = interval
        self.running = False
        self.motors = motors
        self.motor_inflight = set()
        self.mock_started = False
        self.mockmotor = mockmotor

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

        tick = 0   #降频使用

        while self.running:
            self._check_all_motors_byonce()  #for each motor效率太低，必须改成一次性查询所有电机的状态
            self._check_all_position()

            tick += 1
            if tick % 10 == 0:
                self._check_all_errors()

            time.sleep(self.interval)

    
    #检测所有电机是否有错误
    def _check_all_errors(self):
        self.rs485.execute_command_async(
            "Error_Value",
            ["1","0"],
            callback=self._on_motor_error_handler
        )

    #处理检查到的错误
    def _on_motor_error_handler(self, command,success, resp):
        print("process error here if checked ")
        if not success:
            return
        items = resp[1].split(",")

        # 假设：0~4号电机
        motor_ids = range(len(items))

        if len(items) != len(self.motors):
            print("警告：电机数量与返回不一致")

        for motor_id, status in enumerate(items):
            runtime.set_error(motor_id)
            self.bus.publish(
                "MOTOR_ERROR",
                {"motor_id": motor_id}
            )

    # =========================
    # 电机状态查询（异步化）
    # =========================
    def _check_all_motors(self):

        for motor_id in self.motors:

            if motor_id in self.motor_inflight:
                        continue

            self.motor_inflight.add(motor_id)

            self.rs485.execute_command_async(
                "RunStatus",
                [str(motor_id)],
                callback=lambda c,s, r, mid=motor_id: self._on_motor_status(mid, s, r ,c)
            )

            #print("QUEUE SIZE:", self.rs485.queue.qsize())

    #为最大化查询效率可考虑替换此方法
    def _check_all_motors_byonce(self):

        self.rs485.execute_command_async(
            "ALLRunStatus",
            ["1","0"],
            callback=self._on_motor_status_all
        )

    # =========================
    # 回调：电机状态
    # =========================

    def _on_motor_status_all(self, command, success, resp):

        print("电机状态回调中》》》》》》》")

        # 获取所有正在运行的电机
        running_motors = runtime.get_running_motors()

        # 没有运行中的电机，直接返回
        if not running_motors:
            print("当前没有运行中的电机")
            return

        # 从运行中的电机中随机选择一个
        motor_id = random.choice(running_motors)

        runtime.set_done(motor_id)

        self.bus.publish(
            "MOTOR_DONE",
            {"motor_id": motor_id}
        )

        return
        print("电机状态回调中>>>>>>>>>>")

        if not success:
            return

        items = resp[1].split(",")

        # 假设：0~4号电机
        motor_ids = range(len(items))

        if len(items) != len(self.motors):
            print("警告：电机数量与返回不一致")

        for motor_id, status in enumerate(items):

            motor_id = int(motor_id)
            status = status.strip()

            # 只处理 runtime 中存在的电机
            if motor_id not in self.motors:
                continue

            # 当前运行参数
            step_params = runtime.get_params(motor_id)
            if not step_params:
                continue

            # =========================
            # quit in advance 判断
            # =========================
            quit_in_advance = False

            if step_params.get("quitinadvance", 0) > 0:

                curpos = runtime.get_position(motor_id)

                if curpos > step_params["quitinadvance"]:
                    quit_in_advance = True

            # =========================
            # 状态处理
            # =========================
            if status == "PAUSEING" or quit_in_advance:

                runtime.set_done(motor_id)

                self.bus.publish(
                    "MOTOR_DONE",
                    {"motor_id": motor_id}
                )

            elif status == "ERROR":

                self.bus.publish(
                    "MOTOR_ERROR",
                    {"motor_id": motor_id}
                )


    def _on_motor_status(self, motor_id, success, response ,command):

        print("电机状态回调中》》》》》》》")
        self.motor_inflight.discard(motor_id)
        #测试的时候关闭
        #仅测试用       
        runtime.set_done(motor_id)
        self.bus.publish("MOTOR_DONE", {"motor_id": motor_id})
        return
        
        
        if not success:
            return

        status = response[1]
        print(f"[Polling] motor {motor_id} status: {status}")
        
        #多电机同时运行情况
        quitInAdvance = False
        step_params = runtime.get_params(motor_id)
        if step_params["quitinadvance"] > 0:
           curpos = runtime.get_position(motor_id)
           if curpos > step_params["quitinadvance"]:
               quitInAdvance = True

        if status == "PAUSEING" or quitInAdvance:
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
    def _on_all_position(self, command,success, resp):
        if self.mock_started:
            #print('mock has been started')
            return
        self.mock_started = True
        self.mockmotor.start()       
        return
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

        ws_data = []

        for idx, pos in enumerate(pos_all):

            motor_id = self.motors[idx].motor_id

            runtime.set_position({
                "motor_id": self.motors[idx].motor_id,
                "position": pos
            })

            # 🔥 同步给前端
            ws_data.append({
                "motor_id": motor_id,
                "position": pos
            })

        # 一次性推送（关键）
        system["websocket"].send(ws_data)

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