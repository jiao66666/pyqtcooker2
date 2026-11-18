#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""mrpc.dll Python ctypes 最小可用封装（串口 / WebSocket + 热像流）"""

import asyncio
import ctypes
import ipaddress
import json
import os
import socket
import threading
import time
from concurrent.futures import Future
from typing import Any, Callable, Dict, List, Optional
from urllib.parse import urlparse, urlunparse

import serial
import serial.tools.list_ports
import websockets

SEND_CB = ctypes.CFUNCTYPE(None, ctypes.c_char_p, ctypes.POINTER(ctypes.c_uint8), ctypes.c_int32)
RESP_CB = ctypes.CFUNCTYPE(None, ctypes.c_uint32, ctypes.c_int32, ctypes.c_char_p, ctypes.c_char_p)
STREAM_CB = ctypes.CFUNCTYPE(None, ctypes.c_char_p, ctypes.c_char_p, ctypes.POINTER(ctypes.c_uint8), ctypes.c_int32)


class MRpcClient:
    def __init__(self, dll_path: Optional[str] = None):
        if dll_path is None:
            dll_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "bin", "mrpc.dll")
        self.dll = ctypes.CDLL(dll_path)
        self._bind()

        self._lock = threading.RLock()
        self._pending: Dict[int, Future] = {}
        self._early_results: Dict[int, tuple] = {}
        self._send_handlers: Dict[str, Callable[[bytes], None]] = {}
        self._stream_listeners: List[Callable[[str, Dict[str, Any], bytes], None]] = []
        self.token = ""

        self._cb_send = SEND_CB(self._on_send)
        self._cb_resp = RESP_CB(self._on_resp)
        self._cb_stream = STREAM_CB(self._on_stream)

        self.dll.mrpc_init()
        self.dll.mrpc_set_send_cb(self._cb_send)
        self.dll.mrpc_set_response_cb(self._cb_resp)
        self.dll.mrpc_set_stream_cb(self._cb_stream)

    def _bind(self) -> None:
        d = self.dll
        d.mrpc_init.argtypes = []
        d.mrpc_register_port.argtypes = [ctypes.c_char_p, ctypes.c_int32]
        d.mrpc_unregister_port.argtypes = [ctypes.c_char_p]
        d.mrpc_set_send_cb.argtypes = [SEND_CB]
        d.mrpc_set_response_cb.argtypes = [RESP_CB]
        d.mrpc_set_stream_cb.argtypes = [STREAM_CB]
        d.mrpc_feed_bytes.argtypes = [ctypes.c_char_p, ctypes.POINTER(ctypes.c_uint8), ctypes.c_int32]
        d.mrpc_invoke.argtypes = [
            ctypes.c_char_p, ctypes.c_char_p, ctypes.c_char_p,
            ctypes.c_int32, ctypes.c_char_p, ctypes.c_char_p,
        ]
        d.mrpc_invoke.restype = ctypes.c_uint32
        d.mrpc_remove_hook.argtypes = [ctypes.c_uint32]
        d.mrpc_subscribe_topic.argtypes = [ctypes.c_char_p]
        d.mrpc_unsubscribe_topic.argtypes = [ctypes.c_char_p]

        d.mrpc_login.argtypes = [ctypes.c_char_p, ctypes.c_char_p, ctypes.c_int32, ctypes.c_char_p]
        d.mrpc_login.restype = ctypes.c_uint32
        d.mrpc_board_info.argtypes = [ctypes.c_char_p, ctypes.c_int32, ctypes.c_char_p]
        d.mrpc_board_info.restype = ctypes.c_uint32
        d.mrpc_get_chip_temp.argtypes = [ctypes.c_char_p, ctypes.c_int32, ctypes.c_char_p]
        d.mrpc_get_chip_temp.restype = ctypes.c_uint32
        d.mrpc_config_load.argtypes = [ctypes.c_char_p, ctypes.c_int32, ctypes.c_char_p]
        d.mrpc_config_load.restype = ctypes.c_uint32
        d.mrpc_config_save.argtypes = [ctypes.c_char_p, ctypes.c_int32, ctypes.c_char_p]
        d.mrpc_config_save.restype = ctypes.c_uint32
        d.mrpc_config_reset.argtypes = [ctypes.c_char_p, ctypes.c_int32, ctypes.c_char_p]
        d.mrpc_config_reset.restype = ctypes.c_uint32
        d.mrpc_config_set_str.argtypes = [ctypes.c_char_p, ctypes.c_char_p, ctypes.c_char_p, ctypes.c_int32, ctypes.c_char_p]
        d.mrpc_config_set_str.restype = ctypes.c_uint32
        d.mrpc_config_set_int.argtypes = [ctypes.c_char_p, ctypes.c_int64, ctypes.c_char_p, ctypes.c_int32, ctypes.c_char_p]
        d.mrpc_config_set_int.restype = ctypes.c_uint32
        d.mrpc_config_set_float.argtypes = [ctypes.c_char_p, ctypes.c_double, ctypes.c_char_p, ctypes.c_int32, ctypes.c_char_p]
        d.mrpc_config_set_float.restype = ctypes.c_uint32
        d.mrpc_config_set_bool.argtypes = [ctypes.c_char_p, ctypes.c_int32, ctypes.c_char_p, ctypes.c_int32, ctypes.c_char_p]
        d.mrpc_config_set_bool.restype = ctypes.c_uint32
        d.mrpc_sensor_auto_calibrate.argtypes = [ctypes.c_char_p, ctypes.c_int32, ctypes.c_char_p]
        d.mrpc_sensor_auto_calibrate.restype = ctypes.c_uint32
        d.mrpc_wireless_net_info.argtypes = [ctypes.c_char_p, ctypes.c_int32, ctypes.c_char_p]
        d.mrpc_wireless_net_info.restype = ctypes.c_uint32
        d.mrpc_wireless_control.argtypes = [ctypes.c_int32, ctypes.c_char_p, ctypes.c_int32, ctypes.c_char_p]
        d.mrpc_wireless_control.restype = ctypes.c_uint32
        d.mrpc_subscribe_thermal_stream.argtypes = []
        d.mrpc_unsubscribe_thermal_stream.argtypes = []

    def _on_send(self, ch: bytes, ptr, length: int) -> None:
        fn = self._send_handlers.get(ch.decode("utf-8", errors="ignore"))
        if fn:
            fn(ctypes.string_at(ptr, length))

    def _on_resp(self, seq: int, code: int, err: bytes, data: bytes) -> None:
        err_str = err.decode("utf-8", errors="ignore") if err else ""
        data_str = data.decode("utf-8", errors="ignore") if data else "null"
        with self._lock:
            fut = self._pending.pop(seq, None)
            if not fut:
                self._early_results[seq] = (code, err_str, data_str)
                return
        if fut.done():
            return
        self._resolve_future(fut, code, err_str, data_str)

    @staticmethod
    def _resolve_future(fut: Future, code: int, err_str: str, data_str: str) -> None:
        if code != 0:
            fut.set_exception(RuntimeError(f"mRPC [{code}]: {err_str}"))
            return
        try:
            fut.set_result(json.loads(data_str))
        except Exception:
            fut.set_result(data_str)

    def _on_stream(self, topic: bytes, meta_json: bytes, ptr, length: int) -> None:
        top = topic.decode("utf-8", errors="ignore")
        try:
            meta = json.loads(meta_json.decode("utf-8", errors="ignore"))
        except Exception:
            meta = {}
        raw = ctypes.string_at(ptr, length) if (ptr and length > 0) else b""
        for cb in list(self._stream_listeners):
            cb(top, meta, raw)

    def register_port(self, ch: str, use_cobs: bool, send_fn: Callable[[bytes], None]) -> None:
        self._send_handlers[ch] = send_fn
        self.dll.mrpc_register_port(ch.encode("utf-8"), 1 if use_cobs else 0)

    def unregister_port(self, ch: str) -> None:
        self._send_handlers.pop(ch, None)
        self.dll.mrpc_unregister_port(ch.encode("utf-8"))

    def feed_bytes(self, ch: str, data: bytes) -> None:
        if data:
            buf = (ctypes.c_uint8 * len(data)).from_buffer_copy(data)
            self.dll.mrpc_feed_bytes(ch.encode("utf-8"), buf, len(data))

    def add_stream_listener(self, cb: Callable[[str, Dict[str, Any], bytes], None]) -> None:
        self._stream_listeners.append(cb)

    def subscribe_topic(self, topic: str) -> None:
        self.dll.mrpc_subscribe_topic(topic.encode("utf-8"))

    def unsubscribe_topic(self, topic: str) -> None:
        self.dll.mrpc_unsubscribe_topic(topic.encode("utf-8"))

    def subscribe_thermal_stream(self) -> None:
        self.dll.mrpc_subscribe_thermal_stream()

    def unsubscribe_thermal_stream(self) -> None:
        self.dll.mrpc_unsubscribe_thermal_stream()

    def remove_hook(self, seq: int) -> None:
        self.dll.mrpc_remove_hook(seq)

    def _await_seq(self, invoke_fn: Callable[[], int], timeout_ms: int = 4000) -> Any:
        fut: Future = Future()
        with self._lock:
            seq = invoke_fn()
            if seq == 0:
                raise RuntimeError("mRPC 调用发送失败 (seq=0)")
            early = self._early_results.pop(seq, None)
            if early is not None:
                self._resolve_future(fut, *early)
            else:
                self._pending[seq] = fut
        try:
            return fut.result(timeout=timeout_ms / 1000.0 + 0.5)
        except Exception:
            with self._lock:
                self._pending.pop(seq, None)
                self._early_results.pop(seq, None)
            self.dll.mrpc_remove_hook(seq)
            raise

    def invoke(
        self,
        method: str,
        req: Any = None,
        timeout_ms: int = 4000,
        channel: str = "",
        metadata: Optional[Dict[str, str]] = None,
    ) -> Any:
        req_json = json.dumps(req, ensure_ascii=False) if req is not None else ""
        meta_json = json.dumps(metadata, ensure_ascii=False) if metadata else ""
        return self._await_seq(
            lambda: self.dll.mrpc_invoke(
                method.encode("utf-8"),
                req_json.encode("utf-8"),
                self.token.encode("utf-8"),
                timeout_ms,
                channel.encode("utf-8"),
                meta_json.encode("utf-8"),
            ),
            timeout_ms,
        )

    def login(self, username: str = "admin", password: str = "", timeout_ms: int = 4000, channel: str = "") -> Any:
        res = self._await_seq(
            lambda: self.dll.mrpc_login(
                username.encode("utf-8"), password.encode("utf-8"), timeout_ms, channel.encode("utf-8")
            ),
            timeout_ms,
        )
        if isinstance(res, dict) and res.get("token"):
            self.token = str(res["token"])
        elif isinstance(res, str) and res:
            self.token = res
        return res

    def board_info(self, timeout_ms: int = 3000, channel: str = "") -> Any:
        return self._await_seq(
            lambda: self.dll.mrpc_board_info(self.token.encode("utf-8"), timeout_ms, channel.encode("utf-8")),
            timeout_ms,
        )

    def get_chip_temp(self, timeout_ms: int = 2000, channel: str = "") -> Any:
        return self._await_seq(
            lambda: self.dll.mrpc_get_chip_temp(self.token.encode("utf-8"), timeout_ms, channel.encode("utf-8")),
            timeout_ms,
        )

    def config_load(self, timeout_ms: int = 3000, channel: str = "") -> Dict[str, Any]:
        res = self._await_seq(
            lambda: self.dll.mrpc_config_load(self.token.encode("utf-8"), timeout_ms, channel.encode("utf-8")),
            timeout_ms,
        )
        if isinstance(res, str):
            return json.loads(res)
        return res if isinstance(res, dict) else {}

    def config_save(self, timeout_ms: int = 3000, channel: str = "") -> Any:
        return self._await_seq(
            lambda: self.dll.mrpc_config_save(self.token.encode("utf-8"), timeout_ms, channel.encode("utf-8")),
            timeout_ms,
        )

    def config_reset(self, timeout_ms: int = 3000, channel: str = "") -> Any:
        return self._await_seq(
            lambda: self.dll.mrpc_config_reset(self.token.encode("utf-8"), timeout_ms, channel.encode("utf-8")),
            timeout_ms,
        )

    def config_set_str(self, key: str, value: str, timeout_ms: int = 3000, channel: str = "") -> Any:
        return self._await_seq(
            lambda: self.dll.mrpc_config_set_str(
                key.encode("utf-8"), value.encode("utf-8"), self.token.encode("utf-8"), timeout_ms, channel.encode("utf-8")
            ),
            timeout_ms,
        )

    def config_set_int(self, key: str, value: int, timeout_ms: int = 3000, channel: str = "") -> Any:
        return self._await_seq(
            lambda: self.dll.mrpc_config_set_int(
                key.encode("utf-8"), value, self.token.encode("utf-8"), timeout_ms, channel.encode("utf-8")
            ),
            timeout_ms,
        )

    def config_set_float(self, key: str, value: float, timeout_ms: int = 3000, channel: str = "") -> Any:
        return self._await_seq(
            lambda: self.dll.mrpc_config_set_float(
                key.encode("utf-8"), value, self.token.encode("utf-8"), timeout_ms, channel.encode("utf-8")
            ),
            timeout_ms,
        )

    def config_set_bool(self, key: str, value: bool, timeout_ms: int = 3000, channel: str = "") -> Any:
        return self._await_seq(
            lambda: self.dll.mrpc_config_set_bool(
                key.encode("utf-8"), 1 if value else 0, self.token.encode("utf-8"), timeout_ms, channel.encode("utf-8")
            ),
            timeout_ms,
        )

    def config_set(self, key: str, value: Any, timeout_ms: int = 3000, channel: str = "") -> Any:
        if isinstance(value, bool):
            return self.config_set_bool(key, value, timeout_ms, channel)
        if isinstance(value, int):
            return self.config_set_int(key, value, timeout_ms, channel)
        if isinstance(value, float):
            return self.config_set_float(key, value, timeout_ms, channel)
        return self.config_set_str(key, str(value), timeout_ms, channel)

    def sensor_auto_calibrate(self, timeout_ms: int = 5000, channel: str = "") -> Any:
        return self._await_seq(
            lambda: self.dll.mrpc_sensor_auto_calibrate(self.token.encode("utf-8"), timeout_ms, channel.encode("utf-8")),
            timeout_ms,
        )

    def wireless_net_info(self, timeout_ms: int = 3000, channel: str = "") -> Any:
        res = self._await_seq(
            lambda: self.dll.mrpc_wireless_net_info(self.token.encode("utf-8"), timeout_ms, channel.encode("utf-8")),
            timeout_ms,
        )
        if isinstance(res, str):
            try:
                return json.loads(res)
            except Exception:
                return res
        return res

    def wireless_control(self, enable: bool, timeout_ms: int = 3000, channel: str = "") -> Any:
        return self._await_seq(
            lambda: self.dll.mrpc_wireless_control(
                1 if enable else 0, self.token.encode("utf-8"), timeout_ms, channel.encode("utf-8")
            ),
            timeout_ms,
        )


