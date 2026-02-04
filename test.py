from lib.basecom import RS485Communication
from lib.motordriver import MotorDriver
from lib.boardtype import *
from lib.boardcontroller import BoardController
import time



def testSystemSend():
    #comm1 = RS485Communication(port="COM6", baudrate=115200, timeout=1.0, boardtype=BOARDTYPE_FIVE_AXIS)
    board = BoardController(BOARDTYPE_FIVE_AXIS, board_name="五轴控制板")
    #time.sleep(3)
    board.connect(port="COM6", baudrate=115200)
    board.motors[1].enable_all_motors()
    #motor1 = MotorDriver(rs485_instance=comm1, motor_id=1, board_type=BOARDTYPE_FIVE_AXIS,name="1号锅旋转电机")
    #motor1.enable_all_motors()



def testSystemSend2():
    print("=== RS485通信类接口测试 ===")

    # 创建通信对象
    print("1. 创建通信对象")
    comm1 = RS485Communication(port="COM6", baudrate=115200, timeout=1.0, boardtype=BOARDTYPE_FIVE_AXIS)
   
    print(f"   串口: {comm1.port}, 波特率: {comm1.baudrate}, 超时: {comm1.timeout}秒, 主板类型: {comm1.boardtype}")
    
    # 连接串口
    print("\n2. 连接串口")
    if comm1.connect() :
        print("   串口连接成功")

        try:
           print("\n3. 发送步进电机测试命令: ENABLE ALL .")
           comm1.execute_command("ENABLE", ["1", "0","11111"])
          
        finally:
            # 断开连接
            print("\n断开连接")
            comm1.disconnect()
            print("   串口连接已断开")
    else: 
        print("   无法连接到串口")

    print("\n=== 测试完成 ===")    



testSystemSend2()

