import os
import gc
import time
import psutil
import threading


def memory_check():
    process = psutil.Process(os.getpid())

    rss = process.memory_info().rss / 1024 / 1024

    print(
        f"[MEMORY] "
        f"RSS={rss:.2f}MB "
        f"THREADS={threading.active_count()} "
        f"OBJECTS={len(gc.get_objects())}"
    )


def memory_monitor_loop(interval=300):
    while True:
        memory_check()
        time.sleep(interval)


def start_memory_monitor():
    t = threading.Thread(
        target=memory_monitor_loop,
        args=(1,),  # 5分钟一次
        daemon=True,
        name="MemoryMonitor"
    )
    t.start()