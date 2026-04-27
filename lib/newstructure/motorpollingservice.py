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

    def start(self):
        self.running = True
        threading.Thread(target=self._loop, daemon=True).start()

    def stop(self):
        self.running = False


    def _loop(self):
        while self.running:
            self._check_all_motors()
            self._check_all_position()
            time.sleep(self.interval)

    def _check_all_motors(self):
        for motor_id in self.motors:
            success, response = self.rs485.execute_command(
                "RunStatus",
                [str(motor_id)]
            )

            #only used for test
            #runtime.set_done(motor_id)
            #self.bus.publish("MOTOR_DONE", {
            #    "motor_id": motor_id
            #})
        

            if not success:
                continue

            status = response[1]
            print(f"[Polling] motor {motor_id} status: {status}")

            if status == "PAUSEING":
                runtime.set_done(motor_id)
                self.bus.publish("MOTOR_DONE", {
                    "motor_id": motor_id
                })

            elif status == "ERROR":
                self.bus.publish("MOTOR_ERROR", {
                    "motor_id": motor_id
                })            


    def _check_all_position(self):
        #读取所有电机已转脉冲数
        success, resp = self.rs485.execute_command(
            "ALLPulse", 
            [str(self.rs485.board_id), "0"]
        )

        if not success:
            print(f"错误: {resp}")
            return False,[f"错误: {resp}"]
        
        items = resp[1].split(",")
        if len(items) != 5:
            return False,[f"错误: {resp}"]
        
        return True,[f"反馈成功，返回数据为:{[self.convert_pulses_to_position(int(x), int(idx)) for idx, x in enumerate(items)]}",[self.convert_pulses_to_position(int(x), int(idx)) for idx, x in enumerate(items)]]        


    def convert_pulses_to_position(self, pulses: int, motor_id: int) -> float:       
        """将脉冲数转换为实际位置MICROSTEP细分，步距角1.8，每转200脉冲"""
        if motor_id in [1,2]:
            if pulses < 0:
               circles = abs( pulses / (MICRO_STEP*200) )
            else:
               circles = -abs( pulses / (MICRO_STEP*200))
        else:
            circles = pulses / (MICRO_STEP*200) 

        return round(circles,2)   