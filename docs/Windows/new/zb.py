import os, sys, winreg, logging

# 通用变量
version = "2.0.0"
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


# 更好的路径拼接
def pj(*data):
    path = ""
    for i in data:
        path = os.path.join(path, i)
    path = path.replace("//", r"\ "[:-1]).replace(r"\\ "[:-1], r"\ "[:-1]).replace("\/", r"\ "[:-1]).replace("/\ "[:-1], r"\ "[:-1]).replace("/", r"\ "[:-1])
    return path


# 日志功能配置
try:
    os.makedirs(pj(user_path, "zb"))
except:
    pass
try:
    os.remove(pj(user_path, "zb/zb.log"))
except:
    pass
logger = logging.getLogger("mylogger")
logger.setLevel(logging.INFO)
rf_handler = logging.StreamHandler(sys.stderr)
rf_handler.setLevel(logging.INFO)
rf_handler.setFormatter(logging.Formatter("[%(asctime)s %(filename)s %(process)d] %(levelname)s:%(message)s"))

f_handler = logging.FileHandler(pj(user_path, "zb/zb.log"))
f_handler.setLevel(logging.DEBUG)
f_handler.setFormatter(logging.Formatter("[%(asctime)s %(filename)s %(process)d] %(levelname)s:%(message)s"))

logger.addHandler(rf_handler)
logger.addHandler(f_handler)
logging = logger
logging.info("程序开始运行")

# 初始化设置
from configparser import ConfigParser

conf = ConfigParser()
if os.path.exists(pj(user_path, "zb/settings.ini")):
    conf.read(pj(user_path, "zb/settings.ini"), encoding="utf-8")
    logging.debug("成功读取设置文件，路径：" + pj(user_path, "zb/settings.ini"))
else:
    if not os.path.exists(pj(user_path, "zb")):
        os.makedirs(pj(user_path, "zb"))
    with open(pj(user_path, "zb/settings.ini"), "w+", encoding="utf-8") as file:
        logging.debug("成功读取设置文件，路径：" + pj(user_path, "zb/settings.ini"))


# 读取设置
def readSetting(name):
    if os.path.exists(pj(user_path, "zb/settings.ini")):
        conf.read(pj(user_path, "zb/settings.ini"), encoding="utf-8")
        logging.debug("成功读取设置文件，路径：" + pj(user_path, "zb/settings.ini"))
    else:
        if not os.path.exists(pj(user_path, "zb")):
            os.makedirs(pj(user_path, "zb"))
        with open(pj(user_path, "zb/settings.ini"), "w+", encoding="utf-8") as file:
            logging.debug("成功读取设置文件，路径：" + pj(user_path, "zb/settings.ini"))
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
    if os.path.exists(pj(user_path, "zb/settings.ini")):
        conf.read(pj(user_path, "zb/settings.ini"), encoding="utf-8")
        logging.debug("成功读取设置文件，路径：" + pj(user_path, "zb/settings.ini"))
    else:
        if not os.path.exists(pj(user_path, "zb")):
            os.makedirs(pj(user_path, "zb"))
        with open(pj(user_path, "zb/settings.ini"), "w+", encoding="utf-8") as file:
            logging.debug("成功读取设置文件，路径：" + pj(user_path, "zb/settings.ini"))
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
    with open(pj(user_path, "zb/settings.ini"), "w", encoding="utf-8") as file:
        conf.write(file)


# 重复运行检测
p = os.popen("tasklist |findstr " + readSetting(abs_cache))
if "python" in p.read().strip():
    saveSetting("show", "1")
    logging.info("已运行zb小程序，将其唤醒，新运行的zb小程序自动退出")
    sys.exit()

# 导入运行库
import traceback, shutil, re, time, hashlib, threading, ctypes, pickle, stat, bs4, lxml, requests, send2trash, winshell, platform, webbrowser, win32api, win32con, win32com.client, random

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

#更好的CMD
def cmd(command):
    return os.popen(str(command)).read()
