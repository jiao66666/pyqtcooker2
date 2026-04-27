import time
from lib.newstructure.runtime import runtime 
class MotionController:

    def __init__(self, rs485):
        self.rs485 = rs485
        self.tasks = []

    def add_task(self, motor_id, start, end):
        self.tasks.append({
            "motor_id": motor_id,
            "start": start,
            "end": end
        })

    def loop(self):
        while True:
            for task in self.tasks:
                self._update_speed(task)

            time.sleep(0.05)


    def _update_speed(self, task):
        motor_id = task["motor_id"]

        pos = runtime.get_position(motor_id)
        if pos is None:
            return

        start = task["start"]
        end = task["end"]

        progress = (pos - start) / (end - start)

        if progress < 0.2:
            speed = 100   # 加速
        elif progress < 0.8:
            speed = 300   # 匀速
        else:
            speed = 100   # 减速

        self._send_speed(motor_id, speed)           

    def _send_speed(self, motor_id, speed):
        self.rs485.execute_command(
            "SET_SPEED",
            [str(motor_id), str(speed)]
        )