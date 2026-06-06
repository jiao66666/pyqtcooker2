import serial
import threading
import queue
from typing import Optional, List, Tuple, Callable, Any
from lib.newstructure.constant import *
from lib.newstructure.protocols import ProtocolFactory


class RS485Communication:
    """RS485通信类（队列化 + 异步 + 同步兼容）"""

    def __init__(self, port: str, baudrate: int = 115200, timeout: float = 1.0, board_id: int = BOARDTYPE_FIVE_AXIS):
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.board_id = board_id

        self.serial_conn: Optional[serial.Serial] = None
        self.protocol = ProtocolFactory.create(board_id)
        self.connected = False

        # 核心：优先级队列
        self.queue = queue.PriorityQueue()
        self.counter = 0

        # worker线程
        self.worker_thread = threading.Thread(target=self._worker, daemon=True)
        self.running = False

    # =========================
    # 串口连接
    # =========================
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

            # 启动 worker
            self.running = True
            self.worker_thread.start()

            return True
        except Exception as e:
            print(f"连接串口失败: {e}")
            return False

    def disconnect(self):
        if self.serial_conn and self.serial_conn.is_open:
            self.running = False
            self.serial_conn.close()
            self.connected = False
            return True
        return False

    # =========================
    # 核心：Worker线程（唯一通信入口）
    # =========================
    def _worker(self):
        while self.running:
            try:
                priority, _, item = self.queue.get()

                command = item["command"]
                params = item["params"]
                callback = item["callback"]

                success, resp = self._execute_command_sync(command, params)

                if callback:
                    try:
                        callback(success, resp)
                    except Exception as e:
                        print(f"回调执行异常: {e}")

            except Exception as e:
                print(f"Worker异常: {e}")

    # =========================
    # 真正的同步IO（只允许内部调用）
    # =========================
    def _execute_command_sync(self, command: str, params: List[str] = None) -> Tuple[bool, List[str]]:

        if params is None:
            params = []

        if not self.serial_conn or not self.serial_conn.is_open:
            print("串口未连接")
            return False, ["串口未连接"]

        try:
            cmd_str = self.protocol.build_command(command, params)

            print("发送指令中....")
            self.serial_conn.write(cmd_str.encode('utf-8'))
            self.serial_conn.flush()

            print("主板返回消息>>>>>>")
            res = self.serial_conn.readline().decode('utf-8').strip()
            print(res)

            print("解析消息>>>>>>>")
            success, resp_cmd, resp_result = self.protocol.parse_response(command, res)

            if not success:
                return False, resp_result

            if resp_cmd != command:
                return False, [f"响应类型不匹配，期望: {command}，实际: {resp_cmd}"]

            return True, resp_result

        except Exception as e:
            print(f"发送命令失败: {e}")
            return False, [str(e)]

    # =========================
    # 异步接口（推荐使用）
    # =========================
    def execute_command_async(
        self,
        command: str,
        params: List[str] = None,
        callback: Optional[Callable[[bool, List[str]], Any]] = None,
        priority: int = PRIORITY_NORMAL
    ):
        if params is None:
            params = []

        item = {
            "command": command,
            "params": params,
            "callback": callback
        }

        self.counter += 1
        self.queue.put((priority,self.counter, item))
        return True

    # =========================
    # 同步接口（兼容旧代码）    # WARNING: blocking API - DO NOT USE IN tick loop
    # =========================
    def execute_command(self, command: str, params: List[str] = None) -> Tuple[bool, List[str]]:

        event = threading.Event()
        result = {}

        def cb(success, resp):
            result["data"] = (success, resp)
            event.set()

        self.execute_command_async(command, params, callback=cb)

        event.wait()  # 阻塞等待结果

        return result["data"]

