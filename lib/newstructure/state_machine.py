import queue

class PotStateMachine:
    def __init__(self, pot_id, bus, track_manager):
        self.pot_id = pot_id
        self.state = "IDLE"

        self.bus = bus
        self.current_step = 0
        self.steps = None
        self.track = track_manager
        self.command_queue = queue.Queue()

        
        # 订阅电机完成事件
        self.bus.subscribe("MOTOR_DONE", self.on_motor_done)
    def submit_task(self, steps):
        self.command_queue.put(steps)


    def tick(self):
        if self.state in ["STOPPED", "WAITING"]:
            return

        elif self.state == "IDLE":
            if not self.command_queue.empty():
                self.steps = self.command_queue.get()
                self.current_step = 0
                self.state = "CHECK_HOME"
            return

        elif self.state == "CHECK_HOME":
            if self.check_home():
                self.state = "RUNNING"
            return

        elif self.state == "RUNNING":
            step = self.steps[self.current_step]

            if self.need_track(step["action"]) and not self.track.try_acquire(self.pot_id, step["action"]):
                print(f"Pot {self.pot_id} waiting track")
                if "on_block" in step:
                   self.insert_steps(step["on_block"])
                return

            step["motor"].move(step["action"])
            self.state = "WAITING"

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
        if self.state != "WAITING":
            return

        step = self.steps[self.current_step]
        if data["action"] != step["action"]:
            return
        
        if self.need_track(step["action"]):  #如果需要跨动作释放，则加变量self.track_accuired 进行保存跨多个动作判断
            self.track.release(self.pot_id, step["action"])

        self.current_step += 1

        if self.current_step >= len(self.steps):
            self.state = "DONE"
        else:
            self.state = "RUNNING"