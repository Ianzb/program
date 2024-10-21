from .log import *
import os


class System:
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
