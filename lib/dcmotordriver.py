# motor_driver.py
from lib.basecom import RS485Communication
from lib.boardtype import *


# 定义直流电机驱动类-DC电机板
class DCMotorDriver:
    def __init__(self, rs485_instance: RS485Communication, motor_id: int, board_type: int = BOARDTYPE_DC,name: str = ""):
        """
        :param rs485_instance: 已经初始化并连接好的串口对象
        :param motor_id: 板子上的电机ID (1-10)
        :param name: 电机的自定义名称 (如 "X轴", "抓手")
        """
        self.com = rs485_instance # 持有串口引用
        self.motor_id = motor_id
        self.name = name
        self.board_id = board_type



 

