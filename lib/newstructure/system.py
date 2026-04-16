from lib.newstructure.eventbus import EventBus
from lib.newstructure.motor import Motor
from lib.newstructure.state_machine import PotStateMachine
from lib.newstructure.scancycle import ScanCycle

def build_system():
    bus = EventBus()

  # 锅1电机
    v_motor_1 = Motor("V1", bus)
    h_motor_1 = Motor("H1", bus)

    # 锅2电机
    v_motor_2 = Motor("V2", bus)
    h_motor_2 = Motor("H2", bus)

    # 状态机绑定各自电机
    pot1 = PotStateMachine(1, v_motor_1, h_motor_1, bus)
    pot2 = PotStateMachine(2, v_motor_2, h_motor_2, bus)

    pot1.start()
    pot2.start()

    return ScanCycle([pot1, pot2])


def main():
    system = build_system()
    system.run()
