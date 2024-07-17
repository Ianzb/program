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
    VERSION = "4.1.0"  # 程序版本
    TITLE = f"{NAME} {VERSION}"  # 程序窗口标题
    URL = "https://ianzb.github.io/project/"  # 程序网址
    AUTHOR_NAME = "Ianzb"  # 作者名称
    AUTHOR_URL = "https://ianzb.github.io/"  # 作者网址
    UPDATE_URL = "https://vip.123pan.cn/1813801926/code/program/index.json"  # 更新网址
    UPDATE_INSTALLER_URL = "https://vip.123pan.cn/1813801926/code/program/zbProgram_setup.exe"  # 更新安装包链接
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
    ADDON_URL = "https://vip.123pan.cn/1813801926/code/addon/addon.json"  # 插件信息网址
    STARTUP_ARGUMENT = sys.argv[1:]  # 程序启动参数
    UNINSTALL_FILE = "unins000.exe"  # 卸载程序
    REQUEST_HEADER = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36 Edg/124.0.0.0",
                      "zbprogram": VERSION}  # 程序默认网络请求头
    ADDON_IMPORT = {}  # 导入的插件的对象
    ADDON_MAINPAGE = {}  # 导入的插件的主页

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

        if not self.isEXE:
            self.ADDON_PATH = os.path.join(self.INSTALL_PATH, "../addon")

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
    def isEXE(self) -> bool:
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
        return f.pathJoin(self.SOURCE_PATH, name)

    def cache(self, name: str) -> str:
        """
        快捷获取程序缓存文件路径
        @param name: 文件名
        @return: 文件路径
        """
        return f.pathJoin(self.DATA_PATH, "cache", name)

    def close(self):
        """
        关闭程序
        """
        sys.exit()

    def restart(self):
        """
        重启程序
        """
        f.cmd(self.MAIN_FILE_PATH)
        sys.exit()

    def detectRepeatRun(self):
        """
        程序重复运行检测
        """
        value = False
        if f.existPath(f.pathJoin(self.DATA_PATH, "zb.lock")):
            with open(f.pathJoin(self.DATA_PATH, "zb.lock"), "r+", encoding="utf-8") as file:
                pid = file.read().strip()
                if pid:
                    data = f.cmd(f"tasklist |findstr {pid}", True)
                    if "zbProgram.exe" in data:
                        value = True
        if value:
            open(f.pathJoin(self.DATA_PATH, "zb.unlock"), "w").close()
            logging.info(f"当前程序为重复运行，自动退出")
            self.close()
        else:
            f.delete(f.pathJoin(self.DATA_PATH, "zb.unlock"))
            with open(f.pathJoin(self.DATA_PATH, "zb.lock"), "w+", encoding="utf-8") as file:
                file.write(str(self.PROGRAM_PID))


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
        handler1.setFormatter(logging.Formatter("[%(levelname)s %(asctime)s %(filename)s %(process)d]:%(message)s"))

        handler2 = logging.FileHandler(program.LOGGING_FILE_PATH)
        handler2.setLevel(logging.DEBUG)
        handler2.setFormatter(logging.Formatter("[%(levelname)s %(asctime)s %(filename)s %(process)d]:%(message)s"))

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


