from lib.newstructure.eventbus import EventBus
from lib.newstructure.motor import Motor
from lib.newstructure.state_machine import PotStateMachine
from lib.newstructure.scancycle import ScanCycle
from lib.newstructure.trackmanager import TrackManager

def build_system():
    bus = EventBus()
    trackmanager = TrackManager()

    # 锅1电机
    v_motor_1 = Motor("pot1_flip_motor",1, bus)
    h_motor_1 = Motor("pot1_move_motor",2, bus)

    # 锅2电机
    v_motor_2 = Motor("pot2_flip_motor",3, bus)
    h_motor_2 = Motor("pot2_move_motor",4, bus)



    steps1 = [
        {"motor": v_motor_1, "action": "flip_out_togetfood_1"},
        {"motor": h_motor_1, "action": "move_out_togetfood_1"},
        {"motor": h_motor_1, "action": "move_in_tofirefood_1"},
        {"motor": v_motor_1, "action": "flip_in_tofirefood_1"}
    ]
    pot1 = PotStateMachine(1, steps1, bus, trackmanager)


    steps2 = [
        {"motor": v_motor_2, "action": "flip_out_togetfood_2"},
        {"motor": h_motor_2, "action": "move_out_togetfood_2"},
        {"motor": h_motor_2, "action": "move_in_tofirefood_2"},
        {"motor": v_motor_2, "action": "flip_in_tofirefood_2"}
    ]
    pot2 = PotStateMachine(2, steps2, bus, trackmanager)

    pot1.start()
    pot2.start()

    return ScanCycle([pot1, pot2])


def main():
    system = build_system()
    system.run()
