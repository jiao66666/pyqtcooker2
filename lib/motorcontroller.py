from lib.motordriver import MotorDriver
from typing import List
import threading
from lib.boardtype import *


class MotorController:
    def __init__(self, allmotors: List[MotorDriver]):
        self.is_track_using = False
        self.motors = allmotors
        self.tracker_userid = None
        self.share_area_isclear_event = threading.Event()  # 类成员事件,通知 共享区是否清空安全可进入


    def require_track(self,motorid) -> bool:
        if not self.is_track_using and self.tracker_userid == None:
            self.is_track_using = True
            self.tracker_userid = motorid
            return True
        return False

    def release_track(self,motorid) -> bool:  # 仅限使用者有权限释放
        if self.is_track_using and self.tracker_userid == motorid:
            self.is_track_using = False
            self.tracker_userid = None
            return True
        return False
    
    def get_tracker_userid(self) -> int:
        return self.tracker_userid  
    
    def doTask(self, pot:int,action:str):  #以锅为单位来进行
        if pot == 1:
            move_motorid = POT1_MOVE_MOTOR
            flip_motorid = POT1_FLIP_MOTOR
        else:
            move_motorid = POT2_MOVE_MOTOR
            flip_motorid = POT2_FLIP_MOTOR

        if self.require_track(move_motorid):
           self.doActionAll(action,move_motorid,flip_motorid)
        else:
           self.doActionBySteps(action,move_motorid,flip_motorid)
     
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