from queue import Queue
import threading
from lib.threadmanager import ThreadManager

class ActionQueueManager:
    def __init__(self, name):
        self.name = name
        self.queue = Queue()
        self.stop_event = threading.Event()
        # 直接获取单例线程池
        self.thread_manager = ThreadManager()
        self.thread_manager.submit_task(self.worker)

    def worker(self):
        while not self.stop_event.is_set():
            try:
                task = self.queue.get(timeout=1)  # 可安全退出
            except:
                continue
            task.execute()
            self.queue.task_done()

    def submit_task(self, task):
        self.queue.put(task)

    def stop(self):
        self.stop_event.set()