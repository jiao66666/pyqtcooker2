from abc import ABC, abstractmethod
from typing import List,Tuple,Type, Union
from lib.newstructure.constant import *
from lib.newstructure.tools import CRCUtil
from lib.newstructure.tools import parse_motor_pulses,parse_motor_status,parse_all_motor_pulses,parse_all_motor_status


class ProtocolBase(ABC):
    @abstractmethod
    def build_command(self, command: str, params: List[str]) -> str:
        pass
    def parse_response(self, command:str,response: str) -> Tuple[bool, str, List[str]]:
        pass

class StepProtocol(ProtocolBase):
    def build_command(self, command: str, params: List[str] = None) -> str:
        cmd_str = f"#{command}"
        if params:
            cmd_str += f",{','.join(params)}"

            # 计算LRC校验码，这里要计算从 # 到 * 之间的字符的累加和
        lrc = CRCUtil.lrc(cmd_str + "*")  # 包含 * 进行校验
        cmd_str += f"*{lrc}"
        print(f"将构建命令串(带上LRC): {cmd_str}")
        return cmd_str
    def parse_response(self, command:str, response: str) -> Tuple[bool, str, List[str]]:
        status = None
        if command == "RunStatus":
            status = parse_motor_status(response)
            if status is None:
                print("电机状态解析失败")
                return False, "ERROR",["单电机状态解析失败","Fail"]
        elif command == "Pulse":   
            status = parse_motor_pulses(response)
            if status is None:
                print("电机脉冲数解析失败")
                return False,"ERROR", ["单电机状态解析失败","Fail"] 
        elif command == "ALLPulse":
            status = parse_all_motor_pulses(response)
            if status is None:
                print("电机脉冲数解析失败")
                return False,"ERROR", ["所有电机状态解析失败","Fail"] 
        elif command == "ALLRunStatus":
            status = parse_all_motor_status(response)
            if status is None:
                print("电机脉冲数解析失败")
                return False,"ERROR", ["所有电机状态解析失败","Fail"]     

        else:
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
        return True, command, [status]                