class SerialTransport:
    def __init__(self, rpc: MRpcClient):
        self.rpc = rpc
        self.ser: Optional[serial.Serial] = None
        self._running = False
        self._lock = threading.Lock()

    @staticmethod
    def list_ports() -> List[str]:
        return [p.device for p in serial.tools.list_ports.comports()]

    def connect(self, port: str, baudrate: int = 921600) -> None:
        self.disconnect()
        self.ser = serial.Serial(port, baudrate=baudrate, timeout=0.05, write_timeout=1.0)
        self.rpc.register_port("serial", True, self._send)
        self._running = True
        threading.Thread(target=self._loop, daemon=True).start()

    def _send(self, data: bytes) -> None:
        if self.ser and self.ser.is_open:
            with self._lock:
                self.ser.write(data)

    def _loop(self) -> None:
        while self._running and self.ser and self.ser.is_open:
            try:
                n = self.ser.in_waiting
                chunk = self.ser.read(n if n > 0 else 1)
                if chunk:
                    self.rpc.feed_bytes("serial", chunk)
            except Exception:
                time.sleep(0.02)

    def disconnect(self) -> None:
        self._running = False
        self.rpc.unregister_port("serial")
        if self.ser:
            try:
                self.ser.close()
            except Exception:
                pass
            self.ser = None


