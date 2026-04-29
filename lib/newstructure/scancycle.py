import time

class ScanCycle:
    def __init__(self, pots):
        self.pots = pots
        self.running = True

    def run(self):
        while self.running:
            for p in self.pots:
                p.tick()

            time.sleep(0.05)  # 20Hz控制周期

    def stop(self):
        self.running = False            