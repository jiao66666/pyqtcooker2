import threading
import time
from lib.newstructure.boardtype import *
from lib.newstructure.runtime import runtime

class MotorPollingService:
    def __init__(self, rs485, bus, interval=0.2):
        self.rs485 = rs485
        self.bus = bus
        self.interval = interval
        self.running = False

    def start(self):
        self.running = True
        threading.Thread(target=self._loop, daemon=True).start()

    def stop(self):
        self.running = False

    def _loop(self):
        while self.running:
            self._check_all_motors()
            time.sleep(self.interval)

    def _check_all_motors(self):
        for motor_id in MOTOR_LIST:
            success, response = self.rs485.read_command(
                "RunStatus",
                [str(motor_id)]
            )

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