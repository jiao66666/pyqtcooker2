import threading


class RuntimeContext:
    """
    最小运行时状态中心（线程安全）
    - 管理 motor 状态
    - 提供统一读写入口
    """

    def __init__(self):
        self._lock = threading.Lock()

        # motor 状态表
        self.motors = {}
        # 结构：
        # motor_id: {
        #     "state": "IDLE / RUNNING / DONE / ERROR",
        #     "action": str,
        #     "pot_id": int
        # }

    # ---------------------------
    # 初始化
    # ---------------------------
    def init_motor(self, motor_id: int):
        with self._lock:
            self.motors[motor_id] = {
                "state": "IDLE",
                "action": None,
                "pot_id": None
            }

    # ---------------------------
    # 状态变更
    # ---------------------------
    def set_running(self, motor_id: int, action: str, pot_id: int = None):
        with self._lock:
            self.motors[motor_id] = {
                "state": "RUNNING",
                "action": action,
                "pot_id": pot_id
            }

    def set_done(self, motor_id: int):
        with self._lock:
            if motor_id in self.motors:
                self.motors[motor_id]["state"] = "DONE"

    def set_error(self, motor_id: int):
        with self._lock:
            if motor_id in self.motors:
                self.motors[motor_id]["state"] = "ERROR"

    def set_idle(self, motor_id: int):
        with self._lock:
            if motor_id in self.motors:
                self.motors[motor_id]["state"] = "IDLE"
                self.motors[motor_id]["action"] = None

    # ---------------------------
    # 查询
    # ---------------------------
    def get(self, motor_id: int):
        with self._lock:
            return self.motors.get(motor_id)

    def get_state(self, motor_id: int):
        with self._lock:
            m = self.motors.get(motor_id)
            return m["state"] if m else None

    def is_busy(self, motor_id: int) -> bool:
        with self._lock:
            m = self.motors.get(motor_id)
            return bool(m and m["state"] == "RUNNING")
        

runtime = RuntimeContext()        