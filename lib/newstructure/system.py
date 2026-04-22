from lib.newstructure.eventbus import EventBus
from lib.newstructure.motor import Motor
from lib.newstructure.state_machine import PotStateMachine
from lib.newstructure.scancycle import ScanCycle
from lib.newstructure.trackmanager import TrackManager
from lib.newstructure.boardtype import *
from lib.newstructure.stepbuilder import StepBuilder

def build_system():
    bus = EventBus()
    trackmanager = TrackManager()

    pot1 = PotStateMachine(1, bus, trackmanager)
    pot2 = PotStateMachine(2, bus, trackmanager)

    motors = {
        POT1_FLIP_MOTOR: Motor("pot1_flip_motor", 1, bus),
        POT1_MOVE_MOTOR: Motor("pot1_move_motor", 2, bus),
        POT2_FLIP_MOTOR: Motor("pot2_flip_motor", 3, bus),
        POT2_MOVE_MOTOR: Motor("pot2_move_motor", 4, bus),
    }

    stepbuilder = StepBuilder(motors)
    steps1 = stepbuilder.build("takefood_fire",1)
    pot1.submit_task(steps1)
    steps2 = stepbuilder.build("takefood_fire",2)
    pot2.submit_task(steps2)

    return ScanCycle([pot1, pot2])


def main():
    system = build_system()
    system.run()