class FeederProtocol(ProtocolBase):
    """
    新版 WKLY 二进制锁控协议。

    帧格式：
    WKLY + 帧长度 + 板地址 + 指令字 + 数据域 + XOR

    注意：build_command 返回 bytes，不再返回 ASCII 字符串。
    """
    binary_mode = True

    HEADER = bytes([0x57, 0x4B, 0x4C, 0x59])

    CMD_OPENLOCK = 0x82
    CMD_GETFB = 0x83
    CMD_GETALLFB = 0x84
    CMD_DOOR_CHANGED = 0x85
    CMD_OPEN_ALL = 0x86
    CMD_OPEN_MULTIPLE = 0x87
    CMD_OUTPUT_ON = 0x88
    CMD_OUTPUT_OFF = 0x89
    CMD_OPEN_SIMULTANEOUS = 0x93
    CMD_OPENLOCK_TIME = 0x94
    CMD_MULTI_OUTPUT = 0x95
    CMD_DOOR_UPLOAD_ENABLE = 0x55

    COMMAND_MAP = {
        "OPENLOCK": CMD_OPENLOCK,
        "GETFB": CMD_GETFB,
        "GETALLFB": CMD_GETALLFB,
        "OPEN_ALL": CMD_OPEN_ALL,
        "OPEN_MULTIPLE": CMD_OPEN_MULTIPLE,
        "OUTPUT_ON": CMD_OUTPUT_ON,
        "OUTPUT_OFF": CMD_OUTPUT_OFF,
        "OPEN_SIMULTANEOUS": CMD_OPEN_SIMULTANEOUS,
        "OPENLOCK_TIME": CMD_OPENLOCK_TIME,
        "MULTI_OUTPUT": CMD_MULTI_OUTPUT,
        "DOOR_UPLOAD_ENABLE": CMD_DOOR_UPLOAD_ENABLE,
    }

    @staticmethod
    def _to_int(value) -> int:
        """将十进制字符串、整数或 0x 开头的字符串转换为整数。"""
        if isinstance(value, int):
            return value
        return int(str(value), 0)

    @staticmethod
    def _xor(data: bytes) -> int:
        result = 0
        for value in data:
            result ^= value
        return result

    def build_command(
        self,
        command: str,
        params: List[str] = None
    ) -> bytes:
        """
        根据指令名称和参数生成完整二进制帧。

        params 约定：
        OPENLOCK:           [board_id, channel]
        GETFB:               [board_id, channel]
        GETALLFB:            [board_id]
        OPEN_ALL:            [board_id]
        OPEN_MULTIPLE:       [board_id, channel1, channel2, ...]
        OUTPUT_ON/OFF:       [board_id, channel]
        OPEN_SIMULTANEOUS:   [board_id, channel1, channel2, ...]
        OPENLOCK_TIME:       [board_id, milliseconds, channel1, ...]
        MULTI_OUTPUT:        [board_id, state, channel1, channel2, ...]
        DOOR_UPLOAD_ENABLE:  [board_id, 0或1]
        """

        params = params or []

        if command not in self.COMMAND_MAP:
            raise ValueError(f"不支持的锁控指令: {command}")

        cmd = self.COMMAND_MAP[command]

        if not params:
            raise ValueError(f"{command} 缺少板地址参数")

        board_id = self._to_int(params[0])

        if not 0 <= board_id <= 0xFF:
            raise ValueError("board_id 必须在 0～255 之间")

        args = [self._to_int(value) for value in params[1:]]

        # 根据指令组装数据域
        if cmd in (self.CMD_GETALLFB, self.CMD_OPEN_ALL):
            data = []

        elif cmd in (self.CMD_OPENLOCK, self.CMD_GETFB,
                     self.CMD_OUTPUT_ON, self.CMD_OUTPUT_OFF):
            if len(args) != 1:
                raise ValueError(f"{command} 需要一个通道号")
            data = args

        elif cmd in (self.CMD_OPEN_MULTIPLE,
                     self.CMD_OPEN_SIMULTANEOUS):
            if not args:
                raise ValueError(f"{command} 至少需要一个通道号")
            if len(args) > 255:
                raise ValueError("通道数量不能超过 255")
            data = [len(args)] + args

        elif cmd == self.CMD_OPENLOCK_TIME:
            if len(args) < 2:
                raise ValueError("OPENLOCK_TIME 需要持续时间和至少一个通道号")

            milliseconds = args[0]
            channels = args[1:]

            if not 1 <= milliseconds <= 65535:
                raise ValueError("开锁时间必须在 1～65535 毫秒之间")
            if len(channels) > 255:
                raise ValueError("通道数量不能超过 255")

            data = [
                (milliseconds >> 8) & 0xFF,
                milliseconds & 0xFF,
                len(channels),
                *channels
            ]

        elif cmd == self.CMD_MULTI_OUTPUT:
            if len(args) < 2:
                raise ValueError("MULTI_OUTPUT 需要状态和至少一个通道号")

            state = args[0]
            channels = args[1:]

            if state not in (0, 1):
                raise ValueError("输出状态只能是 0（关闭）或 1（启动）")
            if len(channels) > 255:
                raise ValueError("通道数量不能超过 255")

            data = [state, len(channels), *channels]

        elif cmd == self.CMD_DOOR_UPLOAD_ENABLE:
            if len(args) != 1 or args[0] not in (0, 1):
                raise ValueError("门状态上传使能参数必须为 0 或 1")
            data = args

        else:
            raise ValueError(f"{command} 尚未实现数据域组装")

        if any(not 0 <= value <= 0xFF for value in data):
            raise ValueError("数据域中的每个字节必须在 0～255 之间")

        # 长度包括起始符、长度、地址、指令、数据域和校验字节
        frame_length = 4 + 1 + 1 + 1 + len(data) + 1

        if not 8 <= frame_length <= 255:
            raise ValueError(f"帧长度超出协议范围: {frame_length}")

        frame = (
            self.HEADER
            + bytes([frame_length, board_id, cmd])
            + bytes(data)
        )

        checksum = self._xor(frame)
        frame += bytes([checksum])

        print(
            f"构建锁控命令: {command}, "
            f"数据帧: {frame.hex(' ').upper()}"
        )

        return frame

    def parse_response(
        self,
        command: str,
        response: Union[bytes, bytearray, str]
    ) -> Tuple[bool, str, List[str]]:
        """
        解析二进制响应。

        返回格式与旧协议一致：
        (success, command, params)

        params 中的字节转换成十进制字符串。
        """

        if isinstance(response, str):
            # 兼容以 latin-1 一对一映射保存原始字节的情况。
            # 如果上层已经用 UTF-8 等方式解码二进制数据，
            # 必须先修改上层，不能在这里恢复丢失的字节。
            response = response.encode("latin-1")

        response = bytes(response)

        if len(response) < 8:
            return False, "INVALID", []

        if not response.startswith(self.HEADER):
            return False, "INVALID", []

        frame_length = response[4]

        if frame_length != len(response):
            return False, "INVALID", []

        if self._xor(response[:-1]) != response[-1]:
            return False, "INVALID", []

        board_id = response[5]
        cmd = response[6]
        data = list(response[7:-1])

        # 主动上传的门状态变化，不是普通命令应答。
        if cmd == self.CMD_DOOR_CHANGED:
            if len(data) != 2:
                return False, "INVALID", []
            return True, "DOOR_CHANGED", [
                str(board_id),
                str(data[0]),  # 通道号
                str(data[1]),  # 锁状态
            ]

        command_names = {
            value: key for key, value in self.COMMAND_MAP.items()
        }
        response_command = command_names.get(cmd, f"0x{cmd:02X}")

        # 状态字节是所有普通命令应答的数据域第一个字节。
        if not data:
            return False, response_command, []

        status = data[0]

        if status != 0:
            return False, response_command, [str(status)]

        # 不同指令的应答数据域结构不同。
        if cmd in (self.CMD_OPENLOCK, self.CMD_GETFB):
            # 状态 + 通道号 + 锁状态
            if len(data) != 3:
                return False, "INVALID", []
            params = [str(data[1]), str(data[2])]

        elif cmd == self.CMD_GETALLFB:
            # 状态 + 锁数量 + 每个通道的状态
            if len(data) < 2:
                return False, "INVALID", []
            count = data[1]
            if len(data) != count + 2:
                return False, "INVALID", []
            params = [str(count)] + [str(v) for v in data[2:]]

        elif cmd in (self.CMD_OUTPUT_ON, self.CMD_OUTPUT_OFF):
            # 文档示例响应：状态 + 通道号
            if len(data) != 2:
                return False, "INVALID", []
            params = [str(data[1])]

        else:
            # 其他控制命令通常只返回状态字节。
            if len(data) != 1:
                return False, "INVALID", []
            params = []

        return True, response_command, params

