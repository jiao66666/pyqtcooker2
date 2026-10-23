from lib.newstructure.runtime import runtime
from lib.newstructure.constant import *
class IceService:
    def __init__(self,system):
        self.system = system
        #关键：动作注册表
        self.action_map = {
            "go":self._go_action,
            "pause":self._pause_action,
            "stop":self._stop_action,
        }

        self.task_running = None

    def resetRunning(self, task_id=None):
        print(f"请求重置运行状态，current={self.task_running}, request={task_id}")
        # 只有锁的持有者才能释放
        if self.task_running != task_id:
            print(
                f"运行锁释放失败："
                f"当前持有者={self.task_running}，请求释放者={task_id}"
            )
            return False

        self.task_running = None
        return True

    def reset(self):
        self.task_running = None
        
    def setRunning(self, task_id):
        if self.task_running is not None:
            print(f"运行锁设置失败：当前已经被 {self.task_running} 占用")
            return False

        self.task_running = task_id
        print(f"设置运行锁：{task_id}")
        return True

    def check_workable(self):
        state = self.system["state"]
        # 系统脏状态
        if state["dirty"]:
            return False,"系统被异常终止，请检查后重新启动"

        # 系统模式检查
        if state["mode"] != "READY":
            return False,"系统状态还为准备就绪"

        # 电机使能检查
        if not runtime.is_all_enabled():
            return False,"电机未使能"
        
        # 检查运行锁
        print(self.task_running)
        if self.task_running is not None:
            return False, f"冰柜正在执行任务：{self.task_running}"

        return True,"workable OK"

    # 运行电机动作组[多动作互斥]
    def run_task(self, task_name):
        OK,msg = self.check_workable()
        print(f"OK status:{OK}")
        if not OK:
            return False,msg

        steps = self.system["icebuilder"].build(task_name)
        print("printing.....steps>>>>>>>>>>>>>>>>>>>>>>")
        print(steps)
        
        task_id = f"task:{task_name}"
        self.setRunning(task_id)

        self.system["ice"].submit_task(task_id,steps)
        return True,"submit task OK"

    #纯命令执行非互斥
    def run_control_cmd(self,motor_id,action,params):
        motor = self.system["motors"]["stepmotor"][motor_id]
        def run_fn():
            handler = self.action_map.get(action)
            if not handler:
                return False,f"unknown action: {action}"
            handler(motor, params)
            return True,"run cmd OK"
        ok,msg=run_fn()
        return ok,msg
    
    def _pause_action(self,motor,params):
        motor.pause()

    def _stop_action(self,motor,params):
        motor.stop()
            
    def _go_action(self,motor,params):
        motor.go(
            params["target"],
            params["anglespeed"]
        )      




                            