class SettingFunctions:
    """
    设置相关函数
    """

    def __init__(self):
        self.DEFAULT_SETTING = {"theme": "Theme.AUTO",
                                "themeColor": "#0078D4",
                                "autoHide": True,
                                "downloadPath": program.DOWNLOAD_PATH,
                                "showWindow": False,
                                "micaEffect": True,
                                "showTray": True,
                                "hideWhenClose": True,
                                }
        self.file = open(program.SETTING_FILE_PATH, "a+t", encoding="utf-8")
        self.__read()

    def read(self, name: str):
        """
        读取设置
        @param name: 选项名称
        @return: 选项内容
        """
        logging.debug(f"读取设置{name}")
        try:
            return self.settings[name]
        except:
            self.settings[name] = self.DEFAULT_SETTING[name]
            self.__save()
            return self.DEFAULT_SETTING[name]

    def __read(self):
        self.file.seek(0)
        try:
            self.settings = json.loads(self.file.read())
        except:
            self.settings = self.DEFAULT_SETTING
            self.__save()

    def save(self, name: str, data):
        """
        保存设置
        @param name: 选项名称
        @param data: 选项数据
        """
        logging.debug(f"保存设置{name}：{data}")
        self.settings[name] = data
        self.__save()

    def __save(self):
        self.file.seek(0)
        self.file.truncate()
        self.file.write(json.dumps(self.settings))
        self.file.flush()

    def reset(self, name=None):
        """
        重置设置
        @param name: 选项名称
        """
        if name:
            self.save(name, self.DEFAULT_SETTING[name])
        else:
            self.settings = self.DEFAULT_SETTING
            self.__save()
            program.restart()

    def add(self, name: str, data):
        """
        添加设置项
        @param name: 选项名称
        @param data: 默认数据
        """
        self.DEFAULT_SETTING[name] = data
        if name not in self.settings.keys():
            self.save(name, data)

    def adds(self, data: dict):
        """
        批量添加设置项
        @param data: 数据
        """
        for k, v in data.items():
            self.add(k, v)


class ProcessFunctions:
    """
    数据处理函数
    """

    def clearString(self, data: str) -> str:
        """
        清理字符串\n\r空格符号
        @param data: 源字符串
        @return: 处理结果
        """
        data = data.replace(r"\n", "").replace(r"\r", "").replace(r"\t", "").strip()
        return data

    def removeIllegalPath(self, path: str, mode: int = 0) -> str:
        """
        去除路径中的非法字符
        @param path: 路径
        @param mode: 模式：0 全部替换 1 不替换斜杠
        @return: 去除非法字符后的字符串
        """
        import re
        if mode == 0:
            return re.sub(r'[\\\/:*?"<>|]', "", path)
        elif mode == 1:
            return re.sub(r'[*?"<>|]', "", path)

    def compareVersion(self, version1: str, version2: str) -> str:
        """
        比较版本号大小
        @param version1: 版本号1
        @param version2: 版本号2
        @return: 返回大的版本号
        """
        list1 = version1.split(".")
        list2 = version2.split(".")
        for i in range(len(list1)) if len(list1) < len(list2) else range(len(list2)):
            if int(list1[i]) == int(list2[i]):
                pass
            elif int(list1[i]) < int(list2[i]):
                return version2
            else:
                return version1
        if len(list1) >= len(list2):
            return version1
        else:
            return version2

    def sortVersion(self, version: list, reverse: bool = False, clear_repeat: bool = True) -> list:
        """
        版本号列表排序
        @param version: 版本号列表
        @param reverse: 是否逆序
        @param clear_repeat: 是否清除重复版本
        @return: 排序
        """
        if clear_repeat:
            version = list(set(version))
        version.sort(key=lambda x: tuple(int(v) for v in x.split(".")), reverse=reverse)
        return version

    def urlJoin(self, *args):
        """
        拼接网址
        @param args: 网址
        @return: 拼接结果
        """
        import urllib.parse
        data = ""
        for i in range(len(args)):
            data = urllib.parse.urljoin(data, args[i])
        return data

    def cmd(self, command: str, pause: bool = False) -> str:
        """
        简单的使用cmd
        @param command: 命令
        @param pause: 是否等待并返回输出结果
        @return: 输出结果
        """
        logging.debug(f"cmd执行命令{command}")
        value = os.popen(command)
        if pause:
            return value.read()

    def requestGet(self, url: str, header=None, timeout=(5, 10), is_text: bool = True, try_times: int = 5):
        """
        可重试的get请求
        @param url: 链接
        @param header: 请求头
        @param timeout: 超时
        @param is_text: 文本
        @param try_times: 重试次数
        @return:
        """
        logging.info(f"正在发送Get请求到{url}")
        for i in range(try_times):
            try:
                response = requests.get(url, headers=header, stream=True, timeout=timeout)
                if is_text:
                    response.encoding = "utf-8"
                    response = response.text
                else:
                    response = response.content
                return response
            except:
                continue

    def requestPost(self, url: str, json: dict, header=None, timeout=(5, 10), try_times: int = 5):
        """
        可重试的post请求
        @param url: 链接
        @param json: 发送数据
        @param header: 请求头
        @param timeout: 超时
        @param try_times: 重试次数
        @return:
        """
        logging.info(f"正在发送Post请求到{url}")
        for i in range(try_times):
            try:
                response = requests.post(url, headers=header, json=json, timeout=timeout)
                return response
            except:
                continue

    def numberAddUnit(self, value: int) -> str:
        """
        数字加单位
        @param value: 值
        @return: 字符串
        """
        units = ["", "万", "亿", "兆"]
        size = 10000.0
        for i in range(len(units)):
            if (value / size) < 1:
                return f"%.{i}f%s" % (value, units[i])
            value = value / size

    def fileSizeAddUnit(self, value: int) -> str:
        """
        文件比特大小加单位
        @param value: 值
        @return: 字符串
        """
        units = ["B", "KB", "MB", "GB", "TB", "PB"]
        size = 1024.0
        for i in range(len(units)):
            if (value / size) < 1:
                return "%.2f%s" % (value, units[i])
            value = value / size


