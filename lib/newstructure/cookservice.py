from lib.newstructure.runtime import runtime
from lib.newstructure.constant import *
from lib.newstructure.tools import get_task_resources
import uuid

#锅服务代码  #多动作使用task,单动作使用action
class CookerService:
    def __init__(self,system,resource_manager):
        self.system = system
        self.resource_manager = resource_manager
        #关键：动作注册表
        self.action_map = {
            "pot_runlong": self._pot_runlong_action,
            "pot_pause":self._pot_pause_action,
            "pot_stop":self._pot_stop_action,
            "pot_go":self._pot_go_action,
            "pot_reset":self._pot_reset_action,
            "feeder_timeopen":self._feeder_timeopen_action,
            "feeder_longon":self._feeder_longon_action,
            "feeder_longoff":self._feeder_longoff_action,
            "spin_longrun":self._spin_longrun_action,
            "spin_run":self._spin_run_action,
            "spin_stop":self._spin_stop_action,
            "spin_speed":self._spin_speed_action,
            "spin_speedall":self._spin_speedall_action
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

    # 运行锅电机动作组
    def run_task(self, task_name, pot_id,repeat=1):
        OK, msg = self.check_workable()
        if not OK:
            return False, msg

        # 获取动作组需要占用的全部电机资源
        resources = get_task_resources(task_name, pot_id=pot_id)

        # 每次任务执行都生成唯一 ID
        task_id = f"task:{pot_id}:{uuid.uuid4().hex}"

        # 申请整个动作组的资源
        success = self.resource_manager.acquire_resources(
            task_id,
            "task",
            resources
        )

        if not success:
            return False, "电机资源被占用，任务无法启动"

        try:
            steps = self.system["stepbuilder"].build(task_name, pot_id)

            print("printing.....steps>>>>>>>>>>>>>>>>>>>>>>")
            print(steps)

            # 提交给状态机执行
            self.system["pots"][pot_id].submit_task(task_id, steps,repeat)

            return True, "submit task OK"

        except Exception as e:
            # 提交失败时，释放本次申请的资源
            self.resource_manager.release_resources(task_id)

            print(f"任务提交失败：{e}")
            return False, f"任务提交失败：{e}"

    def run_potmotor_cmd(self, motor_id, action, params):
        motor = self.system["motors"]["stepmotor"][motor_id]

        return self._run_motor_action(
            motor,
            BOARDTYPE_STEP,
            motor_id,
            action,
            params
        )


    def run_tastemotor_cmd(self, motor_id, action, params):
        motor = self.system["motors"]["feedermotor"][motor_id]

        return self._run_motor_action(
            motor,
            BOARDTYPE_FEEDER,
            motor_id,
            action,
            params
        )


    def run_dcmotor_cmd(self, motor_id, action, params):
        motor = self.system["motors"]["spinmotor"][motor_id]

        return self._run_motor_action(
            motor,
            BOARDTYPE_SPIN,
            motor_id,
            action,
            params
        )

    def _pot_pause_action(self,motor,params):
        motor.pause()

    def _pot_stop_action(self,motor,params):
        motor.stop()
            
    def _pot_runlong_action(self, motor, params):
        motor.runlong(
            params["speed"],
            params["direction"]
        )    
    def _pot_go_action(self,motor,params):
        motor.go(
            params["target"],
            params["speed"]
        )

    def _pot_reset_action(self,motor,params):
        motor.reset_zero()       

    def _feeder_timeopen_action(self,motor,params):
        motor.run(params["overtime"])

    def _feeder_longon_action(self,motor,params):
        motor.output_on()

    def _feeder_longoff_action(self,motor,params):
        motor.output_off()

    def _spin_longrun_action(self,motor,params):
        motor.longrun(params["direction"],params["speed"])

    def _spin_run_action(self,motor,params):
        motor.run(params["direction"],params["time"],params["speed"])

    def _spin_stop_action(self,motor,params):
        motor.stop()    

    def _spin_speed_action(self,motor,params):
        motor.setspeed(params["speed"])     

    def _spin_speedall_action(self,motor,params):
        self.system["spinmotorsmanager"].setspeedall(params["speed"])    


    def _run_motor_action(self, motor, board_id, motor_id, action, params):
        handler = self.action_map.get(action)
        if not handler:
            return False, f"unknown action: {action}"

        # 控制类动作不申请资源
        control_actions = (
            "pot_pause",
            "pot_stop",
            "spin_stop",
            "feeder_longoff",
        )

        # 控制类动作直接执行，不作为新的运行任务登记
        if action in control_actions:
            try:
                handler(motor, params)
                return True, "run cmd OK"
            except Exception as e:
                return False, f"执行动作失败：{e}"

        resource_id = (board_id, motor_id)
        action_id = f"action:{uuid.uuid4().hex}"

        # 1. 申请独立动作资源
        success = self.resource_manager.acquire_resources(
            action_id,
            "action",
            {resource_id}
        )

        if not success:
            return False, f"电机资源被占用：{resource_id}"

        try:
            # 2. 登记 Runtime
            runtime.set_running(
                motor_id=motor_id,
                action=action,
                params=params,
                task_id=action_id,
                board_id=board_id,
                owner_type="action",
            )

            # 3. 执行命令
            handler(motor, params)

            return True, "run cmd OK"

        except Exception as e:
            # 命令提交失败，清理运行登记并释放资源
            runtime.clear_execution(
                motor_id,
                board_id=board_id
            )

            self.resource_manager.release_resources(action_id)

            return False, f"执行动作失败：{e}"                

