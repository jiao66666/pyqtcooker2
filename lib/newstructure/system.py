from lib.newstructure.eventbus import EventBus
from lib.newstructure.motor import Motor
from lib.newstructure.state_machine import PotStateMachine
from lib.newstructure.scancycle import ScanCycle
from lib.newstructure.trackmanager import TrackManager
from lib.newstructure.boardtype import *
from lib.newstructure.stepbuilder import StepBuilder
from lib.newstructure.basecom import RS485Communication
import threading
from lib.newstructure.runtime import runtime
from lib.newstructure.motorpollingservice import MotorPollingService

def build_system():
    bus = EventBus()
    trackmanager = TrackManager()
    rs485 = RS485Communication(port="COM3", baudrate="19200", timeout=1.0, boardtype=BOARDTYPE_FIVE_AXIS)
    rs485.connect()

    motors = {
        POT1_FLIP_MOTOR: Motor("pot1_flip_motor", 1, bus, rs485),
        POT1_MOVE_MOTOR: Motor("pot1_move_motor", 2, bus, rs485),
        POT2_FLIP_MOTOR: Motor("pot2_flip_motor", 3, bus, rs485),
        POT2_MOVE_MOTOR: Motor("pot2_move_motor", 4, bus, rs485),
    }

    stepbuilder = StepBuilder(motors)

    pot1 = PotStateMachine(1, bus, trackmanager)
    pot2 = PotStateMachine(2, bus, trackmanager)


    polling_service = MotorPollingService(rs485, bus)

    return {
        "bus": bus,
        "trackmanager": trackmanager,
        "stepbuilder": stepbuilder,
        "pots": {
            1: pot1,
            2: pot2
        },
        "polling": polling_service,
    }

def init_system():
    for motor_id in MOTOR_LIST:
        runtime.init_motor(motor_id)

def run_system(system):
    system["polling"].start()
    ScanCycle([
        system["pots"][1],
        system["pots"][2]
    ]).run()


_system = None
_lock = threading.Lock()


def get_system():
    global _system

    if _system is None:
        with _lock:
            if _system is None:   # 双重检查锁（防并发）
                _system = build_system()

    return _system