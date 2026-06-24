import os
import gc
import time
import psutil
import threading
from collections import Counter
from lib.newstructure.system_runtime import system

_last_objects = 0


def memory_check():

    global _last_objects

    process = psutil.Process(os.getpid())

    rss = process.memory_info().rss / 1024 / 1024

    objs = gc.get_objects()

    obj_count = len(objs)

    print(
        f"[MEMORY] "
        f"RSS={rss:.2f}MB "
        f"THREADS={threading.active_count()} "
        f"OBJECTS={obj_count} "
        f"DIFF={obj_count - _last_objects:+}"
    )

    _last_objects = obj_count

    # 对象增长过快时打印TOP20
    if obj_count % 2000 < 200:

        counter = Counter(
            type(obj).__name__
            for obj in objs
        )

        print("\n===== TOP OBJECTS =====")

        for name, count in counter.most_common(20):
            print(f"{name:<30} {count}")

        print("=======================\n")


def memory_monitor_loop(interval=1):

    while True:

        try:
            memory_check()
            ouput_moreinfo()
            find_motor_callback_count()

        except Exception as e:
            print("memory monitor error:", e)

        time.sleep(interval)


def start_memory_monitor():

    t = threading.Thread(
        target=memory_monitor_loop,
        daemon=True,
        name="MemoryMonitor"
    )

    t.start()

def ouput_moreinfo():
    try:

        bus = system["bus"]

        total_callbacks = 0

        for callbacks in bus.subscribers.values():
            total_callbacks += len(callbacks)

        print(
            f"[BUS] "
            f"EVENTS={len(bus.subscribers)} "
            f"CALLBACKS={total_callbacks}"
        )

    except Exception as e:
        print("BUS INFO ERROR:", e)


def find_motor_callback_count():

    count = 0

    for obj in gc.get_objects():

        try:
            if callable(obj):

                if getattr(obj, "__name__", "") == "_cb":
                    count += 1

        except:
            pass

    print("[CALLBACK _cb]", count)        