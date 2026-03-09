# motor_driver.py
from lib.basecom import RS485Communication
from lib.boardtype import *
from typing import Optional, List, Tuple, Union

# 定义DC电机驱动类-加料电机板
class FeederMotorDriver:
    def __init__(self, rs485_instance: RS485Communication, motor_id: int, board_type: int = BOARDTYPE_FEEDER,name: str = ""):
        """
        :param rs485_instance: 已经初始化并连接好的串口对象
        :param motor_id: 板子上的电机ID (1-10)
        :param name: 电机的自定义名称 (如 "X轴", "抓手")
        """
        self.com = rs485_instance # 持有串口引用
        self.motor_id = motor_id
        self.name = name
        self.board_id = board_type

        self.overtime = 1000  # 默认加料电机持续运行时间1秒

        
    def ping(self):
        print("测试加料板连通性....")
        success, resp = self.com.execute_command(
            "PING", 
            [str(self.board_id)]
        )
        if not success:
            print(f"错误: {resp}")
            return False
        
        return True      


    def run(self, overtime:int):
        """运转加料电机"""  ##相对运动
        print("####运行加料电机####")
        if not self.com or not self.com.connected:
            print("错误: 串口未连接，无法运行电机")
            return False
         
        self.overtime = overtime  # 更新持续运行时间
         # 发送运行命令,默认使用模式0（按持续时间开锁），锁开启后反馈为高电平(1)
        success, resp = self.com.execute_command(
            "OPENLOCK", 
            [str(self.board_id), str(self.motor_id),str(overtime),"0","1"]
        )
        if not success:
            print(f"错误: {resp}")
            return False
        return True

    def getfb(self,mode:int)-> Tuple[bool, List[str]]:
        """获取加料电机反馈""" 
        print("####获取加料电机反馈####")
        if not self.com or not self.com.connected:
            print("错误: 串口未连接，无法运行电机")
            return False
         
         # 发送运行命令,默认使用模式0（按持续时间开锁），锁开启后反馈为高电平(1)

        if mode == 0:
            print("获取所有加料电机反馈")
            motors = "1-24"
        else:
            print("获取指定加料电机反馈")
            motors = str(self.motor_id)

        success, resp = self.com.execute_command(
            "GETFB", 
            [str(self.board_id), motors,"0","1"]
        )
        if not success:
            print(f"错误: {resp}")
            return False,[f"错误: {resp}"]
        return True,resp
    
if __name__ == "__main__":
    

    print("\n=== 测试完成 ===")    



