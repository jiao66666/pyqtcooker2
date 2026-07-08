import queue
from lib.newstructure.runtime import runtime
import time
from lib.newstructure.constant import TIMEOUT


class PotStateMachine:
    def __init__(self, pot_id, bus, track_manager, motioncontroller):
        self.pot_id = pot_id
        self.state = "IDLE"

        self.bus = bus
        self.current_step = 0
        self.steps = None
        self.track = track_manager
        self.command_queue = queue.Queue()
        self.wait_start_time = 0
        self.motioncontroller = motioncontroller
        self.running_tasks = set()
        self.running_taskname = None
        self.cookservice = None

        
        # 订阅电机完成事件
        self.bus.subscribe("MOTOR_DONE", self.on_motor_done)
        self.bus.subscribe("ESTOP_TRIGGERED", self.on_estop)
        self.bus.subscribe("MOTOR_ERROR", self.on_motor_error)

    def set_cookservice(self,cookservice):
        self.cookservice = cookservice

    def submit_task(self, task_name,steps):
        if task_name in self.running_tasks:
           print("任务还在执行中，请稍后...")
           return False
        self.running_tasks.add(task_name)
        self.running_taskname = task_name
        self.command_queue.put(steps)
        print("submitt task OK@!>>>>")
        #print(self.command_queue.qsize())

    def clear_running_task(self):
        self.running_tasks = set()
        self.running_taskname = None

    def tick(self):
        if self.state in ["STOPPED"]:
            print(f"{self.pot_id} state machine state is STOPPED")
            return

        elif self.state == "IDLE":
            #print(f"{self.pot_id} machine status is IDLE")
            if not self.command_queue.empty():
                self.steps = self.command_queue.get()
                self.current_step = 0
                self.state = "CHECK_HOME"
            return

        elif self.state == "CHECK_HOME":
            print(f"{self.pot_id} machine status is CHECK_HOME")
            if self.check_home():
                self.state = "RUNNING"
            return

        elif self.state == "RUNNING":
            print(f"{self.pot_id} machine state is RUNNING")
            step = self.steps[self.current_step]
            
            if self.need_track(step["action"]) and not self.track.try_acquire(self.pot_id, step["action"]):
                print(f"Pot {self.pot_id} waiting track")
                if "on_block" in step:
                   self.insert_steps(step["on_block"])
                return
            
            runtime.set_running(
                motor_id=step["motor"].motor_id,
                action=step["action"],
                pot_id=self.pot_id,
                params=step["params"],
                task_id=f"task_{self.running_taskname}"
            )

            step["motor"].go_action(step["action"],step["params"])
            
            #可选动态调速
            if step["params"]["varspeed"] == True:
                startpos = runtime.get_position(step["motor"].motor_id)
                self.motioncontroller.add_task(
                    motor_id=step["motor"].motor_id,
                    start=startpos,
                    end=step["params"]["target"]
                )

            self.state = "WAITING"
            self.wait_start_time = time.time()
   
        elif self.state == "WAITING":
            #print(f"{self.pot_id} machine state is WAITING")
            if time.time() - self.wait_start_time > TIMEOUT:
                print("motor time out !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
                step = self.steps[self.current_step]
                #system = get_system()
                #system["motorsmanager"].stop_all_motors()
                self.state = "ERROR"
                self.error_info = {
                    "step": self.current_step,
                    "action": step["action"],
                    "reason": "timeout"
                }
        elif self.state == "DONE":
            #print("ALL ACTION IS DONE!!!!!!!!!!!")
            print(f"{self.pot_id} machine state is DONE")
            #self.bus.unsubscribe("MOTOR_DONE", self.on_motor_done)
            self.cookservice.resetRunning(self.pot_id)
            self.state = "IDLE"

        elif self.state == "ERROR":
            print(f"{self.pot_id} machine state is ERROR")  
            self.bus.unsubscribe("MOTOR_ERROR", self.on_motor_error)
  

    def reset(self):
        self.state = "IDLE"

    def check_home(self):
        return True            

    def insert_steps(self, new_steps):
        # 把 fallback 插入到当前步骤前
        self.steps = (
            self.steps[:self.current_step] +
            new_steps +
            self.steps[self.current_step:]
        )

    def need_track(self,action: str):
        return action.startswith("move_out_togetfood")

    def on_motor_done(self, data):
        print("电机完成运动@@@@@@@@@@@@@@@@@@@@@@@@----statemachine")
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
        print(f"OK检查未过关OK{ctx['action']},{step['action']},{data['motor_id']},{step['motor'].motor_id}")

        if self.need_track(step["action"]):  #如果需要跨动作释放，则加变量self.track_accuired 进行保存跨多个动作判断
            self.track.release(self.pot_id, step["action"])

        self.current_step += 1

        if self.current_step < len(self.steps):
            self.state = "RUNNING"                #继续取下一个动作执行
        else:
            self.state = "DONE"                   #动作组完成，变更状态
            self.running_tasks.remove(self.running_taskname)


    def on_estop(self, data=None):
        print(f"[Pot {self.pot_id}] ESTOP triggered!")

        self.state = "STOPPED"

        # 清队列
        while not self.command_queue.empty():
            self.command_queue.get()

        # 清 track
        self.track.release(self.pot_id)

        # 清运行任务
        self.clear_running_task()

        # 通知 motioncontroller
        self.motioncontroller.stop()

        # 更新 runtime
        runtime.clear_pot(self.pot_id)            

    def on_motor_error(self):
        self.state = "ERROR"    


    def destroy(self):
        self.bus.unsubscribe("MOTOR_DONE", self.on_motor_done)
        self.bus.unsubscribe("ESTOP_TRIGGERED", self.on_estop)
        self.bus.unsubscribe("MOTOR_ERROR", self.on_motor_error)     