#更好的复制
#更好的删除
#更好的移动
#更好的创建

# 获取文件md5
def getMd5(file):
    with open(file, "rb") as file:
        data = file.read()
    return hashlib.md5(data).hexdigest()


# 清理空文件
def clearEmpty(path):
    if not os.path.exists(path):
        return
    logging.info("开始清理" + path + "下的空文件")
    dir_list = []
    for root, dirs, files in os.walk(path):
        dir_list.append(root)
    for root in dir_list[::-1]:
        if not os.listdir(root):
            try:
                os.rmdir(root)
            except:
                pass
    for root, dirs, files in os.walk(path):
        for file in files:
            src_file = pj(root, file)
            if os.path.getsize(src_file) == 0:
                try:
                    os.remove(src_file)
                except:
                    pass


# 清理重复整理文件
def clearRepeat(path):
    if not os.path.exists(path):
        return
    logging.info("开始清理" + path + "下的重复文件")
    size = []
    name = []
    for i in os.listdir(path):
        real_path = pj(path, i)
        if os.path.isfile(real_path) == True:
            md5 = getMd5(real_path)
            if md5 in size:
                num = size.index(md5)
                if len(name[num]) <= len(real_path):
                    os.remove(real_path)
                    continue
                else:
                    os.remove(name[num])
                    size.remove(size[num])
                    name.remove(name[num])
            size.append(md5)
            name.append(real_path)


# 整理指定目录文件到指定位置
def movePath(old, new, mode=True):
    logging.info("开始整理文件" + old + "至" + new)
    list2 = []
    list3 = os.walk(old)
    for i in list3: list2.append(i)
    try:
        list3 = list2[0][2]
    except:
        return False
    ppt = []
    doc = []
    xls = []
    img = []
    mp3 = []
    zip = []
    name1 = ["PPT", "文档", "表格", "图片", "音视频", "压缩包"]
    name2 = [ppt, doc, xls, img, mp3, zip]
    for name in range(len(name1)):
        if name == 0: ends = ["ppt"]
        if name == 1: ends = ["doc", "txt", "pdf", "json"]
        if name == 2: ends = ["xls", "xlt", "csv"]
        if name == 3: ends = ["png", "jpg", "jpeg", "webp", "gif"]
        if name == 4: ends = ["mp", "wav", "ogg", "flv"]
        if name == 5: ends = ["zip", "rar", "7z"]
        for i in list3:
            for j in ends:
                if j in i[i.rfind("."):].lower() and "~$" not in i: name2[name].append(i)
    for name in range(len(name1)):
        for i in range(len(name2[name])):
            if os.path.exists(pj(new, name1[name], name2[name][i])):
                j = 1
                while os.path.exists(pj(new, name1[name], name2[name][i][:name2[name][i].rfind(".")], "(", str(j), ")", name2[name][i][name2[name][i].rfind("."):])): j = j + 1
                name2[name][i] = name2[name][i] + "(" + str(j) + ")"
    for name in range(len(name1)):
        if not os.path.exists(pj(new, name1[name])): os.makedirs(pj(new, name1[name]))
    for name in range(len(name1)):
        for i in name2[name]:
            try:
                os.chmod(pj(old, i), stat.S_IWRITE)
                shutil.move(pj(old, i), pj(new, name1[name], i))
            except:
                try:
                    os.chmod(pj(old, i[:i.rfind("(")]), stat.S_IWRITE)
                    shutil.move(pj(old, i[:i.rfind("(")]), pj(new, name1[name], i[:i.rfind(".")] + i[i.rfind("("):] + i[i.rfind("."):i.rfind("(")]))
                except Exception as e:
                    logging.info("无法移动" + pj(old, i[:i.rfind("(")]) + "异常类型：" + e)
    # 以下为文件夹整理部分
    if mode == True:
        list3 = list2[0][1]
        fold = []
        not1 = ["软件", "备份", "MobileFile"]
        if not os.path.exists(pj(new, "文件夹")): os.makedirs(pj(new, "文件夹"))
        for i in list3:
            if i not in not1: fold.append(i)
        for i in range(len(fold)):
            if os.path.exists(pj(new, "文件夹", fold[i])):
                j = 1
                while os.path.exists(pj(new, "文件夹", fold[i] + "(" + str(j) + ")")): j = j + 1
                fold[i] = fold[i] + "(" + str(j) + ")"
        for i in fold:
            try:
                shutil.move(pj(old, i), pj(new, "文件夹", i))
            except:
                shutil.move(pj(old, i[:i.rfind("(")]), pj(new, "文件夹", i))
    logging.info("成功整理" + old + "至" + new)


