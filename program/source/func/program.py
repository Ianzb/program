import functools
import json
import os
import sys
import shutil
import threading
import webbrowser
import time
import requests
import bs4
import lxml
import winshell
import importlib
from send2trash import *
from traceback import format_exception
from PyQt5 import *
from PyQt5.Qt import *
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
from DownloadKit import DownloadKit


class Program:
    """
    程序信息
    """
    NAME = "zb小程序"  # 程序名称
    VERSION = "4.2.0"  # 程序版本
    TITLE = f"{NAME} {VERSION}"  # 程序窗口标题
    URL = "https://ianzb.github.io/project/"  # 程序网址
    AUTHOR_NAME = "Ianzb"  # 作者名称
    AUTHOR_URL = "https://ianzb.github.io/"  # 作者网址
    UPDATE_URL = "https://vip.123pan.cn/1813801926/Code/program/index.json"  # 更新网址
    UPDATE_INSTALLER_URL = "https://vip.123pan.cn/1813801926/Code/program/zbProgram_setup.exe"  # 更新安装包链接
    GITHUB_URL = "https://github.com/Ianzb/program/"  # Github网址
    MAIN_FILE_PATH = sys.argv[0]  # 程序主文件路径
    MAIN_FILE_NAME = os.path.basename(MAIN_FILE_PATH)  # 当前程序文件名称
    INSTALL_PATH = os.path.dirname(MAIN_FILE_PATH)  # 程序安装路径
    SOURCE_PATH = "source/img"  # 程序资源文件路径
    PROGRAM_PID = os.getpid()  # 程序pid
    USER_PATH = os.path.expanduser("~")  # 系统用户路径
    DATA_PATH = os.path.join(USER_PATH, "zb")  # 程序数据路径
    SETTING_FILE_PATH = os.path.join(DATA_PATH, "settings.json")  # 程序设置文件路径
    LOGGING_FILE_PATH = os.path.join(DATA_PATH, "logging.log")  # 程序日志文件路径
    ADDON_PATH = os.path.join(DATA_PATH, "addon")  # 程序插件路径
    ADDON_URL = "https://vip.123pan.cn/1813801926/Code/addon/addon.json"  # 插件信息网址
    STARTUP_ARGUMENT = sys.argv[1:]  # 程序启动参数
    UNINSTALL_FILE = "unins000.exe"  # 卸载程序
    REQUEST_HEADER = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36 Edg/124.0.0.0",
                      "zbprogram": VERSION}  # 程序默认网络请求头

    def __init__(self):
        # 创建数据目录
        if not os.path.exists(self.DATA_PATH):
            os.mkdir(self.DATA_PATH)

        # 切换运行路径
        os.chdir(self.INSTALL_PATH)

        # 设置任务栏
        import ctypes

        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(self.NAME)

        # 关闭SSL证书验证
        import ssl

        ssl._create_default_https_context = ssl._create_unverified_context()

        # 开发者插件目录切换
        if not self.isExe:
            self.ADDON_PATH = os.path.join(self.INSTALL_PATH, "../addon")

        # 添加插件路径
        sys.path.append(self.ADDON_PATH)

    @property
    def WINDOWS_VERSION(self) -> list:
        """
        获得windows版本
        @return: 返回列表，例：[10,0,22631]
        """
        version = sys.getwindowsversion()
        return [version.major, version.minor, version.build]

    @property
    def DESKTOP_PATH(self) -> str:
        """
        获得桌面路径
        @return: 桌面路径
        """
        import winreg
        return winreg.QueryValueEx(winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders"), "Desktop")[0]

    @property
    def DOWNLOAD_PATH(self) -> str:
        """
        获得下载路径
        @return: 桌面路径
        """
        import winreg
        return winreg.QueryValueEx(winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders"), "{374DE290-123F-4565-9164-39C4925E467B}")[0]

    @property
    def ICON(self) -> str:
        return program.source("program.png")

    @property
    def isStartup(self) -> bool:
        """
        判断程序是否为开机自启动
        @return: bool
        """
        return "startup" in self.STARTUP_ARGUMENT

    @property
    def isExe(self) -> bool:
        """
        判断程序是否为
        @return:
        """
        return ".exe" in self.MAIN_FILE_NAME

    def source(self, name: str) -> str:
        """
        快捷获取程序资源文件路径
        @param name: 文件名
        @return: 文件路径
        """
        return os.path.join(self.SOURCE_PATH, name)

    def cache(self, name: str) -> str:
        """
        快捷获取程序缓存文件路径
        @param name: 文件名
        @return: 文件路径
        """
        return os.path.join(self.DATA_PATH, "cache", name)

    def close(self):
        """
        关闭程序
        """
        sys.exit()

    def restart(self):
        """
        重启程序
        """
        os.popen(self.MAIN_FILE_PATH)
        sys.exit()

    def detectRepeatRun(self):
        """
        程序重复运行检测
        """
        value = False
        if os.path.exists(os.path.join(self.DATA_PATH, "zb.lock")):
            with open(os.path.join(self.DATA_PATH, "zb.lock"), "r+", encoding="utf-8") as file:
                pid = file.read().strip()
                if pid:
                    data = os.popen(f"tasklist |findstr {pid}")
                    if "zbProgram.exe" in data.read():
                        value = True
        if value:
            open(os.path.join(self.DATA_PATH, "zb.unlock"), "w").close()
            self.close()
        else:
            if os.path.exists(os.path.join(self.DATA_PATH, "zb.unlock")):
                os.remove(os.path.join(self.DATA_PATH, "zb.unlock"))
            with open(os.path.join(self.DATA_PATH, "zb.lock"), "w+", encoding="utf-8") as file:
                file.write(str(self.PROGRAM_PID))


program = Program()
