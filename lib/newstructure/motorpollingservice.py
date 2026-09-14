import threading
import time
from lib.newstructure.constant import *
from lib.newstructure.runtime import runtime
import random
from lib.newstructure.tools import is_dev_mode

class MotorPollingService:

    def __init__(self, rs485, bus, motors, mockmotor,websocket_server,interval=0.2):
        self.rs485 = rs485
        self.bus = bus
        self.interval = interval
        self.running = False
        self.motors = motors
        self.motor_inflight = set()
        self.mock_started = False
        self.mockmotor = mockmotor
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

        #tick = 0   #降频使用

        while self.running:
            self._check_all_motors_status()  #for each motor效率太低，必须改成一次性查询所有电机的状态
            self._check_all_position()

            #tick += 1
            #if tick % 10 == 0:
            #    self._check_all_errors()

            time.sleep(self.interval)


    """
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

    """
    #为最大化查询效率可考虑替换此方法
    def _check_all_motors_status(self):

        self.rs485.execute_command_async(
            "ALLRunStatus",
            [str(self.rs485.board_id),"0"],
            callback=self._on_motor_status_all
        )

   
    # =========================
    # 回调：所有电机状态
    # =========================
    def _on_motor_status_all(self, command, success, resp):

        #if is_dev_mode():
        #    print("执行开发模式电机状态模拟。。。")
        #    self.dev_handle_motorstatus_all()
        #    return
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
            # #ALLRunStatus,2,0*00000*B3
            #
            # resp[1] -> "00000"
            #
            # 每一个字符对应一路电机：
            #
            # index 0 -> 电机0
            # index 1 -> 电机1
            # index 2 -> 电机2
            # index 3 -> 电机3
            # index 4 -> 电机4
            # ==================================================

            status_data = resp[1].strip()

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
            # 遍历所有返回状态
            # ==================================================

            for motor_id, status_code in enumerate(status_data):

                # 只处理当前系统存在的电机
                if motor_id not in self.motors:
                    continue

                status_code = status_code.strip()

                # ------------------------------------------------
                # 当前电机运行参数
                # ------------------------------------------------

                step_params = runtime.get_params(motor_id)

                # ==================================================
                # 状态 0
                #
                # STOPING
                # 电机处于急停状态
                # ==================================================

                if status_code == "0":

                    print(
                        f"电机 {motor_id} 状态：STOPING（急停）"
                    )

                    # 急停状态交给系统的急停逻辑处理
                    # 如果你的系统已经有 ESTOP_TRIGGERED，
                    # 建议在这里发布急停事件

                    self.bus.publish(
                        "ESTOP_TRIGGERED",
                        {
                            "motor_id": motor_id
                        }
                    )

                # ==================================================
                # 状态 1
                #
                # PAUSEING
                # 电机处于使能暂停状态
                #
                # 对于动作执行来说，可以认为电机已经完成
                # ==================================================

                elif status_code == "1":

                    print(
                        f"电机 {motor_id} 状态：PAUSEING（完成/暂停）"
                    )

                    # 只有当前存在运行任务时才处理完成
                    if not step_params:
                        continue

                    runtime.set_done(motor_id)

                    self.bus.publish(
                        "MOTOR_DONE",
                        {
                            "motor_id": motor_id
                        }
                    )

                # ==================================================
                # 状态 2
                #
                # ORGING
                # 电机正在复位
                # ==================================================

                elif status_code == "2":

                    print(
                        f"电机 {motor_id} 状态：ORGING（复位中）"
                    )

                    # 复位中，不触发完成
                    # 保持当前运行状态即可

                    continue

                # ==================================================
                # 状态 3
                #
                # RUNING
                # 电机正在运行
                # ==================================================

                elif status_code == "3":

                    print(
                        f"电机 {motor_id} 状态：RUNING（运行中）"
                    )

                    # ------------------------------------------------
                    # quitinadvance 判断
                    # ------------------------------------------------

                    if not step_params:
                        continue

                    quit_in_advance = step_params.get(
                        "quitinadvance",
                        0
                    )

                    if quit_in_advance > 0:

                        curpos = runtime.get_position(
                            motor_id
                        )

                        # 达到提前退出位置
                        if curpos >= quit_in_advance:

                            print(
                                f"电机 {motor_id} "
                                f"达到提前退出位置："
                                f"{curpos} >= {quit_in_advance}"
                            )

                            runtime.set_done(
                                motor_id
                            )

                            self.bus.publish(
                                "MOTOR_DONE",
                                {
                                    "motor_id": motor_id
                                }
                            )

                # ==================================================
                # 状态 4
                #
                # ERROR
                # 电机故障
                # ==================================================

                elif status_code == "4":

                    print(
                        f"电机 {motor_id} 状态：ERROR（故障）"
                    )

                    self.bus.publish(
                        "MOTOR_ERROR",
                        {
                            "motor_id": motor_id
                        }
                    )

                # ==================================================
                # 未知状态
                # ==================================================

                else:

                    print(
                        f"电机 {motor_id} "
                        f"未知状态：{status_code}"
                    )

        except Exception as e:

            print(
                "处理所有电机状态异常:",
                e
            )


    def dev_handle_motorstatus_all(self):

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
    # 回调：所有电机位置更新
    # =========================
    def _on_all_position(self, command, success, resp):

        #if is_dev_mode():
        #    print("执行开发模式电机位置更新模拟")
        #    self.dev_handle_all_position()
        #    return
        
        print("执行生成环境位置更新。。。")
        if not success:
            print(f"查询所有电机位置失败: {resp}")
            return

        try:

            print(f"ALLPulse返回数据: {resp}")

            pulse_data = resp[1].strip()

            if not pulse_data:
                print("错误：所有电机脉冲数据为空")
                return

            items = pulse_data.split(",")

            if len(items) != len(self.motors):

                print(
                    f"错误：返回电机数量与系统电机数量不一致，"
                    f"返回={len(items)}，"
                    f"系统={len(self.motors)}"
                )

                return

            ws_data = []

            for motor_id, pulse_str in enumerate(items):

                # 确保系统存在该电机
                if motor_id not in self.motors:
                    continue

                # +2096 / -117660 都可以直接转换
                pulse = int(
                    pulse_str.strip()
                )

                # 脉冲转换实际位置
                pos = self.convert_pulses_to_position(
                    pulse,
                    motor_id
                )

                # 更新 runtime
                runtime.set_position({
                    "motor_id": motor_id,
                    "position": pos
                })

                # 前端数据
                ws_data.append({
                    "type": "cordinate",
                    "motor_id": motor_id,
                    "position": pos
                })

            # 一次性发送
            if ws_data:
                self.websocket_server.send(
                    ws_data
                )

            print(
                f"反馈成功，返回数据为: {items}"
            )

        except Exception as e:

            print(
                f"处理ALLPulse位置数据异常: {e}"
            )

    def  dev_handle_all_position(self):

        if self.mock_started:
            #print('mock has been started')
            return
        self.mock_started = True
        self.mockmotor.start()       
        return


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