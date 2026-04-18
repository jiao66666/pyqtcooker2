class PotStateMachine:
    def __init__(self, pot_id, steps, bus, track_manager):
        self.pot_id = pot_id
        self.state = "IDLE"

        self.bus = bus
        self.current_step = 0
        self.steps = steps

        self.track = track_manager


        # 订阅电机完成事件
        self.bus.subscribe("MOTOR_DONE", self.on_motor_done)

        self.pending_event = None

    def start(self):
        self.state = "CHECK_HOME"

    def tick(self):
        if self.state in ["IDLE", "STOPPED", "WAITING"]:
            return

        if self.state == "CHECK_HOME":
            if self.check_home():
                self.state = "RUNNING"
            return

        if self.state == "RUNNING":
            step = self.steps[self.current_step]

            # 🟢 关键：先申请轨道
            if self.need_track(step["action"]) and not self.track.try_acquire(self.pot_id, step["action"]):
                print(f"Pot {self.pot_id} waiting track")
                return



            step["motor"].move(step["action"])
            self.state = "WAITING"

    def reset(self):
        self.state = "IDLE"

    def check_home(self):
        return True            

    def need_track(self,action: str):
        return action.startswith("move_out_togetfood")

    def on_motor_done(self, data):
        if self.state != "WAITING":
            return

        step = self.steps[self.current_step]
        if data["action"] != step["action"]:
            return
        

        # 🟢 释放轨道
        if self.need_track(step["action"]):  #如果需要跨动作释放，则加变量self.track_accuired 进行保存跨多个动作判断
            self.track.release(self.pot_id, step["action"])

        self.current_step += 1

        if self.current_step >= len(self.steps):
            self.state = "DONE"
        else:
            self.state = "RUNNING"