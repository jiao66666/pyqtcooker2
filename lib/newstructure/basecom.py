import serial
import threading
from typing import Optional, List, Tuple
from lib.boardtype import *
from lib.newstructure.protocols import ProtocolFactory

class RS485Communication:
    """RS485通信类，实现主板通信协议"""
    def __init__(self, port: str, baudrate: int = 115200, timeout: float = 1.0, boardtype: int = BOARDTYPE_FIVE_AXIS):
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.boardtype = boardtype
        self.serial_conn: Optional[serial.Serial] = None
        self.lock = threading.Lock()
        self.protocol = ProtocolFactory.create(boardtype)
        self.connected = False

    def connect(self) -> bool:
        try:
            self.serial_conn = serial.Serial(
                port=self.port,
                baudrate=self.baudrate,
                bytesize=serial.EIGHTBITS,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
                timeout=self.timeout
            )
            print(f"串口{self.port}已成功打开")
            self.connected = True
            return True
        except Exception as e:
            print(f"连接串口失败: {e}")
            return False

    def disconnect(self):
        """断开串口连接"""
        if self.serial_conn and self.serial_conn.is_open:
            self.serial_conn.close()
            self.connected = False
            return True
        return False

    def execute_command(self, command: str, params: List[str] = None) -> Tuple[bool, List[str]]:

        if params is None:
            params = []
       
        if not self.serial_conn or not self.serial_conn.is_open:
                print("串口未连接")
                return False

        try:
            with self.lock:
                cmd_str = self.protocol.build_command(command, params)
                print("发送指令中....")
                self.serial_conn.write(cmd_str.encode('utf-8'))
                self.serial_conn.flush()
                print("主板返回消息>>>>>>")
                res = self.serial_conn.readline().decode('utf-8').strip()
                print(res)
                # 解析响应
                print("解析消息>>>>>>>")
                success, resp_type, resp_params = self.protocol.parse_response(res)

                print(f"Success: {success}")
                print(f"Response Type: {resp_type}")
                print(f"Response Parameters: {resp_params}")

                if not success:
                    if resp_type == "ERROR":
                        print(False, resp_params)  # 控制台输出 False 和 resp_params
                    else:
                        print(False, ["无效响应"])  # 控制台输出 False 和无效响应

                if resp_type != command:
                    print(False, [f"响应类型不匹配，期望: {command}，实际: {resp_type}"])  # 控制台输出错误信息

                return True,["命令执行成功",f"实际执行命令为{cmd_str},返回信息: {resp_params},期望: {command}，实际: {resp_type}"]
        except Exception as e:
            print(f"发送命令失败: {e}")
            return False            








