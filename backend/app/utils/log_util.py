# !/usr/bin/env python
# -*- coding:utf-8 -*-

"""
@author       weimenghua
@time         2022/4/16 20:03
@description  日志工具类
"""

import logging
import urllib.parse


class Logger(object):
    """
    终端打印不同颜色的日志，在pycharm中如果强行规定了日志的颜色，这个方法不会起作用，但是对于终端，这个方法是可以打印不同颜色的日志的。
    """

    # 在这里定义StreamHandler，可以实现单例， 所有的logger()共用一个StreamHandler
    ch = logging.StreamHandler()

    def __init__(self):
        self.logger = logging.getLogger()

        if not self.logger.handlers:
            # 如果self.logger没有handler， 就执行以下代码添加handler

            # 将日志级别设置为 INFO 或更高，这样 DEBUG 级别的日志将不会输出
            # self.logger.setLevel(logging.INFO)
            self.logger.setLevel(logging.DEBUG)

            # 设置 requests 和 urllib3 日志级别，这样这两个库 DEBUG 级别的日志将不会输出
            logging.getLogger("requests").setLevel(logging.WARNING)
            logging.getLogger("urllib3").setLevel(logging.WARNING)

            """
            log_path = '.tmp/log'
            self.log_path = log_path
            if not os.path.exists(self.log_path):
                os.makedirs(self.log_path)

            # 创建一个handler,用于写入日志文件
            fh = logging.FileHandler(self.log_path + '/log_' + time.strftime("%Y%m%d", time.localtime()) + '.log',
                                     encoding='utf-8')

            fh.setLevel(logging.INFO)

            # 定义handler的输出格式
            formatter = logging.Formatter('[%(asctime)s] - [%(levelname)s] - %(message)s')
            fh.setFormatter(formatter)

            # 给logger添加handler
            self.logger.addHandler(fh)
            """

            # 抑制requests库的debug日志
            null_handler = logging.NullHandler()
            requests_logger = logging.getLogger("requests")
            requests_logger.addHandler(null_handler)

    def debug(self, message):
        message = urllib.parse.unquote(str(message))
        if not isinstance(message, str):
            message = str(message)
        self.fontColor('\033[0;32m%s\033[0m')
        self.logger.debug(message)

    def info(self, message):
        self.fontColor('\033[0;34m%s\033[0m')
        self.logger.info(message)

    def warning(self, message):
        self.fontColor('\033[0;37m%s\033[0m')
        self.logger.warning(message)

    def error(self, message):
        self.fontColor('\033[0;31m%s\033[0m')
        self.logger.error(message)

    def critical(self, message):
        self.fontColor('\033[0;35m%s\033[0m')
        self.logger.critical(message)

    def fontColor(self, color):
        # 不同的日志输出不同的颜色
        formatter = logging.Formatter(color % '[%(asctime)s] - [%(levelname)s] - %(message)s')
        self.ch.setFormatter(formatter)
        self.logger.addHandler(self.ch)


if __name__ == "__main__":
    logger = Logger()
    logger.info("12345")
    logger.debug("12345")
    logger.warning("12345")
    logger.error("12345")
