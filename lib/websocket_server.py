# websocket_server.py

import asyncio
import websockets
import json

class WebSocketServer:
    _instance = None
    server = None  # 用于存储服务器实例

    def __new__(cls):
        """确保 WebSocketServer 只有一个实例（单例模式）"""
        if not cls._instance:
            cls._instance = super().__new__(cls)
            cls._instance.clients = set()
        return cls._instance

    async def register(self, websocket):
        """注册一个新的客户端连接"""
        self.clients.add(websocket)

    async def unregister(self, websocket):
        """注销客户端连接"""
        self.clients.remove(websocket)

    async def send_coordinates(self, coordinates):
        """向所有连接的客户端发送坐标数据"""
        message = json.dumps(coordinates)
        for client in self.clients:
            await client.send(message)

    async def handler(self, websocket, path):
        """处理客户端连接"""
        await self.register(websocket)
        try:
            await websocket.wait_closed()
        finally:
            await self.unregister(websocket)

    async def start(self, host="localhost", port=8765):
        """启动 WebSocket 服务器"""
        if self.server is None:  # 只有在没有启动时才启动服务器
            self.server = await websockets.serve(self.handler, host, port)
            await self.server.wait_closed()
        else:
            print("WebSocket server is already running!")

    def stop(self):
        """停止 WebSocket 服务器"""
        if self.server:
            self.server.close()
            self.server = None
            print("WebSocket server stopped.")
