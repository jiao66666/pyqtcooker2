from lib.newstructure.eventbus import EventBus
from lib.newstructure.stepmotordriver import StepMotor
from lib.newstructure.dcmotordriver import DCMotor
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
from lib.newstructure.command_dispatcher import CommandDispatcher
from lib.newstructure.taskresourcemanager import TaskResourceManager
import lib.newstructure.tools as tools
from lib.newstructure.websocket_runtime import websocket_server
from lib.newstructure.mock import MockMotor

#系统构建中心
def build_system():
    bus = EventBus()
    trackmanager = TrackManager()
    
    boards = buildboards()

    motors = buildmotors(bus,boards)

    motors_manager = buildmotors_manager(bus,boards,motors)

    stepbuilder = StepBuilder(motors["stepmotor"])

    motion_controller = MotionController(boards["stepmotor"])

    from lib.newstructure.cookservice import CookerService

    pot1 = PotStateMachine(1, bus, trackmanager, motion_controller)
    pot2 = PotStateMachine(2, bus, trackmanager, motion_controller)


    mockmotor = MockMotor(websocket_server)
    motorpolling = MotorPollingService(boards["stepmotor"],bus,motors["stepmotor"],mockmotor)

    resource_manager = TaskResourceManager(bus)
    dispatcher = CommandDispatcher(resource_manager,bus)
  
    system = {
        "state": {
            "mode": "READY",   # READY / EMERGENCY / RECOVERING / ERROR
            "dirty": False     # 是否需要恢复重新初始化
        },

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
        "motorsmanager":motors_manager,
        "dispatcher":dispatcher,
        "mockmotor":mockmotor,
    }

    cookservice = CookerService(system)
    system["cookservice"] = cookservice
    pot1.set_cookservice(cookservice)
    pot2.set_cookservice(cookservice)
   
    return system


def set_system_state(system, mode):
    system["state"]["mode"] = mode


def set_system_dirty(system, value: bool):
    system["state"]["dirty"] = value



def recovery_system(system):
    print("recovery system .....")
    system["state"]["dirty"]=False
    system["state"]["mode"]="READY"
    system["mockmotor"].start()
    return True


def shutdown_device(system):
    motors = system["motorsmanager"]
    motors.stop_all_motors()
    system["state"]["mode"] = "OFF"
    system["state"]["dirty"] = True
    system["mockmotor"].stop()
    return True

def shutdown_system(system):
    print("系统关闭中...")

    # A. 关闭模拟数据
    system["mockmotor"].stop()

    # =========================
    # 0. 先安全停止所有电机（新增）
    # =========================
    try:
        if "motorsmanager" in system:
            print("停止所有电机...")
            system["motorsmanager"].stop_all_motors()
            system["motorsmanager"].reset_home_all()
    except Exception as e:
        print(f"停止电机失败: {e}")

    # =========================
    # 1. 清理系统运行状态（新增重点）
    # =========================
    try:
        if runtime:
            print("清理runtime状态...")
            runtime.clear_pot(POT1)  
            runtime.clear_pot(POT2)  
    except Exception as e:
        print(f"runtime清理失败: {e}")

    # 2. 停止循环类组件
    if "motorpolling" in system:
        system["motorpolling"].stop()

    if "scancycle" in system:
        system["scancycle"].stop()

    if "motioncontroller" in system:
        system["motioncontroller"].stop()  

    if "websocket" in system:
        system["websocket"].stop()          

    # 3. 关闭所有 RS485 连接
    boards = system.get("boards", {})
    for name, board in boards.items():
        try:
            if hasattr(board, "disconnect"):
                print(f"关闭串口: {name}")
                board.disconnect()
        except Exception as e:
            print(f"关闭 {name} 失败: {e}")

    # =========================
    # 4. 最终系统状态标记（新增）
    # =========================
    try:
        system["state"]["mode"]  = "OFF"
        system["state"]["dirty"] = False
    except Exception as e:
        print(f"系统状态设置失败: {e}")



    print("系统关闭完成")
    return True

#RS485连接创建
def buildboards():
    boards = {}
    boardlist = tools.get_boardlist()
    for item in boardlist:
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
        },
        "spinmotor":{
            POT1_SPIN_MOTOR:DCMotor("pot1_spin_motor", 1, bus, boards["spinmotor"]),
            POT2_SPIN_MOTOR:DCMotor("pot2_spin_motor", 2, bus, boards["spinmotor"])
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
