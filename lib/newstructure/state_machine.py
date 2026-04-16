class PotStateMachine:
    def __init__(self, pot_id, v_motor, h_motor, bus):
        self.pot_id = pot_id
        self.state = "IDLE"

        self.v = v_motor
        self.h = h_motor
        self.bus = bus

        # 订阅电机完成事件
        self.bus.subscribe("MOTOR_DONE", self.on_motor_done)

        self.pending_event = None

    def start(self):
        self.state = "CHECK_HOME"

    def tick(self):
        if self.state == "IDLE":
            return  # 未启动

        if self.state == "STOPPED":
            return  # 已结束

        if self.state == "CHECK_HOME":
            if self.check_home():
                self.state = "READY"
            else:
                print(f"Pot {self.pot_id} home not ready")
            return

        if self.state == "READY":
            self.state = "V1"
            return

        if self.state == "V1":
            self.v.move("vertical_down")
            self.state = "WAIT_V1"

        elif self.state == "H1_READY":
            self.h.move("horizontal_move")
            self.state = "WAIT_H1"

        elif self.state == "DONE":
            print(f"Pot {self.pot_id} finished")
            self.state = "STOPPED"

    def reset(self):
        self.state = "IDLE"

    def check_home(self):
        return True            

    def on_motor_done(self, data):
        if data["source"] == self.v.name and self.state == "WAIT_V1":
            self.state = "H1_READY"

        elif data["source"] == self.h.name and self.state == "WAIT_H1":
            self.state = "DONE"