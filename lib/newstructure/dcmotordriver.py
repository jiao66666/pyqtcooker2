from lib.newstructure.constant import *

# 定义直流电机驱动类-DC电机板
class SpinMotor:
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

    def stop(self):
        """急停电机"""
        print("####急停电机####")
        print(f"[{self.name}] ID:{self.motor_id} 急停中... 主板类型:{self.board_id}")
         # 发送运行命令
        self.com.execute_command_async(
            "STOP", 
            [str(self.board_id), str(self.motor_id)]
        )
        
        return True 

 
    def longrun(self,direction,speed):
        """长运行DC电机"""
        print("####长运行DC电机####")
        print(f"[{self.name}] ID:{self.motor_id} 长运行DC电机...,方向:{direction}，速度：{speed} 主板类型:{self.board_id}")
      
         # 发送运行命令
        self.com.execute_command_async(
            "LONG", 
            [str(self.board_id), str(self.motor_id),str(direction),str(speed)]
        )
       
        return True 


    def run(self,direction,time,speed):
        """运行DC电机"""
        print("####运行DC电机####")
        print(f"[{self.name}] ID:{self.motor_id} 运行DC电机...方向:{direction},运行时间:{time},速度:{speed} ,主板类型:{self.board_id}")
      
        if direction >0 :
            time = time
        else:
            time = -abs(int(time))   

        print(f"time is{time}")      
         # 发送运行命令
        self.com.execute_command_async(
            "RUN", 
            [str(self.board_id), str(self.motor_id),str(time),str(speed)]
        )
        
        return True 



    def setspeed(self,speed):
        """设置电机速度"""
        print("####设置电机速度####")
        print(f"[{self.name}] ID:{self.motor_id} 设置DC电机速度... 主板类型:{self.board_id}")
      
         # 发送运行命令
        self.com.execute_command_async(
            "SPEED", 
            [str(self.board_id), str(self.motor_id),str(speed)]
        )
      
        return True         
    
       
    