from .function import *


class Init():
    """
    初始化程序
    """

    def __init__(self):

        # 切换运行路径
        os.chdir(program.PROGRAM_PATH)

        # 设置任务栏
        import ctypes

        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(program.PROGRAM_NAME)

        # 关闭SSL证书验证
        import ssl

        ssl._create_default_https_context = ssl._create_unverified_context()

        # 重复运行检测
        if "python" in f.cmd(f"tasklist |findstr {setting.read("pid")}", True):
            setting.save("showWindow", "1")
            logging.info(f"当前程序为重复运行，自动退出")
            sys.exit()
        setting.save("pid", str(program.PROGRAM_PID))

        # 日志过大检测
        if f.getSize(program.LOGGING_FILE_PATH) / 1024 >= 32:
            logging.reset()


Init()

logging.debug("init.py初始化成功")
