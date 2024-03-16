import functools
import json
import os
import sys
import shutil
import threading
import webbrowser
import time
import logging
from traceback import format_exception

try:
    import requests
    import bs4
    import lxml
    from PyQt5.Qt import *
    from qfluentwidgets import *
    from qfluentwidgets.components.material import *
    from qfluentwidgets import FluentIcon as FIF
    from DownloadKit import DownloadKit
except ImportError:
    os.popen("download.pyw error")


class Program:
    """
    程序信息
    """
    PROGRAM_NAME = "zb小程序"  # 程序名称
    PROGRAM_VERSION = "3.9.0"  # 程序版本
    PROGRAM_TITLE = f"{PROGRAM_NAME} {PROGRAM_VERSION}"  # 程序窗口标题
    AUTHOR_NAME = "Ianzb"  # 作者名称
    AUTHOR_URL = "https://ianzb.github.io/"  # 作者网址
    PROGRAM_URL = "https://ianzb.github.io/project/"  # 程序网址
    GITHUB_URL = "https://github.com/Ianzb/program/"  # Github网址
    PROGRAM_MAIN_FILE_PATH = sys.argv[0]  # 程序主文件路径
    PROGRAM_PATH = os.path.dirname(PROGRAM_MAIN_FILE_PATH)  # 程序安装路径
    SOURCE_PATH = os.path.join(PROGRAM_PATH, "img")  # 程序资源文件路径
    FILE_NAME = os.path.basename(PROGRAM_MAIN_FILE_PATH)  # 当前程序文件名称
    PROGRAM_PID = os.getpid()  # 程序pid
    USER_PATH = os.path.expanduser("~")  # 系统用户路径
    PROGRAM_DATA_PATH = os.path.join(USER_PATH, "zb")  # 程序数据路径
    SETTING_FILE_PATH = os.path.join(PROGRAM_DATA_PATH, "settings.json")  # 程序设置文件路径
    LOGGING_FILE_PATH = os.path.join(PROGRAM_DATA_PATH, "logging.log")  # 程序日志文件路径
    ADDON_PATH = os.path.join(PROGRAM_DATA_PATH, "addon")  # 程序插件路径
    ADDON_URL = "https://ianzb.github.io/program/addon/addon.json"  # 插件信息网址
    STARTUP_ARGUMENT = sys.argv[1:]  # 程序启动参数
    PYTHON_VERSION = sys.version[:sys.version.find(" ")]  # Python版本
    REQUEST_HEADER = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36 Edg/122.0.0.0",
                      "zbprogram": PROGRAM_VERSION}  # 程序默认网络请求头

    REQUIRE_LIB = ["PyQt-Fluent-Widgets[full]",
                   "qt5-tools",
                   "requests",
                   "bs4",
                   "lxml",
                   "pypiwin32",
                   "pandas",
                   "winshell",
                   "xmltodict",
                   "DownloadKit",
                   ]
    EXTRA_LIB = ["PyQt5",
                 "PyQt5-Frameless-Window",
                 "PyQt5-Qt5",
                 "PyQt5-sip",
                 "beautifulsoup4",
                 "certifi",
                 "charset-normalizer",
                 "click",
                 "colorama",
                 "colorthief",
                 "darkdetect",
                 "idna",
                 "numpy",
                 "pillow",
                 "python-dateutil",
                 "pytz",
                 "pywin32",
                 "qt5-applications",
                 "scipy",
                 "setuptools",
                 "six",
                 "some-package",
                 "soupsieve",
                 "tzdata",
                 "urllib3"]

    def __init__(self):
        # 创建数据目录
        if not os.path.exists(self.PROGRAM_DATA_PATH):
            os.mkdir(self.PROGRAM_DATA_PATH)
        # 切换运行路径
        os.chdir(self.PROGRAM_PATH)

        # 设置任务栏
        import ctypes

        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(self.PROGRAM_NAME)
        # 关闭SSL证书验证
        import ssl

        ssl._create_default_https_context = ssl._create_unverified_context()

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
    def PROGRAM_ICON(self) -> str:
        return program.source("program.png")

    @property
    def UPDATE_URL(self) -> str:
        """
        获得更新网址
        @return: 网址
        """
        if setting.read("updateChannel") == "正式版":
            return "https://vip.123pan.cn/1813801926/code/program/index.json"
        elif setting.read("updateChannel") == "抢先版":
            return "https://ianzb.github.io/program/release/index.json"
        elif setting.read("updateChannel") == "测试版":
            return "https://ianzb.github.io/program/beta/index.json"

    @property
    def isStartup(self) -> bool:
        """
        判断程序是否为开机自启动
        @return: bool
        """
        return "startup" in self.STARTUP_ARGUMENT

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
        return f.pathJoin(self.PROGRAM_DATA_PATH, "cache", name)

    def close(self):
        """
        关闭程序
        """
        sys.exit()

    def restart(self):
        """
        重启程序
        """
        f.cmd(self.PROGRAM_MAIN_FILE_PATH)
        sys.exit()

    def detectRepeatRun(self):
        """
        程序重复运行检测
        """
        value = False
        if f.existPath(f.pathJoin(self.PROGRAM_DATA_PATH, "zb.lock")):
            with open(f.pathJoin(self.PROGRAM_DATA_PATH, "zb.lock"), "r+", encoding="utf-8") as file:
                pid = file.read().strip()
                if pid:
                    if "python" in f.cmd(f"tasklist |findstr {pid}", True):
                        value = True
        if value:
            open(f.pathJoin(self.PROGRAM_DATA_PATH, "zb.unlock"), "w").close()
            logging.info(f"当前程序为重复运行，自动退出")
            self.close()
        else:
            f.delete(f.pathJoin(self.PROGRAM_DATA_PATH, "zb.unlock"))
            with open(f.pathJoin(self.PROGRAM_DATA_PATH, "zb.lock"), "w+", encoding="utf-8") as file:
                file.write(str(self.PROGRAM_PID))


