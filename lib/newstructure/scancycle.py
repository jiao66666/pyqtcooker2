import threading
import time

class ScanCycle:
    def __init__(self, pots, interval):
        self.pots = pots
        self.running = False
        self.thread = None
        self.interval = interval

    def _loop(self):
        while self.running:
            for p in self.pots:
                p.tick()

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