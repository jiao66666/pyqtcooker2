
import sys
import os
import queue
import threading
from datetime import datetime


class AsyncTeeLogger:
    def __init__(self, console, log_path, capture_all_print=False):
        self.console = console
        self.capture_all_print = capture_all_print  # 是否记录所有 print

        self.queue = queue.Queue(maxsize=50000)
        self.running = True

        self.dropped = 0
        self.dropped_lock = threading.Lock()

        self.log_file = open(
            log_path, "a", encoding="utf-8", buffering=1
        )

        self.worker = threading.Thread(
            target=self._write_loop,
            name="LogWriter",
            daemon=True
        )
        self.worker.start()

    def write(self, message):
        """普通 print：控制台输出，根据开关决定是否写入文件"""

        if isinstance(message, bytes):
            message = message.decode("utf-8", errors="replace")

        self.console.write(message)
        self.console.flush()

        # 开启开关后，所有普通 print 也记录到文件
        if self.capture_all_print and message:
            self._put_log(message)

    def _put_log(self, message):
        """统一异步写入队列"""

        timestamp = datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S.%f"
        )[:-3]

        try:
            self.queue.put_nowait(
                f"[{timestamp}] {message}"
            )
        except queue.Full:
            with self.dropped_lock:
                self.dropped += 1

    def log_to_file(self, *args, sep=" ", end="\n"):
        """指定内容写入本地文件，不影响普通 print"""

        message = sep.join(str(arg) for arg in args) + end
        self._put_log(message)

    def _write_loop(self):
        while self.running or not self.queue.empty():
            try:
                message = self.queue.get(timeout=0.5)
            except queue.Empty:
                continue

            try:
                self.log_file.write(message)
            except Exception as e:
                try:
                    self.console.write(
                        f"\n日志文件写入失败: {e}\n"
                    )
                    self.console.flush()
                except Exception:
                    pass
            finally:
                self.queue.task_done()

        self.log_file.flush()

    def flush(self):
        self.console.flush()

    def isatty(self):
        return self.console.isatty()

    def fileno(self):
        return self.console.fileno()

    def log(self, *args, **kwargs):
        self.log_to_file(*args, **kwargs)


_logger = None


def init_logger():
    global _logger

    if _logger is not None:
        return _logger

    log_dir = "logs"
    os.makedirs(log_dir, exist_ok=True)

    filename = datetime.now().strftime(
        "cooker_%Y%m%d_%H%M%S.log"
    )

    log_path = os.path.join(log_dir, filename)

    # True：记录所有 print
    # False：只记录主动调用 log_to_file 的内容
    logger = AsyncTeeLogger(
        sys.__stdout__,
        log_path,
        capture_all_print=False
    )

    sys.stdout = logger
    sys.stderr = logger

    _logger = logger
    return logger


def log_to_file(*args, **kwargs):
    """供其他模块直接调用"""

    if _logger is not None:
        _logger.log_to_file(*args, **kwargs)
