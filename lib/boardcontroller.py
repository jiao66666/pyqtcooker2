from lib.basecom import RS485Communication
from lib.motordriver import MotorDriver
from lib.boardtype import BoardType


class BoardController:
    def __init__(self, board_type: BoardType,board_name: str = ""):
        """
        :param board_type: 主板类型 (BoardType.FIVE_AXIS, BoardType.SIX_AXIS, BoardType.EIGHT_AXIS) 决定电机发送指令
        :param name: 主板名称 (如 "五轴控制板")
        """
        self.board_type = board_type
        self.board_name = board_name
        self.comm = None
        self.connected = False
        self.motors= []
    
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
                print(f"成功连接到主板，端口: {port}, 波特率: {baudrate}")
                self.init_motors()
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
       motor_nums = 1
       if self.board_type == BoardType.FIVE_AXIS:
           motor_nums = 5
       elif self.board_type == BoardType.FEEDER:
           motor_nums = 24

       for i in range(motor_nums):
            motor = MotorDriver(rs485_instance=self.comm, motor_id=i, board_type=self.board_type, name=f"{i}号电机")
            self.motors.append(motor)   

    
