import serial
import time
import crcmod
import threading
from typing import Optional, List, Tuple, Union


class RS485Communication:
    """RS485通信类，实现主板通信协议"""
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

    def calculate_lrc(self, data: str) -> str:
        """
        计算累加校验和 (LRC)

        根据文档的要求：
        1. 计算从 # 到 * (包含首尾) 的所有字符 ASCII 累加和。
        2. 取和的低8位 (sum % 256)。
        3. 转换为2位大写十六进制字符串。

        参数:
            data: 完整指令字符串 (例如: "#RUN,1,0,2560000,360*")

        返回:
            str: 2位十六进制校验值（大写）
        """
        total = 0
        # 找到 # 和 * 的位置
        start_idx = data.find('#')
        end_idx = data.find('*')
        
        if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
            # 计算 # 到 * 之间的字符的ASCII累加和
            for char in data[start_idx:end_idx + 1]:
                total += ord(char)

        # 取低8位 (对应C语言中的 uint8_t 自动溢出，或者 sum & 0xFF)
        checksum = total % 256
        
        # 转换为2位大写十六进制字符串 (对应C语言中的转换逻辑)
        return f"{checksum:02X}"
    

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



    def build_command(self, command: str, params: List[str] = None, checksum_method: str = 'lrc',cmdtype: int = 1) -> str:
        """
        构建命令字符串

        参数:
            command: 命令名称，如 'OPENLOCK'
            params: 参数列表，默认为空
            checksum_method: 使用何种校验方法，默认为lrc
            cmdtype: 命令类型，默认为1,五轴电机板 2，加料电机板

        返回:
            str: 完整的命令字符串，包含<CR><LF>结尾
        """
        if params is None:
            params = []

        # 构建基本命令: #<指令名>,<板子ID>,<参数1>,<参数2>...

        if cmdtype == 1:
           cmd_str = f"#{command}"
        elif cmdtype == 2:
           cmd_str = f"YT+{command}="

        if params:
            if cmdtype == 1:
              cmd_str += f",{','.join(params)}"
            elif cmdtype == 2:
              cmd_str += f"{','.join(params)}"    
        
        # 打印命令字符串（调试用）
        print(f"将构建命令串(不带LRC): {cmd_str}")

        # 计算并添加校验码
        if checksum_method == 'crc':
            # 添加CRC校验（如果需要）
            crc = self.calculate_crc16(cmd_str)
            cmd_str += f"*{crc}"
            print(f"将构建命令串(带上CRC):{cmd_str}")
        elif checksum_method == 'lrc':
            # 计算LRC校验码，这里要计算从 # 到 * 之间的字符的累加和
            lrc = self.calculate_lrc(cmd_str + "*")  # 包含 * 进行校验
            cmd_str += f"*{lrc}"
            print(f"将构建命令串(带上LRC): {cmd_str}")
        # 添加<CR><LF>结尾
        cmd_str += "\r\n"
        
        return cmd_str
    

    def send_command(self,  command: str,  params: List[str] = None, checksum_method: str = 'lrc', cmdtype: int = 1) -> bool:
        """
        发送命令

        参数:
            command: 命令名称，如 'OPENLOCK'
            params: 参数列表，默认为空
            checksum_method: 使用何种校验方法，默认为lrc
            cmdtype: 命令类型，默认为1,五轴电机板 2，加料电机板

        返回:
            bool: 发送是否成功
        """
        if not self.serial_conn or not self.serial_conn.is_open:
            print("串口未连接")
            return False

        try:
            with self.lock:
                cmd_str = self.build_command(command, params, checksum_method,cmdtype)
                self.serial_conn.write(cmd_str.encode('utf-8'))
                self.serial_conn.flush()
                return True
        except Exception as e:
            print(f"发送命令失败: {e}")
            return False
        
    def execute_command(self, command: str, params: List[str] = None, 
                       checksum_method: str = 'lrc', cmdtype: int = 1, timeout: float = None) -> Tuple[bool, List[str]]:
        """
        执行命令并接收响应

        参数:
            command: 命令名称，如 'OPENLOCK'
            params: 参数列表，默认为空
            checksum_method: 使用何种校验方法，默认为lrc
            cmdtype: 命令类型，默认为1,五轴电机板 2，加料电机板
            timeout: 接收响应的超时时间，单位秒

        返回:
            Tuple[bool, List[str]]: 
                - 命令是否执行成功
                - 响应参数列表（如果是错误响应，则包含错误信息）
        """
        # 发送命令
        if not self.send_command(command, params, checksum_method,cmdtype):
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
           print("\n3. 发送步进电机测试命令: RUN 1 0 2560000 360")
           comm.execute_command("RUN", ["1", "0","2560000","360"], checksum_method='lrc', cmdtype=1,timeout=2.0)

           print("\n4. 发送DC电机测试命令: YT+CHECKSUM")
           comm.execute_command("CHECKSUM", ["1", "0"], checksum_method='crc', cmdtype=2,timeout=2.0)

        finally:
            # 断开连接
            print("\n断开连接")
            comm.disconnect()
            print("   串口连接已断开")
    else: 
        print("   无法连接到串口")

    print("\n=== 测试完成 ===")    