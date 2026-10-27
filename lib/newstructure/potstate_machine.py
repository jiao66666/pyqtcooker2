import queue
from lib.newstructure.runtime import runtime
import time
from lib.newstructure.constant import *

#锅状态机模型
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
        self.running_task_id = None
        self.total_repeat = 0
        self.current_repeat = 0

        
        # 订阅电机完成事件
        self.bus.subscribe("POT_MOTOR_DONE", self.on_potmotor_done)
        self.bus.subscribe("POT_SPIN_DONE", self.on_potspin_done)
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
        #print(self.command_queue.qsize())

    def clear_running_task(self):
        self.running_tasks = set()
        self.running_task_id = None
        self.total_repeat = 0
        self.current_repeat = 0

    def tick(self):
        if self.state in ["STOPPED"]:
            print(f"{self.pot_id} state machine state is STOPPED")
            return

        elif self.state == "IDLE":
            #print(f"{self.pot_id} machine status is IDLE")
            if not self.command_queue.empty():
                self.steps = self.command_queue.get()
                self.reset_step()
                self.state = "CHECK_HOME"
            return

        elif self.state == "CHECK_HOME":
            print(f"{self.pot_id} machine status is CHECK_HOME")
            if self.check_home():
                self.state = "RUNNING"
            return

        elif self.state == "RUNNING":
            print(f"pot {self.pot_id} machine state is RUNNING,current step is:{self.steps[self.current_step]}")
            step = self.steps[self.current_step]
            if step["type"] == "step_pot": 
                if self.need_track_acquire(step["action"]) and not self.track.try_acquire(self.pot_id):
                    print(f"Pot {self.pot_id} waiting track")
                    if "on_block" in step:
                        self.insert_steps(step["on_block"])
                    return
                
                runtime.set_running(
                    board_id=BOARDTYPE_STEP,
                    motor_id=step["motor"].motor_id,
                    action=step["action"],
                    pot_id=self.pot_id,
                    params=step["params"],
                    task_id=f"{self.running_task_id}",
                    owner_type="task"
                )

                if step["dotype"] == "go":
                    success,resp = step["motor"].go_action(step["action"],step["params"])

                    if not success:
                        if resp[0] == "RETRY":
                            print(
                                f"Pot {self.pot_id}: "
                                f"动作 {step['action']} 提交失败，暂不进入 WAITING"
                            )
                            return

                        if resp[0] == "NO_MOVE":
                            print(
                                f"Pot {self.pot_id}: "
                                f"动作 {step['action']} 无需运动"
                            )
                            # 在这里调用你现有的正常步骤完成/推进逻辑
                elif step["dotype"] == "reset":
                    success,resp = step["motor"].reset_zero_byspeed(step["params"]["speed"])
                    if not success:
                        if resp[0] == "RETRY":
                            print(
                                f"Pot {self.pot_id}: "
                                f"动作 {step['action']} 提交失败，暂不进入 WAITING"
                            )
                            return

                        if resp[0] == "NO_MOVE":
                            print(
                                f"Pot {self.pot_id}: "
                                f"动作 {step['action']} 无需运动"
                            )
                else:
                    self.state = "ERROR"
                    print(
                        f"Pot {self.pot_id}: "
                        f"未知动作类型 {step['dotype']}，"
                        f"动作名称：{step['action']}"
                    )
                    return            
                    
                #可选动态调速
                if  step["params"].get("varspeed", False) == True:
                    startpos = runtime.get_position(step["motor"].motor_id,board_id=BOARDTYPE_STEP)
                    self.motioncontroller.add_task(
                        motor_id=step["motor"].motor_id,
                        start=startpos,
                        end=step["params"]["target"]
                    )
         
            elif step["type"] == "spin_pot":
                print(f"<<<<<<<<<<<current action is {step['action']}>>>>>>>>>>>>")
                print(f"spin motor运行参数如下:{step['params']['direction']}，{step['params']['duration']}，{step['params']['speed']}")
                
                runtime.set_running(
                    board_id=BOARDTYPE_SPIN,
                    motor_id=step["motor"].motor_id,
                    action=step["action"],
                    pot_id=self.pot_id,
                    params=step["params"],
                    task_id=f"{self.running_task_id}"
                )
                
                step["motor"].run(step["params"]["direction"],step["params"]["duration"],step["params"]["speed"])


            self.state = "WAITING"
            self.wait_start_time = time.time()
   
        elif self.state == "WAITING":
            #print(f"{self.pot_id} machine state is WAITING")
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
            print(f"{self.pot_id} machine state is DONE")
            self.current_repeat += 1

            if self.current_repeat < self.total_repeat:
                # 还有剩余次数，重新执行当前动作组
                print(
                    f"锅 {self.pot_id} 准备执行第 {self.current_repeat + 1} 次，"
                    f"总次数 {self.total_repeat}"
                )

                self.reset_step()
                self.state = "CHECK_HOME"

            else:
                # 所有次数执行完毕，通知 ResourceManager 释放任务资源
                self.bus.publish("TASK_DONE", {
                    "pot_id": self.pot_id,
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
            print(f"{self.pot_id} machine state is ERROR")  
            self.bus.unsubscribe("MOTOR_ERROR", self.on_motor_error)
  

    def reset(self):
        self.state = "IDLE"    
        self.running_tasks = set()
        self.running_task_id = None

    def check_home(self):
        return True            

    def insert_steps(self, new_steps):
        # 把 fallback 插入到当前步骤前
        self.steps = (
            self.steps[:self.current_step] +
            new_steps +
            self.steps[self.current_step:]
        )

    def need_track_acquire(self, action: str):
        print(f"<<<<<<<<<<<current action is {action}>>>>>>>>>>>>")

        track_actions = [
            "move_out_togetfood",
            "move_to_track",
            "flip_out_pour",
            "flip_in_wash",
            "flip_out_getfood",
        ]

        return any(action.startswith(prefix) for prefix in track_actions)
    

    def need_track_release(self, action):

        release_actions = [
            "move_in_tofirefood",
            "flip_in_firepot"
        ]

        return any(
            action.startswith(prefix)
            for prefix in release_actions
        )

    def go_next_step(self,actor="unknown"):
        print(f"*************actor:{actor} push the state to the next action*****************")
        self.current_step += 1

    def reset_step(self):
        print("now reset the step to 0")
        self.current_step = 0    

    def on_potmotor_done(self, data):
        print("锅步进电机完成运动@@@@@@@@@@@@@@@@@@@@@@@@----statemachine")
        print(f"subscribe data:",data)
        #self.state = "DONE"  #only for test
        motor_id = data["motor_id"]    
        ctx = runtime.get(motor_id,board_id=BOARDTYPE_STEP)
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

        if self.need_track_release(step["action"]):  #如果需要跨动作释放，则加变量self.track_accuired 进行保存跨多个动作判断
            self.track.release(self.pot_id)

        self.go_next_step("on_potmotor_done")

        if self.current_step < len(self.steps):
            print(f"current step is:{self.current_step},small than total{len(self.steps)},continue state running...")
            self.state = "RUNNING"                #继续取下一个动作执行
        else:
            print(f"current step is:{self.current_step},equal bigger than total{len(self.steps)},set state done!")
            self.state = "DONE"                   #动作组完成，变更状态

    def on_potspin_done(self, data):
        print("DC旋转电机完成运动@@@@@@@@@@@@@@@@@@@@@@@@----statemachine")
        print(f"subscribe data:",data)
        print(f"current step is :{self.current_step}")
        motor_id = data["motor_id"]    
        ctx = runtime.get(motor_id,board_id=BOARDTYPE_SPIN)
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

        self.go_next_step("on_potspin_done")

        if self.current_step < len(self.steps):
            print(f"current step is:{self.current_step},small than total{len(self.steps)},continue state running...")
            self.state = "RUNNING"                #继续取下一个动作执行
        else:
            print(f"current step is:{self.current_step},equal bigger than total{len(self.steps)},set state done!")
            self.state = "DONE"                   #动作组完成，变更状态


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
        self.bus.unsubscribe("POT_MOTOR_DONE", self.on_potmotor_done)
        self.bus.unsubscribe("POT_SPIN_DONE", self.on_potspin_done)
        self.bus.unsubscribe("ESTOP_TRIGGERED", self.on_estop)
        self.bus.unsubscribe("MOTOR_ERROR", self.on_motor_error)     