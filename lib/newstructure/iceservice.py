import uuid
from lib.newstructure.tools import get_task_resources
from lib.newstructure.runtime import runtime
from lib.newstructure.constant import *

#多动作使用task,单动作使用action
class IceService:
    def __init__(self,system,resource_manager):
        self.system = system
        self.resource_manager = resource_manager
        #关键：动作注册表
        self.action_map = {
            "go":self._go_action,
            "pause":self._pause_action,
            "stop":self._stop_action,
            "reset":self._resetzero_action,
            "resetboth":self._resetzeroboth_action,
            "runlong":self._runlong_action,
            "goinout":self._goinout_action
        }

        
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
        
        return True,"workable OK"

    # 运行电机动作组[多动作互斥]
    def run_task(self, task_name, repeat=1):
        OK, msg = self.check_workable()
        if not OK:
            return False, msg

        # 获取整个冰柜动作组需要占用的资源
        resources = get_task_resources(task_name)

        # 每次任务生成唯一 ID
        task_id = f"task:ice:{uuid.uuid4().hex}"

        # 申请整个任务的资源
        success = self.resource_manager.acquire_resources(
            task_id,
            "task",
            resources
        )

        if not success:
            return False, "冰柜电机资源被占用，任务无法启动"

        try:
            steps = self.system["icebuilder"].build(task_name)

            print("printing.....steps>>>>>>>>>>>>>>>>>>>>>>")
            print(steps)

            # 提交任务，repeat 整体执行期间持续占用资源
            self.system["ice"].submit_task(task_id, steps, repeat)

            return True, "submit task OK"

        except Exception as e:
            self.resource_manager.release_resources(task_id)
            print(f"冰柜任务提交失败：{e}")
            return False, f"冰柜任务提交失败：{e}"

    #纯命令执行非互斥
    def run_icmotor_cmd(self, motor_id, action, params):
        motor = self.system["motors"]["icemotor"][motor_id]

        return self._run_motor_action(
            motor,
            BOARDTYPE_ICE,
            motor_id,
            action,
            params
        )
    
    def _pause_action(self,motor,params):
        motor.pause()

    def _stop_action(self,motor,params):
        motor.stop()
            
    def _go_action(self,motor,params):
        motor.go(
            params["target"],
            params["speed"]
        )      

    def _resetzero_action(self,motor,params):
        motor.reset_zero()  

    def _resetzeroboth_action(self,motor,params):
        motor.reset_zero_both(params["direction"],params["speed"])

    def _runlong_action(self,motor,params):  
        motor.runlong(
            params["speed"],
            params["direction"]
        ) 
    def _goinout_action(self,motor,params):
        motor.go_InOut(
            params["speed"],
            params["direction"]
        )     

    def _run_motor_action(self, motor, board_id, motor_id, action, params):
        handler = self.action_map.get(action)
        if not handler:
            return False, f"unknown action: {action}"

        resource_id = (board_id, motor_id)
        action_id = f"action:ice:{uuid.uuid4().hex}"

        runtime.set_running(
            motor_id=motor_id,
            action=action,
            params=params,
            board_id=board_id,
            owner_type="action",
            task_id=action_id
        )

        # pause / stop 是控制命令，允许干预正在运行的电机
        if action not in ("pause", "stop"):
            success = self.resource_manager.acquire_resources(
                action_id,
                "action",
                {resource_id}
            )

            if not success:
                return False, f"电机资源被占用：{resource_id}"

        try:
            handler(motor, params)
            return True, "run cmd OK"
        except Exception as e:
            # 只有能确认电机没有启动时，才适合立即释放资源。
            # 如果命令可能已启动，应由后续状态/完成事件处理。
            print(f"执行动作失败：{e}")
            return False, f"执行动作失败：{e}"
                            

