import os
import gc
import time
import psutil
import threading
from collections import Counter
from lib.newstructure.system_runtime import system
from lib.newstructure.websocket_runtime import websocket_server
import tracemalloc


_last_objects = 0
_last_snapshot = None


def memory_monitor_strong():
    global _last_objects, _last_snapshot

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

    # =========================
    # 1. list 泄漏“趋势判断”
    # =========================
    list_objs = [o for o in objs if isinstance(o, list)]

    # 统计“大list”（重点）
    big_lists = [l for l in list_objs if len(l) > 100]

    print(f"[LIST] total={len(list_objs)} big_lists={len(big_lists)}")

    # =========================
    # 2. tracemalloc 分析
    # =========================
    snapshot = tracemalloc.take_snapshot()

    if _last_snapshot:
        top_stats = snapshot.compare_to(_last_snapshot, "traceback")

        print("\n===== TOP MEMORY (CALL STACK) =====")
        for stat in top_stats[:10]:
            print(stat)
        print("==================================\n")

        # 🔥 关键增强：只看 list 相关分配
        list_stats = [
            stat for stat in top_stats
            if "list" in str(stat)
        ]

        if list_stats:
            print("\n===== LIST ALLOCATION HOTSPOTS =====")
            for stat in list_stats[:10]:
                print(stat)
            print("====================================\n")

    _last_snapshot = snapshot


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
            websocket_check()  
            memory_monitor_strong()

        except Exception as e:
            print("memory monitor error:", e)

        time.sleep(interval)


def start_memory_monitor():
    tracemalloc.start(25)   

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



def websocket_check():
    try:
        ws = websocket_server  # 你全局实例

        client_count = len(ws.clients)

        print(f"[WS] CLIENTS={client_count}")

        # ⚠️ 如果 loop 存在，检查 task backlog
        if ws.loop:
            import asyncio

            tasks = asyncio.all_tasks(ws.loop)
            print(f"[WS] ASYNC_TASKS={len(tasks)}")

    except Exception as e:
        print("[WS] CHECK ERROR:", e)    