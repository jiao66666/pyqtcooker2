import threading
import time


# =========================
# 🚧 共享资源：轨道锁
# =========================
class TrackManager:
    def __init__(self):
        self.lock = threading.Lock()
        self.owner = None

    def acquire(self, pot_id):
        print(f"Pot {pot_id} requesting track...")
        self.lock.acquire()
        self.owner = pot_id
        print(f"✅ Track acquired by Pot {pot_id}")

    def release(self, pot_id):
        print(f"🚪 Pot {pot_id} releasing track")
        self.owner = None
        self.lock.release()


track_manager = TrackManager()


# =========================
# ⚙️ Action 执行单元
# =========================
class ActionRunner:

    def __init__(self, pot_id, action_name):
        self.pot_id = pot_id
        self.action_name = action_name
        self.done_event = threading.Event()
        self.stop_speed_event = threading.Event()

    # 模拟电机状态轮询
    def monitor_motor(self):
        while not self.done_event.is_set():
            print(f"[Pot {self.pot_id}] monitoring {self.action_name}...")
            time.sleep(0.5)
        print(f"[Pot {self.pot_id}] monitor exit")

    # 动态调速线程
    def speed_control(self):
        while not self.stop_speed_event.is_set():
            print(f"[Pot {self.pot_id}] adjusting speed...")
            time.sleep(0.3)
        print(f"[Pot {self.pot_id}] speed control stopped")

    def execute(self):
        print(f"🔥 Pot {self.pot_id} START action {self.action_name}")

        # 1️⃣ 如果是轨道动作，申请锁
        if "track" in self.action_name:
            track_manager.acquire(self.pot_id)

        # 2️⃣ 启动监控线程
        monitor_thread = threading.Thread(target=self.monitor_motor)
        monitor_thread.start()

        # 3️⃣ 启动调速线程
        speed_thread = threading.Thread(target=self.speed_control)
        speed_thread.start()

        # 4️⃣ 模拟动作执行
        time.sleep(2)

        # 5️⃣ 动作结束
        self.done_event.set()
        self.stop_speed_event.set()

        monitor_thread.join()
        speed_thread.join()

        # 6️⃣ 释放轨道
        if "track" in self.action_name:
            track_manager.release(self.pot_id)

        print(f"✅ Pot {self.pot_id} FINISH {self.action_name}")


# =========================
# 🍲 Pot 执行线程
# =========================
class PotRunner(threading.Thread):

    def __init__(self, pot_id, actions):
        super().__init__()
        self.pot_id = pot_id
        self.actions = actions

    def run(self):
        print(f"🍲 Pot {self.pot_id} START")

        for action in self.actions:
            runner = ActionRunner(self.pot_id, action)
            runner.execute()

        print(f"🏁 Pot {self.pot_id} DONE")


# =========================
# 🚀 启动系统
# =========================
if __name__ == "__main__":

    pot1_actions = ["heat", "track_move", "stir"]
    pot2_actions = ["stir", "track_move", "heat"]

    pot1 = PotRunner(1, pot1_actions)
    pot2 = PotRunner(2, pot2_actions)

    pot1.start()
    pot2.start()

    pot1.join()
    pot2.join()

    print("🎉 ALL DONE")