class FileFunctions(ProcessFunctions):
    """
    文件处理函数
    """

    def __init__(self):
        super().__init__()

    def formatPath(self, path: str) -> str:
        """
        格式化路径
        @param path: 路径
        @return: 格式化结果
        """
        path = os.path.normpath(path).replace("//", r"\ "[:-1]).replace("\\ "[:-1], r"\ "[:-1])
        return path

    def pathJoin(self, *data) -> str:
        """
        拼接路径
        @param data: 多个字符串参数
        @return: 拼接后的字符串
        """
        path = ""
        for i in data:
            path = os.path.join(path, str(i))
        return self.formatPath(path)

    def isSameFile(self, path1: str, path2: str) -> bool:
        """
        判断路径是否相同
        @param path1: 路径1
        @param path2: 路径2
        @return: 是否相同
        """

        return self.formatPath(path1) == self.formatPath(path2)

    def existPath(self, path: str) -> bool:
        """
        文件是否存在
        @param path: 文件路径
        @return: bool
        """
        return os.path.exists(path)

    def isFile(self, path: str) -> bool:
        """
        文件是否为文件
        @param path: 文件路径
        @return: bool
        """
        if not self.existPath(path):
            return False
        return os.path.isfile(path)

    def isDir(self, path: str) -> bool:
        """
        文件是否为目录
        @param path: 文件路径
        @return: bool
        """
        if not self.existPath(path):
            return False
        return os.path.isdir(path)

    def setOnlyRead(self, path: str, enable: bool):
        """
        只读权限
        @param path: 文件路径
        @param enable: 启用/禁用
        """
        from stat import S_IREAD, S_IWRITE
        if self.isFile(path):
            if enable:
                os.chmod(path, S_IREAD)
            else:
                os.chmod(path, S_IWRITE)

    def delete(self, path: str, trash: bool = False, force: bool = False):
        """
        删除文件/目录
        @param path: 文件路径
        @param trash: 是否发送到回收站
        @param force: 是否使用命令行强制删除
        """
        try:
            if trash:
                if self.existPath(path):
                    send2trash(path)
            else:
                if self.isFile(path):
                    self.setOnlyRead(path, False)
                    os.remove(path)
                elif self.isDir(path):
                    shutil.rmtree(path)
        except Exception as ex:
            if self.isFile(path):
                self.cmd(f'del /F /Q "{path}"', True)
            elif self.isDir(path):
                self.cmd(f'rmdir /S /Q "{path}"', True)
            logging.warning(f"文件{path}无法删除{ex}")

    def getMD5(self, path: str) -> str:
        """
        获取文件MD5值
        @param path: 文件路径
        @return: MD5值
        """
        from hashlib import md5
        if self.isFile(path):
            data = open(path, "rb").read()
            return md5(data).hexdigest()

    def getSha1(self, path: str) -> str:
        """
        获取文件sha1值
        @param path: 文件路径
        @return: sha1值
        """
        from hashlib import sha1
        if self.isFile(path):
            data = open(path, "rb").read()
            return sha1(data).hexdigest()

    def splitPath(self, path: str, mode: int = 0) -> str:
        """
        分割路径信息
        @param path: 文件路径
        @param mode: 模式：0 文件完整名称 1 文件名称 2 文件扩展名 3 文件所在目录
        @return: 文件名信息
        """
        if mode == 0:
            return os.path.basename(path)
        if mode == 1:
            return os.path.splitext(os.path.basename(path))[0]
        if mode == 2:
            return os.path.splitext(os.path.basename(path))[1]
        if mode == 3:
            return os.path.dirname(path)

    def makeDir(self, path: str):
        """
        创建文件夹
        @param path: 文件路径
        """
        if not self.existPath(path):
            os.makedirs(path)

    def getSize(self, path: str) -> int:
        """
        获取文件/夹大小
        @param path: 文件路径
        @return: 文件大小
        """
        if self.isFile(path):
            return os.path.getsize(path)
        elif self.isDir(path):
            return sum([self.getSize(self.pathJoin(path, file)) for file in self.walkFile(path)])

    def walkDir(self, path: str, mode=0) -> list:
        """
        遍历子文件夹
        @param path: 文件夹路径
        @param mode: 模式：0 包含所有层级文件夹 1 仅包含次级文件夹
        @return: 文件夹路径列表
        """
        list1 = []
        if self.existPath(path):
            if mode == 0:
                if self.isDir(path):
                    paths = os.walk(path)
                    for path, dir_lst, file_lst in paths:
                        for dir_name in dir_lst:
                            list1.append(self.pathJoin(path, dir_name))
            if mode == 1:
                for i in os.listdir(path):
                    if self.isDir(self.pathJoin(path, i)):
                        list1.append(self.pathJoin(path, i))
            if not list1:
                list1 = []
        return list1

    def walkFile(self, path: str, mode=0) -> list:
        """
        遍历子文件
        @param path: 文件夹路径
        @param mode: 模式：0 包含所有层级文件 1 仅包含次级文件
        @return: 文件路径列表
        """
        list1 = []
        if self.existPath(path):
            if mode == 0:
                paths = os.walk(path)
                if self.isDir(path):
                    for path, dir_lst, file_lst in paths:
                        for file_name in file_lst:
                            list1.append(self.pathJoin(path, file_name))
            if mode == 1:
                for i in os.listdir(path):
                    if self.isFile(self.pathJoin(path, i)):
                        list1.append(self.pathJoin(path, i))
            if not list1:
                list1 = []
        return list1

    def copyFile(self, old: str, new: str):
        """
        复制文件
        @param old: 旧文件（夹）路径
        @param new: 新文件（夹）路径
        """
        if self.isFile(old):
            if self.isDir(new) or "." not in new:
                self.makeDir(new)
                new = self.pathJoin(new, self.splitPath(old))
            if self.existPath(new):
                i = 1
                while self.existPath(self.pathJoin(self.splitPath(new, 3), self.splitPath(new, 1) + " (" + str(i) + ")" + self.splitPath(new, 2))):
                    i = i + 1
                new = self.pathJoin(self.splitPath(new, 3), self.splitPath(new, 1) + " (" + str(i) + ")" + self.splitPath(new, 2))
            try:
                shutil.copy(self.pathJoin(old), self.pathJoin(new))
            except:
                self.setOnlyRead(old, False)
                shutil.copy(self.pathJoin(old), self.pathJoin(new))
        if self.isDir(old):
            if self.existPath(new):
                i = 1
                while self.existPath(new + " (" + str(i) + ")"):
                    i = i + 1
                new = new + " (" + str(i) + ")"
            try:
                shutil.copytree(self.pathJoin(old), self.pathJoin(new))
            except:
                try:
                    for i in self.walkFile(old):
                        self.setOnlyRead(i, False)
                    shutil.copytree(self.pathJoin(old), self.pathJoin(new))
                except:
                    pass

    def moveFile(self, old: str, new: str):
        """
        移动文件
        @param old: 旧文件（夹）路径
        @param new: 新文件（夹）路径
        """
        self.copyFile(old, new)
        if self.existPath(old):
            self.delete(old)

    def clearDir(self, path: str):
        """
        清空文件夹（无法删除则跳过）
        @param path: 路径
        """
        if self.isDir(path):
            for i in self.walkDir(path, 1):
                self.delete(i)
            for i in self.walkFile(path, 1):
                self.delete(i)

    def clearProgramCache(self):
        """
        清理本软件缓存
        """
        try:
            logging.reset()
            self.clearDir(f.pathJoin(program.DATA_PATH, "cache"))
        except:
            pass

    def showFile(self, path: str):
        """
        在文件资源管理器中打开目录
        @param path: 路径
        """
        if path and self.existPath(path):
            if f.isDir(path):
                os.startfile(path)
            else:
                f.cmd(f"explorer /select,{path}")

    def extractZip(self, path: str, goal: str, delete=False):
        """
        解压zip文件
        @param path: zip文件路径
        @param goal: 解压到的目录路径
        @param delete: 解压后删除
        """
        import zipfile
        if self.existPath(path):
            try:
                file = zipfile.ZipFile(path)
                file.extractall(goal)
                file.close()
                if delete:
                    self.delete(path)
                logging.debug(f"{path}解压成功")
            except Exception as ex:
                logging.warning(f"{path}解压失败{ex}")


