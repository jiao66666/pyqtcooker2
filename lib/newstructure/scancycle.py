import threading
import time

class ScanCycle:
    def __init__(self, state_machines, interval):
        self.state_machines = state_machines
        self.running = False
        self.thread = None
        self.interval = interval

    def _loop(self):
        while self.running:
            for s in self.state_machines:
                s.tick()

            time.sleep(self.interval)

    def start(self):
        if self.running:
            return

        self.running = True

        self.thread = threading.Thread(
            target=self._loop,
            daemon=True
        )

        self.thread.start()

    def stop(self):
        self.running = False