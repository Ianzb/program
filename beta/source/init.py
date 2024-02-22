from .function import *


class Init():
    """
    初始化程序
    """

    def __init__(self):

        # 重复运行检测
        program.detectRepeatRun()

        # 日志过大检测
        if f.getSize(program.LOGGING_FILE_PATH) / 1024 >= 32:
            logging.reset()

        # 插件检测
        f.clearFile(program.ADDON_PATH)


Init()

logging.debug("init.py初始化成功")
