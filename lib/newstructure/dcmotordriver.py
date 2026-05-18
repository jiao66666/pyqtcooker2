from lib.newstructure.constant import *

# 定义直流电机驱动类-DC电机板
class DCMotor:
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
    
    def allrun(self,direction1,time1,speed1,direction2,time2,speed2):
        """设置全部电机旋转"""
        print("####设置全部电机旋转####")
        print(f"[{self.name}] ID:{self.motor_id} 设置DC电机全部旋转... 主板类型:{self.board_id}")
      
        if direction1 >0 :
            time1 = time1
        else:
            time1 = time1 * -1         

        if direction2 >0 :
            time2 = time2
        else:
            time2 = time2 * -1    
         # 发送运行命令
        self.com.execute_command_async(
            "ALLRUN", 
            [str(self.board_id), "0",str(time1),str(speed1),str(time2),str(speed2)]
        )
      
        return True         
    

    def getpowerinfo(self):
        """获取电流电压温度相关信息"""
        print("####获取电流电压温度关信息####")
        print(f"[{self.name}] ID:{self.motor_id} 获取电流电压温度相关信息... 主板类型:{self.board_id}")
      
         # 发送运行命令
        self.com.execute_command_async(
            "Power_Value", 
            [str(self.board_id), "0"]
        )
     
        return True 
    

    def getmotorinfo(self):
        """获取电机相关信息"""
        print("####获取电机相关信息####")
        print(f"[{self.name}] ID:{self.motor_id} 获取电机相关信息... 主板类型:{self.board_id}")
    
        # 发送运行命令
        self.com.execute_command_async(
            "RunStatus", 
            [str(self.board_id), "0"]
        )
        
        return True 

    def geterrorinfo(self):
        """获取电机相关错误信息"""
        print("####获取电机相关错误信息####")
        print(f"[{self.name}] ID:{self.motor_id} 获取电机相关信息... 主板类型:{self.board_id}")
    
        # 发送运行命令
        self.com.execute_command_async(
            "Error_Value", 
            [str(self.board_id), str(self.motor_id)]
        )
        
        return True         
    
    def getrpminfo(self):
        """获取电机转速信息"""
        print("####获取电机转速信息####")
        print(f"[{self.name}] ID:{self.motor_id} 获取电机相关信息... 主板类型:{self.board_id}")
    
        # 发送运行命令
        self.com.execute_command_async(
            "RPM", 
            [str(self.board_id), str(self.motor_id)]
        )
       
        return True         