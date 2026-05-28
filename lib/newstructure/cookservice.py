import threading
from lib.newstructure.system import get_system
from lib.newstructure.runtime import runtime
class CookerService:
    def __init__(self,system):
        self.system = system
        self.dispatcher = system["dispatcher"]
        #关键：动作注册表
        self.action_map = {
            "run": self._run_action,
            "runlong": self._runlong_action,
            "reset": self._reset_action,
            "move": self._move_action,
            "go":self._go_action,
            "pause":self._pause_action,
            "stop":self._stop_action
        }


    def check_workable(self):
        state = self.system["state"]

        # 系统脏状态
        if state["dirty"]:
            return False,"系统被异常终止，请检查后重新初始化"

        # 系统模式检查
        if state["mode"] != "READY":
            return False,"系统状态还为准备就绪"

        # 电机使能检查
        if not runtime.is_all_enabled():
            return False,"电机未使能"
        
        return True,"workable OK"

    # 运行锅电机动作组
    def run_task(self, task_name, pot_id):
        OK,msg = self.check_workable()
        print(f"OK status:{OK}")
        if not OK:
            return False,msg

        steps = self.system["stepbuilder"].build(task_name, pot_id)
        self.system["pots"][pot_id].submit_task(task_name,steps)
        return True,"submit task OK"

    def run_single_action(self, motor_id, action, params):
        OK,msg = self.check_workable()
        print(f"OK status:{OK}")
        if not OK:
            return False,msg

        motor = self.system["motors"]["stepmotor"][motor_id]
        task_id = f"single:{motor_id}:{action}"
        def run_fn():
            handler = self.action_map.get(action)
            if not handler:
                raise Exception(f"unknown action: {action}")
            handler(motor, params)

        runtime.set_running(
            motor_id=motor_id,
            action=action,
            pot_id=0,
            params=params,
            task_id=task_id
        )

        self.dispatcher.submit(
            task_id=task_id,
            resources=[motor_id],
            run_fn=run_fn
        )

        return True,"submit task ok"
    
    def run_control_cmd(self,motor_id,action,params):
        motor = self.system["motors"]["stepmotor"][motor_id]
        def run_fn():
            handler = self.action_map.get(action)
            if not handler:
                raise Exception(f"unknown action: {action}")
            handler(motor, params)
        ok=run_fn()
        return ok

    def _pause_action(self,motor,params):
        motor.pause()

    def _stop_action(self,motor,params):
        motor.stop()
            
    def _runlong_action(self, motor, params):
        motor.runlong(
            params["speed"],
            params["direction"]
        )    

    def _reset_action(self, motor, params):
        motor.reset_zero() 

    def _move_action(self, motor, params):
        motor.go_action(
            params["action"],
            params
        )     

    def _run_action(self, motor, params):
        motor.run(
            params["circle"],
            params["speed"],
            params["direction"]
        )     

    def _go_action(self,motor,params):
        motor.go(
            params["target"],
            params["anglespeed"]
        )                 

_service = None
_service_lock = threading.Lock()

def get_cookservice():
    global _service

    if _service is None:
        with _service_lock:
            if _service is None:
                _service = CookerService(get_system())

    return _service

cookservice = get_cookservice()
