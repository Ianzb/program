from .program import *


class LoggingFunctions:
    """
    日志相关函数
    """

    def __init__(self):
        import logging
        self.log = logging.getLogger(__name__)
        self.log.setLevel(logging.DEBUG)
        handler1 = logging.StreamHandler(sys.stderr)
        handler1.setLevel(logging.INFO)
        handler1.setFormatter(logging.Formatter("[%(levelname)s %(asctime)s %(filename)s %(process)downloadKit]:%(message)s"))

        handler2 = logging.FileHandler(program.LOGGING_FILE_PATH)
        handler2.setLevel(logging.DEBUG)
        handler2.setFormatter(logging.Formatter("[%(levelname)s %(asctime)s %(filename)s %(process)downloadKit]:%(message)s"))

        self.log.addHandler(handler1)
        self.log.addHandler(handler2)

    def reset(self):
        """
        重置日志文件
        """
        open(program.LOGGING_FILE_PATH, "w", encoding="utf-8").close()

    def debug(self, data: str):
        """
        调试日志
        @param data: 数据
        """
        self.log.debug(data)

    def info(self, data: str):
        """
        信息日志
        @param data: 数据
        """
        self.log.info(data)

    def warning(self, data: str):
        """
        警告日志
        @param data: 数据
        """
        self.log.warning(data)

    def error(self, data: str):
        """
        错误日志
        @param data: 数据
        """
        self.log.error(data)

    def critical(self, data: str):
        """
        异常日志
        @param data: 数据
        """
        self.log.critical(data)

    def fatal(self, data: str):
        """
        崩溃日志
        @param data: 数据
        """
        self.log.fatal(data)


logging = LoggingFunctions()