# 清理整理目录下的无效文件
def clearUselessFiles(path):
    new_list = []
    name1 = ["PPT", "文档", "表格", "图片", "音视频", "压缩包", "文件夹"]
    for i in name1:
        new_list.append(pj(path, i))
    for i in new_list:
        clearEmpty(i)
        clearRepeat(i)


# MC版本爬虫
def getMc():
    logging.info("开始获取我的世界最新版本")
    useful = ["{{v|java}}", "{{v|java-experimental}}", "{{v|java-snap}}", "{{v|java-combat}}", "{{v|bedrock}}", "{{v|bedrock-beta}}", "{{v|bedrock-preview}}", "{{v|dungeons}}", "{{v|legends}}", "{{v|launcher}}", "{{v|launcher-beta}}", "{{v|education}}", "{{v|education-beta}}", "{{v|china-win}}", "{{v|china-android}}"]
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
        if v3[i] in useful and v2[i] != "":
            str1 = str1 + v1[i] + "版本：" + v2[i] + "\n"
    logging.info("我的世界最新版本获取成功")
    return str1


# 重启PPT小助手
def restartPPT():
    logging.info("重启PPT小助手")
    try:
        cmd("taskkill -f -im PPTService.exe & C:/Program Files (x86)/Seewo/PPTService/Main/PPTService.exe")
    except:
        pass


# 清理希沃视频展台文件
def clearSeewo():
    logging.info("开始清理希沃视频展台文件")
    try:
        for j in [chr(i) for i in range(65, 91)]:
            if os.path.exists(j + ":/EasiCameraPhoto"):
                list = os.walk(j + ":/EasiCameraPhoto")
                list2 = []
                for i in list: list2.append(i)
                list = list2[0][1]
                for i in list:
                    if i != time.strftime("%Y-%m-%d"):
                        send2trash.send2trash(pj(j + ":/EasiCameraPhoto", i))
        logging.info("成功清理希沃视频展台文件")
    except:
        pass


# 整理微信文件
def clearWechat(old, new):
    logging.info("开始整理微信文件")
    list = []
    list2 = []
    for i in os.walk(old): list.append(i)
    for i in list[0][1]:
        if os.path.exists(pj(old, i, "FileStorage/File")): list2.append(pj(old, i, "FileStorage/File"))
    logging.info("获取到的微信用户文件目录为" + str(list2))
    list = []
    for i in range(len(list2)):
        list3 = []
        for j in os.walk(list2[i]):
            list3.append(j)
        for k in list3[0][1]:
            list.append(pj(list2[i], k))
    for i in list:
        movePath(i, new)
        clearEmpty(i)
    for i in list2:
        movePath(i, new, False)
        clearEmpty(i)
    logging.info("成功整理微信文件")


# 整理桌面文件
def clearDesk(to):
    movePath(abs_desktop, to)


# 清理系统缓存
def clearCache():
    logging.info("开始清理系统缓存")
    list = []
    list1 = os.walk(os.getenv("TEMP"))
    for i in list1: list.append(i)
    if list: list1 = list[0][1]
    list2 = list[0][2]
    for i in list1:
        try:
            shutil.rmtree(pj(os.getenv("TEMP"), i))
        except:
            pass
    for i in list2:
        try:
            os.remove(pj(os.getenv("TEMP"), i))
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


