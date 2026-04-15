from lib.newstructure.eventbus import EventBus
from lib.newstructure.motor import Motor
from lib.newstructure.state_machine import PotStateMachine
from lib.newstructure.scancycle import ScanCycle

def build_system():
    bus = EventBus()

    v_motor = Motor("V_MOTOR", bus)
    h_motor = Motor("H_MOTOR", bus)

    pot1 = PotStateMachine(1, v_motor, h_motor, bus)
    pot2 = PotStateMachine(2, v_motor, h_motor, bus)

    pot1.start()
    pot2.start()

    return ScanCycle([pot1, pot2])


def main():
    system = build_system()
    system.run()
