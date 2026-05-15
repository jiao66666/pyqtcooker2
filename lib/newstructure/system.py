from lib.newstructure.eventbus import EventBus
from lib.newstructure.stepmotor import StepMotor
from lib.newstructure.fdmotordriver import FeederMotor
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
from lib.newstructure.stepmotor_manager import StepMotorManager

#系统构建中心
def build_system():
    bus = EventBus()
    trackmanager = TrackManager()
    
    boards = buildboards()

    motors = buildmotors(bus,boards)

    motors_manager = buildmotors_manager(bus,boards,motors)

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
        "motors":motors,
        "motorsmanager":motors_manager
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
            POT_BACKUP_MOTOR: StepMotor("pot_backup_motor", 0, bus, boards["stepmotor"]),
            POT1_FLIP_MOTOR: StepMotor("pot1_flip_motor", 1, bus, boards["stepmotor"]),
            POT1_MOVE_MOTOR: StepMotor("pot1_move_motor", 2, bus, boards["stepmotor"]),
            POT2_FLIP_MOTOR: StepMotor("pot2_flip_motor", 3, bus, boards["stepmotor"]),
            POT2_MOVE_MOTOR: StepMotor("pot2_move_motor", 4, bus, boards["stepmotor"])
        },
        "feedermotor":{
            POT1_FLAVORMOTOR1: FeederMotor("pot1_flavor_motor1", 1, bus, boards["feedermotor"]),
            POT1_FLAVORMOTOR2: FeederMotor("pot1_flavor_motor2", 2, bus, boards["feedermotor"]),
            POT1_FLAVORMOTOR3: FeederMotor("pot1_flavor_motor3", 3, bus, boards["feedermotor"]),
            POT1_FLAVORMOTOR4: FeederMotor("pot1_flavor_motor4", 4, bus, boards["feedermotor"]),
            POT1_FLAVORMOTOR5: FeederMotor("pot1_flavor_motor5", 5, bus, boards["feedermotor"]),
            POT1_FLAVORMOTOR6: FeederMotor("pot1_flavor_motor6", 6, bus, boards["feedermotor"]),
            POT1_FLAVORMOTOR7: FeederMotor("pot1_flavor_motor7", 7, bus, boards["feedermotor"]),
            POT1_FLAVORMOTOR8: FeederMotor("pot1_flavor_motor8", 8, bus, boards["feedermotor"]),
            POT1_FLAVORMOTOR9: FeederMotor("pot1_flavor_motor9", 9, bus, boards["feedermotor"]),
            POT1_FLAVORMOTOR10: FeederMotor("pot1_flavor_motor10", 10, bus, boards["feedermotor"]),
            POT1_FLAVORMOTOR11: FeederMotor("pot1_flavor_motor11", 11, bus, boards["feedermotor"]),
            POT1_FLAVORMOTOR12: FeederMotor("pot1_flavor_motor12", 12, bus, boards["feedermotor"]),

            POT2_FLAVORMOTOR13: FeederMotor("pot2_flavor_motor1", 13, bus, boards["feedermotor"]),
            POT2_FLAVORMOTOR14: FeederMotor("pot2_flavor_motor2", 14, bus, boards["feedermotor"]),
            POT2_FLAVORMOTOR15: FeederMotor("pot2_flavor_motor3", 15, bus, boards["feedermotor"]),
            POT2_FLAVORMOTOR16: FeederMotor("pot2_flavor_motor4", 16, bus, boards["feedermotor"]),
            POT2_FLAVORMOTOR17: FeederMotor("pot2_flavor_motor5", 17, bus, boards["feedermotor"]),
            POT2_FLAVORMOTOR18: FeederMotor("pot2_flavor_motor6", 18, bus, boards["feedermotor"]),
            POT2_FLAVORMOTOR19: FeederMotor("pot2_flavor_motor7", 19, bus, boards["feedermotor"]),
            POT2_FLAVORMOTOR20: FeederMotor("pot2_flavor_motor8", 20, bus, boards["feedermotor"]),
            POT2_FLAVORMOTOR21: FeederMotor("pot2_flavor_motor9", 21, bus, boards["feedermotor"]),
            POT2_FLAVORMOTOR22: FeederMotor("pot2_flavor_motor10", 22, bus, boards["feedermotor"]),
            POT2_FLAVORMOTOR23: FeederMotor("pot2_flavor_motor11", 23, bus, boards["feedermotor"]),
            POT2_FLAVORMOTOR24: FeederMotor("pot2_flavor_motor12", 24, bus, boards["feedermotor"])
        }
    }

#电机管理器创建
def buildmotors_manager(bus,boards,motors):
    return StepMotorManager(boards["stepmotor"].board_id,motors["stepmotor"],boards["stepmotor"])

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
    system["scancycle"].start()


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
