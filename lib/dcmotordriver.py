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

    def stop(self):
        """急停电机"""
        print("####急停电机####")
        if not self.com or not self.com.connected:
            print("错误: 串口未连接，无法运行电机")
            return False
        print(f"[{self.name}] ID:{self.motor_id} 急停中... 主板类型:{self.board_id}")
      
         # 发送运行命令
        success, resp = self.com.execute_command(
            "STOP", 
            [str(self.board_id), str(self.motor_id)]
        )
        if not success:
            print(f"错误: {resp}")
            return False
        return True 

 
    def longrun(self,direction,speed):
        """长运行DC电机"""
        print("####长运行DC电机####")
        if not self.com or not self.com.connected:
            print("错误: 串口未连接，无法运行电机")
            return False
        print(f"[{self.name}] ID:{self.motor_id} 长运行DC电机...,方向:{direction}，速度：{speed} 主板类型:{self.board_id}")
      
         # 发送运行命令
        success, resp = self.com.execute_command(
            "LONG", 
            [str(self.board_id), str(self.motor_id),str(direction),str(speed)]
        )
        if not success:
            print(f"错误: {resp}")
            return False
        return True 


    def run(self,direction,time,speed):
        """运行DC电机"""
        print("####运行DC电机####")
        if not self.com or not self.com.connected:
            print("错误: 串口未连接，无法运行电机")
            return False
        print(f"[{self.name}] ID:{self.motor_id} 运行DC电机...方向:{direction},运行时间:{time},速度:{speed} ,主板类型:{self.board_id}")
      
        if direction >0 :
            time = time
        else:
            time = time * -1    
         # 发送运行命令
        success, resp = self.com.execute_command(
            "RUN", 
            [str(self.board_id), str(self.motor_id),str(time),str(speed)]
        )
        if not success:
            print(f"错误: {resp}")
            return False
        return True 