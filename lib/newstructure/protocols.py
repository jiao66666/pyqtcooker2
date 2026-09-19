from abc import ABC, abstractmethod
from typing import List,Tuple,Type
from lib.newstructure.constant import BOARDTYPE_FEEDER,BOARDTYPE_FIVE_AXIS,BOARDTYPE_SPIN
from lib.newstructure.tools import CRCUtil
from lib.newstructure.tools import parse_motor_pulses,parse_motor_status,parse_all_motor_pulses,parse_all_motor_status


class ProtocolBase(ABC):
    @abstractmethod
    def build_command(self, command: str, params: List[str]) -> str:
        pass
    def parse_response(self, command:str,response: str) -> Tuple[bool, str, List[str]]:
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
    def parse_response(self, command:str, response: str) -> Tuple[bool, str, List[str]]:
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
    def build_command(self, command: str, params: List[str] = None) -> str:
        cmd_str = f"YT+{command}="
        if params:
            cmd_str += ",".join(params)

        crc = CRCUtil.crc16(cmd_str)
        cmd_str += f"*{crc}"

        # YT_LOCKER24 协议要求以 CRLF 结尾
        cmd_str += "\r\n"
        print(f"将构建命令串(带CRC和结束符): {repr(cmd_str)}")
        return cmd_str
    
    def parse_response(
            self,
            command: str,
            response: str
        ) -> Tuple[bool, str, List[str]]:

        # 去除串口返回数据末尾的 CRLF / 空白字符
        response = response.strip()

        # ==================================================
        # 正常响应
        #
        # 例如：
        #
        # +GETFB:1,111111111111111111111111
        #
        # 解析结果：
        #
        # success = True
        # cmd     = GETFB
        # params  = ["1", "111111111111111111111111"]
        # ==================================================
        if response.startswith("+") and ":" in response:

            cmd, params_with_crc = response[1:].split(":", 1)

            # 去除可能存在的 CRC
            if "*" in params_with_crc:
                params_part, crc = params_with_crc.split("*", 1)
            else:
                params_part = params_with_crc

            params = [
                param.strip()
                for param in params_part.split(",")
            ]

            return True, cmd, params

        # ==================================================
        # 错误响应
        #
        # 例如：
        #
        # +ERRORxxx:xxxx
        # ==================================================
        if response.startswith("+ERROR") and ":" in response:

            error_with_params = response[7:].split(":", 1)

            error_code = error_with_params[0].strip()
            error_message = error_with_params[1].strip()

            return False, "ERROR", [
                error_code,
                error_message
            ]

        # ==================================================
        # 无法识别的响应
        # ==================================================

        return False, "INVALID", []

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
ProtocolFactory.register(BOARDTYPE_FIVE_AXIS, FiveAxisProtocol)    
ProtocolFactory.register(BOARDTYPE_SPIN, SpinerProtocol)    