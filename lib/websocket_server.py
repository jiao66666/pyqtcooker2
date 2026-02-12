import websockets
import json
# WebSocketServer 类中不再需要 async 方法，而是直接用同步方式启动
class WebSocketServer:
    def __init__(self):
        self.server = None
        self.clients = set()

    async def register(self, websocket):
        """注册新的 WebSocket 客户端"""
        self.clients.add(websocket)

    async def unregister(self, websocket):
        """注销 WebSocket 客户端"""
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
