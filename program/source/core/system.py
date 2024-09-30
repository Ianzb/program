from log import *
import os
import threading


def easyCmd(command: str, pause: bool = False):
    """
    简单的调用cmd命令。
    @param command: 命令
    @param pause: 是否等待并返回输出结果
    @return: 输出结果
    """
    value = os.popen(command)
    if pause:
        value = value.read()
        logging.info(f"执行Cmd命令{command}的返回值为{value}。")
        return value


class EasyThread(threading.Thread):
    """
    threading多线程优化
    """

    def __init__(self, func, *args):
        super().__init__()

        self.func = func
        self.args = args

        self.daemon = True
        self.start()

    def run(self):
        self.func(*self.args)
