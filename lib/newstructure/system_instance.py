# system_instance.py

from lib.newstructure.system import build_system
import threading

_system = None
_lock = threading.Lock()


def get_system():
    global _system

    if _system is None:
        with _lock:
            if _system is None:   # 双重检查锁（防并发）
                _system = build_system()

    return _system