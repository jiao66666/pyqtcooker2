# motor_driver.py
from basecom import RS485Communication

class MotorDriver:
    def __init__(self, rs485_instance: RS485Communication, motor_id: int, name: str = ""):
        """
        :param rs485_instance: 已经初始化并连接好的串口对象
        :param motor_id: 板子上的电机ID (1-10)
        :param name: 电机的自定义名称 (如 "X轴", "抓手")
        """
        self.com = rs485_instance # 持有串口引用
        self.motor_id = motor_id
        self.name = name
        
        # 如果需要，可以在这里缓存电机状态
        self.current_position = 0 

    def move(self, position: int, speed: int = 1000):
        """移动电机"""
        # 根据之前的代码，cmdtype=1 代表五轴电机板
        # 注意：这里假设你的 build_command 已经在 basecom 里处理好了协议细节
        print(f"[{self.name}] ID:{self.motor_id} 移动到 {position}")
        success, resp = self.com.execute_command(
            "RUN", 
            [str(self.motor_id), "0", str(speed), str(position)], 
            checksum_method='lrc', 
            cmdtype=1
        )
        if not success:
            print(f"错误: {resp}")
            return False
        return True

    def stop(self):
        """停止电机"""
        self.com.execute_command("STOP", [str(self.motor_id)], cmdtype=1)


