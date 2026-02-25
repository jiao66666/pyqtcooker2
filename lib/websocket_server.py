import asyncio
import websockets
import json
import threading


class WebSocketServer:
    _instance = None  # 单例

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not hasattr(self, "initialized"):
            self.server = None
            self.clients = set()
            self.loop = None              # WebSocket 所在事件循环
            self.loop_thread = None       # WebSocket 所在线程
            self.initialized = True

    # ================= WebSocket 生命周期 =================

    async def register(self, websocket):
        print("################### 新的 WebSocket 客户端连接 ###################")
        self.clients.add(websocket)
        print(f"当前客户数量: {len(self.clients)}")

    async def unregister(self, websocket):
        print("**************** WebSocket 客户端断开连接 ****************")
        self.clients.discard(websocket)

    async def handler(self, websocket, path):
        await self.register(websocket)
        try:
            await websocket.wait_closed()
        finally:
            await self.unregister(websocket)

    # ================= 启动 WebSocket 服务器 =================

    async def _start_async(self, host="0.0.0.0", port=8765):
        self.loop = asyncio.get_running_loop()
        self.server = await websockets.serve(self.handler, host, port)
        print(f"WebSocket server started at ws://{host}:{port}")
        await self.server.wait_closed()

    def start_in_thread(self, host="0.0.0.0", port=8765):
        """
        在独立线程启动 WebSocket 事件循环
        """
        if self.loop_thread:
            return

        def _run():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(self._start_async(host, port))

        t = threading.Thread(target=_run, daemon=True)
        t.start()
        self.loop_thread = t

    # ================= 线程安全发送 =================

    async def _send_coordinates_async(self, coordinates):
        if not self.clients:
            return

        message = json.dumps(coordinates)
        for client in list(self.clients):
            try:
                await client.send(message)
            except Exception as e:
                print("WebSocket 发送异常:", e)
                self.clients.discard(client)

    def send_coordinates_threadsafe(self, coordinates):
        """
        给外部线程调用的安全发送接口
        """
        if not self.loop:
            return

        asyncio.run_coroutine_threadsafe(
            self._send_coordinates_async(coordinates),
            self.loop
        )