class ProgramFunctions(FileFunctions):
    """
    应用函数
    """

    def __init__(self):
        super().__init__()

    def downloadFile(self, link: str, path: str):
        """
        下载文件
        @param link: 文件链接
        @param path: 下载路径
        """
        try:
            path = os.path.abspath(path)
            data = self.requestGet(link, program.REQUEST_HEADER, is_text=False, try_times=2)
            self.makeDir(self.splitPath(path, 3))
            with open(path, "wb") as file:
                file.write(data)
            logging.debug(f"文件{link}下载成功")
        except Exception as ex:
            logging.warning(f"文件{link}下载失败{ex}")

    def addToStartup(self, mode: bool = True):
        """
        添加开机自启动
        @param mode: True添加/False删除
        """
        import win32api, win32con
        key = win32api.RegOpenKey(win32con.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run", 0, win32con.KEY_ALL_ACCESS)
        try:
            if mode:
                win32api.RegSetValueEx(key, program.NAME, 0, win32con.REG_SZ, f"{program.MAIN_FILE_PATH} startup")
                win32api.RegCloseKey(key)
                logging.debug("启动项添加成功")
            else:
                win32api.RegDeleteValue(key, program.NAME)
                win32api.RegCloseKey(key)
                logging.debug("启动项删除成功")
        except Exception as ex:
            logging.warning(f"启动项编辑失败{ex}")

    def checkStartup(self):
        """
        检查开机自启动
        @return: 是否
        """
        import win32api, win32con
        try:
            key = win32api.RegOpenKeyEx(win32con.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run", 0, win32con.KEY_READ)
            win32api.RegQueryValueEx(key, program.NAME)
            win32api.RegCloseKey(key)
            return True
        except win32api.error:
            return False

    def getNewestVersion(self) -> str:
        """
        获取程序最新版本
        @return: 程序最新版本
        """
        response = self.requestGet(program.UPDATE_URL, program.REQUEST_HEADER, (15, 30))
        data = json.loads(response)["version"]
        logging.info(f"程序最新版本：{data}")
        return data

    def getAddonDict(self) -> dict:
        """
        获取插件字典
        @return: 字典
        """
        response = self.requestGet(program.ADDON_URL, program.REQUEST_HEADER, (15, 30))
        data = json.loads(response)
        logging.debug("插件信息获取成功")
        return data

    def getAddonInfo(self, url: str) -> dict:
        """
        获取指定插件信息
        @param url: 链接
        @return: 信息
        """
        if not url.endswith("/"):
            url += "/"
        response = self.requestGet(self.urlJoin(url, "addon.json"), program.REQUEST_HEADER, (15, 30))
        data = json.loads(response)
        data["url"] = url
        logging.debug(f"插件{data["name"]}信息获取成功")
        return data

    def downloadAddon(self, data: dict):
        """
        下载插件
        @param data: 插件信息
        """
        self.makeDir(self.pathJoin(program.ADDON_PATH, data["id"]))
        if "__init__.py" not in data["file"]:
            open(self.pathJoin(program.ADDON_PATH, data["id"], "__init__.py"), "w", encoding="utf-8").close()
        if "addon.json" not in data["file"]:
            data["file"].append("addon.json")
        for i in data["file"]:
            if self.splitPath(self.pathJoin(program.ADDON_PATH, data["id"], i), 2) == ".zip":
                self.downloadFile(self.urlJoin(data["url"], i), self.pathJoin(program.ADDON_PATH, i).replace("init.py", "__init__.py"))
                f.extractZip(self.pathJoin(program.ADDON_PATH, i), program.ADDON_PATH, True)
            else:
                self.downloadFile(self.urlJoin(data["url"], i), self.pathJoin(program.ADDON_PATH, data["id"], i).replace("init.py", "__init__.py"))
        logging.debug(f"插件{data["name"]}下载成功")

    def importAddon(self, path: str):
        """
        导入本体插件
        @param path: 目录
        """
        self.extractZip(path, program.cache(self.splitPath(path)))
        if self.existPath(self.pathJoin(program.cache(self.splitPath(path)), "addon.json")):
            with open(self.pathJoin(program.cache(self.splitPath(path)), "addon.json"), "r", encoding="utf-8") as file:
                data = json.loads(file.read())
            self.extractZip(path, self.pathJoin(program.ADDON_PATH, data[id]))
        else:
            for i in self.walkDir(program.cache(self.splitPath(path))):
                if self.existPath(self.pathJoin(i, "addon.json")):
                    with open(self.pathJoin(i, "addon.json"), "r", encoding="utf-8") as file:
                        data = json.loads(file.read())
                    break
            self.extractZip(path, program.ADDON_PATH)
        self.delete(program.cache(self.splitPath(path)))
        return data

    def getInstalledAddonInfo(self) -> dict:
        """
        获取本地插件信息
        @return: 信息
        """
        data = {}
        for i in f.walkDir(program.ADDON_PATH, 1):
            if f.existPath(f.pathJoin(i, "addon.json")):
                with open(f.pathJoin(i, "addon.json"), encoding="utf-8") as file:
                    data[f.splitPath(i)] = json.loads(file.read())
        return data


class DownloadFile:
    def __init__(self, link: str, path: str, wait: bool = True, suffix: str = "", header=None):
        """
        下载
        @param link: 链接
        @param path: 路径
        @param wait: 是否等待
        @param suffix: 临时后缀名
        @param header: 请求头
        """
        suffix = suffix.removeprefix(".")
        if f.isDir(path):
            path = f.pathJoin(path, link.split("/")[-1])
        if f.existPath(path):
            i = 1
            while f.existPath(f.pathJoin(f.splitPath(path, 3), f.splitPath(path, 1) + " (" + str(i) + ")" + f.splitPath(path, 2))) or f.existPath(
                    f.pathJoin(f.splitPath(path, 3), f.splitPath(path, 1) + " (" + str(i) + ")" + f.splitPath(path, 2) + ("." if suffix else "") + suffix)):
                i = i + 1
            path = f.pathJoin(f.splitPath(path, 3), f.splitPath(path, 1) + " (" + str(i) + ")" + f.splitPath(path, 2))
        self.path = path + ("." if suffix else "") + suffix
        logging.info(f"开始使用DownloadKit下载{link}到{self.path}")
        self.d = DownloadKit(f.splitPath(path, 3))
        self.file = self.d.add(link, rename=f.splitPath(path, 0), suffix=suffix, headers=header, allow_redirects=True, file_exists="skip")
        if wait:
            self.file.wait()

    def rate(self):
        return int(self.file.rate) if self.file.rate else 0

    def result(self):
        if self.file.result == "success":
            return True
        elif self.file.result == None:
            return None
        elif self.file.result == "skipped":
            return False

    def stop(self):
        self.file.cancel()
        self.file.session.close()
        self.d.cancel()

    def delete(self):
        self.file.del_file()


program = Program()
logging = LoggingFunctions()
setting = SettingFunctions()
f = ProgramFunctions()
