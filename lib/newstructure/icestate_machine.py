import queue
from lib.newstructure.runtime import runtime
import time
from lib.newstructure.constant import *

#冰柜状态机模型
class IceStateMachine:
    def __init__(self, bus):
        self.state = "IDLE"

        self.bus = bus
        self.current_step = 0
        self.steps = None
        self.command_queue = queue.Queue()
        self.wait_start_time = 0
        self.running_tasks = set()
        self.running_task_id = None
        self.total_repeat = 0
        self.current_repeat = 0


        # 当前动作执行类型
        self.current_action_type = "single"
        # 并行动作组中尚未完成的电机
        # {(board_id, motor_id): step}
        self.parallel_pending = {}
        # 当前并行动作组
        self.parallel_actions = []        

        
        # 订阅电机完成事件
        self.bus.subscribe("ICE_MOTOR_DONE", self.on_icemotor_done)
        self.bus.subscribe("ESTOP_TRIGGERED", self.on_estop)
        self.bus.subscribe("MOTOR_ERROR", self.on_motor_error)


    def submit_task(self, running_task_id,steps,repeat=1):

        if not isinstance(repeat, int) or isinstance(repeat, bool) or repeat < 1:
                return False

        if not steps:
            print(f"任务 {running_task_id} 的动作组为空，拒绝提交")
            return False
        
        if running_task_id in self.running_tasks:
           print("任务还在执行中，请稍后...")
           return False
        self.running_tasks.add(running_task_id)
        self.running_task_id = running_task_id

        print(f"=========当前任务执行次数为{repeat}次==========")
        self.total_repeat = repeat
        self.current_repeat = 0

        self.command_queue.put(steps)
        print("submitt task OK@!>>>>")

    def clear_running_task(self):
        self.running_tasks = set()
        self.running_task_id = None
        self.total_repeat = 0
        self.current_repeat = 0

        self.parallel_pending.clear()
        self.parallel_actions = []
        self.current_action_type = "single"

    def tick(self):
        if self.state in ["STOPPED"]:
            print(f"ice state machine state is STOPPED")
            return

        elif self.state == "IDLE":
            if not self.command_queue.empty():
                self.steps = self.command_queue.get()
                self.reset_step()
                self.state = "CHECK_HOME"
            return

        elif self.state == "CHECK_HOME":
            print(f"ice machine status is CHECK_HOME")
            if self.check_home():
                self.state = "RUNNING"
            return

        elif self.state == "RUNNING":
            print(f"ice machine state is RUNNING,current step is:{self.steps[self.current_step]}")
            step = self.steps[self.current_step]



            if step["type"] == "parallel_ice":
                self.start_parallel_actions(step["actions"])
            elif step["type"] == "step_ice":
                print(f"<<<<<<<<<<<current action is {step['action']}>>>>>>>>>>>>")
                print(f"icemotor运行参数如下:{step['params']}")
                
                runtime.set_running(
                    board_id=BOARDTYPE_ICE,
                    motor_id=step["motor"].motor_id,
                    action=step["action"],
                    params=step["params"],
                    task_id=f"{self.running_task_id}"
                )
                if step["dotype"] == "reset":
                    step["motor"].reset_zero_byspeed(step["params"]["speed"])  
                elif step["dotype"] == "go":
                    step["motor"].go(step["params"]["target"],step["params"]["speed"]) 
                else:
                    self.state = "ERROR"
                    print(
                        f"未知动作类型 {step['dotype']}，"
                        f"动作名称：{step['action']}"
                    )
                    return 

                # 步进电机等待完成反馈
                self.state = "WAITING"
                self.wait_start_time = time.time()

            elif step["type"] == "dc_ice":
                runtime.set_running(
                    board_id=BOARDTYPE_FEEDER,
                    motor_id=step["motor"].motor_id,
                    action=step["action"],
                    params=step["params"],
                    task_id=f"{self.running_task_id}"
                )
                if step["dotype"] == "on":
                    step["motor"].output_on()
                    time.sleep(step["params"]["delay"])  #阻塞一定时间以确保吸住
                elif step["dotype"] == "off":
                    step["motor"].output_off()    
                    time.sleep(step["params"]["delay"])  #阻塞一定时间以确保吸住
                else:
                    self.state = "ERROR"
                    print(
                        f"未知动作类型 {step['dotype']}，"
                        f"动作名称：{step['action']}"
                    )
                    return 

                # 当前磁吸动作完成，推进下一步
                self.go_next_step("on_icedc_done")
                if self.current_step >= len(self.steps):
                    self.state = "DONE"
                else:
                    self.state = "RUNNING"
   
        elif self.state == "WAITING":
            if time.time() - self.wait_start_time > TIMEOUT:
                print("motor time out !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")

                step = self.steps[self.current_step]

                if self.current_action_type == "parallel":

                    self.error_info = {
                        "step": self.current_step,
                        "actions": [
                            item["action"]
                            for item in self.parallel_pending.values()
                        ],
                        "reason": "parallel_timeout"
                    }

                else:

                    self.error_info = {
                        "step": self.current_step,
                        "action": step["action"],
                        "reason": "timeout"
                    }

                self.state = "ERROR"

        elif self.state == "DONE":
            print("ice machine state is DONE")
            self.current_repeat += 1

            if self.current_repeat < self.total_repeat:
                # 还有剩余次数，重新执行当前动作组
                print(
                    f"准备执行第 {self.current_repeat + 1} 次，"
                    f"总次数 {self.total_repeat}"
                )

                self.reset_step()
                self.state = "CHECK_HOME"

            else:
                # 所有次数执行完毕，通知 ResourceManager 释放任务资源
                self.bus.publish("TASK_DONE", {
                    "task_id": self.running_task_id,
                    "owner_id": self.running_task_id,
                    "owner_type": "task",
                })

                # 清理任务
                self.running_tasks.remove(self.running_task_id)
                self.running_task_id = None
                self.steps = None
                self.state = "IDLE"

                # 重置重复执行计数
                self.total_repeat = 0
                self.current_repeat = 0

        elif self.state == "ERROR":
            print(f"ice machine state is ERROR")  




    def start_parallel_actions(self, actions):

        print("========== 开始执行并行动作组 ==========")

        self.current_action_type = "parallel"

        self.parallel_actions = actions
        self.parallel_pending = {}

        # 第一步：检查并登记所有电机
        for step in actions:

            if step["type"] != "step_ice":
                print(f"当前并行动作组暂不支持该电机类型: {step['type']}")
                self.state = "ERROR"
                return

            motor_id = step["motor"].motor_id
            resource_id = (BOARDTYPE_ICE, motor_id)

            # 一个并行动作组中不允许重复使用同一个电机
            if resource_id in self.parallel_pending:
                print(f"并行动作组存在重复电机: {resource_id}")
                self.state = "ERROR"
                return

            if step["dotype"] not in ("go", "reset"):
                print(f"未知并行动作类型: {step['dotype']}")
                self.state = "ERROR"
                return

            self.parallel_pending[resource_id] = step

        # 第二步：提前登记所有电机运行状态
        for resource_id, step in self.parallel_pending.items():

            runtime.set_running(
                board_id=resource_id[0],
                motor_id=resource_id[1],
                action=step["action"],
                params=step["params"],
                task_id=f"{self.running_task_id}"
            )

        # 第三步：先进入等待状态，再提交运动指令
        self.state = "WAITING"
        self.wait_start_time = time.time()

        # 第四步：依次提交三个电机的运动指令
        for resource_id, step in self.parallel_pending.items():

            print(
                f"并行启动电机 {resource_id}, "
                f"action={step['action']}"
            )

            if step["dotype"] == "reset":

                step["motor"].reset_zero_byspeed(
                    step["params"]["speed"]
                )

            elif step["dotype"] == "go":

                step["motor"].go(
                    step["params"]["target"],
                    step["params"]["speed"]
                )

        print("========== 并行动作组启动完成 ==========")

    def reset(self):
        self.state = "IDLE"    
        self.running_tasks = set()
        self.running_task_id = None

    def check_home(self):
        return True            


    def go_next_step(self,actor="unknown"):
        print(f"*************actor:{actor} push the state to the next action*****************")
        self.current_step += 1

    def reset_step(self):
        print("now reset the step to 0")
        self.current_step = 0
        self.current_action_type = "single"
        self.parallel_pending.clear()
        self.parallel_actions = []

    def on_icemotor_done(self, data):
        print("冰柜步进电机完成运动@@@@@@@@@@@@@@@@@@@@@@@@----statemachine")
        print(f"subscribe data:",data)
        #self.state = "DONE"  #only for test
        motor_id = data["motor_id"]    
        ctx = runtime.get(motor_id,board_id=BOARDTYPE_ICE)
        if not ctx:
            print("》》》没有ctx《《《《")
            return      

        if self.state != "WAITING":
            print("》》》状态不对《《《")
            return          

        # ==============================
        # 并行动作组完成事件
        # ==============================
        if self.current_action_type == "parallel":

            self.handle_parallel_motor_done(
                motor_id,
                ctx
            )

            return

        step = self.steps[self.current_step]
       
        if ctx["action"] != step["action"] or data["motor_id"] != step["motor"].motor_id:  #确保数据的一致性
            print(f"》》》检查未过关《《《{ctx['action']},{step['action']},{data['motor_id']},{step['motor'].motor_id}")
            return
        
        print(f"motor {motor_id} done the action {step['action']}")
        print(f"OK检查过关OK{ctx['action']},{step['action']},{data['motor_id']},{step['motor'].motor_id}")

        self.go_next_step("on_icemotor_done")

        if self.current_step < len(self.steps):
            print(f"current step is:{self.current_step},small than total{len(self.steps)},continue state running...")
            self.state = "RUNNING"                #继续取下一个动作执行
        else:
            print(f"current step is:{self.current_step},equal bigger than total{len(self.steps)},set state done!")
            self.state = "DONE"                   #动作组完成，变更状态


    def handle_parallel_motor_done(self, motor_id, ctx):

        resource_id = (BOARDTYPE_ICE, motor_id)

        step = self.parallel_pending.get(resource_id)

        if not step:
            print(f"该电机不属于当前并行动作组: {resource_id}")
            return

        # 校验动作名称
        if ctx["action"] != step["action"]:

            print(
                f"并行电机动作不匹配: "
                f"{ctx['action']} != {step['action']}"
            )
            return

        print(
            f"并行电机 {motor_id} 完成动作 {step['action']}"
        )

        # 从等待集合中移除已完成电机
        self.parallel_pending.pop(resource_id)

        print(
            f"并行动作剩余等待电机: "
            f"{list(self.parallel_pending.keys())}"
        )

        # 所有电机完成
        if not self.parallel_pending:

            print("========== XYZ 并行动作全部完成 ==========")

            self.parallel_actions = []

            self.go_next_step("parallel_actions_done")

            if self.current_step < len(self.steps):

                self.state = "RUNNING"

            else:

                self.state = "DONE"     

    def on_estop(self, data=None):
        print(f"ice machine ESTOP triggered!")

        self.state = "STOPPED"

        # 清队列
        while not self.command_queue.empty():
            self.command_queue.get()

        # 清运行任务
        self.clear_running_task()

    def on_motor_error(self):
        self.state = "ERROR"    

    def destroy(self):
        self.bus.unsubscribe("ICE_MOTOR_DONE", self.on_icemotor_done)
        self.bus.unsubscribe("ESTOP_TRIGGERED", self.on_estop)
        self.bus.unsubscribe("MOTOR_ERROR", self.on_motor_error)     