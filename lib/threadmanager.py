from concurrent.futures import ThreadPoolExecutor
import threading

class ThreadManager:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls, max_workers=4):
        with cls._lock:
            if not cls._instance:
                cls._instance = super(ThreadManager, cls).__new__(cls)
                cls._instance.executor = ThreadPoolExecutor(max_workers=max_workers)
        return cls._instance

    def submit_task(self, task):
        """提交任务到线程池"""
        self.executor.submit(task)

    def shutdown(self):
        """关闭线程池"""
        self.executor.shutdown(wait=True)