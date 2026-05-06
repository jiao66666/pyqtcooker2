import threading

class _RuntimeSignals:
    def __init__(self):
        self.server_ready = threading.Event()
        self.system_ready = threading.Event()
        self.webview_ready = threading.Event()


# ===== 单例容器 =====
_signals = None
_lock = threading.Lock()


def get_signals():
    global _signals

    if _signals is None:
        with _lock:
            if _signals is None:
                _signals = _RuntimeSignals()

    return _signals