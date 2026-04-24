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

#系统构建中心
def build_system():
    bus = EventBus()
    trackmanager = TrackManager()
    
    boards = buildboards()

    motors = buildmotors(bus,boards)

    stepbuilder = StepBuilder(motors["stepmotor"])

    pot1 = PotStateMachine(1, bus, trackmanager)
    pot2 = PotStateMachine(2, bus, trackmanager)

    
    pollings = buildpollings(bus,boards,motors)

    return {
        "bus": bus,
        "trackmanager": trackmanager,
        "stepbuilder": stepbuilder,
        "pots": {
            1: pot1,
            2: pot2
        },
        "polling": pollings,
    }

#RS485连接创建
def buildboards():
    rs485_stepmotor = RS485Communication(port="COM3", baudrate="19200", timeout=1.0, boardtype=BOARDTYPE_FIVE_AXIS)
    rs485_stepmotor.connect()

    return {
        "stepmotor":rs485_stepmotor
    }

#电机创建
def buildmotors(bus,boards):
    return {
        "stepmotor":{
            POT1_FLIP_MOTOR: Motor("pot1_flip_motor", 1, bus, boards["stepmotor"]),
            POT1_MOVE_MOTOR: Motor("pot1_move_motor", 2, bus, boards["stepmotor"]),
            POT2_FLIP_MOTOR: Motor("pot2_flip_motor", 3, bus, boards["stepmotor"]),
            POT2_MOVE_MOTOR: Motor("pot2_move_motor", 4, bus, boards["stepmotor"])
        }
    }

#轮询创建
def buildpollings(bus,boards,motors):
    pollings = []
    for key, board in boards.items():
        polling = MotorPollingService(
            board,
            bus,
            motors[key]   # ⭐ 关键修复
        )
        pollings.append(polling)
    return pollings    

#初始化轮询状态
def init_system():
    for motor_id in MOTOR_LIST:
        runtime.init_motor(motor_id)

#启动主TICK循环
def run_system(system):
    for p in system["polling"]:
       p.start()

    ScanCycle([
        system["pots"][1],
        system["pots"][2]
    ]).run()


_system = None
_lock = threading.Lock()

#获取系统实例
def get_system():
    global _system

    if _system is None:
        with _lock:
            if _system is None:   # 双重检查锁（防并发）
                _system = build_system()

    return _system