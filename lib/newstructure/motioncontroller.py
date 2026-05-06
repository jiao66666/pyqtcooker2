import time
import threading
from lib.newstructure.runtime import runtime 


class MotionController:

    def __init__(self, rs485, interval=0.05):
        self.rs485 = rs485
        self.tasks = {}
        self.lock = threading.Lock()

        self.interval = interval  # 控制频率（秒）
        self.running = False
        self.thread = None

    # =========================
    # 生命周期控制
    # =========================
    def start(self):
        if self.running:
            return

        self.running = True
        self.thread = threading.Thread(target=self._loop, daemon=True)
        self.thread.start()
        print("MotionController started")

    def stop(self):
        self.running = False
        if self.thread:
            self.thread.join(timeout=1)
        print("MotionController stopped")

    # =========================
    # 任务管理
    # =========================
    def add_task(self, motor_id, start, end):
        if not self.running:
            raise RuntimeError("MotionController not started")

        if end == start:
            return  # 防止除零

        with self.lock:
            self.tasks[motor_id] = {
                "motor_id": motor_id,
                "start": start,
                "end": end
            }

    def remove_task(self, motor_id):
        with self.lock:
            self.tasks.pop(motor_id, None)

    # =========================
    # 主循环（控制回路）
    # =========================
    def _loop(self):
        print("start SPEED loop")
        while self.running:
            # 拷贝任务，避免锁住执行逻辑
            with self.lock:
                tasks_copy = list(self.tasks.items())
            for motor_id, task in tasks_copy:
                self._update_speed(task)

            time.sleep(self.interval)

    # =========================
    # 调速逻辑
    # =========================
    def _update_speed(self, task):
        motor_id = task["motor_id"]
        """
        pos = runtime.get_position(motor_id)
        if pos is None:
            return
        
        start = task["start"]
        end = task["end"]

        distance = end - start
        if distance == 0:
            self.remove_task(motor_id)
            return

        progress = (pos - start) / distance

        # 限制范围（防止超出）
        if progress < 0:
            progress = 0
        elif progress > 1:
            progress = 1

        # 三段速度（可后续升级为曲线）
        if progress < 0.2:
            speed = 100
        elif progress < 0.8:
            speed = 300
        else:
            speed = 100

        # 结束判断
        if progress >= 1.0:
            self.remove_task(motor_id)
            return
        """
        speed = 1
        self._send_speed(motor_id, speed)

    # =========================
    # 发送指令
    # =========================
    def _send_speed(self, motor_id, speed):
        try:
            self.rs485.execute_command_async(
                "SPEED",
                [str(self.rs485.board_id), str(motor_id), str(speed)]
            )
        except Exception as e:
            print(f"send speed failed: {e}")