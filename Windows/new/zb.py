import os
import sys
import shutil


class ProgramInfo():
    """
    zb小程序信息类-处理信息
    """
    PROGRAM_NAME = "zb小程序"
    PROGRAM_VERSION = "3.0.0beta"
    TITLE_NAME = f"{PROGRAM_NAME} {PROGRAM_VERSION}"
    AUTHOR_NAME = "Ianzb"
    AUTHOR_URL = "https://ianzb.github.io/"
    PROGRAM_URL = "https://ianzb.github.io/program/"
    GITHUB_URL = "https://github.com/Ianzb/program/"
    UPDATE_URL = "https://ianzb.github.io/program/Windows/"
    PROGRAM_PATH = os.path.dirname(sys.argv[0])
    FILE_PATH = os.path.basename(sys.argv[0])
    PROGRAM_PID = os.getpid()
    USER_PATH = os.path.expanduser("~")
    PROGRAM_FILE_PATH = os.path.join(USER_PATH, "zb")
    STARTUP_ARGUMENT = sys.argv[1:]
    REQUIRE_LIB = ["PyQt5",
                   "PyQt-Fluent-Widgets",
                   "requests",
                   "bs4",
                   "lxml",
                   "pypiwin32",
                   "pandas",
                   "send2trash",
                   "winshell",
                   ]

    def __init__(self):
        os.chdir(self.PROGRAM_PATH)

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

    def keepProgramFilePath(self):
        """
        保存程序生成文件目录
        """
        if not os.path.exists(self.PROGRAM_FILE_PATH):
            os.makedirs(self.PROGRAM_FILE_PATH)


program = ProgramInfo()


class FileFunctions():
    """
    文件相关函数
    """
    names = ["PPT",
             "文档",
             "表格",
             "图片",
             "音视频",
             "压缩包"]
    ends = [[".ppt", ".pptx"],
            [".doc", ".docx"".txt", ".pdf", ".json"],
            [".xls", ".xlsx", ".xlt", ".csv"],
            [".png", ".jpg", ".jpeg", ".webp", ".gif"],
            [".mp3", ".mp4", ".wav", ".ogg", ".flv"],
            [".zip", ".rar", ".7z"]]

    def __init__(self):
        pass

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
        :param mode: 模式：1 文件完整名称 2 文件名称 3 文件扩展名 4 文件所在目录
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
                        list.append(os.path.join(path, dir_name))
        if mode == 1:
            for i in os.listdir(path):
                if self.isDir(os.path.join(path, i)):
                    list.append(os.path.join(path, i))
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
                        list.append(os.path.join(path, file_name))
        if mode == 1:
            for i in os.listdir(path):
                if self.isFile(os.path.join(path, i)):
                    list.append(os.path.join(path, i))
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
                new = os.path.join(new, self.baseName(old))
            if self.exists(new):
                i = 1
                while self.exists(os.path.join(self.baseName(new, 3), self.baseName(new, 1) + " (" + str(i) + ")" + self.baseName(new, 2))):
                    i = i + 1
                new = os.path.join(self.baseName(new, 3), self.baseName(new, 1) + " (" + str(i) + ")" + self.baseName(new, 2))
            try:
                shutil.copy(os.path.join(old), os.path.join(new))
            except:
                self.onlyRead(old, False)
                shutil.copy(os.path.join(old), os.path.join(new))
        if self.isDir(old):
            if self.exists(new):
                i = 1
                while self.exists(new + " (" + str(i) + ")"):
                    i = i + 1
                new = new + " (" + str(i) + ")"
            try:
                shutil.copytree(os.path.join(old), os.path.join(new))
            except:
                try:
                    for i in self.walkFile(old):
                        self.onlyRead(i, False)
                    shutil.copytree(os.path.join(old), os.path.join(new))
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
                            self.move(i, self.join(new, self.names[j]))
        if mode in [0, 2]:
            list = self.walkDir(old, 1)
            if list != []:
                for i in list:
                    if i[i.rfind("\ "[:-1]) + 1:] not in ["软件"]:
                        self.move(i, self.join(new, "文件夹", i[i.rfind("\ "[:-1]) + 1:]))
        for i in self.names + ["文件夹"]:
            self.clearFile(self.join(new, i))
        self.clearEmptyDir(new)


file = FileFunctions()


class settingFunctions():
    """
    设置相关函数
    """
    SETTING_FILE_PATH = os.path.join(program.PROGRAM_FILE_PATH, "settings.ini")

    def __init__(self):
        from configparser import ConfigParser
        self.config = ConfigParser()

    def reload(self):
        """
        重新读取设置文件
        """
        if not os.path.exists(self.SETTING_FILE_PATH):
            file = open(self.SETTING_FILE_PATH, "w", encoding="utf-8")
            file.close()
        self.config.read(self.SETTING_FILE_PATH, encoding="utf-8")
        try:
            self.config.add_section("data")
        except:
            pass

    def readSetting(self, name: str) -> str:
        """
        读取设置
        :param name: 选项名称
        :return: 选项内容
        """
        self.reload()
        try:
            data = self.config["data"][name]
        except:
            data = None
        return data

    def saveSetting(self, name: str, data: str):
        self.reload()
        self.config.set("data", name, data)
        file = open(self.SETTING_FILE_PATH, "w", encoding="utf-8")
        self.config.write(file)
        file.close()


setting = settingFunctions()


class Functions():
    """
    相关函数
    """

    def __init__(self):
        pass

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

    def pipInstall(self, lib_name: str):
        """
        pip安装运行库
        :param lib_name: 运行库名称
        """
        self.cmd(f"pip install {lib_name} -i https://pypi.tuna.tsinghua.edu.cn/simple some-package")

    def pipUpdate(self, lib_name: str):
        """
        pip更新运行库
        :param lib_name: 运行库名称
        """
        self.cmd(f"pip install --upgrade {lib_name} -i https://pypi.tuna.tsinghua.edu.cn/simple some-package")

    @property
    def getMC(self) -> str:
        """
        获取我的世界最新版本
        :return: 字符串
        """
        import requests, bs4, lxml
        useful = ["{{v|java}}", "{{v|java-experimental}}", "{{v|java-snap}}", "{{v|java-combat}}", "{{v|bedrock}}", "{{v|bedrock-beta}}", "{{v|bedrock-preview}}", "{{v|dungeons}}", "{{v|legends-win}}", "{{v|launcher}}", "{{v|launcher-beta}}", "{{v|education}}", "{{v|education-beta}}", "{{v|china-win}}", "{{v|china-android}}"]
        response = requests.get("https://minecraft.fandom.com/zh/wiki/Template:Version#table")
        response.encoding = "UTF-8"
        soup = bs4.BeautifulSoup(response.text, "lxml")
        data1 = soup.find_all(name="td")
        l1 = [n.text.replace("\n", "") for n in data1]
        v1 = l1[::3]
        v2 = l1[1::3]
        v3 = l1[2::3]
        str1=""
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
                str1 = str1 + v1[i] + "版本：" + v2[i] + "\n"
        return str1


f = Functions()
# 重复运行检测
if "python" in f.cmd(f"tasklist |findstr {setting.readSetting('pid')}", True):
    setting.saveSetting("shownow", "1")
    sys.exit()
setting.saveSetting("pid", str(program.PROGRAM_PID))
# 设置任务栏
import ctypes

ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("zb小程序")
# 多线程优化
import threading


class MyThread(threading.Thread):
    def __init__(self, func, *args):
        super().__init__()

        self.func = func
        self.args = args

        self.daemon = True
        self.start()

    def run(self):
        self.func(*self.args)


print(f.getMC)
