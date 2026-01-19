import serial
import time
import crcmod
import threading
from typing import Optional, List, Tuple, Union

class RS485Communication:
    """RS485通信类，实现YT_LOCKER24路锁控板的通信协议"""

    def __init__(self, port: str, baudrate: int = 9600, timeout: float = 1.0):
        """
        初始化RS485通信

        参数:
            port: 串口名称，如 'COM1' 或 '/dev/ttyUSB0'
            baudrate: 波特率，默认为9600
            timeout: 读取超时时间，单位秒，默认为1.0
        """
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.serial_conn: Optional[serial.Serial] = None
        self.lock = threading.Lock()
        self.crc16_func = crcmod.mkCrcFun(0x18005, rev=True, initCrc=0xFFFF, xorOut=0x0000)

    def connect(self) -> bool:
        """
        连接到串口

        返回:
            bool: 连接是否成功
        """
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
            return True
        except Exception as e:
            print(f"连接串口失败: {e}")
            return False

    def disconnect(self):
        """断开串口连接"""
        if self.serial_conn and self.serial_conn.is_open:
            self.serial_conn.close()

    def calculate_crc16(self, data: str) -> str:
        """
        计算CRC16-MODBUS校验值

        参数:
            data: 要计算校验值的字符串

        返回:
            str: 4位十六进制CRC校验值（大写）
        """
        crc_value = self.crc16_func(data.encode('utf-8'))
        return f"{crc_value:04X}"

    def build_command(self, command: str, board_id: int, params: List[str] = None, use_crc: bool = True) -> str:
        """
        构建命令字符串

        参数:
            command: 命令名称，如 'OPENLOCK'
            board_id: 板子ID
            params: 参数列表，默认为空
            use_crc: 是否使用CRC校验，默认为True

        返回:
            str: 完整的命令字符串，包含<CR><LF>结尾
        """
        if params is None:
            params = []

        # 构建基本命令: YT+<指令名>=<板子ID>,<参数1>,<参数2>...
        cmd_str = f"YT+{command}={board_id}"
        if params:
            cmd_str += f",{','.join(params)}"
            print(f"将构建命令串(不带CRC):{cmd_str}")

        # 添加CRC校验（如果需要）
        if use_crc:
            crc = self.calculate_crc16(cmd_str)
            cmd_str += f"*{crc}"
            print(f"将构建命令串(带上CRC):{cmd_str}")

        # 添加<CR><LF>结尾
        cmd_str += "\r\n"

        return cmd_str

    def send_command(self, command: str, board_id: int, params: List[str] = None, use_crc: bool = True) -> bool:
        """
        发送命令

        参数:
            command: 命令名称，如 'OPENLOCK'
            board_id: 板子ID
            params: 参数列表，默认为空
            use_crc: 是否使用CRC校验，默认为True

        返回:
            bool: 发送是否成功
        """
        if not self.serial_conn or not self.serial_conn.is_open:
            print("串口未连接")
            return False

        try:
            with self.lock:
                cmd_str = self.build_command(command, board_id, params, use_crc)
                self.serial_conn.write(cmd_str.encode('utf-8'))
                self.serial_conn.flush()
                return True
        except Exception as e:
            print(f"发送命令失败: {e}")
            return False

    def receive_response(self, timeout: float = None) -> Optional[str]:
        """
        接收响应

        参数:
            timeout: 接收超时时间，单位秒，如果为None则使用初始化时设置的timeout

        返回:
            Optional[str]: 接收到的响应字符串，不包含<CR><LF>，如果超时或出错则返回None
        """
        if not self.serial_conn or not self.serial_conn.is_open:
            print("串口未连接")
            return None

        try:
            with self.lock:
                # 设置超时
                original_timeout = self.serial_conn.timeout
                if timeout is not None:
                    self.serial_conn.timeout = timeout

                # 读取响应
                response = self.serial_conn.readline().decode('utf-8').strip()

                # 恢复原始超时设置
                self.serial_conn.timeout = original_timeout

                if not response:
                    return None

                return response
        except Exception as e:
            print(f"接收响应失败: {e}")
            return None

    def parse_response(self, response: str) -> Tuple[bool, str, List[str]]:
        """
        解析响应

        参数:
            response: 接收到的响应字符串

        返回:
            Tuple[bool, str, List[str]]: 
                - 是否为成功响应
                - 响应类型（命令名称或"ERROR"）
                - 参数列表
        """
        # 检查是否是错误响应
        if response.startswith("+ERROR:"):
            # 解析错误响应: +ERROR: <板子ID>,<错误信息>*<CRC16>
            content = response[7:]  # 去掉"+ERROR:"
            if '*' in content:
                content = content.split('*')[0]  # 去掉CRC校验值
            parts = content.split(',', 1)  # 最多分成两部分
            board_id = parts[0] if parts else ""
            error_msg = parts[1] if len(parts) > 1 else ""
            return False, "ERROR", [board_id, error_msg]

        # 解析正确响应: +<指令名>:<板子ID>,<参数1>,<参数2>...*<CRC16>
        if not response.startswith('+'):
            return False, "INVALID", []

        # 提取命令名和参数部分
        if ':' not in response:
            return False, "INVALID", []

        cmd_part, param_part = response[1:].split(':', 1)  # 去掉开头的'+'

        # 去掉CRC校验值（如果存在）
        if '*' in param_part:
            param_part = param_part.split('*')[0]

        # 解析参数
        params = param_part.split(',') if param_part else []

        return True, cmd_part, params

    def execute_command(self, command: str, board_id: int, params: List[str] = None, 
                       use_crc: bool = True, timeout: float = None) -> Tuple[bool, List[str]]:
        """
        执行命令并接收响应

        参数:
            command: 命令名称，如 'OPENLOCK'
            board_id: 板子ID
            params: 参数列表，默认为空
            use_crc: 是否使用CRC校验，默认为True
            timeout: 接收响应的超时时间，单位秒

        返回:
            Tuple[bool, List[str]]: 
                - 命令是否执行成功
                - 响应参数列表（如果是错误响应，则包含错误信息）
        """
        # 发送命令
        if not self.send_command(command, board_id, params, use_crc):
            return False, ["发送命令失败"]

        # 接收响应
        response = self.receive_response(timeout)
        if response is None:
            return False, ["接收响应超时"]

        # 解析响应
        success, resp_type, resp_params = self.parse_response(response)

        if not success:
            if resp_type == "ERROR":
                return False, resp_params
            else:
                return False, ["无效响应"]

        # 检查响应类型是否匹配命令
        if resp_type != command:
            return False, [f"响应类型不匹配，期望: {command}，实际: {resp_type}"]
        
        return True, resp_params

  

  

# 示例用法
if __name__ == "__main__":
    print("=== RS485通信类接口测试 ===")

    # 创建通信对象
    print("1. 创建通信对象")
    comm = RS485Communication(port="COM2", baudrate=9600, timeout=1.0)
    print(f"   串口: {comm.port}, 波特率: {comm.baudrate}, 超时: {comm.timeout}秒")

    # 连接串口
    print("\n2. 连接串口")
    if comm.connect():
        print("   串口连接成功")

        try:
            # 测试CRC计算
            print("\n测试五轴电机开始>>>>>>>>>>>>>>>")
            



        
        finally:
            # 断开连接
            print("\n断开连接")
            comm.disconnect()
            print("   串口连接已断开")
    else: 
        print("   无法连接到串口")

    print("\n=== 测试完成 ===")
