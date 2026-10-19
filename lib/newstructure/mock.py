import threading
import time
import random
from lib.newstructure.constant import *


class MockMotor:

    def __init__(self,boardid,websocket_server,interval):
        self.websocket_server = websocket_server
        self._thread = None
        self._running = False
        self._lock = threading.Lock()
        self.interval = interval
        self.boardid = boardid

    def _worker(self):
        print("worker start")

        positions = {0:0,1: 0, 2: 0, 3: 0, 4: 0}

        while self._running:

            for motor_id in positions:
                positions[motor_id] += random.randint(5, 30)

            if self.boardid == BOARDTYPE_STEP:
                self.websocket_server.send([
                    {
                        "type": "potcordinate",
                        "motor_id": mid,
                        "position": pos
                    }
                    for mid, pos in positions.items()
                ])
            elif self.boardid == BOARDTYPE_ICE:   
                self.websocket_server.send([
                    {
                        "type": "icecordinate",
                        "motor_id": mid,
                        "position": pos
                    }
                    for mid, pos in positions.items()
                ]) 

            time.sleep(self.interval)

        print("worker exit")
   
    def start(self):
        with self._lock:

            # 已经在运行
            if self._thread is not None and self._thread.is_alive():
                print("mock already running")
                return

            self._running = True

            self._thread = threading.Thread(
                target=self._worker,
                daemon=True
            )

            self._thread.start()

            print("mock started")

    def stop(self):
        with self._lock:

            if self._thread is None:
                return

            self._running = False

        # 等线程退出（放到锁外）
        self._thread.join()

        with self._lock:
            self._thread = None

        print("mock stopped")

    def is_running(self):
        return (
            self._thread is not None
            and self._thread.is_alive()
        )