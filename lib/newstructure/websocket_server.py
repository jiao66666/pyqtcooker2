import asyncio
import websockets
import json
import threading


class WebSocketServer:

    def __init__(self):
        # ===== lifecycle state =====
        self.state = "INIT"

        # ===== runtime =====
        self.server = None
        self.clients = set()

        self.loop = None
        self.thread = None

        # internal sync
        self._lock = threading.Lock()

    # =========================
    # FSM helpers
    # =========================

    def is_running(self):
        return self.state == "RUNNING"

    def is_ready(self):
        return self.state == "RUNNING"

    # =========================
    # WebSocket lifecycle
    # =========================

    async def register(self, websocket):
        self.clients.add(websocket)

    async def unregister(self, websocket):
        self.clients.discard(websocket)

    async def handler(self, websocket, path):
        await self.register(websocket)
        try:
            await websocket.wait_closed()
        finally:
            await self.unregister(websocket)

    # =========================
    # async core
    # =========================

    async def _start_async(self, host, port):
        self.state = "STARTING"

        self.loop = asyncio.get_running_loop()

        self.server = await websockets.serve(self.handler, host, port)

        self.state = "RUNNING"
        print(f"[WS] running at ws://{host}:{port}")

        await self.server.wait_closed()

    # =========================
    # public start
    # =========================

    def start(self, host="0.0.0.0", port=8765):
        if self.state in ("STARTING", "RUNNING"):
            return

        def _run():
            asyncio.set_event_loop(asyncio.new_event_loop())
            loop = asyncio.get_event_loop()
            loop.run_until_complete(self._start_async(host, port))

        self.thread = threading.Thread(target=_run, daemon=True)
        self.thread.start()

    # =========================
    # shutdown (重要补充)
    # =========================

    async def _stop_async(self):
        self.state = "STOPPING"

        if self.server:
            self.server.close()
            await self.server.wait_closed()

        for c in list(self.clients):
            try:
                await c.close()
            except:
                pass

        self.clients.clear()

        self.state = "STOPPED"

    def stop(self):
        if not self.loop:
            return

        asyncio.run_coroutine_threadsafe(
            self._stop_async(),
            self.loop
        )

    # =========================
    # send API
    # =========================

    async def _send_async(self, data):
        if not self.clients:
            return

        msg = json.dumps(data)

        for c in list(self.clients):
            try:
                await c.send(msg)
            except:
                self.clients.discard(c)

    def send(self, data):
        if not self.loop:
            return

        asyncio.run_coroutine_threadsafe(
            self._send_async(data),
            self.loop
        )