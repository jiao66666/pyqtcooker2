import serial
import time
import crcmod
import threading
from typing import Optional, List, Tuple, Union
from lib.boardtype import BoardType



class RS485Communication:
    """RS485通信类，实现主板通信协议"""
    def __init__(self, port: str, baudrate: int = 115200, timeout: float = 1.0, boardtype: BoardType = BoardType.FIVE_AXIS):
        """
        初始化RS485通信

        参数:
            port: 串口名称，如 'COM1' 或 '/dev/ttyUSB0'
            baudrate: 波特率，默认为9600
            timeout: 读取超时时间，单位秒，默认为1.0
            boardtype: 主板类型，1表示五轴电机板，2表示加料电机板，默认为1
        """
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.boardtype = boardtype
        self.serial_conn: Optional[serial.Serial] = None
        self.lock = threading.Lock()
        self.crc16_func = crcmod.mkCrcFun(0x18005, rev=True, initCrc=0xFFFF, xorOut=0x0000)
        self.connected = False
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


    
    def build_command(self, command: str, params: List[str] = None) -> str:
        """
        构建命令字符串

        参数:
            command: 命令名称，如 'OPENLOCK'
            params: 参数列表，默认为空
        
        返回:
            str: 完整的命令字符串，包含<CR><LF>结尾
        """
        if params is None:
            params = []

        # 构建基本命令: #<指令名>,<板子ID>,<参数1>,<参数2>...
       
        if self.boardtype == BoardType.FIVE_AXIS:
           cmd_str = f"#{command}"
        elif self.boardtype == BoardType.FEEDER:
           cmd_str = f"YT+{command}="

        if params:
            if self.boardtype == BoardType.FIVE_AXIS:
              cmd_str += f",{','.join(params)}"
            elif self.boardtype == BoardType.FEEDER:
              cmd_str += f"{','.join(params)}"    
        
        # 打印命令字符串（调试用）
        print(f"将构建命令串(不带LRC): {cmd_str}")

        # 计算并添加校验码
        if self.boardtype == BoardType.FIVE_AXIS:
            # 计算LRC校验码，这里要计算从 # 到 * 之间的字符的累加和
            lrc = self.calculate_lrc(cmd_str + "*")  # 包含 * 进行校验
            cmd_str += f"*{lrc}"
            print(f"将构建命令串(带上LRC): {cmd_str}")
        elif self.boardtype == BoardType.FEEDER:
            # 添加CRC校验（如果需要）
            crc = self.calculate_crc16(cmd_str)
            cmd_str += f"*{crc}"
            print(f"将构建命令串(带上CRC):{cmd_str}")    
        # 添加<CR><LF>结尾，此板不需要
        #cmd_str += "\r\n" 
        
        return cmd_str
    
   
    def execute_command(self, command: str, params: List[str] = None, 
                       ) -> Tuple[bool, List[str]]:

        if params is None:
            params = []
        # 构建基本命令: #<指令名>,<板子ID>,<参数1>,<参数2>...

        if self.boardtype == BoardType.FIVE_AXIS:
           cmd_str = f"#{command}"
        elif self.boardtype == BoardType.FEEDER:
           cmd_str = f"YT+{command}="

        if params:
            if self.boardtype == BoardType.FIVE_AXIS:
              cmd_str += f",{','.join(params)}"
            elif self.boardtype == BoardType.FEEDER:
              cmd_str += f"{','.join(params)}"    
        
        # 打印命令字符串（调试用）
        print(f"将构建命令串(不带LRC): {cmd_str}")

        # 计算并添加校验码
        if self.boardtype == BoardType.FIVE_AXIS:
            # 计算LRC校验码，这里要计算从 # 到 * 之间的字符的累加和
            lrc = self.calculate_lrc(cmd_str + "*")  # 包含 * 进行校验
            cmd_str += f"*{lrc}"
            print(f"将构建命令串(带上LRC): {cmd_str}")
        elif self.boardtype == BoardType.FEEDER:
            # 添加CRC校验（如果需要）
            crc = self.calculate_crc16(cmd_str)
            cmd_str += f"*{crc}"
            print(f"将构建命令串(带上CRC):{cmd_str}")  


        if not self.serial_conn or not self.serial_conn.is_open:
                print("串口未连接")
                return False

        try:
            with self.lock:
                cmd_str = self.build_command(command, params)
                print("发送指令中....")
                self.serial_conn.write(cmd_str.encode('utf-8'))
                self.serial_conn.flush()
                print("主板返回消息>>>>>>")
                res = self.serial_conn.readline().decode('utf-8').strip()
                print(res)
                # 解析响应
                print("解析消息>>>>>>>")
                success, resp_type, resp_params = self.parse_response(res)

                print(f"Success: {success}")
                print(f"Response Type: {resp_type}")
                print(f"Response Parameters: {resp_params}")

                if not success:
                    if resp_type == "ERROR":
                        print(False, resp_params)  # 控制台输出 False 和 resp_params
                    else:
                        print(False, ["无效响应"])  # 控制台输出 False 和无效响应

                # 检查响应类型是否匹配命令
                if resp_type != command:
                    print(False, [f"响应类型不匹配，期望: {command}，实际: {resp_type}"])  # 控制台输出错误信息

                return True
        except Exception as e:
            print(f"发送命令失败: {e}")
            return False            


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
        # 检查是否是成功响应
        if response.endswith("OK"):
            # 提取命令和参数（去掉 # 和 *OK）
            content = response[1:-3]  # 去掉 # 和 *OK
            parts = content.split(',')  # 分割命令和参数
            cmd = parts[0]  # 命令部分
            params = parts[1:]  # 剩下的是参数
            return True, cmd, params

        # 检查是否是失败响应
        if response.endswith("NG"):
            # 提取命令和参数（去掉 # 和 *NG）
            content = response[1:-3]  # 去掉 # 和 *NG
            parts = content.split(',')  # 分割命令和参数
            cmd = parts[0]  # 命令部分
            params = parts[1:]  # 剩下的是参数
            return False, cmd, params

        # 如果不是 OK 或 NG，返回 INVALID
        return False, "INVALID", []







# 示例用法
if __name__ == "__main__":
    print("=== RS485通信类接口测试 ===")

    # 创建通信对象
    print("1. 创建通信对象")
    comm1 = RS485Communication(port="COM2", baudrate=115200, timeout=1.0, boardtype=BoardType.FIVE_AXIS)
   
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