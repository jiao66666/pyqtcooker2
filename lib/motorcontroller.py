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
        self.share_area_isclear_event = threading.Event()  # 类成员事件,通知 共享区是否清空安全可进入

        self.action_flags = {}  # 记录每个锅是否正在执行任务
        self.locks = {}  # 每个锅的独立锁
        self.executor = ThreadPoolExecutor(max_workers=2)  # 设置线程池最大线程数为 2


    def require_track(self,potid) -> bool:
        if not self.is_track_using and self.tracker_userid == None:
            self.is_track_using = True
            self.tracker_userid = potid
            return True
        return False

    def release_track(self,potid) -> bool:  # 仅限使用者有权限释放
        if self.is_track_using and self.tracker_userid == potid:
            self.is_track_using = False
            self.tracker_userid = None
            return True
        return False
    
    def get_tracker_userid(self) -> int:
        return self.tracker_userid  
    
    def doTask(self, potid, action):
        # 将方法放入线程池执行
        self.executor.submit(self.start_action_in_thread, potid,action)

    def start_action_in_thread(self, potid:int,action:str):  #以锅为单位来进行
        if potid == 1:
            move_motorid = POT1_MOVE_MOTOR
            flip_motorid = POT1_FLIP_MOTOR
        else:
            move_motorid = POT2_MOVE_MOTOR
            flip_motorid = POT2_FLIP_MOTOR

        self.share_area_isclear_event.clear()
        # 确保每个锅有独立的锁
        if potid not in self.locks:
            self.locks[potid] = threading.Lock()

        with self.locks[potid]:  # 同一个锅的任务不会被重复执行
            if self.action_flags.get(potid, False):
                print(f"Pot {potid} is already performing an action. Task will be ignored.")
                return  # 如果锅正在执行任务，则放弃当前任务
            
            # 设置锅正在执行任务
            self.action_flags[potid] = True
            print(f"Pot {potid} is starting action: {action}")
            
                      
            # 完成后重置状态
            self.action_flags[potid] = False

            if self.require_track(potid):
               print("start doing all actions for one time>>>")  
                # 执行任务
               time.sleep(10)  # 模拟任务执行时间
               print(f"Pot {potid} action {action} completed.")
               self.share_area_isclear_event.set()
               #self.doActionAll(action,move_motorid,flip_motorid)
            else:
               print("start doing all actions for bysteps>>>>")  
                # 执行任务
               time.sleep(3)  # 模拟任务执行时间
               print(f"Pot {potid} step1 {action} completed.")
               print("now waiting for the share area to be clear.....")
               self.share_area_isclear_event.wait()
               time.sleep(3)  # 模拟任务执行时间
               print(f"Pot {potid} step2 {action} completed.")

               #self.doActionBySteps(action,move_motorid,flip_motorid)
     

    def doActionAll(self,action:str,move_motorid:int,flip_motorid:int):
        print("do all the action for once")
        if action =="takefood": #移动到位置 ，动作类型，决定 下面各种参数 [依据motorid和动作来综合 决定 参数 ]
                print("target ,speeddd....so on ")
                flip_speed = 100
                move_speed = 100
                acc_bound = 100
                dec_bound = 100
        elif action == "firefood":
                flip_speed = 100
                move_speed = 100
                acc_bound = 100
                dec_bound = 100
        self.motors[flip_motorid].gotask_advanced_curve(POT_POS_SAFE_FLIP2,flip_speed,acc_bound,dec_bound)   
        self.motors[move_motorid].gotask_advanced_curve(POT2_POS_INFOOD_LEVEL,move_speed,acc_bound,dec_bound)
        self.motors[move_motorid].gotask_advanced_curve(POT2_POS_FIREPOT_LEVEL,move_speed,acc_bound,dec_bound)
        self.motors[flip_motorid].gotask_advanced_curve(POT2_POS_FIREPOT_FLIP,flip_speed,acc_bound,dec_bound)
        self.motors[flip_motorid].gotask_advanced_curve(POT_POS_SAFE_FLIP2,flip_speed,acc_bound,dec_bound)
        self.motors[move_motorid].gotask_advanced_curve(POT2_POS_INFOOD_LEVEL,move_speed,acc_bound,dec_bound)
        self.motors[flip_motorid].gotask_advanced_curve(POT2_POS_DROPFOOD_FLIP,flip_speed,acc_bound,dec_bound)
        self.motors[flip_motorid].gotask_advanced_curve(POT2_POS_WASHPOT_FLIP,flip_speed,acc_bound,dec_bound)
        self.motors[flip_motorid].gotask_advanced_curve(POT_POS_SAFE_FLIP2,flip_speed,acc_bound,dec_bound)
        self.motors[move_motorid].gotask_advanced_curve(POT2_POS_FIREPOT_LEVEL,move_speed,acc_bound,dec_bound)
        self.motors[flip_motorid].gotask_advanced_curve(POT2_POS_FIREPOT_FLIP,flip_speed,acc_bound,dec_bound)

    def doActionBySteps(self,action:str,move_motorid:int,flip_motorid:int):
        print("do all the action by steps")   
        if action =="takefood": #移动到位置 ，动作类型，决定 下面各种参数 [依据motorid和动作来综合 决定 参数 ]
                print("target ,speeddd....so on ")
                flip_speed = 100
                move_speed = 100
                acc_bound = 100
                dec_bound = 100
        elif action == "firefood":
                flip_speed = 100
                move_speed = 100
                acc_bound = 100
                dec_bound = 100
        self.motors[flip_motorid].gotask_advanced_curve(POT_POS_SAFE_FLIP2,flip_speed,acc_bound,dec_bound)   
        self.motors[move_motorid].gotask_advanced_curve(POT2_POS_INFOOD_LEVEL,move_speed,acc_bound,dec_bound)
        self.motors[move_motorid].gotask_advanced_curve(POT2_POS_FIREPOT_LEVEL,move_speed,acc_bound,dec_bound)
        self.motors[flip_motorid].gotask_advanced_curve(POT2_POS_FIREPOT_FLIP,flip_speed,acc_bound,dec_bound)
        self.motors[flip_motorid].gotask_advanced_curve(POT_POS_SAFE_FLIP2,flip_speed,acc_bound,dec_bound)
        self.motors[move_motorid].gotask_advanced_curve(POT2_POS_INFOOD_LEVEL,move_speed,acc_bound,dec_bound)
        self.motors[flip_motorid].gotask_advanced_curve(POT2_POS_DROPFOOD_FLIP,flip_speed,acc_bound,dec_bound)
        self.motors[flip_motorid].gotask_advanced_curve(POT2_POS_WASHPOT_FLIP,flip_speed,acc_bound,dec_bound)
        self.motors[flip_motorid].gotask_advanced_curve(POT_POS_SAFE_FLIP2,flip_speed,acc_bound,dec_bound)
        self.motors[move_motorid].gotask_advanced_curve(POT2_POS_FIREPOT_LEVEL,move_speed,acc_bound,dec_bound)
        self.motors[flip_motorid].gotask_advanced_curve(POT2_POS_FIREPOT_FLIP,flip_speed,acc_bound,dec_bound)

        self.share_area_isclear_event.wait()


        self.motors[flip_motorid].gotask_advanced_curve(POT_POS_SAFE_FLIP2,flip_speed,acc_bound,dec_bound)   
        self.motors[move_motorid].gotask_advanced_curve(POT2_POS_INFOOD_LEVEL,move_speed,acc_bound,dec_bound)
        self.motors[move_motorid].gotask_advanced_curve(POT2_POS_FIREPOT_LEVEL,move_speed,acc_bound,dec_bound)
        self.motors[flip_motorid].gotask_advanced_curve(POT2_POS_FIREPOT_FLIP,flip_speed,acc_bound,dec_bound)
        self.motors[flip_motorid].gotask_advanced_curve(POT_POS_SAFE_FLIP2,flip_speed,acc_bound,dec_bound)
        self.motors[move_motorid].gotask_advanced_curve(POT2_POS_INFOOD_LEVEL,move_speed,acc_bound,dec_bound)
        self.motors[flip_motorid].gotask_advanced_curve(POT2_POS_DROPFOOD_FLIP,flip_speed,acc_bound,dec_bound)
        self.motors[flip_motorid].gotask_advanced_curve(POT2_POS_WASHPOT_FLIP,flip_speed,acc_bound,dec_bound)
        self.motors[flip_motorid].gotask_advanced_curve(POT_POS_SAFE_FLIP2,flip_speed,acc_bound,dec_bound)
        self.motors[move_motorid].gotask_advanced_curve(POT2_POS_FIREPOT_LEVEL,move_speed,acc_bound,dec_bound)
        self.motors[flip_motorid].gotask_advanced_curve(POT2_POS_FIREPOT_FLIP,flip_speed,acc_bound,dec_bound)

    def is_shared_area_clear(self,target:float):  #clear() ,is_set()
        return target in []         