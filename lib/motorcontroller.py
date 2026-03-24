from lib.motordriver import MotorDriver
from typing import List

class MotorController:
    def __init__(self, motors: List[MotorDriver]):
        self.is_track_using = False
        self.allmotors = motors
        self.tracker_userid = None

    def require_track(self,motorid) -> bool:
        if not self.is_track_using and self.tracker_userid == None:
            self.is_track_using = True
            self.tracker_userid = motorid
            return True
        return False

    def release_track(self,motorid) -> bool:  # 仅限使用者有权限释放（当前还没实现权限控制）
        if self.is_track_using and self.tracker_userid == motorid:
            self.is_track_using = False
            self.tracker_userid = None
            return True
        return False
    
    def get_tracker_userid(self) -> int:
        return self.tracker_userid  
    