def _build_mdns_query_packet(host: str) -> bytes:
    clean_host = host.lower().strip()
    pkt = bytearray([0x00, 0x00, 0x00, 0x00, 0x00, 0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])
    for part in clean_host.split("."):
        if not part:
            continue
        b = part.encode("ascii", errors="ignore")
        pkt.append(len(b))
        pkt.extend(b)
    pkt.append(0x00)
    pkt.extend([0x00, 0x01, 0x80, 0x01])  # QTYPE=A(1), QCLASS=IN(1)|unicast(0x8000)
    return bytes(pkt)


def _parse_mdns_response_packet(data: bytes) -> Optional[str]:
    if len(data) < 12:
        return None
    for i in range(12, len(data) - 13):
        if data[i] == 0x00 and data[i + 1] == 0x01 and (data[i + 2] & 0x7F) == 0x00 and data[i + 3] == 0x01:
            data_len = (data[i + 8] << 8) | data[i + 9]
            if data_len == 4 and i + 14 <= len(data):
                return f"{data[i+10]}.{data[i+11]}.{data[i+12]}.{data[i+13]}"
    return None


def _is_ipv4(host: str) -> bool:
    try:
        ipaddress.IPv4Address(host)
        return True
    except Exception:
        return False


def _tcp_reachable(ip: str, port: int, timeout: float = 0.6) -> bool:
    try:
        with socket.create_connection((ip, port), timeout=timeout):
            return True
    except Exception:
        return False


