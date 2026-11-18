
import threading
import queue
import time
import numpy as np

from drivers.thermal.mrpc_client import MRpcClient, SerialTransport


class ThermalSensor:

    def __init__(self, port, on_data=None):
        self.port = port
        self.on_data = on_data

        self.rpc = MRpcClient()
        self.serial_tx = SerialTransport(self.rpc)

        self.frame_queue = queue.Queue(maxsize=1)
        self.running = False
        self.worker = None

        self.last_time = None
        self.fps = 0.0

        # 注册热成像数据回调
        self.rpc.add_stream_listener(self._on_stream)

    def start(self, username="admin", password=""):

        # 连接串口
        self.serial_tx.connect(self.port, baudrate=921600)

        # 启动数据处理线程
        self.running = True
        self.worker = threading.Thread(
            target=self._process_loop,
            daemon=True
        )
        self.worker.start()

        try:
            # 登录设备
            result = self.rpc.login(
                username,
                password,
                channel="serial"
            )
            print("传感器登录成功:", result)

            # 订阅热成像数据
            self.rpc.subscribe_thermal_stream()
            print("已订阅 Sensor.update")

        except Exception:
            self.stop()
            raise

    def _on_stream(self, topic, meta, raw_bytes):

        if topic != "Sensor.update" or not raw_bytes:
            return

        w = int(meta.get("width", 32))
        h = int(meta.get("height", 24))

        # 只保留最新一帧，避免数据积压
        if self.frame_queue.full():
            try:
                self.frame_queue.get_nowait()
            except queue.Empty:
                pass

        self.frame_queue.put((w, h, raw_bytes))

    def _process_loop(self):

        while self.running:

            try:
                w, h, raw_bytes = self.frame_queue.get(timeout=0.5)

                expected = w * h * 2

                if len(raw_bytes) < expected:
                    continue

                # 解析原始温度数据
                raw16 = np.frombuffer(
                    raw_bytes[:expected],
                    dtype="<u2"
                ).reshape((h, w))

                # 转换成摄氏度
                temps = (
                    raw16.astype(np.float32) - 2732.0
                ) * 0.1

                # 统计温度
                t_max = float(temps.max())
                t_min = float(temps.min())
                t_avg = float(temps.mean())

                # 中心位置温度
                t_fix = float(
                    temps[h // 2, w // 2]
                )

                # 计算 FPS
                now = time.perf_counter()

                if self.last_time is not None:
                    dt = now - self.last_time

                    if dt > 0:
                        current_fps = 1.0 / dt
                        self.fps = (
                            self.fps * 0.85 +
                            current_fps * 0.15
                        )

                self.last_time = now

                result = {
                    "max": round(t_max, 1),
                    "min": round(t_min, 1),
                    "avg": round(t_avg, 1),
                    "fix": round(t_fix, 1),
                    "fps": round(self.fps, 1),
                    "width": w,
                    "height": h,
                }

                if self.on_data:
                    self.on_data(result)

            except queue.Empty:
                continue

            except Exception as e:
                print("温度数据处理异常:", e)

    def stop(self):

        self.running = False

        self.rpc.unsubscribe_thermal_stream()
        self.serial_tx.disconnect()

        if self.worker and self.worker.is_alive():
            self.worker.join(timeout=2)

        print("温度传感器已停止")
