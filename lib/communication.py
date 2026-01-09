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

    # 以下是针对具体命令的便捷方法

    # 检查连接命令
    def check_ping(self, board_id: int, use_crc: bool = True, timeout: float = None) -> Tuple[bool, str]:
        """
        开锁命令

        参数:
            board_id: 板子ID
            use_crc: 是否使用CRC校验
            timeout: 接收响应的超时时间

        返回:
            Tuple[bool, str]: 
                - 命令是否执行成功
                - 响应信息或错误信息
        """
        success, params = self.execute_command("PING", board_id, [], use_crc, timeout)
        if success:
            return True, f"锁控板连接成功"
        else:
            return False, f"锁控板连接失败: {params[0] if params else '未知错误'}"


    # 检查连接命令
    def restart_board(self, board_id: int, use_crc: bool = True, timeout: float = None) -> Tuple[bool, str]:
        """
        开锁命令

        参数:
            board_id: 板子ID
            use_crc: 是否使用CRC校验
            timeout: 接收响应的超时时间

        返回:
            Tuple[bool, str]: 
                - 命令是否执行成功
                - 响应信息或错误信息
        """
        success, params = self.execute_command("REBOOT", board_id, [], use_crc, timeout)
        if success:
            if params[0] != board_id:
                return False, f"锁控板重启失败: 返回板子ID错误"
            else:
                result = params[1]
                if result == 1:
                    return True, f"锁控板重启成功"
                else:
                    return False, f"锁控板重启失败: {params[0] if params else '未知错误'}"
        else:
            return False, f"锁控板重启命令执行失败: {params[0] if params else '未知错误'}"
        

    # 启动通道命令
    def run_channel(self, board_id: int, channel_id: int, params: List[str] = None, use_crc: bool = True, timeout: float = None) -> Tuple[bool, str]:
        """
        开锁命令

        参数:
            board_id: 板子ID
            channel_id: 锁ID
            use_crc: 是否使用CRC校验
            timeout: 接收响应的超时时间

        返回:
            Tuple[bool, str]: 
                - 命令是否执行成功
                - 响应信息或错误信息
        """

        cmd_str =  str(channel_id)
        if params:
            cmd_str += f",{','.join(params)}"

        success, params = self.execute_command("OPENLOCK", board_id, [cmd_str], use_crc, timeout)
        if success:
            return True, f"通道{channel_id}开启成功"
        else:
            return False, f"通道开启失败: {params[0] if params else '未知错误'}"




    def open_lock(self, board_id: int, lock_id: int, use_crc: bool = True, timeout: float = None) -> Tuple[bool, str]:
        """
        开锁命令

        参数:
            board_id: 板子ID
            lock_id: 锁ID
            use_crc: 是否使用CRC校验
            timeout: 接收响应的超时时间

        返回:
            Tuple[bool, str]: 
                - 命令是否执行成功
                - 响应信息或错误信息
        """
        success, params = self.execute_command("OPENLOCK", board_id, [str(lock_id)], use_crc, timeout)
        if success:
            return True, f"锁{lock_id}开启成功"
        else:
            return False, f"开锁失败: {params[0] if params else '未知错误'}"

    def close_lock(self, board_id: int, lock_id: int, use_crc: bool = True, timeout: float = None) -> Tuple[bool, str]:
        """
        关锁命令

        参数:
            board_id: 板子ID
            lock_id: 锁ID
            use_crc: 是否使用CRC校验
            timeout: 接收响应的超时时间

        返回:
            Tuple[bool, str]: 
                - 命令是否执行成功
                - 响应信息或错误信息
        """
        success, params = self.execute_command("CLOSELOCK", board_id, [str(lock_id)], use_crc, timeout)
        if success:
            return True, f"锁{lock_id}关闭成功"
        else:
            return False, f"关锁失败: {params[0] if params else '未知错误'}"

    def get_lock_status(self, board_id: int, lock_id: int, use_crc: bool = True, timeout: float = None) -> Tuple[bool, Union[str, int]]:
        """
        获取锁状态命令

        参数:
            board_id: 板子ID
            lock_id: 锁ID
            use_crc: 是否使用CRC校验
            timeout: 接收响应的超时时间

        返回:
            Tuple[bool, Union[str, int]]: 
                - 命令是否执行成功
                - 锁状态（0=关闭，1=开启）或错误信息字符串
        """
        success, params = self.execute_command("GETLOCKSTATUS", board_id, [str(lock_id)], use_crc, timeout)
        if success and len(params) >= 2:
            try:
                status = int(params[1])
                return True, status
            except ValueError:
                return False, f"无效的状态值: {params[1]}"
        else:
            return False, f"获取锁状态失败: {params[0] if params else '未知错误'}"

    def get_all_locks_status(self, board_id: int, use_crc: bool = True, timeout: float = None) -> Tuple[bool, Union[List[int], str]]:
        """
        获取所有锁状态命令

        参数:
            board_id: 板子ID
            use_crc: 是否使用CRC校验
            timeout: 接收响应的超时时间

        返回:
            Tuple[bool, Union[List[int], str]]: 
                - 命令是否执行成功
                - 所有锁状态列表（每个元素为0或1）或错误信息字符串
        """
        success, params = self.execute_command("GETALLLOCKSSTATUS", board_id, [], use_crc, timeout)
        if success and len(params) >= 2:
            try:
                # 第一个参数是board_id，后面是各个锁的状态
                status_list = [int(status) for status in params[1:]]
                return True, status_list
            except ValueError:
                return False, f"无效的状态值: {params[1:]}"
        else:
            return False, f"获取所有锁状态失败: {params[0] if params else '未知错误'}"


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
            print("\n3. 测试CRC计算")
            test_data = "YT+OPENLOCK=1,1"
            crc = comm.calculate_crc16(test_data)
            print(f"   数据: {test_data}")
            print(f"   CRC16: {crc}")

            test_data2 = "YT+PING=1"
            crc2 = comm.calculate_crc16(test_data2)
            print(f"   数据: {test_data2}")
            print(f"   CRC16: {crc2}")

            test_data3 = "+PING:1"
            crc3 = comm.calculate_crc16(test_data3)
            print(f"   数据: {test_data3}")
            print(f"   CRC16: {crc3}")

            test_data4 = comm.build_command("PING", 1, [], use_crc=True)
            print(f"构建PING命令输出结果:{test_data4}")

            test_data5 = comm.build_command("PING", 1, ["1","500","1","1","200"], use_crc=True)
            print(f"构建PING命令输出结果:{test_data5}")



            print("-------测试接口命令开始-------")
            print("测试板子连通性命令>>>>>>>>")
            comm.check_ping(board_id=1, use_crc=True, timeout=0.3)

            print("测试板子重启命令>>>>>>>>>")
            comm.restart_board(board_id=1, use_crc=True, timeout=0.3)

            print("测试板子通道启动命令>>>>>>>>>")
            comm.run_channel(board_id=1, channel_id=1, params=["500"], use_crc=True, timeout=0.3)


            # 测试命令构建
            print("\n4. 测试命令构建")
            cmd_with_crc = comm.build_command("OPENLOCK", 1, ["1"], use_crc=True)
            cmd_without_crc = comm.build_command("OPENLOCK", 1, ["1"], use_crc=False)
            print(f"   带CRC的命令: {repr(cmd_with_crc)}")
            print(f"   不带CRC的命令: {repr(cmd_without_crc)}")

            # 测试发送和接收原始命令
            print("\n5. 测试发送和接收原始命令")
            success = comm.send_command("OPENLOCK", 1, ["1"])
            print(f"   发送命令结果: {success}")
            if success:
                response = comm.receive_response(timeout=2.0)
                print(f"   接收到的响应: {response}")
                if response:
                    success, resp_type, params = comm.parse_response(response)
                    print(f"   解析结果 - 成功: {success}, 类型: {resp_type}, 参数: {params}")

            # 测试开锁命令
            print("\n6. 测试开锁命令")
            success, message = comm.open_lock(board_id=1, lock_id=1)
            print(f"   开锁结果: {success}, 消息: {message}")

            # 测试关锁命令
            print("\n7. 测试关锁命令")
            success, message = comm.close_lock(board_id=1, lock_id=1)
            print(f"   关锁结果: {success}, 消息: {message}")

            # 测试获取锁状态
            print("\n8. 测试获取锁状态")
            success, result = comm.get_lock_status(board_id=1, lock_id=1)
            if success:
                print(f"   锁状态: {result} (0=关闭, 1=开启)")
            else:
                print(f"   获取锁状态失败: {result}")

            # 测试获取所有锁状态
            print("\n9. 测试获取所有锁状态")
            success, result = comm.get_all_locks_status(board_id=1)
            if success:
                print(f"   所有锁状态: {result}")
                for i, status in enumerate(result, 1):
                    print(f"     锁{i}: {status} (0=关闭, 1=开启)")
            else:
                print(f"   获取所有锁状态失败: {result}")

            # 测试执行通用命令
            print("\n10. 测试执行通用命令")
            success, params = comm.execute_command("GETVERSION", 1)
            if success:
                print(f"   版本信息: {params}")
            else:
                print(f"   获取版本信息失败: {params[0] if params else '未知错误'}")

        finally:
            # 断开连接
            print("\n11. 断开连接")
            comm.disconnect()
            print("   串口连接已断开")
    else:
        print("   无法连接到串口")

    print("\n=== 测试完成 ===")
