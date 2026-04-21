from abc import ABC, abstractmethod
from typing import List,Tuple,Type
from lib.boardtype import BOARDTYPE_FEEDER,BOARDTYPE_FIVE_AXIS
from lib.newstructure.tools import CRCUtil

class ProtocolBase(ABC):
    @abstractmethod
    def build_command(self, command: str, params: List[str]) -> str:
        pass
    def parse_response(self, response: str) -> Tuple[bool, str, List[str]]:
        pass

class FiveAxisProtocol(ProtocolBase):
    def build_command(self, command: str, params: List[str] = None) -> str:
        cmd_str = f"#{command}"
        if params:
            cmd_str += f",{','.join(params)}"

            # 计算LRC校验码，这里要计算从 # 到 * 之间的字符的累加和
        lrc = CRCUtil.lrc(cmd_str + "*")  # 包含 * 进行校验
        cmd_str += f"*{lrc}"
        print(f"将构建命令串(带上LRC): {cmd_str}")
        return cmd_str
    def parse_response(self, response: str) -> Tuple[bool, str, List[str]]:
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
                


class FeederProtocol(ProtocolBase):
    def build_command(self, command: str, params: List[str] = None) -> str:
        cmd_str = f"YT+{command}="
        if params:
            cmd_str += ",".join(params)

        crc = CRCUtil.crc16(cmd_str)
        cmd_str += f"*{crc}"
        print(f"将构建命令串(带上CRC):{cmd_str}")    
        return cmd_str
    
    def parse_response(self, response: str) -> Tuple[bool, str, List[str]]:
             # 检查是否是正确响应
        if response.startswith("+") and ":" in response:
            # 分割指令名和参数部分
            cmd_with_params = response[1:].split(":", 1)
            cmd = cmd_with_params[0]  # 指令名
            params_with_crc = cmd_with_params[1]  # 参数和可能的 CRC

            # 如果有 CRC16 校验值，则分离出来
            if "*" in params_with_crc:
                params_part, crc = params_with_crc.split("*", 1)
                params = params_part.split(",")  # 分割参数
            else:
                params = params_with_crc.split(",")  # 没有 CRC 时直接分割参数

            return True, cmd, params
        # 检查是否是错误响应
        if response.startswith("+ERROR") and ":" in response:
            # 分割错误响应部分
            error_with_params = response[7:].split(":", 1)
            error_code = error_with_params[0]  # 错误码
            error_message = error_with_params[1]  # 错误信息
            return False, "ERROR", [error_code, error_message]        

        return False, "INVALID", []


class ProtocolFactory:
    _registry = {}

    @classmethod
    def register(cls, board_type: int, protocol_cls: Type):
        """
        注册协议类
        """
        cls._registry[board_type] = protocol_cls

    @classmethod
    def create(cls, board_type: int):
        """
        创建协议实例
        """
        protocol_cls = cls._registry.get(board_type)

        if not protocol_cls:
            raise ValueError(f"未知的协议类型: {board_type}")

        return protocol_cls()
    
ProtocolFactory.register(BOARDTYPE_FEEDER, FeederProtocol)
ProtocolFactory.register(BOARDTYPE_FIVE_AXIS, FiveAxisProtocol)    