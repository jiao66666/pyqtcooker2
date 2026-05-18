# motor_driver.py
from lib.newstructure.constant import *
from typing import Optional, List, Tuple, Union

# 定义DC电机驱动类-加料电机板
class FeederMotor:
    def __init__(self, name,motor_id,bus,rs485):
        """
        :param rs485_instance: 已经初始化并连接好的串口对象
        :param motor_id: 板子上的电机ID (1-10)
        :param name: 电机的自定义名称 (如 "X轴", "抓手")
        """
        self.com = rs485 # 持有串口引用
        self.motor_id = motor_id
        self.name = name
        self.board_id = self.com.board_id
        self.bus = bus
        self.overtime = 1000  # 默认加料电机持续运行时间1秒

    def ping(self):
        print("测试加料板连通性....")
        self.com.execute_command_async(
            "PING", 
            [str(self.board_id)]
        )
       
        return True      

    def run(self, overtime:int):
        """运转加料电机"""  ##相对运动
        print("####运行加料电机####")
        self.overtime = overtime  # 更新持续运行时间
         # 发送运行命令,默认使用模式0（按持续时间开锁），锁开启后反馈为高电平(1)
        self.com.execute_command_async(
            "OPENLOCK", 
            [str(self.board_id), str(self.motor_id),str(overtime),"0","1"]
        )

        return True

    def getfb(self,mode:int)-> Tuple[bool, List[str]]:
        """获取加料电机反馈""" 
        print("####获取加料电机反馈####")
        if mode == 0:
            print("获取所有加料电机反馈")
            motors = "1-24"
        else:
            print("获取指定加料电机反馈")
            motors = str(self.motor_id)

        self.com.execute_command_async(
            "GETFB", 
            [str(self.board_id), motors,"0","1"]
        )

        return True