# 重启文件资源管理器
def restartExplorer():
    logging.info("重启文件资源管理器")
    try:
        cmd("taskkill /f /im explorer.exe & start C:/windows/explorer.exe")
    except:
        pass


# 整理+清理常用软件文件
def clearQQ(path):
    logging.info("开始整理QQ文件")
    movePath("D:/文件/应用/QQ/93322252/FileRecv", path)
    logging.info("成功整理QQ文件")


# 更新模块下载文件
def download(link):
    import requests
    response1 = requests.get(link)
    response1.encoding = "UTF-8"
    main = response1.content
    with open(link[link.rfind("/") + 1:], "wb") as file:
        file.write(main)


# pip安装模块
def pipInstall(name):
    logging.info("开始安装" + name + "运行库")
    print(cmd("pip install " + name + " -i  https://pypi.mirrors.ustc.edu.cn/simple/"))
    print(cmd("pip install --upgrade " + name + " -i  https://pypi.mirrors.ustc.edu.cn/simple/"))


# 创建快捷方式
def createLink(name="快捷方式", path="", to=abs_desktop, icon=""):
    to = pj(to, name + ".lnk")
    shell = win32com.client.Dispatch("WScript.Shell")
    shortcut = shell.CreateShortCut(to)
    shortcut.Targetpath = path
    shortcut.IconLocation = icon
    shortcut.save()


# 添加至开始菜单
def addToStartMenu():
    path = pj(user_path, "AppData\Roaming\Microsoft\Windows\Start Menu\Programs")
    createLink(name="zb小程序", path=pj(abs_path, "main.pyw"), to=path, icon=pj(abs_path, "logo.ico"))


# 开机自启动
# autoRun(switch="open", zdynames=os.path.basename(pj(path, "hide.pyw"))
# autoRun(switch="close", zdynames=os.path.basename(pj(path, "hide.pyw"))
# 判断键是否存在
def judgeKey(key_name,
             reg_root=win32con.HKEY_CURRENT_USER,  # 根节点  其中的值可以有：HKEY_CLASSES_ROOT、HKEY_CURRENT_USER、HKEY_LOCAL_MACHINE、HKEY_USERS、HKEY_CURRENT_CONFIG
             reg_path=r"SOFTWARE\Microsoft\Windows\CurrentVersion\Run",  # 键的路径
             ):
    """
    :param key_name: #  要查询的键名
    :param reg_root: # 根节点
    #win32con.HKEY_CURRENT_USER
    #win32con.HKEY_CLASSES_ROOT
    #win32con.HKEY_CURRENT_USER
    #win32con.HKEY_LOCAL_MACHINE
    #win32con.HKEY_USERS
    #win32con.HKEY_CURRENT_CONFIG
    :param reg_path: #  键的路径
    :return:feedback是（0/1/2/3：存在/不存在/权限不足/报错）
    """
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


def autoRun(switch="open",  # 开：open # 关：close
            zdynames=None,
            current_file=None,
            abspath=abs_path):
    """
    :param switch: 注册表开启、关闭自启动
    :param zdynames: 当前文件名
    :param current_file: 获得文件名的前部分
    :param abspath: 当前文件路径
    :return:
    """
    logging.info(zdynames)

    path = abspath + "\\" + zdynames  # 要添加的exe完整路径如：
    judge_key = judgeKey(reg_root=win32con.HKEY_CURRENT_USER,
                         reg_path=r"Software\Microsoft\Windows\CurrentVersion\Run",  # 键的路径
                         key_name=current_file)
    # 注册表项名
    KeyName = r"Software\Microsoft\Windows\CurrentVersion\Run"
    key = win32api.RegOpenKey(win32con.HKEY_CURRENT_USER, KeyName, 0, win32con.KEY_ALL_ACCESS)
    if switch == "open":
        # 异常处理
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
                win32api.RegDeleteValue(key, current_file)  # 删除值
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
