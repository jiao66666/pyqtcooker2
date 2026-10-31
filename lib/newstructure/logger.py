
import sys
import os
import queue
import threading
from datetime import datetime


class AsyncTeeLogger:
    def __init__(self, console, log_path):
        self.console = console
        self.queue = queue.Queue(maxsize=50000)
        self.running = True

        os.makedirs(os.path.dirname(log_path), exist_ok=True)

        self.log_file = open(
            log_path, "a", encoding="utf-8", buffering=1
        )

        self.local = threading.local()

        self.worker = threading.Thread(
            target=self._write_loop,
            name="LogWriter",
            daemon=True
        )
        self.worker.start()

    def write(self, message):
        if isinstance(message, bytes):
            message = message.decode("utf-8", errors="replace")

        # 控制台输出
        self.console.write(message)
        self.console.flush()

        if not hasattr(self.local, "buffer"):
            self.local.buffer = ""

        self.local.buffer += message

        while "\n" in self.local.buffer:
            line, self.local.buffer = self.local.buffer.split("\n", 1)

            timestamp = datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S.%f"
            )[:-3]

            try:
                self.queue.put_nowait(
                    f"[{timestamp}] {line}\n"
                )
            except queue.Full:
                # 不阻塞业务线程，记录丢失数量
                self.dropped += 1

    def _write_loop(self):
        while self.running or not self.queue.empty():
            try:
                message = self.queue.get(timeout=0.5)
            except queue.Empty:
                continue

            try:
                self.log_file.write(message)
            finally:
                self.queue.task_done()

        self.log_file.flush()

    def flush(self):
        self.console.flush()

    def isatty(self):
        return self.console.isatty()

    def fileno(self):
        return self.console.fileno()

    def close(self):
        self.running = False
        self.worker.join(timeout=5)

        self.log_file.flush()
        self.log_file.close()


def init_logger():
    log_dir = "logs"
    os.makedirs(log_dir, exist_ok=True)

    filename = datetime.now().strftime(
        "cooker_%Y%m%d_%H%M%S.log"
    )

    log_path = os.path.join(log_dir, filename)

    logger = AsyncTeeLogger(sys.__stdout__, log_path)
    logger.dropped = 0

    sys.stdout = logger
    sys.stderr = logger

    return logger
