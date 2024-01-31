from .function import *


class Init():
    """
    初始化程序
    """

    def __init__(self):

        # 重复运行检测
        if "python" in f.cmd(f"tasklist |findstr {setting.read("pid")}", True):
            setting.save("showWindow", "1")
            logging.info(f"当前程序为重复运行，自动退出")
            sys.exit()
        setting.save("pid", str(program.PROGRAM_PID))

        # 日志过大检测
        if f.getSize(program.LOGGING_FILE_PATH) / 1024 >= 32:
            logging.reset()

        # 插件检测
        f.clearFile(program.ADDON_PATH)


Init()

logging.debug("init.py初始化成功")
