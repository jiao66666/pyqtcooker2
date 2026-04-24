from lib.newstructure.constant import *
class StepBuilder:

    def __init__(self, motors):
        self.motors = motors

    def build(self, action, pot_id):
        if pot_id == 1:
            v = self.motors[POT1_FLIP_MOTOR]
            h = self.motors[POT1_MOVE_MOTOR]
            
        elif pot_id == 2:
            v = self.motors[POT2_FLIP_MOTOR]
            h = self.motors[POT2_MOVE_MOTOR]

        if action == "takefood_fire":
            return [
                {"motor": v, "action": f"flip_out_togetfood_{pot_id}","params":ACTION_PARAMS_CONFIG[f"flip_out_togetfood_{pot_id}"]},
                {"motor": h, "action": f"move_out_togetfood_{pot_id}","params":ACTION_PARAMS_CONFIG[f"move_out_togetfood_{pot_id}"],
                 "on_block": [
                     {"motor": h, "action": f"move_to_wait_{pot_id}","params":ACTION_PARAMS_CONFIG[f"move_to_wait_{pot_id}"]},
                     {"motor": h, "action": f"move_to_track_{pot_id}","params":ACTION_PARAMS_CONFIG[f"move_to_track_{pot_id}"]}
                 ]},
                {"motor": h, "action": f"move_in_tofirefood_{pot_id}","params":ACTION_PARAMS_CONFIG[f"move_in_tofirefood_{pot_id}"]},
                {"motor": v, "action": f"flip_in_tofirefood_{pot_id}","params":ACTION_PARAMS_CONFIG[f"flip_in_tofirefood_{pot_id}"]}
            ]
