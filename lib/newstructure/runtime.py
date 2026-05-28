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


       # =========================
        # 动态动作参数覆盖
        # 例如：
        # {
        #     "move_out_togetfood_1": {
        #         "speed": 1500
        #     }
        # }
        # =========================
        self.action_params = {}

    # ---------------------------
    # 初始化
    # ---------------------------
    def init_motor(self, motor_id: int):
        with self._lock:
            self.motors[motor_id] = {
                "state": "IDLE",
                "enabled": False,
                "action": None,
                "pot_id": None,
                "position": 0    
            }


    # ==================================================
    # 获取所有运行中的电机
    # ==================================================
    def get_running_motors(self):
        with self._lock:

            return [
                motor_id
                for motor_id, info in self.motors.items()
                if info["state"] == "RUNNING"
            ]



    # ==================================================
    # 设置动作参数覆盖
    # ==================================================
    def set_action_override(self, key, params):
        with self._lock:
            if key not in self.action_params:
                self.action_params[key] = {}

            self.action_params[key].update(params)

    # ==================================================
    # 获取动作参数覆盖
    # ==================================================
    def get_action_override(self, key):
        with self._lock:
            return self.action_params.get(key, {}).copy()

    # ==================================================
    # 获取最终动作参数
    # ==================================================
    def get_final_action_params(self, action_key, default_config):
        final_params = default_config.copy()
        override = self.get_action_override(action_key)
        final_params.update(override)
        return final_params
    

    # ---------------------------
    # 状态变更
    # ---------------------------
    def set_running(self, motor_id: int, action: str, pot_id: int = None,params:dict = None,task_id=None):
        if params is None:
            params = {}
        with self._lock:
            self.motors[motor_id]["state"] = "RUNNING"
            self.motors[motor_id]["action"] = action
            self.motors[motor_id]["pot_id"] = pot_id
            self.motors[motor_id]["params"] = params
            self.motors[motor_id]["task_id"] = task_id

    def set_position(self, motor_id: int, pos: float):
        with self._lock:
            self.motors[motor_id]["position"] = pos

    def get_position(self,motor_id: int):
        with self._lock:
            return self.motors[motor_id]["position"]   

    def get_params(self,motor_id:int):
        with self._lock:
            return self.motors[motor_id]["params"]           

    def set_done(self, motor_id: int):
        with self._lock:
            if motor_id in self.motors:
                self.motors[motor_id]["state"] = "DONE"

    def get_taskid(self,motor_id:int):
        with self._lock:
            return self.motors[motor_id]["task_id"]

    def set_error(self, motor_id: int):
        with self._lock:
            if motor_id in self.motors:
                self.motors[motor_id]["state"] = "ERROR"

    def set_idle(self, motor_id: int):

        with self._lock:

            if motor_id in self.motors:

                self._reset_motor_info(
                    self.motors[motor_id]
                )

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

    def set_all_enabled(self, enabled):

        with self._lock:
            for motor in self.motors.values():
                motor["enabled"] = enabled


    def set_enabled(self, motor_id, enabled):
        with self._lock:
            self.motors[motor_id]["enabled"] = enabled


    def is_enabled(self, motor_id):
        with self._lock:
            return self.motors[motor_id].get("enabled", False)            


    def is_all_enabled(self):
        with self._lock:
            return all(
                motor.get("enabled", False)
                for motor in self.motors.values()
            )

    # ---------------------------
    # 内部复位
    # ---------------------------
    def _reset_motor_info(self, info: dict):

        info["state"] = "IDLE"
        info["enabled"] = False
        info["action"] = None
        info["pot_id"] = None
        info["params"] = {}
        info["task_id"] = None        


    # ---------------------------
    # 清理某个锅相关的运行状态
    # ---------------------------
    def clear_pot(self, pot_id: int):

        with self._lock:

            for info in self.motors.values():

                if info["pot_id"] == pot_id:

                    self._reset_motor_info(info)


runtime = RuntimeContext()        