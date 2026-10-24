import threading
from lib.newstructure.constant import *


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
    def init_motor(
        self,
        board_id: int,
        motor_id: int,
        motor_type: str,
        pot_id: int = None
    ):
        key = (board_id, motor_id)

        with self._lock:
            self.motors[key] = {
                # 通用字段
                "board_id": board_id,
                "motor_id": motor_id,
                "type": motor_type,
                "state": "IDLE",
                "enabled": False,
                "action": None,
                "task_id": None,
                "params": {},

                # 所属锅：非锅所属电机可以为 None
                "pot_id": pot_id,

                # 位置反馈：尚未获取时为 None
                "position": None
            }

    # ==================================================
    # 获取所有运行中的电机
    # ==================================================
    def get_running_motors(self):
        with self._lock:
            return [
                key
                for key, info in self.motors.items()
                if info["state"] == "RUNNING"
            ]

    # ==================================================
    # 获取指定控制板中所有运行中的电机
    # ==================================================
    def get_running_motors_byboardid(self, board_id: int):
        with self._lock:
            return [
                motor_id
                for (bid, motor_id), info in self.motors.items()
                if bid == board_id and info["state"] == "RUNNING"
            ]

    def set_action_override(self, key, params):
        if params is None:
            params = {}

        with self._lock:
            self.action_params[key] = params.copy()



    def set_motor_type_action_override(self, motor_type, action_name, params):
        if params is None:
            params = {}

        key = (motor_type, action_name)
        with self._lock:
            self.action_params[key] = params.copy()


    def get_action_override(self, key):
        with self._lock:
            return self.action_params.get(key, {}).copy()

    # ==================================================
    # 获取最终动作参数
    # ==================================================
    def get_final_action_params(self, action_key, default_config, motor_type=None):
        final_params = default_config.copy()

        # 原有逻辑：按动作名称覆盖，保持不变
        override = self.get_action_override(action_key)
        final_params.update(override)

        # 新增逻辑：按电机类型和动作名称覆盖
        if motor_type is not None:
            key = (motor_type, action_key)
            with self._lock:
                override = self.action_params.get(key, {}).copy()
            final_params.update(override)

        return final_params
    

    # ---------------------------
    # 状态变更
    # ---------------------------
    def set_running(self, motor_id: int, action: str, pot_id: int = None,params:dict = None,task_id=None ,board_id:int = BOARDTYPE_STEP):
        if params is None:
            params = {}

        key = (board_id, motor_id)
        with self._lock:
            self.motors[key]["state"] = "RUNNING"
            self.motors[key]["action"] = action
                    # 仅在明确传入 pot_id 时更新归属
            if pot_id is not None:
                self.motors[key]["pot_id"] = pot_id
            
            self.motors[key]["params"] = params.copy()
            self.motors[key]["task_id"] = task_id

    def set_position(self, motor_id: int, pos: float,board_id:int = BOARDTYPE_STEP):
        key = (board_id, motor_id)
        with self._lock:
            self.motors[key]["position"] = pos

    def get_position(self,motor_id: int,board_id:int = BOARDTYPE_STEP):
        key = (board_id, motor_id)
        with self._lock:
            return self.motors[key]["position"]   

    def get_params(self,motor_id:int,board_id:int = BOARDTYPE_STEP):
        key = (board_id, motor_id)
        with self._lock:
             return self.motors[key].get("params", {})
    def set_done(self, motor_id: int,board_id:int = BOARDTYPE_STEP):
        key = (board_id, motor_id)
        with self._lock:
            if key in self.motors:
                self.motors[key]["state"] = "DONE"

    def get_taskid(self,motor_id:int,board_id:int = BOARDTYPE_STEP):
        key = (board_id, motor_id)
        with self._lock:
            return self.motors[key]["task_id"]

    def set_error(self, motor_id: int,board_id:int = BOARDTYPE_STEP):
        key = (board_id, motor_id)
        with self._lock:
            if key in self.motors:
                self.motors[key]["state"] = "ERROR"

    def set_idle(self, motor_id: int,board_id:int = BOARDTYPE_STEP):
        key = (board_id, motor_id)
        with self._lock:
            if key in self.motors:
                self._reset_motor_info(
                    self.motors[key]
                )
    # ---------------------------
    # 查询
    # ---------------------------
    def get(self, motor_id: int,board_id:int = BOARDTYPE_STEP):
        key = (board_id, motor_id)
        with self._lock:
            return self.motors.get(key)

    def get_state(self, motor_id: int,board_id:int = BOARDTYPE_STEP):
        key = (board_id, motor_id)
        with self._lock:
            m = self.motors.get(key)
            return m["state"] if m else None

    def is_busy(self, motor_id: int,board_id:int = BOARDTYPE_STEP) -> bool:
        key = (board_id, motor_id)
        with self._lock:
            m = self.motors.get(key)
            return bool(m and m["state"] == "RUNNING")

    def set_all_enabled(self, enabled):
        with self._lock:
            for motor in self.motors.values():
                motor["enabled"] = enabled


    def set_enabled(self, motor_id, enabled,board_id:int = BOARDTYPE_STEP):
        key = (board_id, motor_id)
        with self._lock:
            self.motors[key]["enabled"] = enabled


    def is_enabled(self, motor_id,board_id:int = BOARDTYPE_STEP):
        key = (board_id, motor_id)
        with self._lock:
            return self.motors[key].get("enabled", False)            


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