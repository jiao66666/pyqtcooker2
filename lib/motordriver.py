# motor_driver.py
from lib.basecom import RS485Communication
from lib.boardtype import *
from lib.tools import circles_to_pulses
from typing import Optional, List, Tuple, Union
import threading
import time
from lib.websocket_server import WebSocketServer
import random
import asyncio



# 定义步进电机驱动类-5轴电机板
class MotorDriver:
    def __init__(self, rs485_instance: RS485Communication, motor_id: int, board_type: int = BOARDTYPE_FIVE_AXIS,name: str = "", websocket_server: WebSocketServer = None):
        """
        :param rs485_instance: 已经初始化并连接好的串口对象
        :param motor_id: 板子上的电机ID (1-10)
        :param name: 电机的自定义名称 (如 "X轴", "抓手")
        """
        self.com = rs485_instance # 持有串口引用
        self.motor_id = motor_id
        self.name = name
        self.board_id = board_type

        
        # 如果需要，可以在这里缓存电机状态
        self.current_position = 0.0  # 当前记忆位置 
        self.homed = False  # 是否已回零位
        self.fb_position = 0.0  # 来自电机实时反馈位置
       
        self.websocket_server = websocket_server  # 使用全局 WebSocket 服务器实例


        
    # 获取电机反馈值 ,暂用于测试，实际 使用read_pulses方法获取脉冲数并转化 
    def get_feedback(self):  
        cur_pos = random.randint(0, 100)
        self.fb_position = cur_pos
        return cur_pos

    def convert_pulses_to_position(self, pulses: int) -> float:       
        """将脉冲数转换为实际位置 128 细分，步距角1.8，每转200脉冲"""
        if self.motor_id in [1,2]:
            circles = abs( pulses / (128*200) ) 
        else:
            circles = pulses / (128*200) 

        return circles    

    #任务执行高级模式，可提前跳出当前电机任务，同步执行后面的电机任务，适用于多个电机需要同时运动的情况,如果wait_for_completion = false ,必须指定提前退出位置 。 exit_pos需要<target
    def gotask_advanced(self, target: float, anglespeed: int, wait_for_completion: bool = True,exit_pos:int = 0):
        """单次运转电机"""  ##绝对运动
        print("####运行电机高级任务####")
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


        # 1. 执行命令
        print("执行指令...")
        command = "RUN"
        params = [str(self.board_id), str(self.motor_id), str(pulses), str(anglespeed)]
        success, response = self.com.execute_command(command, params)
        
        if not success:
            print(f"命令执行失败,{response}")
            return False

        readparams = list(map(str, params[:2]))
        timeout = 0.2

        # 2. 创建一个线程来轮询电机状态
        print("启动电机状态轮询...")
        state_thread = threading.Thread(target=self.wait_for_motor_to_pause_advanced,args=(command, readparams,timeout,wait_for_completion,exit_pos))
        state_thread.start()

        # 3. 等待轮询线程完成
        state_thread.join()  # 等待线程完成后继续执行
        print("任务完成，执行下一步")
        return True        
    
    #因为要用到电机的位置值 ，所以只能将方法放到电机类中。
    def wait_for_motor_to_pause_advanced(self, command: str, params: List[str], check_interval: int = 0.2,wait_for_completion: bool = True,exit_pos:int = 0) -> bool:
        """轮询电机状态，直到电机进入 PAUSING 状态"""
        while True:
            success, response = self.com.read_command("RunStatus", params)
            if not success:
                print("读取电机状态失败")
                return False

            status = response[1]  # 获取电机状态
            print(f"当前电机状态: {status}")

            if status == "PAUSEING":
                print("电机暂停，任务结束")
                return True
            elif status == "RUNING" or status == "ORGING":
                print("电机正在运行，等待中...")
                if not wait_for_completion:
                    if self.fb_position >= exit_pos:
                        print(f"电机已达到提前退出位置{exit_pos}，任务结束")
                        return True
                time.sleep(check_interval)  # 每隔 check_interval 检查一次
            elif status == "ERROR":
                print("电机发生错误，停止轮询")
                return False
            else:
                print(f"未知状态: {status}")
                return False     

    def reset_one_motor(self)-> Tuple[bool, List[str]]:
        """复位单个电机"""
        print("####复位电机####")
        if not self.com or not self.com.connected:
            print("错误: 串口未连接，无法运行电机")
            return False
        print(f"[{self.name}] ID:{self.motor_id} 运行 复位电机【{self.name}】, 主板类型:{self.board_id}")
        # 复位脉冲数
        pulses = 3200000

        # 复位方向
        if self.motor_id in [1,2]:  # 1号锅
            direction = 1
        else:
            direction = -1     

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
            return False,[f"错误: {resp}"]

        self.current_position = 0
        self.homed = True
        
        return True,[f"电机{self.name}复位成功"]
    

    def resettask(self)-> Tuple[bool, List[str]]:
        """运行动作任务"""
        print("####运行电机复位任务####")
        if not self.com or not self.com.connected:
            print("错误: 串口未连接，无法运行电机")
            return False
        
        print(f"[{self.name}] ID:{self.motor_id} 运行 复位电机【{self.name}】, 主板类型:{self.board_id}")
        # 复位脉冲数
        pulses = 3200000

        # 复位方向
        if self.motor_id in [1,2]:  # 1号锅
            direction = 1
        else:
            direction = -1     

        if direction >=0:
            pulses = abs(pulses)
        else:
            pulses = -abs(pulses)   

        #复位速度
        anglespeed = 360      
         # 发送运行命令
        success, resp = self.com.run_task(
            "ORGRST", 
            [str(self.board_id), str(self.motor_id), str(pulses), "0",str(anglespeed)]
        )

        if not success:
            print(f"错误: {resp}")
            return False,[f"错误: {resp}"]

        self.current_position = 0
        self.homed = True
        
        return True,[f"电机{self.name}复位成功"]
        
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
        
        if self.homed :
            self.homed = False  # 长运转后位置未知，需要重新回零

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
    
    # mode 0 获取所有电机反馈，mode 1 获取单个电机反馈
    def readpulse(self,mode)-> Tuple[bool, List[str]]:
        """读取电机已转动的脉冲数"""
        print("####读取电机已转脉冲数####")
        if not self.com or not self.com.connected:
            print("错误: 串口未连接，无法运行电机")
            return False,[f"错误: 串口未连接，无法运行电机"]
        print(f"[{self.name}] ID:{self.motor_id} 读取已转脉冲数... 主板类型:{self.board_id}")
      
        if mode == 0:
            command = "ALLPulse"
            motorid = "0"
        else:
            command = "Pulse"
            motorid = str(self.motor_id)
         # 发送运行命令
        success, resp = self.com.read_command(
            command, 
            [str(self.board_id), motorid]
        )
        if not success:
            print(f"错误: {resp}")
            return False,[f"错误: {resp}"]
        return True,[f"反馈成功，返回数据为:{resp[1]}",resp[1]]        

 
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
    comm1 = RS485Communication(port="COM2", baudrate=9600, timeout=2.0, boardtype=BOARDTYPE_FIVE_AXIS)
    print(f"   串口: {comm1.port}, 波特率: {comm1.baudrate}, 超时: {comm1.timeout}秒, 主板类型: {comm1.boardtype}")
    motor0 = MotorDriver(rs485_instance=comm1, motor_id=0, board_type=BOARDTYPE_FIVE_AXIS,name="1号锅旋转电机")
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

