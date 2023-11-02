import json
import os
import sys
import shutil
import threading
import webbrowser
import time


class MyThread(threading.Thread):
    """
    多线程优化
    """

    def __init__(self, func, *args):
        super().__init__()

        self.func = func
        self.args = args

        self.daemon = True
        self.start()

    def run(self):
        self.func(*self.args)


class ProgramInit():
    """
    zb小程序信息类-处理信息
    """
    PROGRAM_NAME = "zb小程序"  # 程序名称
    PROGRAM_VERSION = "3.0.0"  # 程序版本
    PROGRAM_TITLE = f"{PROGRAM_NAME} {PROGRAM_VERSION}"  # 程序窗口标题
    AUTHOR_NAME = "Ianzb"  # 作者名称
    AUTHOR_URL = "https://ianzb.github.io/"  # 作者网址
    PROGRAM_URL = "https://ianzb.github.io/program/"  # 程序网址
    GITHUB_URL = "https://github.com/Ianzb/program/"  # Github网址
    UPDATE_URL = "https://ianzb.github.io/program/Windows/index.json"  # 更新网址
    PROGRAM_MAIN_FILE_PATH = sys.argv[0]  # 程序主文件路径
    PROGRAM_PATH = os.path.dirname(PROGRAM_MAIN_FILE_PATH)  # 程序安装路径
    SOURCE_PATH = os.path.join(PROGRAM_PATH, "img")  # 程序资源文件路径
    FILE_NAME = os.path.basename(PROGRAM_MAIN_FILE_PATH)  # 当前程序文件名称
    PROGRAM_PID = os.getpid()  # 程序pid
    USER_PATH = os.path.expanduser("~")  # 系统用户路径
    PROGRAM_DATA_PATH = os.path.join(USER_PATH, "zb")  # 程序数据路径
    SETTING_FILE_PATH = os.path.join(PROGRAM_DATA_PATH, "settings.json")  # 程序设置文件路径
    STARTUP_ARGUMENT = sys.argv[1:]  # 程序启动参数
    REQUEST_HEADER = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36 Edg/118.0.2088.76"}  # 程序默认网络请求头

    REQUIRE_LIB = ["PyQt-Fluent-Widgets",
                   "qt5_tools",
                   "requests",
                   "bs4",
                   "lxml",
                   "pypiwin32",
                   "pandas",
                   "winshell",
                   ]

    def __init__(self):
        pass

    @property
    def DESKTOP_PATH(self) -> str:
        """
        获得桌面路径
        :return: 桌面路径
        """
        import winreg
        return winreg.QueryValueEx(winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders"), "Desktop")[0]

    @property
    def isStartup(self) -> bool:
        """
        判断程序是否为开机自启动
        :return: bool
        """
        return "startup" in self.STARTUP_ARGUMENT

    def source(self, name: str) -> str:
        """
        快捷获取程序资源文件路径
        :param name: 文件名
        :return: 文件路径
        """
        return f.pathJoin(self.SOURCE_PATH, name)


program = ProgramInit()


class SettingFunctions():
    """
    设置相关函数
    """

    def __init__(self):
        pass

    def reload(self):
        """
        重新读取设置文件
        """
        if not f.exists(program.SETTING_FILE_PATH):
            with open(program.SETTING_FILE_PATH, "w", encoding="utf-8") as file:
                file.write("{}")
        else:
            with open(program.SETTING_FILE_PATH, "r+", encoding="utf-8") as file:
                if not file.read():
                    file.write("{}")

    def read(self, name: str):
        """
        读取设置
        :param name: 选项名称
        :return: 选项内容
        """
        self.reload()
        with open(program.SETTING_FILE_PATH, "r+", encoding="utf-8") as file:
            settings = json.loads(file.read())
        try:
            return settings[name]
        except:
            if name == "theme":
                setting.save("theme", "Theme.AUTO")
                return "Theme.AUTO"
            if name == "themeColor":
                setting.save("themeColor", "#0078D4")
                return "#0078D4"
            if name == "autoStartup":
                setting.save("autoStartup", False)
                return False
            if name == "autoHide":
                setting.save("autoHide", True)
                return True
            if name == "autoUpdate":
                setting.save("autoUpdate", False)
                return False
            if name == "pid":
                setting.save("pid", "0")
                return 0
            if name == "sortPath":
                setting.save("sortPath", "")
                return ""
            if name == "wechatPath":
                setting.save("wechatPath", "")
                return ""

    def save(self, name: str, data):
        """
        保存设置
        :param name: 选项名称
        :param data: 选项数据
        """
        self.reload()
        with open(program.SETTING_FILE_PATH, "r+", encoding="utf-8") as file:
            settings = json.loads(file.read())
        settings[name] = data
        with open(program.SETTING_FILE_PATH, "w", encoding="utf-8") as file:
            file.write(json.dumps(settings))


setting = SettingFunctions()


class Functions():
    """
    程序相关函数
    """
    names = ["PPT",
             "文档",
             "表格",
             "图片",
             "音视频",
             "压缩包",
             ]
    ends = [[".ppt", ".pptx"],
            [".doc", ".docx"".txt", ".pdf", ".json"],
            [".xls", ".xlsx", ".xlt", ".csv"],
            [".png", ".jpg", ".jpeg", ".webp", ".gif"],
            [".mp3", ".mp4", ".wav", ".ogg", ".flv"],
            [".zip", ".rar", ".7z"],
            ]

    def __init__(self):
        pass

    def pathJoin(self, *data) -> str:
        """
        拼接路径
        :param data: 多个字符串参数
        :return: 拼接后的字符串
        """
        path = ""
        for i in data:
            path = os.path.join(path, i)
        path = path.replace("//", r"\ "[:-1]).replace(r"\\ "[:-1], r"\ "[:-1]).replace("\/", r"\ "[:-1]).replace("/\ "[:-1], r"\ "[:-1]).replace("/", r"\ "[:-1])
        return path

    def exists(self, path: str) -> bool:
        """
        文件是否存在
        :param path: 文件路径
        :return: bool
        """
        return os.path.exists(path)

    def isFile(self, path: str) -> bool:
        """
        文件是否为文件
        :param path: 文件路径
        :return: bool
        """
        if not self.exists(path):
            return False
        return os.path.isfile(path)

    def isDir(self, path: str) -> bool:
        """
        文件是否为目录
        :param path: 文件路径
        :return: bool
        """
        if not self.exists(path):
            return False
        return os.path.isdir(path)

    def onlyRead(self, path: str, enable: bool):
        """
        只读权限
        :param path: 文件路径
        :param enable: 是否开启
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
        :param path: 文件路径
        """
        if self.isFile(path):
            self.onlyRead(path, False)
            os.remove(path)
        if self.isDir(path):
            shutil.rmtree(path)

    def getMD5(self, path: str) -> str:
        """
        获取文件MD5值
        :param path: 文件路径
        :return: MD5值
        """
        from hashlib import md5
        if self.isFile(path):
            with open(path, "rb") as file:
                data = file.read()
            return md5(data).hexdigest()

    def baseName(self, path: str, mode: int = 0) -> str:
        """
        获取文件名信息
        :param path: 文件路径
        :param mode: 模式：0 文件完整名称 1 文件名称 2 文件扩展名 3 文件所在目录
        :return: 文件名信息
        """
        if self.isFile(path):
            if mode == 0:
                return os.path.basename(path)
            if mode == 1:
                return os.path.splitext(os.path.basename(path))[0]
            if mode == 2:
                return os.path.splitext(os.path.basename(path))[1]
            if mode == 3:
                return os.path.dirname(path)

    def mkDir(self, path: str):
        """
        创建文件夹
        :param path: 文件路径
        """
        if not self.exists(path):
            os.makedirs(path)

    def getSize(self, path: str) -> int:
        """
        获取文件大小
        :param path: 文件路径
        :return: 文件大小
        """
        if self.isFile(path):
            return os.path.getsize(path)

    def walkDir(self, path: str, mode=0) -> list:
        """
        遍历子文件夹
        :param path: 文件夹路径
        :param mode: 模式：0 包含所有层级文件夹 1 仅包含次级文件夹
        :return: 文件夹路径列表
        """
        list = []
        if mode == 0:
            if self.isDir(path):
                paths = os.walk(path)
                for path, dir_lst, file_lst in paths:
                    for dir_name in dir_lst:
                        list.append(self.pathJoin(path, dir_name))
        if mode == 1:
            for i in os.listdir(path):
                if self.isDir(self.pathJoin(path, i)):
                    list.append(self.pathJoin(path, i))
        if not list:
            list = []
        return list

    def walkFile(self, path: str, mode=0) -> list:
        """
        遍历子文件
        :param path: 文件夹路径
        :param mode: 模式：0 包含所有层级文件 1 仅包含次级文件
        :return: 文件路径列表
        """
        list = []
        if mode == 0:
            paths = os.walk(path)
            if self.isDir(path):
                for path, dir_lst, file_lst in paths:
                    for file_name in file_lst:
                        list.append(self.pathJoin(path, file_name))
        if mode == 1:
            for i in os.listdir(path):
                if self.isFile(self.pathJoin(path, i)):
                    list.append(self.pathJoin(path, i))
        if not list:
            list = []
        return list

    def copy(self, old: str, new: str):
        """
        复制文件
        :param old: 旧文件（夹）路径
        :param new: 新文件（夹）路径
        """
        if self.isFile(old):
            if self.isDir(new) or "." not in new:
                self.mkDir(new)
                new = self.pathJoin(new, self.baseName(old))
            if self.exists(new):
                i = 1
                while self.exists(self.pathJoin(self.baseName(new, 3), self.baseName(new, 1) + " (" + str(i) + ")" + self.baseName(new, 2))):
                    i = i + 1
                new = self.pathJoin(self.baseName(new, 3), self.baseName(new, 1) + " (" + str(i) + ")" + self.baseName(new, 2))
            try:
                shutil.copy(self.pathJoin(old), self.pathJoin(new))
            except:
                self.onlyRead(old, False)
                shutil.copy(self.pathJoin(old), self.pathJoin(new))
        if self.isDir(old):
            if self.exists(new):
                i = 1
                while self.exists(new + " (" + str(i) + ")"):
                    i = i + 1
                new = new + " (" + str(i) + ")"
            try:
                shutil.copytree(self.pathJoin(old), self.pathJoin(new))
            except:
                try:
                    for i in self.walkFile(old):
                        self.onlyRead(i, False)
                    shutil.copytree(self.pathJoin(old), self.pathJoin(new))
                except:
                    pass

    def move(self, old: str, new: str):
        """
        移动文件
        :param old: 旧文件（夹）路径
        :param new: 新文件（夹）路径
        """
        self.copy(old, new)
        if self.exists(old):
            self.delete(old)

    def clearEmptyFile(self, path: str):
        """
        删除空文件
        :param path: 文件夹路径
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
        :param path: 文件夹路径
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
        :param path: 文件夹路径
        """
        if self.isDir(path):
            sizes = []
            names = self.walkFile(path)
            if not names:
                return
            names.sort(key=lambda i: len(i))
            for i in names:
                md5 = self.getMD5(i)
                if md5 in sizes:
                    self.delete(i)
                else:
                    sizes.append(md5)

    def clearFile(self, path: str):
        """
        清理文件夹3合1
        :param path: 文件夹路径
        """
        self.clearEmptyFile(path)
        self.clearEmptyDir(path)
        self.clearRepeatFile(path)

    def sortDir(self, old: str, new: str, mode: int = 0):
        """
        整理文件
        :param old: 旧文件夹路径
        :param new: 新文件夹路径
        :param mode: 模式：0 全部整理 1 仅文件 2 仅文件夹
        """
        if mode in [0, 1]:
            list = self.walkFile(old, 1)
            if list != []:
                for i in list:
                    for j in range(len(self.ends)):
                        if self.baseName(i, 2) in self.ends[j]:
                            self.move(i, self.pathJoin(new, self.names[j]))
        if mode in [0, 2]:
            list = self.walkDir(old, 1)
            if list != []:
                for i in list:
                    if i[i.rfind("\ "[:-1]) + 1:] not in ["软件"]:
                        self.move(i, self.pathJoin(new, "文件夹", i[i.rfind("\ "[:-1]) + 1:]))
        for i in self.names + ["文件夹"]:
            self.clearFile(self.pathJoin(new, i))
        self.clearEmptyDir(new)

    def sortWechatFiles(self):
        """
        整理微信文件
        """
        try:
            list = []
            list2 = []
            for i in self.walkDir(setting.read("wechatPath"), 1):
                if self.exists(self.pathJoin(i, "FileStorage/File")):
                    list.append(self.pathJoin(i, "FileStorage/File"))
            for i in list:
                if self.walkDir(i, 1) == None:
                    return
                list2 = list2 + self.walkDir(i, 1)
            for i in list2:
                self.sortDir(i, setting.read("sortPath"))
            for i in list:
                self.sortDir(i, setting.read("sortPath"), 1)
        except:
            pass

    def sortDesktopFiles(self):
        """
        整理桌面文件
        """
        self.sortDir(program.DESKTOP_PATH, setting.read("sortPath"))

    def clearCache(self):
        """
        清理系统缓存
        """
        try:
            path = os.getenv("TEMP")
            for i in self.walkDir(path, 1):
                try:
                    self.delete(i)
                except:
                    pass
            for i in self.walkFile(path, 1):
                try:
                    self.delete(i)
                except:
                    pass
        except:
            pass

    def clearRubbish(self):
        """
        清空回收站
        """
        import winshell
        try:
            winshell.recycle_bin().empty(confirm=False, show_progress=False, sound=False)
        except:
            pass

    def urlJoin(self, *args):
        """
        拼接网址
        :param args: 网址
        :return: 拼接结果
        """
        import urllib.parse
        data = ""
        for i in range(len(args)):
            data = urllib.parse.urljoin(data, args[i])
        return data

    def cmd(self, command: str, pause: bool = False) -> str:
        """
        简单的使用cmd
        :param command: 命令
        :param pause: 是否返回输出结果
        :return: 输出结果
        """
        value = os.popen(command)
        if pause:
            return value.read()

    def pipInstall(self, lib_name: str | list):
        """
        pip安装运行库
        :param lib_name: 运行库名称
        """
        if type(lib_name) == str:
            self.cmd(f"pip install {lib_name} -i https://pypi.tuna.tsinghua.edu.cn/simple some-package", True)
        elif type(lib_name) == list:
            for i in lib_name:
                self.cmd(f"pip install {i} -i https://pypi.tuna.tsinghua.edu.cn/simple some-package", True)

    def pipUpdate(self, lib_name: str | list):
        """
        pip更新运行库
        :param lib_name: 运行库名称
        """
        if type(lib_name) == str:
            self.cmd(f"pip install --upgrade {lib_name} -i https://pypi.tuna.tsinghua.edu.cn/simple some-package", True)
        elif type(lib_name) == list:
            for i in lib_name:
                self.cmd(f"pip install --upgrade {i} -i https://pypi.tuna.tsinghua.edu.cn/simple some-package", True)

    def changeList(self, data: list, index: dict):
        """
        批量替换元素
        :param data: 数据列表
        :param index: 替换字典{键值替换键名}
        :return:
        """
        for i in range(len(data)):
            for k, v in index.items():
                data[i] = data[i].replace(k, v)
        return data

    def getMC(self) -> str:
        """
        获取Minecraft最新版本
        :return: 字符串
        """
        import requests, bs4, lxml
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
            response = requests.get("https://minecraft.fandom.com/zh/wiki/Template:Version#table", headers=program.REQUEST_HEADER, stream=True, timeout=(5, 10)).text
        except:
            try:
                response = requests.get("https://wiki.biligame.com/mc/%E6%A8%A1%E6%9D%BF:Version#table", headers=program.REQUEST_HEADER, stream=True, timeout=(60, 600)).text
            except:
                return "无法连接至服务器"
        soup = bs4.BeautifulSoup(response, "lxml")
        data1 = soup.find_all(name="td")
        l1 = [n.text.replace("\n", "") for n in data1]
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
        return str1

    def downloadFile(self, link: str, path: str):
        """
        下载文件
        :param link: 文件链接
        :param path: 下载路径
        """
        path = os.path.abspath(path)
        import requests
        data = requests.get(link, headers=program.REQUEST_HEADER).content
        self.mkDir(self.baseName(path, 3))
        with open(path, "wb") as file:
            file.write(data)

    def createShortcut(self, old: str, new: str = program.DESKTOP_PATH, icon: str = "", arguments: str = ""):
        """
        创建快捷方式
        :param old: 源文件路径
        :param new: 新文件路径
        :param icon: 图标
        :param arguments: 参数
        """
        import win32com.client
        if not new.endswith(".lnk"):
            new += ".lnk"
        shell = win32com.client.Dispatch("WScript.Shell")
        shortcut = shell.CreateShortCut(new)
        shortcut.Targetpath = old
        shortcut.IconLocation = icon
        shortcut.Arguments = arguments
        shortcut.save()

    def addToStartMenu(self):
        """
        添加开始菜单快捷方式
        """
        self.createShortcut(program.PROGRAM_MAIN_FILE_PATH, f.pathJoin(program.USER_PATH, "AppData\Roaming\Microsoft\Windows\Start Menu\Programs", "zb小程序"), program.source("logo.ico"))

    def addToStartup(self, name: str, path: str, mode: bool = True):
        """
        添加开机自启动
        :param name: 启动项名字
        :param path: 文件路径
        :param mode: True添加/False删除
        """
        import win32api, win32con
        key = win32api.RegOpenKey(win32con.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run", 0, win32con.KEY_ALL_ACCESS)
        try:
            if mode:
                win32api.RegSetValueEx(key, name, 0, win32con.REG_SZ, f"{path} startup")
                win32api.RegCloseKey(key)
            else:
                win32api.RegDeleteValue(key, name)
                win32api.RegCloseKey(key)
        except:
            pass

    def getNewestVersion(self) -> str:
        """
        获取程序最新版本
        :return: 程序最新版本
        """
        import requests, json
        response = requests.get(program.UPDATE_URL, headers=program.REQUEST_HEADER, stream=True).text
        data = json.loads(response)["version"]
        return data


f = Functions()
# 切换运行路径

os.chdir(program.PROGRAM_PATH)

# 设置任务栏
import ctypes

ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(program.PROGRAM_NAME)

# 重复运行检测
if "python" in f.cmd(f"tasklist |findstr {setting.read('pid')}", True):
    setting.save("showWindow", "1")
    sys.exit()
setting.save("pid", str(program.PROGRAM_PID))

# UI多线程
from PyQt5.Qt import *
from qfluentwidgets import *
from qfluentwidgets import FluentIcon as FIF


class NewThread(QThread):
    """
    多线程模块
    """
    signalStr = pyqtSignal(str)
    signalBool = pyqtSignal(bool)
    signalList = pyqtSignal(list)
    signalDict = pyqtSignal(dict)

    def __init__(self, mode: str, data=None):
        super().__init__()
        self.mode = mode
        self.data = data

    def run(self):
        if self.mode == "展示窗口":
            while True:
                time.sleep(0.1)
                if setting.read("showWindow") == "1":
                    setting.save("showWindow", "0")
                    self.signalStr.emit("展示窗口")
        if self.mode == "更新运行库":
            for i in range(len(program.REQUIRE_LIB)):
                self.signalDict.emit({"名称": program.REQUIRE_LIB[i], "序号": i, "完成": False})
                f.pipUpdate(program.REQUIRE_LIB[i])
            self.signalDict.emit({"名称": "", "序号": 0, "完成": True})
        if self.mode == "检查更新":
            try:
                data = f.getNewestVersion()
            except:
                self.signalDict.emit({"更新": False, "版本": data})
                return
            if data == program.PROGRAM_VERSION:
                self.signalDict.emit({"更新": False, "版本": data})
            else:
                self.signalDict.emit({"更新": True, "版本": data})
        if self.mode == "立刻更新":
            try:
                data = f.getNewestVersion()
            except:
                self.signalDict.emit({"数量": len(data), "完成": "失败", "名称": "", "序号": 0})
                return
            if data == program.PROGRAM_VERSION:
                self.signalDict.emit({"数量": len(data), "完成": "失败", "名称": "", "序号": 0})
                return
            import requests, json
            response = requests.get(program.UPDATE_URL, headers=program.REQUEST_HEADER, stream=True).text
            data = json.loads(response)["list"]
            for i in range(len(data)):
                self.signalDict.emit({"数量": len(data), "完成": False, "名称": data[i], "序号": i})
                f.downloadFile(f.urlJoin(program.UPDATE_URL, data[i]), f.pathJoin(program.PROGRAM_PATH, data[i]))
            self.signalDict.emit({"数量": len(data), "完成": True, "名称": "", "序号": 0})
        if self.mode == "一键整理+清理":
            try:
                MyThread(lambda: f.clearRubbish())
                MyThread(lambda: f.clearCache())
                f.sortDesktopFiles()
                if setting.read("wechatPath") != "":
                    f.sortWechatFiles()
                f.clearFile(setting.read("sortPath"))
                self.signalBool.emit(True)
            except:
                self.signalBool.emit(False)
        if self.mode == "重启文件资源管理器":
            f.cmd("taskkill /f /im explorer.exe", True)
            self.signalStr.emit("完成")
            f.cmd("start C:/windows/explorer.exe", True)
        if self.mode == "Minecraft最新版本":
            self.signalStr.emit(f.getMC())
