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
        self.running_taskname = None
        self.iceservice = None

        
        # 订阅电机完成事件
        self.bus.subscribe("ICE_MOTOR_DONE", self.on_icemotor_done)
        self.bus.subscribe("ESTOP_TRIGGERED", self.on_estop)
        self.bus.subscribe("MOTOR_ERROR", self.on_motor_error)

    def set_iceservice(self,iceservice):
        self.iceservice = iceservice

    def submit_task(self, task_name,steps):
        if task_name in self.running_tasks:
           print("任务还在执行中，请稍后...")
           return False
        self.running_tasks.add(task_name)
        self.running_taskname = task_name
        self.command_queue.put(steps)
        print("submitt task OK@!>>>>")

    def clear_running_task(self):
        self.running_tasks = set()
        self.running_taskname = None

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
            if step["type"] == "spin_pot":
                print(f"<<<<<<<<<<<current action is {step['action']}>>>>>>>>>>>>")
                print(f"spin motor运行参数如下:{step['params']['direction']}，{step['params']['duration']}，{step['params']['speed']}")
                
                runtime.set_running(
                    board_id=BOARDTYPE_SPIN,
                    motor_id=step["motor"].motor_id,
                    action=step["action"],
                    params=step["params"],
                    task_id=f"{self.running_taskname}"
                )
                
                step["motor"].run(step["params"]["direction"],step["params"]["duration"],step["params"]["speed"])


            self.state = "WAITING"
            self.wait_start_time = time.time()
   
        elif self.state == "WAITING":
            if time.time() - self.wait_start_time > TIMEOUT:
                print("motor time out !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
                step = self.steps[self.current_step]
                #system = get_system()
                #system["stepmotorsmanager"].stop_all_motors()
                self.state = "ERROR"
                self.error_info = {
                    "step": self.current_step,
                    "action": step["action"],
                    "reason": "timeout"
                }
        elif self.state == "DONE":
            #print("ALL ACTION IS DONE!!!!!!!!!!!")
            print(f"ice machine state is DONE")
            self.iceservice.resetRunning(self.running_taskname)
            self.state = "IDLE"

        elif self.state == "ERROR":
            print(f"ice machine state is ERROR")  
            self.bus.unsubscribe("MOTOR_ERROR", self.on_motor_error)
  

    def reset(self):
        self.state = "IDLE"    
        self.running_tasks = set()
        self.running_taskname = None

    def check_home(self):
        return True            


    def go_next_step(self,actor="unknown"):
        print(f"*************actor:{actor} push the state to the next action*****************")
        self.current_step += 1

    def reset_step(self):
        print("now reset the step to 0")
        self.current_step = 0    

    def on_icemotor_done(self, data):
        print("冰柜步进电机完成运动@@@@@@@@@@@@@@@@@@@@@@@@----statemachine")
        print(f"subscribe data:",data)
        #self.state = "DONE"  #only for test
        motor_id = data["motor_id"]    
        ctx = runtime.get(motor_id)
        if not ctx:
            print("》》》没有ctx《《《《")
            return      

        if self.state != "WAITING":
            print("》》》状态不对《《《")
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
            self.running_tasks.remove(self.running_taskname)

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