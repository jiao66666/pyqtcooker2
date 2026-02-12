from lib.basecom import RS485Communication
from lib.motordriver import MotorDriver
from lib.dcmotordriver import DCMotorDriver
from lib.boardtype import *
from lib.websocket_server import WebSocketServer


class BoardController:
    def __init__(self, board_type: int,board_name: str = ""):
        """
        :param board_type: 主板类型 (BOARDTYPE_FIVE_AXIS, BoardType.SIX_AXIS, BoardType.EIGHT_AXIS) 决定电机发送指令
        :param name: 主板名称 (如 "五轴控制板")
        """
        self.board_type = board_type
        self.board_name = board_name
        self.comm = None
        self.connected = False
        self.motors= []
        self.websocket_server = WebSocketServer()

    
    def connect(self, port: str, baudrate: int) -> bool:
        """连接主板"""
        print("####连接主板####")
        if self.connected:
            print("已经连接到主板")
            return True
        try:
            self.comm = RS485Communication(port=port, baudrate=baudrate, timeout=1.0, boardtype=self.board_type)
            self.connected = self.comm.connect()
            if self.connected:
                print(f"成功连接到主板{self.board_type}，端口: {port}, 波特率: {baudrate}")
                if self.board_type == BOARDTYPE_FIVE_AXIS:
                    print("五轴板连接成功,初始化电机中...")
                    self.init_motors()
                    print("五轴板电机初始化完成")
                elif self.board_type == BOARDTYPE_FEEDER:
                    print("加料板连接成功,初始化电机中...")
                    self.init_dcmotors()    
                    print("加料板电机初始化完成")
            else:
                print(f"连接主板失败，端口: {port}, 波特率: {baudrate}")
            return self.connected
        except Exception as e:
            print(f"连接主板异常: {e}")
            self.connected = False
            return False

    def disconnect(self):
        """断开连接"""
        print("####断开连接####")
        if self.comm:
            self.comm.disconnect()
            self.comm = None
            self.connected = False
            self.motors = []
            print("断开连接成功")
            return True
        else:
            print("未连接到主板")

    def init_motors(self):
       """初始化电机"""
       motor_nums = 5
       for i in range(motor_nums):
            motor = MotorDriver(rs485_instance=self.comm, motor_id=i, board_type=self.board_type, name=f"{i}号电机",websocket_server=self.websocket_server)
            self.motors.append(motor) 

       self.motors[1].enable_all_motors()    


    def init_dcmotors(self):
       """初始化电机"""
       motor_nums = 24
       for i in range(1,motor_nums):
            motor = DCMotorDriver(rs485_instance=self.comm, motor_id=i, board_type=self.board_type, name=f"{i}号电机")
            self.motors.append(motor)   

       
    
