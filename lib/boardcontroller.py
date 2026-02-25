from lib.basecom import RS485Communication
from lib.motordriver import MotorDriver
from lib.dcmotordriver import DCMotorDriver
from lib.boardtype import *
from lib.websocket_server import WebSocketServer
import threading
import asyncio
import time



class BoardController:
    def __init__(self, board_type: int,board_name: str = ""):
        """
        :param board_type: 主板类型 (BOARDTYPE_FIVE_AXIS, BoardType.SIX_AXIS, BoardType.EIGHT_AXIS) 决定电机发送指令
        :param name: 主板名称 (如 "五轴控制板")
        """
        self.board_type = board_type
        self.board_name = board_name
        self.comm = None
        self.connected = False
        self.motors= []
        self.websocket_server = WebSocketServer()
        self._feedback_thread_started = False
        self._stop_feedback_loop = False  # 停止标志


    def start_feedback_loop(self, interval: float = 1.0):
        """统一启动多电机反馈调度"""
        if self._stop_feedback_loop :
            self._stop_feedback_loop = False

        if self._feedback_thread_started:
            print("反馈调度线程已启动")
            return
        t = threading.Thread(target=self._run_feedback_loop, args=(interval,))
        t.daemon = True
        t.start()
        self._feedback_thread_started = True

    def _run_feedback_loop(self, interval: float):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(self._feedback_loop(interval))

    async def _feedback_loop(self, interval: float):
        while not self._stop_feedback_loop:  # 检查停止标志:
            start_time = time.time()

            payload = []
            pos_all = self.motors[0].get_feedback_all()
            #print(f"pos_all value is {pos_all}")
            if pos_all is None:
                print("获取反馈失败")
                continue
            for idx,pos in enumerate(pos_all):
                #print(f"电机{idx}反馈值:{pos}")
                payload.append({
                    "motor_id": self.motors[idx].motor_id,
                    "position": pos
                })
                self.motors[idx].updateFb_position(pos)

            if self.websocket_server:
                try:
                    # 一次性发送所有电机状态
                    #print("发送数据给前端>>>>>>>>>>>")
                    self.websocket_server.send_coordinates_threadsafe(payload)
                except Exception as e:
                    print(f"发送数据异常: {e}")

            # 控制“网络发送节奏”
            elapsed = time.time() - start_time
            sleep_time = max(0, interval - elapsed)
            await asyncio.sleep(sleep_time)
    def connect(self, port: str, baudrate: int) -> bool:
        """连接主板"""
        print("####连接主板####")
        if self.connected:
            print("已经连接到主板")
            return True
        try:
            self.comm = RS485Communication(port=port, baudrate=baudrate, timeout=1.0, boardtype=self.board_type)
            self.connected = self.comm.connect()
            if self.connected:
                print(f"成功连接到主板{self.board_type}，端口: {port}, 波特率: {baudrate}")
                if self.board_type == BOARDTYPE_FIVE_AXIS:
                    print("五轴板连接成功,初始化电机中...")
                    self.init_motors()
                    print("五轴板电机初始化完成")
                elif self.board_type == BOARDTYPE_FEEDER:
                    print("加料板连接成功,初始化电机中...")
                    self.init_dcmotors()    
                    print("加料板电机初始化完成")
            else:
                print(f"连接主板失败，端口: {port}, 波特率: {baudrate}")
            return self.connected
        except Exception as e:
            print(f"连接主板异常: {e}")
            self.connected = False
            return False

    def disconnect(self):
        """断开连接"""
        print("####断开连接####")
        if self.comm:
            self.comm.disconnect()
            self.comm = None
            self.connected = False
            self.motors = []
            self._stop_feedback_loop = True
            self._feedback_thread_started = False

            print("断开连接成功")
            return True
        else:
            print("未连接到主板")

    def init_motors(self):
       """初始化电机"""
       motor_nums = 5
       for i in range(motor_nums):
            motor = MotorDriver(rs485_instance=self.comm, motor_id=i, board_type=self.board_type, name=f"{i}号电机",websocket_server=self.websocket_server)
            self.motors.append(motor) 

       self.motors[1].enable_all_motors()    
       self.start_feedback_loop(0.2)


    def init_dcmotors(self):
       """初始化电机"""
       motor_nums = 24
       for i in range(1,motor_nums):
            motor = DCMotorDriver(rs485_instance=self.comm, motor_id=i, board_type=self.board_type, name=f"{i}号电机")
            self.motors.append(motor)   

       
    