def probe_mdns_device(host: str = "OpenThermal.local", port: int = 80, timeout_sec: float = 1.5) -> Optional[str]:
    """与 application/lib/rpc/websocket_transport.dart 对齐的 UDP 5353 mDNS 快速探测"""
    if _is_ipv4(host):
        return host

    sock = None
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        sock.settimeout(0.15)
        sock.bind(("0.0.0.0", 0))

        query = _build_mdns_query_packet(host)
        sock.sendto(query, ("224.0.0.251", 5353))

        # 向本机所有 IPv4 网卡的子网 .255 与 .1 广播查询（突破多网卡组播限制）
        try:
            for info in socket.getaddrinfo(socket.gethostname(), None, socket.AF_INET):
                ip_str = info[4][0]
                if "." in ip_str and not ip_str.startswith("127."):
                    prefix = ip_str.rsplit(".", 1)[0]
                    for target in (f"{prefix}.255", f"{prefix}.1"):
                        try:
                            sock.sendto(query, (target, 5353))
                        except Exception:
                            pass
        except Exception:
            pass

        deadline = time.monotonic() + timeout_sec
        while time.monotonic() < deadline:
            try:
                data, _ = sock.recvfrom(2048)
                ip = _parse_mdns_response_packet(data)
                if ip and _tcp_reachable(ip, port, 0.6):
                    return ip
            except socket.timeout:
                continue
            except Exception:
                break
    except Exception:
        pass
    finally:
        if sock:
            try:
                sock.close()
            except Exception:
                pass

    # 兜底：系统 DNS 解析
    try:
        ip = socket.gethostbyname(host)
        if ip and _tcp_reachable(ip, port, 1.0):
            return ip
    except Exception:
        pass
    return None


