import websockets
import json

class WebSocketServer:
    _instance = None  # 存储唯一的实例

    def __new__(cls, *args, **kwargs):
        """确保 WebSocketServer 只有一个实例"""
        if cls._instance is None:
            cls._instance = super().__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self):
        # 如果已经有实例，则不再初始化
        if not hasattr(self, 'initialized'):  # 防止重复初始化
            self.server = None
            self.clients = set()  # 用于存储连接的客户端
            self.initialized = True

    async def register(self, websocket):
        """注册新的 WebSocket 客户端"""
        print("###################新的 WebSocket 客户端连接###################################")
        self.clients.add(websocket)
        print(f"当前客户数量: {len(self.clients)}")
        print(f"当前客户列表: {self.clients}")

    async def unregister(self, websocket):
        """注销 WebSocket 客户端"""
        print("*************************WebSocket 客户端断开连接*****************")
        self.clients.remove(websocket)

    async def send_coordinates(self, coordinates):
        """向所有客户端发送数据"""
        message = json.dumps(coordinates)
        for client in self.clients:
            await client.send(message)

    async def handler(self, websocket, path):
        """处理 WebSocket 客户端连接"""
        await self.register(websocket)
        try:
            await websocket.wait_closed()
        finally:
            await self.unregister(websocket)

    async def start(self, host="localhost", port=8765):
        """启动 WebSocket 服务器"""
        if self.server is None:
            self.server = await websockets.serve(self.handler, host, port)
            await self.server.wait_closed()
