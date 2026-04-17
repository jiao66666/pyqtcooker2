import threading
import time


class TrackManager:
    def __init__(self):
        # 当前轨道是否被占用
        self.lock = threading.Lock()
        self.occupied = False
        self.owner = None

    def try_acquire(self, pot_id, action):
        """
        尝试占用轨道
        返回 True / False
        """
        with self.lock:
            if self.occupied:
                return False

            self.occupied = True
            self.owner = {
                "pot_id": pot_id,
                "action": action,
                "time": time.time()
            }
            return True

    def release(self, pot_id, action):
        """
        释放轨道
        """
        with self.lock:
            # 防止误释放
            if not self.occupied:
                return

            if self.owner and self.owner["pot_id"] == pot_id:
                self.occupied = False
                self.owner = None

    def status(self):
        with self.lock:
            return {
                "occupied": self.occupied,
                "owner": self.owner
            }