class WebSocketTransport:
    def __init__(self, rpc: MRpcClient):
        self.rpc = rpc
        self._loop: Optional[asyncio.AbstractEventLoop] = None
        self._ws = None
        self._evt = threading.Event()
        self._err: Optional[Exception] = None
        self._auto_reconnect = False
        self._manual_close = False
        self.cached_device_ip: Optional[str] = None

    def _resolve_ws_url(self, url: str) -> str:
        parsed = urlparse(url)
        host = parsed.hostname or ""
        port = parsed.port or (443 if parsed.scheme == "wss" else 80)
        if host and not _is_ipv4(host):
            ip = probe_mdns_device(host, port)
            if ip:
                self.cached_device_ip = ip
                netloc = f"{ip}:{port}" if parsed.port else ip
                return urlunparse((parsed.scheme, netloc, parsed.path, parsed.params, parsed.query, parsed.fragment))
        return url

    def connect(self, url: str = "ws://OpenThermal.local:80/ws", auto_reconnect: bool = True) -> None:
        self.disconnect()
        self._manual_close = False
        self._auto_reconnect = auto_reconnect
        self._evt.clear()
        self._err = None

        resolved_url = self._resolve_ws_url(url)
        threading.Thread(target=self._run, args=(resolved_url, url), daemon=True).start()
        if not self._evt.wait(timeout=5.0):
            self.disconnect()
            raise TimeoutError(f"连接超时: {resolved_url}")
        if self._err:
            err = self._err
            self.disconnect()
            raise err

    def _run(self, resolved_url: str, raw_url: str) -> None:
        self._loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self._loop)
        try:
            self._loop.run_until_complete(self._main_loop(resolved_url, raw_url))
        except Exception as e:
            self._err = e
            self._evt.set()
        finally:
            self._loop.close()
            self._loop = None

    async def _main_loop(self, resolved_url: str, raw_url: str) -> None:
        first_attempt = True
        target_url = resolved_url
        while not self._manual_close:
            try:
                async with websockets.connect(target_url, max_size=4 * 1024 * 1024) as ws:
                    self._ws = ws
                    self.rpc.register_port("ws", False, self._send)
                    self._evt.set()
                    first_attempt = False
                    async for msg in ws:
                        if isinstance(msg, (bytes, bytearray)):
                            self.rpc.feed_bytes("ws", bytes(msg))
                        elif isinstance(msg, str):
                            self.rpc.feed_bytes("ws", msg.encode("utf-8"))
            except Exception as e:
                if first_attempt:
                    self._err = e
                    self._evt.set()
                    return
            finally:
                self._ws = None
                self.rpc.unregister_port("ws")

            if self._manual_close or not self._auto_reconnect:
                break
            await asyncio.sleep(3.0)
            target_url = self._resolve_ws_url(raw_url)

    def _send(self, data: bytes) -> None:
        if self._loop and self._ws:
            asyncio.run_coroutine_threadsafe(self._ws.send(data), self._loop)

    def disconnect(self) -> None:
        self._manual_close = True
        self._auto_reconnect = False
        self.rpc.unregister_port("ws")
        if self._loop and self._ws:
            asyncio.run_coroutine_threadsafe(self._ws.close(), self._loop)
        self._ws = None
