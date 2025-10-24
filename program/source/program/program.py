import logging
import subprocess
import traceback
import importlib
import time
from concurrent.futures import ThreadPoolExecutor

import functools
from PyQt5 import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5 import QtCore
from PyQt5 import QtGui
from PyQt5 import QtWidgets
from qtpy import *
from qfluentwidgets import *
from qfluentwidgets.components.material import *
from qfluentwidgets import FluentIcon as FIF

import zbToolLib as zb
import zbWidgetLib as zbw
from zbWidgetLib import ZBF
from qtpy import *


class Program:
    """
    程序信息
    """
    NAME = "zb小程序"  # 程序名称
    VERSION = "5.6.1"  # 程序版本
    VERSION_CODE = 58  # 版本序数
    ADDON_API_VERSION = 2  # 插件版本序数
    CORE_VERSION = "5.3.5"  # 内核版本
    TITLE = f"{NAME} {VERSION}"  # 程序标题
    URL = "https://ianzb.github.io/project/program.html"  # 程序网址
    LICENSE = "GPLv3"  # 程序许可协议
    INFO = "© 2022-2025 Ianzb. GPLv3 License."
    UPDATE_URL = "https://drive.ianzb.cn/code/program/index.json"  # 更新网址
    UPDATE_INSTALLER_URL = "https://drive.ianzb.cn/code/program/zbProgram_setup.exe"  # 更新安装包链接
    ADDON_URL = "https://drive.ianzb.cn/code/program/addon/addon.json"  # 插件信息网址
    UNINSTALL_FILE = "unins000.exe"  # 卸载程序名称

    AUTHOR_NAME = "Ianzb"  # 作者名称
    AUTHOR_URL = "https://ianzb.github.io/"  # 作者网址
    GITHUB_URL = "https://github.com/Ianzb/program/"  # Github网址

    MAIN_FILE_PATH = sys.argv[0]  # 程序主文件路径
    MAIN_FILE_NAME = zb.getFileName(MAIN_FILE_PATH)  # 当前程序文件名称
    INSTALL_PATH = zb.getFileDir(MAIN_FILE_PATH)  # 程序安装路径
    SOURCE_PATH = r"source\img"  # 程序资源文件路径
    PID = os.getpid()  # 程序pid
    DATA_PATH = zb.joinPath(zb.USER_PATH, "zb")  # 程序数据路径
    SETTING_FILE_PATH = zb.joinPath(DATA_PATH, "settings.json")  # 程序设置文件路径
    LOGGING_FILE_PATH = zb.joinPath(DATA_PATH, "logging.log")  # 程序日志文件路径
    ADDON_PATH = zb.joinPath(DATA_PATH, "addon")  # 程序插件路径
    PACKAGE_PATH = zb.joinPath(DATA_PATH, "package")

    STARTUP_ARGUMENT = sys.argv[1:]  # 程序启动参数
    THREAD_POOL = ThreadPoolExecutor()  # 程序公用线程池

    def __init__(self):
        # 创建数据目录
        zb.createDir(self.DATA_PATH)

        # 切换运行路径
        os.chdir(self.INSTALL_PATH)

        # 设置任务栏
        import ctypes

        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(self.NAME)

        # 开发者插件目录切换
        if not self.isExe:
            self.ADDON_PATH = zb.joinPath(self.INSTALL_PATH, "../addon")

        # 添加插件路径
        sys.path.append(self.ADDON_PATH)
        sys.path.append(self.PACKAGE_PATH)

        # 打包后资源路径切换
        if self.isExe:
            self.SOURCE_PATH = sys._MEIPASS + r"\img"

    @property
    def ICON(self):
        return self.source("program.png")

    @property
    def isStartup(self):
        """
        判断程序是否为开机自启动
        @return: bool
        """
        return "startup" in self.STARTUP_ARGUMENT

    @property
    def isExe(self):
        """
        判断程序是否为
        @return:
        """
        return ".exe" in self.MAIN_FILE_NAME

    def source(self, *args):
        """
        快捷获取程序资源文件路径
        @param name: 文件名
        @return: 文件路径
        """
        return zb.joinPath(self.SOURCE_PATH, *args)

    def cache(self, *args):
        """
        快捷获取程序缓存文件路径
        @param name: 文件名
        @return: 文件路径
        """
        return zb.joinPath(self.DATA_PATH, "cache", *args)

    def close(self):
        """
        退出程序
        """
        logging.info("程序已退出！")
        os._exit(0)

    def restart(self):
        """
        重启程序
        """
        subprocess.Popen(self.MAIN_FILE_PATH)
        logging.info("程序正在重启中！")
        os._exit(0)

    def detectRepeatRun(self):
        """
        程序重复运行检测
        """
        if not self.isExe:
            return
        if zb.existPath(zb.joinPath(self.DATA_PATH, "zb.lock")):
            with open(zb.joinPath(self.DATA_PATH, "zb.lock"), "r+", encoding="utf-8") as file:
                pid = file.read().strip()
            if pid and "zbProgram.exe" in zb.easyCmd(f"tasklist |findstr {pid}", True):
                open(zb.joinPath(self.DATA_PATH, "zb.unlock"), "w").close()
                logging.info(f"检测到重复PID{pid}，程序重复运行，自动关闭！")
                self.close()
        if zb.existPath(zb.joinPath(self.DATA_PATH, "zb.unlock")):
            os.remove(zb.joinPath(self.DATA_PATH, "zb.unlock"))
        with open(zb.joinPath(self.DATA_PATH, "zb.lock"), "w+", encoding="utf-8") as file:
            file.write(str(self.PID))
        logging.info(f"程序运行锁创建成功，PID{self.PID}！")

    def addToStartup(self, mode: bool = True):
        """
        添加开机自启动
        @param mode: True添加/False删除
        """
        import win32api, win32con
        key = win32api.RegOpenKey(win32con.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run", 0, win32con.KEY_ALL_ACCESS)
        try:
            if mode:
                win32api.RegSetValueEx(key, self.NAME, 0, win32con.REG_SZ, f"{self.MAIN_FILE_PATH} startup")
                win32api.RegCloseKey(key)
                logging.info("启动项添加成功")
            else:
                win32api.RegDeleteValue(key, self.NAME)
                win32api.RegCloseKey(key)
                logging.info("启动项删除成功")
        except:
            logging.warning(f"启动项编辑失败{traceback.format_exc()}")

    def checkStartup(self):
        """
        检查开机自启动
        @return: 是否
        """
        import win32api, win32con
        try:
            key = win32api.RegOpenKeyEx(win32con.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run", 0, win32con.KEY_READ)
            win32api.RegQueryValueEx(key, self.NAME)
            win32api.RegCloseKey(key)
            return True
        except win32api.error:
            return False

    def getNewestVersion(self):
        """
        获取程序最新版本
        @return: 程序最新版本
        """
        response = zb.getUrl(self.UPDATE_URL, headers=zb.REQUEST_HEADER)
        data = json.loads(response.text)
        logging.info(f"服务器最新版本：{data}")
        return data


program = Program()