class LoggingFunctions:
    """
    日志相关函数
    """

    def __init__(self):
        self.log = logging.getLogger(__name__)
        self.log.setLevel(logging.DEBUG)
        handler1 = logging.StreamHandler(sys.stderr)
        handler1.setLevel(logging.DEBUG)
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
                                "autoStartup": False,
                                "autoHide": True,
                                "autoUpdate": False,
                                "sortPath": "",
                                "wechatPath": "",
                                "downloadPath": program.DOWNLOAD_PATH,
                                "showWindow": False,
                                "sortBlacklist": [],
                                "updateChannel": "正式版",
                                "micaEffect": True,
                                "showTray": True,
                                "hideWhenClose": True,
                                "sortFolder": [],
                                "sortFormat": {"PPT": [".ppt", ".pptx"],
                                               "文档": [".doc", ".docx", ".txt", ".pdf"],
                                               "表格": [".xls", ".xlsx", ".xlsm", ".xlsb", ".xlt", ".csv"],
                                               "图片": [".png", ".jpg", ".jpeg", ".webp", ".gif", ".tif", ".tga", ".bmp", ".dds", ".svg", ".eps", ".hdr", ".raw", ".exr", ".psd"],
                                               "音频": [".mp3", ".wav", ".ogg", ".wma", ".ape", ".flac", ".aac"],
                                               "视频": [".mp4", ".flv", ".mov", ".avi", ".mkv", ".wmv"],
                                               "压缩包": [".zip", ".rar", ".7z", ".tar", ".gz", ".bz2"],
                                               "镜像": [".iso", ".img", ".bin"],
                                               "安装包": [".exe", ".msi"]
                                               }
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
        data = data.replace("\n", "").replace("\r", "").replace(" ", "")
        return data

    def xmlToJson(self, data: str) -> dict:
        """
        xml转json
        @param data: xml字符串
        @return: 字典格式json数据
        """
        import xmltodict
        data = xmltodict.parse(data)
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
        @param pause: 是否返回输出结果
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
            path = os.path.join(path, i)
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

    def delete(self, path: str):
        """
        删除文件/目录
        @param path: 文件路径
        """
        try:
            if self.isFile(path):
                self.setOnlyRead(path, False)
                os.remove(path)
            if self.isDir(path):
                shutil.rmtree(path)
        except Exception as ex:
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

    def getHash(self, path: str) -> str:
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
        获取文件大小
        @param path: 文件路径
        @return: 文件大小
        """
        if self.isFile(path):
            return os.path.getsize(path)

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

    def clearEmptyFile(self, path: str):
        """
        删除空文件
        @param path: 文件夹路径
        """
        if self.isDir(path):
            paths = self.walkFile(path, 1)
            if paths:
                for i in paths:
                    if self.getSize(i) == 0:
                        self.delete(i)

    def clearEmptyDir(self, path):
        """
        删除空文件夹
        @param path: 文件夹路径
        """
        if self.isDir(path):
            paths = self.walkDir(path, 1)
            if paths:
                for i in paths:
                    try:
                        os.rmdir(i)
                    except:
                        pass

    def clearRepeatFile(self, path: str):
        """
        清理重复文件
        @param path: 文件夹路径
        """
        if self.isDir(path):
            sizes = []
            names = self.walkFile(path)
            if not names:
                return
            names.sort(key=lambda i: len(i))
            for i in names:
                if self.getSize(i) / 1024 / 1024 >= 128:
                    continue
                md5 = self.getMD5(i)
                if md5 in sizes:
                    self.delete(i)
                else:
                    sizes.append(md5)

    def clearFile(self, path: str):
        """
        清理文件夹3合1
        @param path: 文件夹路径
        """
        try:
            self.clearEmptyFile(path)
            self.clearEmptyDir(path)
            self.clearRepeatFile(path)
            logging.debug(f"成功清理{path}文件夹")
        except Exception as ex:
            logging.warning(f"无法清理{path}文件夹{ex}")

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

    def belongDir(self, path: str, parent: str) -> bool:
        """
        文件夹是否包含
        @param path: 子文件夹
        @param parent: 母文件夹
        @return: 是否
        """
        path = os.path.abspath(path)
        parent = os.path.abspath(parent)
        try:
            data = os.path.commonpath([parent]) == os.path.commonpath([parent, path])
        except:
            data = False
        return data

    def sortDir(self, old: str, new: str, mode: int = 0):
        """
        整理文件
        @param old: 旧文件夹路径
        @param new: 新文件夹路径
        @param mode: 模式：0 全部整理 1 仅文件 2 仅文件夹
        """

        try:
            if mode in [0, 1]:
                file_list = self.walkFile(old, 1)
                if file_list:
                    for i in file_list:
                        for j in range(len(setting.read("sortFormat").values())):
                            if self.splitPath(i, 2).lower() in list(setting.read("sortFormat").values())[j]:
                                if self.splitPath(i, 0) not in self.getSortBlacklist():
                                    self.moveFile(i, self.pathJoin(new, list(setting.read("sortFormat").keys())[j]))
            if mode in [0, 2]:
                file_list = self.walkDir(old, 1)
                if file_list:
                    for i in file_list:
                        if self.splitPath(i, 0) not in self.getSortBlacklist():
                            self.moveFile(i, self.pathJoin(new, "文件夹", self.splitPath(i, 0)))
            logging.debug(f"成功整理{old}文件夹")
        except Exception as ex:
            logging.warning(f"无法整理{old}文件夹{ex}")

    def sortWechatFiles(self):
        """
        整理微信文件
        """
        try:
            list1 = []
            list2 = []
            for i in self.walkDir(setting.read("wechatPath"), 1):
                if self.existPath(self.pathJoin(i, "FileStorage/File")):
                    list1.append(self.pathJoin(i, "FileStorage/File"))
            for i in list1:
                if self.walkDir(i, 1) == None:
                    return
                list2 = list2 + self.walkDir(i, 1)
            for i in list2:
                self.sortDir(i, setting.read("sortPath"))
            for i in list1:
                self.sortDir(i, setting.read("sortPath"), 1)
            logging.debug("成功整理微信文件")
        except Exception as ex:
            logging.warning(f"无法整理微信文件{ex}")

    def clearSystemCache(self):
        """
        清理系统缓存
        """
        try:
            self.clearDir(os.getenv("TEMP"))
        except:
            pass

    def clearProgramCache(self):
        """
        清理本软件缓存
        """
        try:
            logging.reset()
            self.clearDir(f.pathJoin(program.PROGRAM_DATA_PATH, "cache"))
        except:
            pass

    def clearRubbish(self):
        """
        清空回收站
        """
        import winshell
        try:
            winshell.recycle_bin().empty(confirm=False, show_progress=False, sound=False)
            logging.debug("成功清空回收站")
        except Exception as ex:
            logging.warning(f"无法清空回收站{ex}")

    def getSortBlacklist(self):
        """
        获取整理文件黑名单
        @return: 整理文件黑名单列表
        """
        self.makeDir(setting.read("sortPath"))
        data = setting.read("sortBlacklist")

        if self.isSameFile(setting.read("sortPath"), program.DESKTOP_PATH):
            data += list(setting.read("sortFormat").keys()) + ["文件夹"]
        elif f.belongDir(setting.read("sortPath"), program.DESKTOP_PATH):
            dirs = self.walkDir(program.DESKTOP_PATH, 1)
            for i in dirs:
                if f.belongDir(setting.read("sortPath"), i):
                    data.append(self.splitPath(i))
        return data

    def showFile(self, path: str):
        """
        在文件资源管理器中打开目录
        @param path: 路径
        """
        if path and self.existPath(path):
            if f.isDir(path):
                os.startfile(path)
            else:
                f.cmd(f"explorer /select {path}")

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

    def pipTest(self):
        """
        测试pip是否生效
        @return: 是否生效
        """
        return "pip <command> [options]" in self.cmd("pip", True)

    def pipInstall(self, lib_name: str | list):
        """
        pip安装运行库
        @param lib_name: 运行库名称
        """
        logging.debug(f"pip安装{lib_name}")
        if type(lib_name) is str:
            self.cmd(f"pip install {lib_name} -i https://pypi.tuna.tsinghua.edu.cn/simple some-package", True)
        elif type(lib_name) is list:
            for i in lib_name:
                self.cmd(f"pip install {i} -i https://pypi.tuna.tsinghua.edu.cn/simple some-package", True)

    def pipUpdate(self, lib_name: str | list):
        """
        pip更新运行库
        @param lib_name: 运行库名称
        """
        logging.debug(f"pip更新{lib_name}")
        if type(lib_name) is str:
            self.cmd(f"pip install --upgrade {lib_name} -i https://pypi.tuna.tsinghua.edu.cn/simple some-package", True)
        elif type(lib_name) is list:
            for i in lib_name:
                self.cmd(f"pip install --upgrade {i} -i https://pypi.tuna.tsinghua.edu.cn/simple some-package", True)

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

    def createShortcut(self, old: str, new: str, icon: str, arguments: str = ""):
        """
        创建快捷方式
        @param old: 源文件路径
        @param new: 新文件路径
        @param icon: 图标
        @param arguments: 参数
        """
        try:
            import win32com.client
            if not new.endswith(".lnk"):
                new += ".lnk"
            shell = win32com.client.Dispatch("WScript.Shell")
            shortcut = shell.CreateShortCut(new)
            shortcut.Targetpath = old
            shortcut.IconLocation = icon
            shortcut.Arguments = arguments
            shortcut.save()
            logging.debug(f"快捷方式{new}添加成功")
        except Exception as ex:
            logging.warning(f"快捷方式添加失败{ex}")

    def addToStartup(self, name: str, path: str, mode: bool = True):
        """
        添加开机自启动
        @param name: 启动项名字
        @param path: 文件路径
        @param mode: True添加/False删除
        """
        import win32api, win32con
        key = win32api.RegOpenKey(win32con.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run", 0, win32con.KEY_ALL_ACCESS)
        try:
            if mode:
                win32api.RegSetValueEx(key, name, 0, win32con.REG_SZ, f"{path} startup")
                win32api.RegCloseKey(key)
                logging.debug("启动项添加成功")
            else:
                win32api.RegDeleteValue(key, name)
                win32api.RegCloseKey(key)
                logging.debug("启动项删除成功")
        except Exception as ex:
            logging.warning(f"启动项编辑失败{ex}")

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
        @param data: 链接
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
        for i in data["lib"]:
            self.pipInstall(i)
            self.pipUpdate(i)
        logging.debug(f"插件{data["name"]}下载成功")

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

    def checkInternet(self, link: str = "https://www.baidu.com/", header=None):
        """
        测试链接是否有效
        @param link: 链接
        @param header: 请求头
        @return: 是否连接
        """
        try:
            response = requests.get(link, headers=header, stream=True)
            logging.debug(f"访问{link}的结果为{response.status_code == 200}")
            return response.status_code == 200
        except:
            logging.warning(f"访问{link}失败")
            return False


class Functions(ProgramFunctions):
    """
    程序相关函数
    """

    def __init__(self):
        super().__init__()

    def changeList(self, data: list, index: dict):
        """
        批量替换元素
        @param data: 数据列表
        @param index: 替换字典{键值替换键名}
        @return:
        """
        for i in range(len(data)):
            for k, v in index.items():
                data[i] = data[i].replace(k, v)
        return data

    def getMC(self) -> str:
        """
        获取Minecraft最新版本
        @return: 字符串
        """
        useful = ["{{v|java}}",
                  "{{v|java-experimental}}",
                  "{{v|java-snap}}",
                  "{{v|bedrock}}",
                  "{{v|bedrock-beta}}",
                  "{{v|bedrock-preview}}",
                  "{{v|dungeons}}",
                  "{{v|legends-win}}",
                  "{{v|launcher}}",
                  "{{v|launcher-beta}}",
                  "{{v|education}}",
                  "{{v|education-beta}}",
                  "{{v|china-win}}",
                  "{{v|china-android}}",
                  ]
        try:
            response = self.requestGet("https://zh.minecraft.wiki/w/Template:Version", timeout=(5, 10))
        except Exception as ex:
            logging.warning(f"无法连接至Minecraft Wiki服务器{ex}")
            return "无法连接至服务器"
        soup = bs4.BeautifulSoup(response, "lxml")
        data = soup.find_all(name="td")
        l1 = [n.text.replace("\n", "") for n in data]
        v1 = l1[::3]
        v2 = l1[1::3]
        v3 = l1[2::3]
        str1 = ""
        v1 = self.changeList(v1, {"（": "", "）": ""})
        for i in range(len(v1)):
            if v1[i][-1] == "版":
                v1[i] = v1[i] + "正式版"
            if v3[i] == "{{v|china-win}}":
                v1[i] = "中国版端游"
            if v3[i] == "{{v|china-android}}":
                v1[i] = "中国版手游"
            if v3[i] == "{{v|legends-win}}":
                v1[i] = "我的世界：传奇"
            if v3[i] == "{{v|dungeons}}":
                v1[i] = "我的世界：地下城"
            if v3[i] in useful and v2[i] != "":
                str1 += v1[i] + "版本：" + v2[i] + "\n"
        logging.debug("成功获取我的世界最新版本")
        return str1


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
            while f.existPath(f.pathJoin(f.splitPath(path, 3), f.splitPath(path, 1) + " (" + str(i) + ")" + f.splitPath(path, 2))) or f.existPath(f.pathJoin(f.splitPath(path, 3), f.splitPath(path, 1) + " (" + str(i) + ")" + f.splitPath(path, 2) + ("." if suffix else "") + suffix)):
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
f = Functions()