class SpinerProtocol(ProtocolBase):
    
    def build_command(self, command: str, params: List[str] = None) -> str:
         cmd_str = f"#{command}"
         if params:
             cmd_str += f",{','.join(params)}"
 
             # 计算LRC校验码，这里要计算从 # 到 * 之间的字符的累加和
         lrc = CRCUtil.lrc(cmd_str + "*")  # 包含 * 进行校验
         cmd_str += f"*{lrc}"
         print(f"将构建命令串(带上LRC): {cmd_str}")
         return cmd_str
    def parse_response(self, command:str, response: str) -> Tuple[bool, str, List[str]]:
         if command == "RunStatus":
             status = parse_motor_status(response)
             if status is None:
                 print("电机状态解析失败")
                 return False, "ERROR",["单电机状态解析失败","Fail"]
             
             return True, command, [status]
         else:
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

class ProtocolFactory:
    _registry = {}

    @classmethod
    def register(cls, board_id: int, protocol_cls: Type):
        """
        注册协议类
        """
        cls._registry[board_id] = protocol_cls

    @classmethod
    def create(cls, board_id: int):
        """
        创建协议实例
        """
        protocol_cls = cls._registry.get(board_id)

        if not protocol_cls:
            raise ValueError(f"未知的协议类型: {board_id}")

        return protocol_cls()
    
ProtocolFactory.register(BOARDTYPE_FEEDER, FeederProtocol)
ProtocolFactory.register(BOARDTYPE_STEP, StepProtocol)    
ProtocolFactory.register(BOARDTYPE_SPIN, SpinerProtocol)    
ProtocolFactory.register(BOARDTYPE_ICE, StepProtocol)    