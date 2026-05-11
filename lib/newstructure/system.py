from lib.newstructure.eventbus import EventBus
from lib.newstructure.stepmotor import StepMotor
from lib.newstructure.state_machine import PotStateMachine
from lib.newstructure.scancycle import ScanCycle
from lib.newstructure.trackmanager import TrackManager
from lib.newstructure.constant import *
from lib.newstructure.stepbuilder import StepBuilder
from lib.newstructure.basecom import RS485Communication
import threading
from lib.newstructure.runtime import runtime
from lib.newstructure.motorpollingservice import MotorPollingService
from lib.newstructure.motioncontroller import MotionController

#系统构建中心
def build_system():
    bus = EventBus()
    trackmanager = TrackManager()
    
    boards = buildboards()

    motors = buildmotors(bus,boards)

    stepbuilder = StepBuilder(motors["stepmotor"])

    motion_controller = MotionController(boards["stepmotor"])

    pot1 = PotStateMachine(1, bus, trackmanager, motion_controller)
    pot2 = PotStateMachine(2, bus, trackmanager, motion_controller)

    motorpolling = MotorPollingService(boards["stepmotor"],bus,motors["stepmotor"])

    from lib.newstructure.websocket_server import WebSocketServer
    websocket_server = WebSocketServer()
    
    return {
        "bus": bus,
        "trackmanager": trackmanager,
        "stepbuilder": stepbuilder,
        "pots": {
            1: pot1,
            2: pot2
        },
        "motorpolling": motorpolling,
        "motioncontroller":motion_controller,
        "boards":boards,
        "websocket":websocket_server,
        "motors":motors
    }


def shutdown_system(system):
    print("系统关闭中...")

    # 1. 停止循环类组件
    if "motorpolling" in system:
        system["motorpolling"].stop()

    if "scancycle" in system:
        system["scancycle"].stop()

    if "motioncontroller" in system:
        system["motioncontroller"].stop()  

    if "websocket" in system:
        system["websocket"].stop()          

    # 2. 关闭所有 RS485 连接
    boards = system.get("boards", {})
    for name, board in boards.items():
        try:
            if hasattr(board, "disconnect"):
                print(f"关闭串口: {name}")
                board.disconnect()
        except Exception as e:
            print(f"关闭 {name} 失败: {e}")

    print("系统关闭完成")


#RS485连接创建
def buildboards():
    boards = {}
    for item in BOARDLIST:
        conn = RS485Communication(
            port=item["port"],
            baudrate=item["baudrate"],
            timeout=item["timeout"],
            board_id=item["board_id"]
        )
        conn.connect()
        boards[item["name"]] = conn
    return boards

#电机创建
def buildmotors(bus,boards):
    return {
        "stepmotor":{
            POT1_FLIP_MOTOR: StepMotor("pot1_flip_motor", 1, bus, boards["stepmotor"]),
            POT1_MOVE_MOTOR: StepMotor("pot1_move_motor", 2, bus, boards["stepmotor"]),
            POT2_FLIP_MOTOR: StepMotor("pot2_flip_motor", 3, bus, boards["stepmotor"]),
            POT2_MOVE_MOTOR: StepMotor("pot2_move_motor", 4, bus, boards["stepmotor"])
        }
    }

#初始化轮询状态
def init_system():
    for motor_id in MOTOR_LIST:
        runtime.init_motor(motor_id)

#启动主TICK循环
def run_system(system):
    system["motorpolling"].start()
    system["motioncontroller"].start()
    system["websocket"].start()
    system["scancycle"]=ScanCycle([
        system["pots"][1],
        system["pots"][2]
    ])
    system["scancycle"].run()


_system = None
_system_lock = threading.Lock()

#获取系统实例
def get_system():
    global _system

    if _system is None:
        with _system_lock:
            if _system is None:   # 双重检查锁（防并发）
                _system = build_system()

    return _system
