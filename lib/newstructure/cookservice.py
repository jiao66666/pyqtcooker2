import threading
from lib.newstructure.system import get_system
from lib.newstructure.runtime import runtime
from lib.newstructure.tools import get_pot_id
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
            "stop":self._stop_action,
            "ping":self._ping_action,
            "openfeeder":self._openfeedermotor_action,
            "getfeeder":self._getfeedermotor_action,
            "dc_longrun":self._dclongrun_action,
            "dc_run":self._dcrun_action,
            "dc_stop":self._dcstop_action
        }

        self.task_running = {
            1: False,
            2: False
        }


    def resetRunning(self, pot_id):
        print(f"{pot_id} 重置运行状态")
        self.task_running[pot_id] = False

    def setRunning(self, pot_id):
        self.task_running[pot_id] = True 

    def check_workable(self,pot_id):
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
        

        # 检查锅运行锁
        print(f"%&&&&&&&&&Task running lock info:current pot is:{pot_id}")
        print(self.task_running)
        if self.task_running.get(pot_id, False):
            return False, f"{pot_id} 正在执行任务"

        return True,"workable OK"

    # 运行锅电机动作组
    def run_task(self, task_name, pot_id):
        OK,msg = self.check_workable(pot_id)
        print(f"OK status:{OK}")
        if not OK:
            return False,msg

        steps = self.system["stepbuilder"].build(task_name, pot_id)
        print("printing.....steps>>>>>>>>>>>>>>>>>>>>>>")
        print(steps)
        self.setRunning(pot_id)
        self.system["pots"][pot_id].submit_task(task_name,steps)
        return True,"submit task OK"

    def run_single_action(self, motor_id, action, params):
        potid = get_pot_id(motor_id)
        OK,msg = self.check_workable(potid)
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
            pot_id=potid,
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
        """ 
        OK,msg = self.check_workable()
        print(f"OK status:{OK}")
        if not OK:
            return False,msg
        """

        motor = self.system["motors"]["stepmotor"][motor_id]
        def run_fn():
            handler = self.action_map.get(action)
            if not handler:
                return False,f"unknown action: {action}"
            handler(motor, params)
            return True,"run cmd OK"
        ok,msg=run_fn()
        return ok,msg

    def run_tastemotor_cmd(self,motor_id,action,params):
        motor = self.system["motors"]["feedermotor"][motor_id]
        def run_fn():
            handler = self.action_map.get(action)
            if not handler:
                return False,f"unknown action: {action}"
            handler(motor, params)
        run_fn()
        return True,"run cmd OK"
    
    def run_dcmotor_cmd(self,motor_id,action,params):
        motor = self.system["motors"]["spinmotor"][motor_id]
        def run_fn():
            handler = self.action_map.get(action)
            if not handler:
                return False,f"unknown action: {action}"
            handler(motor, params)
        run_fn()
        return True,"run cmd OK"


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


    def _ping_action(self,motor,params):
        motor.ping()

    def _openfeedermotor_action(self,motor,params):
        motor.run(params["overtime"])

    def _getfeedermotor_action(self,motor,params):
        motor.getfb(params["mode"])  


    def _dclongrun_action(self,motor,params):
        motor.longrun(params["direction"],params["speed"])

    def _dcrun_action(self,motor,params):
        motor.run(params["direction"],params["time"],params["speed"])

    def _dcstop_action(self,motor,params):
        motor.stop()       
                            

