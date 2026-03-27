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
        self.share_area_isclear_event = threading.Event()  # 类成员事件,通知共享区是否清空安全可进入

        self.action_flags = {}  # 记录每个锅是否正在执行任务
        self.locks = {}  # 每个锅的独立锁
        self.action_flags_lock = threading.Lock()  # 独立锁，用于确保 action_flags 的更新同步
        self.executor = ThreadPoolExecutor(max_workers=2)  # 设置线程池最大线程数为 2

    def require_track(self, potid) -> bool:
        if not self.is_track_using and self.tracker_userid is None:
            self.is_track_using = True
            self.tracker_userid = potid
            return True
        return False

    def release_track(self, potid) -> bool:  # 仅限使用者有权限释放
        if self.is_track_using and self.tracker_userid == potid:
            self.is_track_using = False
            self.tracker_userid = None
            return True
        return False

    def get_tracker_userid(self) -> int:
        return self.tracker_userid  

    def doTask(self, potid, action):
        # 将方法放入线程池执行
        print(f"doTask started, now execute POT:{potid}, action:{action}")
        self.executor.submit(self.start_action_in_thread, potid, action)

    def start_action_in_thread(self, potid: int, action: str):  # 以锅为单位来进行
        if potid == 1:
            move_motorid = POT1_MOVE_MOTOR
            flip_motorid = POT1_FLIP_MOTOR
        else:
            move_motorid = POT2_MOVE_MOTOR
            flip_motorid = POT2_FLIP_MOTOR

        # 确保每个锅有独立的锁
        if potid not in self.locks:
            print(f"creating threading lock for potid:{potid}")
            self.locks[potid] = threading.Lock()

        with self.locks[potid]:  # 同一个锅的任务不会被重复执行
            print("before doing action, output action_flags")
            print(self.action_flags)

            with self.action_flags_lock:
                # 检查并确保同一个锅的任务只会执行一次
                if self.action_flags.get(potid, False):
                    print(f"Pot {potid} is already performing an action. Task will be ignored.")
                    return  # 如果锅正在执行任务，则放弃当前任务

                # 设置锅正在执行任务
                self.action_flags[potid] = True
                print(f"Pot {potid} is starting action: {action}")

            # 执行任务
            if self.require_track(potid):
                print("start doing all actions for one time>>>")
                time.sleep(10)  # 模拟任务执行时间
                print(f"Pot {potid} action {action} completed.")
                self.share_area_isclear_event.set()  # 共享区域清空
            else:
                print("start doing all actions for bysteps>>>>")
                time.sleep(3)  # 模拟任务执行时间
                print(f"Pot {potid} step1 {action} completed.")
                print("now waiting for the share area to be clear.....")

                # 等待共享区域清空
                self.share_area_isclear_event.wait()
                print("Event received, proceeding with next step...")

                time.sleep(3)  # 模拟任务执行时间
                print(f"Pot {potid} step2 {action} completed.")

            # 完成后重置状态
            with self.action_flags_lock:
                self.action_flags[potid] = False  # 确保状态更新是线程安全的

            print("after doing action, output action_flags")
            print(self.action_flags)

    def doActionAll(self, action: str, move_motorid: int, flip_motorid: int):
        print("do all the action for once")
        # 模拟执行
        # ...这里可以按需实现具体的动作代码...
    
    def doActionBySteps(self, action: str, move_motorid: int, flip_motorid: int):
        print("do all the action by steps")
        # 模拟执行
        # ...这里可以按需实现具体的分步动作代码...