import os, sys, winreg, logging

# 通用变量
version = "2.0.0"
zb_name = "Ianzb"
program_name = "zb小程序"
title_name = program_name + " " + version
zb_url = "https://ianzb.github.io/"
program_url = "https://ianzb.github.io/program/"
github_url = "https://github.com/Ianzb/program/"
old_path = os.getcwd()
abs_path = sys.argv[0][:sys.argv[0].rfind(r"\ "[:-1])]
abs_name = sys.argv[0][sys.argv[0].rfind(r"\ "[:-1]) + 1:]
abs_cache = abs_name[:abs_name.rfind(".")]
abs_pid = os.getpid()
user_path = os.path.expanduser("~")
abs_desktop = winreg.QueryValueEx(winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders"), "Desktop")[0]
lib_list = ["PyQt5-sip", "pyqt5-tools", "PyQt5", "PyQt5Designer", "PyQt-Fluent-Widgets[full]", "lxml", "pypiwin32", "pandas", "numpy", "bs4", "requests", "send2trash", "winshell", "matplotlib", "openpyxl", "PyAudio", "python-xlib", "pymouse", "pyautogui", "PyUserInput", "psutil", "wmi"]

# 切换工作路
os.chdir(abs_path)


# 路径拼接
def join(*data):
    path = ""
    for i in data:
        path = os.path.join(path, i)
    path = path.replace("//", r"\ "[:-1]).replace(r"\\ "[:-1], r"\ "[:-1]).replace("\/", r"\ "[:-1]).replace("/\ "[:-1], r"\ "[:-1]).replace("/", r"\ "[:-1])
    return path


# 日志功能配置
try:
    os.makedirs(join(user_path, "zb"))
except:
    pass
try:
    os.remove(join(user_path, "zb/zb.log"))
except:
    pass
logger = logging.getLogger("mylogger")
logger.setLevel(logging.INFO)
rf_handler = logging.StreamHandler(sys.stderr)
rf_handler.setLevel(logging.INFO)
rf_handler.setFormatter(logging.Formatter("[%(asctime)s %(filename)s %(process)d] %(levelname)s:%(message)s"))

f_handler = logging.FileHandler(join(user_path, "zb/zb.log"))
f_handler.setLevel(logging.DEBUG)
f_handler.setFormatter(logging.Formatter("[%(asctime)s %(filename)s %(process)d] %(levelname)s:%(message)s"))

logger.addHandler(rf_handler)
logger.addHandler(f_handler)
logging = logger
logging.info("程序开始运行")

# 初始化设置
from configparser import ConfigParser

conf = ConfigParser()
if os.path.exists(join(user_path, "zb/settings.ini")):
    conf.read(join(user_path, "zb/settings.ini"), encoding="utf-8")
    logging.debug("成功读取设置文件，路径：" + join(user_path, "zb/settings.ini"))
else:
    if not os.path.exists(join(user_path, "zb")):
        os.makedirs(join(user_path, "zb"))
    with open(join(user_path, "zb/settings.ini"), "w+", encoding="utf-8") as file:
        logging.debug("成功读取设置文件，路径：" + join(user_path, "zb/settings.ini"))


# 读取设置
def readSetting(name):
    if os.path.exists(join(user_path, "zb/settings.ini")):
        conf.read(join(user_path, "zb/settings.ini"), encoding="utf-8")
        logging.debug("成功读取设置文件，路径：" + join(user_path, "zb/settings.ini"))
    else:
        if not os.path.exists(join(user_path, "zb")):
            os.makedirs(join(user_path, "zb"))
        with open(join(user_path, "zb/settings.ini"), "w+", encoding="utf-8") as file:
            logging.debug("成功读取设置文件，路径：" + join(user_path, "zb/settings.ini"))
    try:
        conf.add_section("data")
    except:
        pass
    try:
        data = conf["data"][str(name)]
    except:
        logging.debug("项 " + str(name) + " 不存在")
        return ""
    logging.debug("项 " + str(name) + " 的内容为 " + data)
    if data in ["", None, " "]:
        return ""
    return data


# 保存设置
def saveSetting(name, data):
    if os.path.exists(join(user_path, "zb/settings.ini")):
        conf.read(join(user_path, "zb/settings.ini"), encoding="utf-8")
        logging.debug("成功读取设置文件，路径：" + join(user_path, "zb/settings.ini"))
    else:
        if not os.path.exists(join(user_path, "zb")):
            os.makedirs(join(user_path, "zb"))
        with open(join(user_path, "zb/settings.ini"), "w+", encoding="utf-8") as file:
            logging.debug("成功读取设置文件，路径：" + join(user_path, "zb/settings.ini"))
    try:
        conf.add_section("data")
    except:
        pass
    try:
        old = conf["data"][str(name)]
        conf.set("data", str(name), str(data))
        logging.debug("项 " + str(name) + "的内容从 " + old + " 修改为 " + str(data))
    except:
        conf.set("data", str(name), str(data))
        logging.debug("项 " + str(name) + " 的内容设置为 " + str(data))
    with open(join(user_path, "zb/settings.ini"), "w", encoding="utf-8") as file:
        conf.write(file)


# 重复运行检测
p = os.popen("tasklist |findstr " + readSetting(abs_cache))
if "python" in p.read().strip():
    saveSetting("show", "1")
    logging.info("已运行zb小程序，将其唤醒，新运行的zb小程序自动退出")
    sys.exit()

# 导入运行库
import traceback, shutil, re, time, hashlib, threading, ctypes, stat, bs4, lxml, urllib.parse, requests, send2trash, winshell, platform, webbrowser, win32api, win32con, win32com.client, random

# 任务栏图标加载
ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("zb小程序")


# 多线程优化
class MyThread(threading.Thread):
    def __init__(self, func, *args):
        super().__init__()

        self.func = func
        self.args = args

        self.daemon = True
        self.start()

    def run(self):
        self.func(*self.args)


# 网址拼接
def urlJoin(url1, url2):
    return urllib.parse.urljoin(url1, url2)


# 更好的CMD
def cmd(command):
    return os.popen(str(command)).read()


# 是否存在
def exists(path):
    return os.path.exists(path)


# 是否为文件
def isFile(path):
    if not exists(path):
        return False
    return os.path.isfile(path)


# 是否为目录
def isDir(path):
    if not exists(path):
        return False
    return os.path.isdir(path)


# 删除
def delete(path):
    if isFile(path):
        os.remove(path)
    if isDir(path):
        shutil.rmtree(path)


# 获取文件MD5
def getMd5(path):
    if isFile(path):
        with open(path, "rb") as file:
            data = file.read()
        return hashlib.md5(data).hexdigest()


# 获取文件名/仅名称/仅后缀
def baseName(path, mode=0):
    if isFile(path):
        name = os.path.basename(path)
        if mode == 0:
            return name
        if mode == 1:
            return os.path.splitext(name)[0]
        if mode == 2:
            return os.path.splitext(name)[1]
        if mode == 3:
            return path.replace(name, "")


# 创建文件夹
def mkDir(path):
    if not exists(path):
        os.makedirs(path)


# 获取文件大小
def getSize(path):
    if isFile(path):
        return os.path.getsize(path)


# 遍历子文件夹
def walkDir(path, mode=0):
    list = []
    if mode == 0:
        if isDir(path):
            paths = os.walk(path)
            for path, dir_lst, file_lst in paths:
                for dir_name in dir_lst:
                    list.append(join(path, dir_name))
    if mode == 1:
        for i in os.listdir(path):
            if isDir(join(path, i)):
                list.append(join(path, i))
    if list == None:
        list = []
    return list


# 遍历子文件
def walkFile(path, mode=0):
    list = []
    if mode == 0:
        paths = os.walk(path)
        if isDir(path):
            for path, dir_lst, file_lst in paths:
                for file_name in file_lst:
                    list.append(join(path, file_name))
    if mode == 1:
        for i in os.listdir(path):
            if isFile(join(path, i)):
                list.append(join(path, i))
    if list == None:
        list = []
    return list


# 只读权限
def onlyRead(path, mode):
    if isFile(path):
        if mode:
            os.chmod(path, stat.S_IREAD)
        else:
            os.chmod(path, stat.S_IWRITE)


# 复制
def copy(old, new):
    if isFile(old):
        if isDir(new) or "." not in new:
            mkDir(new)
            new = join(new, baseName(old))
        if exists(new):
            i = 1
            while exists(join(baseName(new, 3), baseName(new, 1) + " (" + str(i) + ")" + baseName(new, 2))):
                i = i + 1
            new = join(baseName(new, 3), baseName(new, 1) + " (" + str(i) + ")" + baseName(new, 2))
        try:
            shutil.copy(join(old), join(new))
        except:
            onlyRead(old, False)
            shutil.copy(join(old), join(new))
    if isDir(old):
        if exists(new):
            i = 1
            while exists(new + " (" + str(i) + ")"):
                i = i + 1
            new = new + " (" + str(i) + ")"
        try:
            shutil.copytree(join(old), join(new))
        except:
            try:
                for i in walkFile(old):
                    onlyRead(i, False)
                shutil.copytree(join(old), join(new))
            except:
                return


# 移动
def move(old, new):
    copy(old, new)
    if exists(old):
        delete(old)


# 清理空文件
def clearEmptyFile(path):
    if isDir(path):
        paths = walkFile(path, 1)
        if paths != []:
            for i in paths:
                if getSize(i) == 0:
                    delete(i)


# 清理空文件夹
def clearEmptyDir(path):
    if isDir(path):
        paths = walkDir(path, 1)
        if paths != []:
            for i in paths:
                try:
                    os.rmdir(i)
                except:
                    pass


# 清理重复文件
def clearRepeatFile(path):
    if isDir(path):
        sizes = []
        names = walkFile(path)
        if names == []:
            return
        names.sort(key=lambda i: len(i))
        for i in names:
            md5 = getMd5(i)
            if md5 in sizes:
                delete(i)
            else:
                sizes.append(md5)


# 清理3合1
def clearFile(path):
    clearEmptyFile(path)
    clearEmptyDir(path)
    clearRepeatFile(path)


# 整理指定目录文件到指定位置
def sortDir(old, new, mode=0):
    names = ["PPT", "文档", "表格", "图片", "音视频", "压缩包"]
    ends = [[".ppt", ".pptx"], [".doc", ".docx", ".txt", ".pdf", ".json"], [".xls", ".xlsx", ".xlt", ".csv"], [".png", ".jpg", ".jpeg", ".webp", ".gif"], [".mp3", ".mp4", ".wav", ".ogg", ".flv"], [".zip", ".rar", ".7z"]]
    if mode != 1:
        list = walkFile(old, 1)
        if list != []:
            for i in list:
                for j in range(len(ends)):
                    if baseName(i, 2) in ends[j]:
                        move(i, join(new, names[j]))
    if mode == 0:
        list = walkDir(old, 1)
        if list != []:
            for i in list:
                if i[i.rfind("\ "[:-1]) + 1:] not in ["软件"]:
                    move(i, join(new, "文件夹", i[i.rfind("\ "[:-1]) + 1:]))
    for i in names + ["文件夹"]:
        clearFile(join(new, i))
    clearEmptyDir(new)


# MC版本爬虫
def getMc():
    logging.info("开始获取我的世界最新版本")
    useful = ["{{v|java}}", "{{v|java-experimental}}", "{{v|java-snap}}", "{{v|java-combat}}", "{{v|bedrock}}", "{{v|bedrock-beta}}", "{{v|bedrock-preview}}", "{{v|dungeons}}", "{{v|legends-win}}", "{{v|launcher}}", "{{v|launcher-beta}}", "{{v|education}}", "{{v|education-beta}}", "{{v|china-win}}", "{{v|china-android}}"]
    temp = os.getenv("TEMP")
    l1 = []
    v1 = []
    v2 = []
    v3 = []
    v = {}
    str1 = ""
    response = requests.get("https://minecraft.fandom.com/zh/wiki/Template:Version#table")
    response.encoding = "UTF-8"
    soup = bs4.BeautifulSoup(response.text, "lxml")
    data1 = soup.find_all(name="td")
    for n in data1: l1.append(n.text)
    for i in range(len(l1)):
        l1[i] = l1[i].replace("\n", "")
        if i % 3 == 0: v1.append(l1[i])
        if i % 3 == 1: v2.append(l1[i])
        if i % 3 == 2: v3.append(l1[i])
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
    logging.info("我的世界最新版本获取成功")
    return str1


# 整理微信文件
def clearWechat(old, new):
    logging.info("开始整理微信文件")
    try:
        list = []
        list2 = []
        for i in walkDir(old, 1):
            if exists(join(i, "FileStorage/File")):
                list.append(join(i, "FileStorage/File"))
        for i in list:
            if walkDir(i, 1) == None:
                return
            list2 = list2 + walkDir(i, 1)
        for i in list2:
            sortDir(i, new)
        for i in list:
            sortDir(i, new, 1)
    except:
        pass
    logging.info("成功整理微信文件")


# 整理桌面文件
def clearDesk(to):
    sortDir(abs_desktop, to)


# 清理系统缓存
def clearCache():
    logging.info("开始清理系统缓存")
    try:
        path = os.getenv("TEMP")
        for i in walkDir(path):
            try:
                delete(i)
            except:
                pass
        for i in walkFile(path):
            try:
                delete(i)
            except:
                pass
    except:
        pass
    logging.info("成功清理系统缓存")


# 清理回收站
def clearRubbish():
    logging.info("开始清理回收站")
    try:
        winshell.recycle_bin().empty(confirm=False, show_progress=False, sound=False)
    except:
        pass
    logging.info("成功清理回收站")


# 更新模块下载文件
def download(link):
    import requests
    response1 = requests.get(link)
    response1.encoding = "UTF-8"
    main = response1.content
    with open(join(abs_path,link.replace("https://ianzb.github.io/program/Windows/", ""), ""), "wb") as file:
        file.write(main)


# pip安装模块
def pipInstall(name):
    logging.info("开始安装" + name + "运行库")
    print(cmd("pip install " + name + " -i  https://pypi.mirrors.ustc.edu.cn/simple/"))
    print(cmd("pip install --upgrade " + name + " -i  https://pypi.mirrors.ustc.edu.cn/simple/"))


# 创建快捷方式
def createLink(name="快捷方式", path="", to=abs_desktop, icon=""):
    to = join(to, name + ".lnk")
    shell = win32com.client.Dispatch("WScript.Shell")
    shortcut = shell.CreateShortCut(to)
    shortcut.Targetpath = path
    shortcut.IconLocation = icon
    shortcut.save()


# 添加至开始菜单
def addToStartMenu():
    path = join(user_path, "AppData\Roaming\Microsoft\Windows\Start Menu\Programs")
    createLink(name="zb小程序", path=join(abs_path, "main.pyw"), to=path, icon=join(abs_path, "img/logo.ico"))


# 开机自启动
def judgeKey(key_name, reg_root=win32con.HKEY_CURRENT_USER, reg_path=r"SOFTWARE\Microsoft\Windows\CurrentVersion\Run"):
    reg_flags = win32con.WRITE_OWNER | win32con.KEY_WOW64_64KEY | win32con.KEY_ALL_ACCESS
    try:
        key = winreg.OpenKey(reg_root, reg_path, 0, reg_flags)
        location, type = winreg.QueryValueEx(key, key_name)
        logging.info("注册表键存在", "location（数据）:" + str(location) + "type:" + str(type))
        feedback = 0
    except FileNotFoundError as e:
        logging.info("注册表键不存在" + str(e))
        feedback = 1
    except PermissionError as e:
        logging.info("注册表权限不足" + str(e))
        feedback = 2
    except:
        logging.info("注册表键查看失败")
        feedback = 3
    return feedback


def autoRun(switch="open", zdynames=None, current_file=None, abspath=abs_path):
    logging.info(zdynames)
    path = abspath + "\\" + zdynames
    judge_key = judgeKey(reg_root=win32con.HKEY_CURRENT_USER, reg_path=r"Software\Microsoft\Windows\CurrentVersion\Run", key_name=current_file)
    KeyName = r"Software\Microsoft\Windows\CurrentVersion\Run"
    key = win32api.RegOpenKey(win32con.HKEY_CURRENT_USER, KeyName, 0, win32con.KEY_ALL_ACCESS)
    if switch == "open":
        try:
            if judge_key == 0:
                logging.info("已经开启开机自启动")
            elif judge_key == 1:
                win32api.RegSetValueEx(key, current_file, 0, win32con.REG_SZ, path)
                win32api.RegCloseKey(key)
                logging.info("开机自启动添加成功！")
        except:
            logging.info("添加失败")
    elif switch == "close":
        try:
            if judge_key == 0:
                win32api.RegDeleteValue(key, current_file)
                win32api.RegCloseKey(key)
                logging.info("成功删除键！")
            elif judge_key == 1:
                logging.info("键不存在")
            elif judge_key == 2:
                logging.info("权限不足")
            else:
                logging.info("出现错误")
        except:
            logging.info("删除失败")


from PyQt5 import *
from PyQt5 import QtCore
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from qfluentwidgets import *
from qfluentwidgets import FluentIcon as FIF
from qfluentwidgets.components.widgets.menu import *
from qframelesswindow import *


class newThread(QThread):
    signal = pyqtSignal(str)

    def __init__(self, mode):
        super().__init__()
        self.mode = mode

    def run(self):
        mode = self.mode
        if mode == 1:
            MyThread(lambda: clearRubbish())
            MyThread(lambda: clearCache())
            clearDesk(readSetting("sort"))
            if readSetting("wechat") != "":
                clearWechat(readSetting("wechat"), readSetting("sort"))
            clearFile(readSetting("sort"))
            self.signal.emit("完成")
        if mode == 2:
            cmd("taskkill /f /im explorer.exe")
            self.signal.emit("完成")
            cmd("start C:/windows/explorer.exe")
        if mode == 3:
            self.signal.emit("开始")
            link = "https://ianzb.github.io/program/Windows/"
            res = requests.get(urlJoin(link, "index.html"))
            res.encoding = "UTF-8"
            soup = bs4.BeautifulSoup(res.text, "lxml")
            data = soup.find_all(name="div", class_="download", text=re.compile("."))
            for i in range(len(data)): data[i] = data[i].text.strip()
            self.signal.emit("总共" + str(len(data)))
            for i in range(len(data)):
                self.signal.emit(data[i])
                download(urlJoin(link, data[i]))
            self.signal.emit("完成")
        if mode == 4:
            for i in range(len(lib_list)):
                self.signal.emit(str(i))
                pipInstall(lib_list[i])
            self.signal.emit("完成")
        if mode == 5:
            str1 = getMc()
            self.signal.emit(str1)

        if mode == 8:
            while True:
                time.sleep(0.1)
                if readSetting("show") == "1":
                    saveSetting("show", "0")
                    self.signal.emit("展示")
