# motor_driver.py
from lib.basecom import RS485Communication
from lib.boardtype import BoardType
from lib.tools import circles_to_pulses

# 定义电机驱动类
class MotorDriver:
    def __init__(self, rs485_instance: RS485Communication, motor_id: int, board_type: BoardType = BoardType.FIVE_AXIS,name: str = ""):
        """
        :param rs485_instance: 已经初始化并连接好的串口对象
        :param motor_id: 板子上的电机ID (1-10)
        :param name: 电机的自定义名称 (如 "X轴", "抓手")
        """
        self.com = rs485_instance # 持有串口引用
        self.motor_id = motor_id
        self.name = name
        self.board_id = board_type.value

        
        # 如果需要，可以在这里缓存电机状态
        self.current_position = 0.0
        self.homed = False  # 是否已回零位

    

    def reset_one_motor(self, direction: int):
        """复位单个电机"""
        print("####复位电机####")
        if not self.com or not self.com.connected:
            print("错误: 串口未连接，无法运行电机")
            return False
        print(f"[{self.name}] ID:{self.motor_id} 运行 复位电机【{self.name}】, 主板类型:{self.board_id}")
        # 复位脉冲数
        pulses = 3200000
        if direction >=0:
            pulses = abs(pulses)
        else:
            pulses = -abs(pulses)   

        #复位速度
        anglespeed = 360      
         # 发送运行命令
        success, resp = self.com.execute_command(
            "ORGRST", 
            [str(self.board_id), str(self.motor_id), str(pulses), "0",str(anglespeed)]
        )
        if not success:
            print(f"错误: {resp}")
            return False
        
        self.current_position = 0
        self.homed = True
        return True
        
    def enable_all_motors(self):
        print("使能所有电机....")
        success, resp = self.com.execute_command(
            "ENABLE", 
            [str(self.board_id),"0",str("11111")]
        )
        if not success:
            print(f"错误: {resp}")
            return False
        return True  
    
    def fix_all_motors(self):
        print("修复所有电机....")
        success, resp = self.com.execute_command(
            "STOP", 
            [str(self.board_id),"0",str("11111")]
        )
        self.enable_all_motors()
        if not success:
            print(f"错误: {resp}")
            return False
        return True      
    

    def stop_all_motors(self):
        print("急停所有电机....")
        success, resp = self.com.execute_command(
            "STOP", 
            [str(self.board_id),"0",str("11111")]
        )
        if not success:
            print(f"错误: {resp}")
            return False
        return True  
             

    def run(self, circles: float, anglespeed: int, direction: int):
        """单次运转电机"""  ##相对运动
        print("####运行电机####")
        if not self.com or not self.com.connected:
            print("错误: 串口未连接，无法运行电机")
            return False
        print(f"[{self.name}] ID:{self.motor_id} 运行 {circles} 圈, 角速度 {anglespeed}, 主板类型:{self.board_id}")
        # 计算脉冲数
        pulses = circles_to_pulses(circles)
        if direction >=0:
            pulses = abs(pulses)
        else:
            pulses = -abs(pulses)    
         # 发送运行命令
        success, resp = self.com.execute_command(
            "RUN", 
            [str(self.board_id), str(self.motor_id), str(pulses), str(anglespeed)]
        )
        if not success:
            print(f"错误: {resp}")
            return False
        return True
    
    def go(self, target: float, anglespeed: int):  # 回零后进行绝对运动，水平离开0点位置 为正值，翻转离开0点 逆时针为正值 ，顺时值为负值
        """单次运转电机"""  ##绝对运动
        print("####运行电机####")
        if not self.com or not self.com.connected:
            print("错误: 串口未连接，无法运行电机")
            return False
        print(f"[{self.name}] ID:{self.motor_id} 运行到位置{target}, 角速度 {anglespeed}, 主板类型:{self.board_id}")

        if not self.homed:
           print("错误: 电机未回零，无法进行绝对运动")
           return False
        # 计算脉冲数
        if self.motor_id in [2,4] and target < 0:
            print("错误: 水平电机不能运动到负值位置")
            return False
        
       
        deltaDistance = target - self.current_position 
        if deltaDistance == 0:
            print("目标位置与当前位置相同，无需运动")
            return True
         # 计算需要运动的圈数

        circles = abs(deltaDistance)

        if deltaDistance >=0:  ## 确定 目标位在当前位置 的左还是右侧
            if self.motor_id in [1,2]:
                direction = -1
            else:
                direction = 1
        else:
            if self.motor_id in [1,2]:
                direction = 1
            else:
                direction = -1

        self.current_position = target       
         # 发送运行命令
        success = self.run(
            circles,
            anglespeed,
            direction
        )
        if not success:
            print(f"错误: 运行命令失败")
            return False
        
        print("执行成功")
        print(f"执行完后当前位置:{self.current_position}")
        return True    


    def runlong(self, anglespeed: int, direction: int):
        """长运转电机"""
        print("####运行电机####")
        if not self.com or not self.com.connected:
            print("错误: 串口未连接，无法运行电机")
            return False
        print(f"[{self.name}] ID:{self.motor_id} 连续运行, 角速度 {anglespeed}, 主板类型:{self.board_id}")
      
         # 发送运行命令
        success, resp = self.com.execute_command(
            "LONG", 
            [str(self.board_id), str(self.motor_id), str(direction), str(anglespeed)]
        )
        if not success:
            print(f"错误: {resp}")
            return False
        return True
    
    def enable(self):
        """使能电机"""
        print("####使能电机####")
        if not self.com or not self.com.connected:
            print("错误: 串口未连接，无法运行电机")
            return False
        print(f"[{self.name}] ID:{self.motor_id} 使能中... 主板类型:{self.board_id}")
      
         # 发送运行命令
        success, resp = self.com.execute_command(
            "ENABLE", 
            [str(self.board_id), str(self.motor_id)]
        )
        if not success:
            print(f"错误: {resp}")
            return False
        return True
    
    def pause(self):
        """暂停电机"""
        print("####暂停电机####")
        if not self.com or not self.com.connected:
            print("错误: 串口未连接，无法运行电机")
            return False
        print(f"[{self.name}] ID:{self.motor_id} 暂停中... 主板类型:{self.board_id}")
      
         # 发送运行命令
        success, resp = self.com.execute_command(
            "PAUSE", 
            [str(self.board_id), str(self.motor_id)]
        )
        if not success:
            print(f"错误: {resp}")
            return False
        return True    
    
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

    def removelimit(self):
        """急停电机"""
        print("####急停电机####")
        if not self.com or not self.com.connected:
            print("错误: 串口未连接，无法运行电机")
            return False
        print(f"[{self.name}] ID:{self.motor_id} 急停中... 主板类型:{self.board_id}")
      
        cmdstr="11111"
        if self.motor_id == 1:
            cmdstr = "12121"
        elif self.motor_id == 3:
            cmdstr = "12121"
         # 发送运行命令
        success, resp = self.com.execute_command(
            "SETSwitchMode", 
            [str(self.board_id), '0',cmdstr]
        )
        if not success:
            print(f"错误: {resp}")
            return False
        return True    

    def recoverylimit(self):
        """急停电机"""
        print("####急停电机####")
        if not self.com or not self.com.connected:
            print("错误: 串口未连接，无法运行电机")
            return False
        print(f"[{self.name}] ID:{self.motor_id} 急停中... 主板类型:{self.board_id}")
      
        cmdstr="11111"
        if self.motor_id == 1:
            cmdstr = "11111"
        elif self.motor_id == 3:
            cmdstr = "11111"
         # 发送运行命令
        success, resp = self.com.execute_command(
            "SETSwitchMode", 
            [str(self.board_id), '0',cmdstr]
        )
        if not success:
            print(f"错误: {resp}")
            return False
        return True            


    def readmotor(self):
        """读取电机"""
        print("####读取电机####")
        if not self.com or not self.com.connected:
            print("错误: 串口未连接，无法运行电机")
            return False
        print(f"[{self.name}] ID:{self.motor_id} 读取中... 主板类型:{self.board_id}")
      
         # 发送运行命令
        success, resp = self.com.read_command(
            "RunStatus", 
            [str(self.board_id), str(self.motor_id)]
        )
        if not success:
            print(f"错误: {resp}")
            return False
        return True
    

    def runtask(self, circles: float, anglespeed: int, direction: int):
        """运行动作任务"""
        print("####运行电机####")
        if not self.com or not self.com.connected:
            print("错误: 串口未连接，无法运行电机")
            return False
        print(f"电机任务[{self.name}] ID:{self.motor_id} 运行 {circles} 圈, 角速度 {anglespeed}, 主板类型:{self.board_id}")
        # 计算脉冲数
        pulses = circles_to_pulses(circles)
        if direction >=0:
            pulses = abs(pulses)
        else:
            pulses = -abs(pulses)    
         # 发送运行命令
        success, resp = self.com.run_task(
            "RUN", 
            [str(self.board_id), str(self.motor_id), str(pulses), str(anglespeed)]
        )
        if not success:
            print(f"错误: {resp[0]}")
            return False
        return True
    

    def gotask(self, target: float, anglespeed: int):
        """单次运转电机"""  ##绝对运动
        print("####运行电机####")
        if not self.com or not self.com.connected:
            print("错误: 串口未连接，无法运行电机")
            return False
        print(f"[{self.name}] ID:{self.motor_id} 运行到位置{target}, 角速度 {anglespeed}, 主板类型:{self.board_id}")

        if not self.homed:
           print("错误: 电机未回零，无法进行绝对运动")
           return False
        # 计算脉冲数
        if self.motor_id in [2,4] and target < 0:
            print("错误: 水平电机不能运动到负值位置")
            return False
        
       
        deltaDistance = target - self.current_position 
        if deltaDistance == 0:
            print("目标位置与当前位置相同，无需运动")
            return True
         # 计算需要运动的圈数

        circles = abs(deltaDistance)

        if deltaDistance >=0:  ## 确定 目标位在当前位置 的左还是右侧
            if self.motor_id in [1,2]:
                direction = -1
            else:
                direction = 1
        else:
            if self.motor_id in [1,2]:
                direction = 1
            else:
                direction = -1

        self.current_position = target  
        # 计算脉冲数
        pulses = circles_to_pulses(circles)
        if direction >=0:
            pulses = abs(pulses)
        else:
            pulses = -abs(pulses)    
         # 发送运行命令
        success, resp = self.com.run_task(
            "RUN", 
            [str(self.board_id), str(self.motor_id), str(pulses), str(anglespeed)]
        )
        if not success:
            print(f"错误: {resp[0]}")
            return False
        return True    


if __name__ == "__main__":
    print("=== RS485通信类接口测试 ===")

    # 创建通信对象
    print("1. 创建通信对象")
    comm1 = RS485Communication(port="COM2", baudrate=9600, timeout=2.0, boardtype=BoardType.FIVE_AXIS)
    print(f"   串口: {comm1.port}, 波特率: {comm1.baudrate}, 超时: {comm1.timeout}秒, 主板类型: {comm1.boardtype}")
    motor0 = MotorDriver(rs485_instance=comm1, motor_id=0, board_type=BoardType.FIVE_AXIS,name="1号锅旋转电机")
    # 连接串口
    print("\n2. 连接串口")
    if comm1.connect():
        print("   串口连接成功")

        try:
           print("\n3. 发送步进电机测试命令: RUN 1 0 2560000 360")
           motor0.run(circles=400.0, anglespeed=360)
        finally:
            # 断开连接
            print("\n断开连接")
            comm1.disconnect()
            print("   串口连接已断开")
    else: 
        print("   无法连接到串口")

    print("\n=== 测试完成 ===")    



