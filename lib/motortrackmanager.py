class MotorTrackManager:
    def __init__(self, motors):
        self.motors = motors
        self.is_track_using = False
        
    def require_track(self):
        self.is_track_using = True

    def release_track(self):
        self.is_track_using = False
