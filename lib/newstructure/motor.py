import threading
import time

class Motor:
    def __init__(self, name, bus):
        self.name = name
        self.bus = bus
        self.busy = False

    def move(self, action):
        if self.busy:
            return

        self.busy = True
        print(f"[{self.name}] start {action}")

        threading.Timer(1.0, self._done, args=(action,)).start()

    def _done(self, action):
        self.busy = False
        print(f"[{self.name}] done {action}")
        self.bus.publish("MOTOR_DONE", {
            "motor": self.name,
            "action": action
        })