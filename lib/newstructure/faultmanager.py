# faultmanager.py

import logging
import os
from datetime import datetime

from lib.newstructure.runtime import runtime


class FaultManager:

    def __init__(self, bus):

        self.bus = bus

        # 初始化日志
        self._init_logger()

        bus.subscribe("command_ack", self.on_command_ack)
        bus.subscribe("command_failed", self.on_command_failed)


    def _init_logger(self):

        log_dir = "logs"

        if not os.path.exists(log_dir):
            os.makedirs(log_dir)


        # 当前日期生成文件名
        today = datetime.now().strftime("%Y%m%d")

        log_file = os.path.join(
            log_dir,
            f"fault_{today}.txt"
        )


        self.logger = logging.getLogger("FaultManager")

        self.logger.setLevel(logging.INFO)


        # 防止重复添加handler
        if not self.logger.handlers:

            handler = logging.FileHandler(
                log_file,
                encoding="utf-8"
            )


            formatter = logging.Formatter(
                "%(asctime)s | %(levelname)s | %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S"
            )


            handler.setFormatter(formatter)

            self.logger.addHandler(handler)

    def write_log(self, level, message):
        """
        写本地日志
        """

        if level == "ERROR":
            self.logger.error(message)

        elif level == "WARNING":
            self.logger.warning(message)

        else:
            self.logger.info(message)



    def on_command_ack(self, data):
        """
        命令收到ACK
        """

        msg = (
            f"motor={data['motor']} "
            f"cmd={data['cmd']}"
        )

        print("[ACK]", msg)

        self.write_log(
            "INFO",
            "ACK " + msg
        )



    def on_command_failed(self, data):
        """
        命令执行失败
        """

        msg = (
            f"motor={data['motor']} "
            f"cmd={data['cmd']} "
            f"reason={data['reason']}"
        )

        print("[ERROR]", msg)


        # 写故障日志
        self.write_log(
            "ERROR",
            msg
        )


        # 设置系统异常状态
        runtime.set_dirty(True)


        # 后续扩展
        # self.stop_all_tasks()
        # self.disable_all_motor()
        # self.notify_frontend()