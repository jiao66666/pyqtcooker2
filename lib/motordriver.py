# motor_driver.py
from basecom import RS485Communication,BoardType
from tools import circles_to_pulses
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
        self.current_position = 0 

    def run(self, circles: int, anglespeed: int = 1000):
        """运转电机"""
        print("####运行电机####")
        print(f"[{self.name}] ID:{self.motor_id} 运行 {circles} 圈, 角速度 {anglespeed}, 主板类型:{self.board_id}")
        # 计算脉冲数
        pulses = circles_to_pulses(circles, step_angle=1.8, microsteps=32)
         # 发送运行命令
        success, resp = self.com.execute_command(
            "RUN", 
            [str(self.board_id), str(self.motor_id), str(pulses), str(anglespeed)]
        )
        if not success:
            print(f"错误: {resp}")
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
           motor0.run(circles=400, anglespeed=360)
        finally:
            # 断开连接
            print("\n断开连接")
            comm1.disconnect()
            print("   串口连接已断开")
    else: 
        print("   无法连接到串口")

    print("\n=== 测试完成 ===")    



