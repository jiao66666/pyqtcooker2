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

        try:
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

                    # ⚠️ 重新抢占轨道（很关键）
                    self.require_track(potid)

                    time.sleep(3)
                    print(f"Pot {potid} STEP2 done")

                    self.release_track(potid)

        finally:
            # ========= 必须保证一定释放（核心） =========
            with self.action_flags_lock:
                self.action_flags[potid] = False

            print(f"🔚 Pot {potid} END")
            print(f"action_flags: {self.action_flags}")


    def doAction(self,potid:int,action:str,step:int = 0):
        print("do all the action for once")
        # 模拟执行
        # ...这里可以按需实现具体的动作代码...
        if potid == 1:
           move_motorid = POT1_MOVE_MOTOR
           flip_motorid = POT1_FLIP_MOTOR
           safe_flip_pos = POT_POS_SAFE_FLIP1
           infood_pos_level = POT1_POS_INFOOD_LEVEL
           firefood_pos_level = POT1_POS_FIREPOT_LEVEL
           firefood_pos_flip  =  POT1_POS_FIREPOT_FLIP
           wait_pos_level = POT1_WAIT_LEVEL
        else:
           move_motorid = POT2_MOVE_MOTOR
           flip_motorid = POT2_FLIP_MOTOR   

           safe_flip_pos = POT_POS_SAFE_FLIP2
           infood_pos_level = POT2_POS_INFOOD_LEVEL
           firefood_pos_level = POT2_POS_FIREPOT_LEVEL
           firefood_pos_flip  =  POT2_POS_FIREPOT_FLIP
           wait_pos_level = POT2_WAIT_LEVEL
        
        flip_speed = 30
        move_speed = 30 
        if action == "pickup_food_fire":
            print("ready to do pickup_food_fire actions")
            if step == 0:   # do all actions once
                print("do it in all ")
                self.motors[flip_motorid].gotask_advanced_curve(safe_flip_pos,flip_speed)   
                self.motors[move_motorid].gotask_advanced_curve(infood_pos_level,move_speed)   
                self.motors[move_motorid].gotask_advanced_curve(firefood_pos_level,move_speed)   
                self.motors[flip_motorid].gotask_advanced_curve(firefood_pos_flip,flip_speed)   
            elif step == 1:   #divided into two steps ,step1
                print("do step 1")
                self.motors[flip_motorid].gotask_advanced_curve(safe_flip_pos,flip_speed)   
                self.motors[move_motorid].gotask_advanced_curve(wait_pos_level,move_speed)   
            elif step == 2:   #divided into two steps ,step2
                print("do step 2")
                self.motors[move_motorid].gotask_advanced_curve(infood_pos_level,move_speed)   
                self.motors[move_motorid].gotask_advanced_curve(firefood_pos_level,move_speed)  
                self.motors[flip_motorid].gotask_advanced_curve(firefood_pos_flip,flip_speed)                    