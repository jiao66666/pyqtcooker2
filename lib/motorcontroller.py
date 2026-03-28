from lib.motordriver import MotorDriver
from typing import List
import threading
from lib.boardtype import *
from concurrent.futures import ThreadPoolExecutor
import time


class MotorController:
    def __init__(self, allmotors: List[MotorDriver]):
        self.motors = allmotors

        self.is_track_using = False
        self.tracker_userid = None
        self.share_area_isclear_event = threading.Event()

        self.action_flags = {}  # 每个锅是否在执行
        self.locks = {}         # 每个锅独立锁
        self.action_flags_lock = threading.Lock()

        self.executor = ThreadPoolExecutor(max_workers=2)

    def require_track(self, potid) -> bool:
        if not self.is_track_using and self.tracker_userid is None:
            self.is_track_using = True
            self.tracker_userid = potid
            return True
        return False

    def release_track(self, potid) -> bool:
        if self.is_track_using and self.tracker_userid == potid:
            self.is_track_using = False
            self.tracker_userid = None
            return True
        return False

    def doTask(self, potid, action):
        print(f"doTask started, POT:{potid}, action:{action}")
        self.executor.submit(self.start_action_in_thread, potid, action)

    def start_action_in_thread(self, potid: int, action: str):

        # ========= 关键1：先判断是否执行中（不阻塞） =========
        with self.action_flags_lock:
            if self.action_flags.get(potid, False):
                print(f"❌ Pot {potid} already running → IGNORE")
                return

            # 先占坑（非常关键！）
            self.action_flags[potid] = True

        # ========= 初始化锁 =========
        if potid not in self.locks:
            print(f"creating lock for potid:{potid}")
            self.locks[potid] = threading.Lock()

        # ========= 进入锅锁（保证同锅串行） =========
        with self.locks[potid]:
            print(f"✅ Pot {potid} START action:{action}")
            print(f"action_flags: {self.action_flags}")

            if self.require_track(potid):
                print(">>> FULL ACTION")
                time.sleep(10)

                print(f"Pot {potid} FULL DONE")

                self.release_track(potid)
                self.share_area_isclear_event.set()

            else:
                print(">>> STEP MODE")

                time.sleep(3)
                print(f"Pot {potid} STEP1 done")

                print("waiting shared area...")
                self.share_area_isclear_event.wait()

                print("got shared area")

                # ⚠️ 这里建议重新抢占轨道
                self.require_track(potid)

                time.sleep(3)
                print(f"Pot {potid} STEP2 done")

                self.release_track(potid)

        # ========= 必须保证一定释放 =========
        with self.action_flags_lock:
            self.action_flags[potid] = False

        print(f"🔚 Pot {potid} END")
        print(f"action_flags: {self.action_flags}")

    def doActionAll(self, action: str, move_motorid: int, flip_motorid: int):
        print("do all the action for once")
        # 模拟执行
        # ...这里可以按需实现具体的动作代码...
    
    def doActionBySteps(self, action: str, move_motorid: int, flip_motorid: int):
        print("do all the action by steps")
        # 模拟执行
        # ...这里可以按需实现具体的分步动作代码...