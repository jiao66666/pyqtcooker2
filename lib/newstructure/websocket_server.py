import asyncio
import websockets
import json
import threading


class WebSocketServer:

    def __init__(self, system=None):

        # =================================================
        # system reference
        # =================================================

        # 不在这里 import system
        # 而是由外部传入 system
        self.system = system


        # =================================================
        # lifecycle state
        # =================================================

        self.state = "INIT"


        # =================================================
        # runtime
        # =================================================

        self.server = None
        self.clients = set()

        self.loop = None
        self.thread = None


        # =================================================
        # internal sync
        # =================================================

        self._lock = threading.Lock()


    # =====================================================
    # System
    # =====================================================

    def set_system(self, system):
        """
        设置 system 引用。

        如果 WebSocket 创建的时候 system 还没有准备好，
        可以后续通过这个方法设置。
        """

        self.system = system


    def _get_system_state(self):
        """
        获取当前系统状态。

        注意：
        这里不自己保存 started / start_time，
        永远从真正的 system 中读取。
        """

        # system 尚未设置
        if self.system is None:

            return {
                "type": "system_state",
                "started": False,
                "start_time": None,
                "mode": "READY",
                "dirty": False
            }


        state = self.system["state"]


        return {
            "type": "system_state",

            "started": state.get(
                "started",
                False
            ),

            "start_time": state.get(
                "start_time",
                None
            ),

            "mode": state.get(
                "mode",
                "READY"
            ),

            "dirty": state.get(
                "dirty",
                False
            )
        }


    # =====================================================
    # FSM helpers
    # =====================================================

    def is_running(self):

        return self.state == "RUNNING"


    def is_ready(self):

        return self.state == "RUNNING"


    # =====================================================
    # System State - send to one client
    # =====================================================

    async def _send_system_state_to_client(
        self,
        websocket
    ):
        """
        新客户端连接时，
        只给这个客户端发送一次当前系统状态。
        """

        data = [
            self._get_system_state()
        ]


        try:

            await websocket.send(
                json.dumps(data)
            )

            print(
                "[WS] send system state:",
                data
            )


        except Exception as e:

            print(
                f"[WS] send system state failed: {e}"
            )

            self.clients.discard(
                websocket
            )


    # =====================================================
    # System State - broadcast
    # =====================================================

    def send_system_state(self):
        """
        广播当前系统状态给所有已经连接的客户端。

        Flask / system 等同步代码可以直接调用：

            get_websocket().send_system_state()
        """

        if not self.loop:
            return


        data = [
            self._get_system_state()
        ]


        asyncio.run_coroutine_threadsafe(
            self._broadcast_system_state(data),
            self.loop
        )


    async def _broadcast_system_state(
        self,
        data
    ):
        """
        真正执行系统状态广播。
        """

        if not self.clients:
            return


        msg = json.dumps(data)


        for client in list(self.clients):

            try:

                await client.send(msg)


            except Exception as e:

                print(
                    f"[WS] broadcast system state failed: {e}"
                )

                self.clients.discard(
                    client
                )


    # =====================================================
    # WebSocket lifecycle
    # =====================================================

    async def register(
        self,
        websocket
    ):

        self.clients.add(
            websocket
        )


        print(
            f"[WS] client connected, "
            f"clients={len(self.clients)}"
        )


        # =================================================
        # ★ 新客户端连接以后
        # ★ 立即发送当前 system 状态
        # =================================================

        await self._send_system_state_to_client(
            websocket
        )


    async def unregister(
        self,
        websocket
    ):

        self.clients.discard(
            websocket
        )


        print(
            f"[WS] client disconnected, "
            f"clients={len(self.clients)}"
        )


    async def handler(
        self,
        websocket,
        path
    ):

        await self.register(
            websocket
        )


        try:

            await websocket.wait_closed()


        finally:

            await self.unregister(
                websocket
            )


    # =====================================================
    # async core
    # =====================================================

    async def _start_async(
        self,
        host,
        port
    ):

        self.state = "STARTING"


        self.loop = (
            asyncio.get_running_loop()
        )


        self.server = await websockets.serve(
            self.handler,
            host,
            port
        )


        self.state = "RUNNING"


        print(
            f"[WS] running at ws://{host}:{port}"
        )


        await self.server.wait_closed()


    # =====================================================
    # public start
    # =====================================================

    def start(
        self,
        host="0.0.0.0",
        port=8765
    ):

        if self.state in (
            "STARTING",
            "RUNNING"
        ):
            return


        def _run():

            loop = asyncio.new_event_loop()

            asyncio.set_event_loop(
                loop
            )


            self.loop = loop


            loop.run_until_complete(
                self._start_async(
                    host,
                    port
                )
            )


        self.thread = threading.Thread(
            target=_run,
            daemon=True
        )


        self.thread.start()


    # =====================================================
    # shutdown
    # =====================================================

    async def _stop_async(self):

        self.state = "STOPPING"


        if self.server:

            self.server.close()

            await self.server.wait_closed()


        for client in list(
            self.clients
        ):

            try:

                await client.close()

            except Exception:

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


    # =====================================================
    # general send API
    # =====================================================

    async def _send_async(
        self,
        data
    ):

        if not self.clients:
            return


        msg = json.dumps(
            data
        )


        for client in list(
            self.clients
        ):

            try:

                await client.send(
                    msg
                )

            except Exception:

                self.clients.discard(
                    client
                )


    def send(
        self,
        data
    ):

        if not self.loop:
            return


        asyncio.run_coroutine_threadsafe(
            self._send_async(data),
            self.loop
        )


# =========================================================
# Global WebSocket instance
# =========================================================

_websocket = None

_websocket_lock = threading.Lock()


def get_websocket(system=None):

    global _websocket


    if _websocket is None:

        with _websocket_lock:

            if _websocket is None:

                _websocket = WebSocketServer(
                    system
                )


    # 如果之前创建的时候没有 system，
    # 后续调用可以补进去
    elif system is not None:

        _websocket.set_system(
            system
        )


    return _websocket