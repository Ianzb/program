import os, time, sys, shutil, logging

logging.basicConfig(level=logging.INFO, filename="zb.log", format="[%(asctime)s %(filename)s %(process)d] %(levelname)s:%(message)s")
logging.info("程序开始运行")
# 通用变量
abs_path = sys.argv[0][:sys.argv[0].rfind(r"\ "[:-1])]
abs_name = sys.argv[0][sys.argv[0].rfind(r"\ "[:-1]) + 1:]
abs_cache = sys.argv[0].replace(".pyw", ".txt")
os.chdir(abs_path)


# 开始加载
def start():
    os.popen("load.pyw")
    logging.info("打开加载窗口")


# 取消加载
def close():
    path = os.path.join(abs_path, "pid.txt")
    try:
        with open(file=path, mode="r") as file:
            pid = file.read()
    except:
        pass
    os.popen("taskkill.exe /F /pid:" + pid)
    logging.info("关闭加载窗口")


if abs_name not in ["hide.pyw", "load.pyw"]:
    start()

from tkinter import *
from tkinter import ttk
from tkinter.ttk import *
from tkinter.messagebox import *
from tkinter.filedialog import *

try:
    import threading, re, pickle, filecmp, glob, stat, bs4, lxml, requests, winreg, send2trash, winshell, platform, psutil, wmi, pythoncom, webbrowser, win32api, win32con, random, pandas, numpy, sv_ttk
except:
    logging.info("未找到运行库")
    showerror("错误", "未找到运行库，请重新安装运行库！")
    sys.exit()
# 通用变量
abs_pid = os.getpid()
abs_desktop = key = winreg.QueryValueEx(winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders"), "Desktop")[0]


# 保存设置
def save_setting(data):
    with open("setting.zb", "wb") as file:
        pickle.dump(data, file)
        logging.info("设置已保存")


# 读取设置
def read_setting():
    if os.path.exists("setting.zb"):
        with open("setting.zb", "rb") as file:
            data = pickle.load(file)
    else:
        data = ["作者个人版", 0, 30, "D:/文件/整理", "D:/文件/应用/微信/WeChat Files"] + [None for i in range(100)]
    logging.info("设置已读取")
    return data


settings = read_setting()

# 多线程优化
class MyThread(threading.Thread):
    def __init__(self, func, *args):
        super().__init__()

        self.func = func
        self.args = args

        self.setDaemon(True)
        self.start()

    def run(self):
        self.func(*self.args)


# 更好的路径拼接
def pj(*a):
    out = ""
    for i in a:
        out = os.path.join(out, i)
    out = out.replace("//", r"\ "[:-1]).replace(r"\\ "[:-1], r"\ "[:-1]).replace("\/", r"\ "[:-1]).replace("/\ "[:-1], r"\ "[:-1]).replace("/", r"\ "[:-1])
    return out


# 关闭程序
def exit():
    logging.info("关闭程序")
    os.popen("taskkill.exe /pid:" + str(os.getpid()))
    sys.exit()


# 不可以打开就关闭程序
def check():
    if os.path.exists(abs_cache):
        with open(file=abs_cache, mode="r") as file:
            pid = file.read()
        try:
            os.kill(int(pid), 0)
            logging.info("检查是否已打开")
            exit()
        except:
            os.remove(abs_cache)
            return None


# 不可以打开程序
def disable(name):
    with open(file=name, mode="w") as file:
        file.write(str(os.getpid()))
        logging.info("标记该程序已打开")


# 关闭所有python程序
def kill_py():
    for root, dirs, files in os.walk("./"):
        for name in files:
            if name.endswith(".txt"):
                os.remove(pj(root, name))
    logging.info("强制关闭Python程序")
    os.popen("taskkill.exe /F /IM py.exe")
    os.popen("taskkill.exe /F /IM pyw.exe")
    os.popen("taskkill.exe /F /IM python.exe")
    os.popen("taskkill.exe /F /IM pythonw.exe")


# 检查图标是否存在
def check_ico(tk, name):
    try:
        tk.wm_iconbitmap(name)
    except:
        pass


# MC版本爬虫去除不符内容1
def pc_remove(d, name):
    for i in [k for (k, v) in d.items() if v == name]:
        del d[i]


# MC版本爬虫去除不符内容2
def remove_if_in(d, name):
    a = []
    for i in d.keys():
        if name in i:
            a.append(i)
    for i in a:
        del d[i]


# 清理重复整理文件
def clear_repeat(name):
    list = []
    list.append(pj(name, "PPT/"))
    list.append(pj(name, "表格/"))
    list.append(pj(name, "图片/"))
    list.append(pj(name, "文档/"))
    list.append(pj(name, "文件夹/"))
    list.append(pj(name, "压缩包/"))
    list.append(pj(name, "音视频/"))
    for path in list:
        file_lst = []
        for i in glob.glob(path + "/**/*", recursive=True):
            if os.path.isfile(i): file_lst.append(i)
        for x in file_lst:
            for y in file_lst:
                if x != y and os.path.exists(x) and os.path.exists(y):
                    if filecmp.cmp(x, y):
                        if len(x) > len(y):
                            os.remove(x)
                        else:
                            os.remove(y)


# 整理指定目录文件到指定位置
def move_files(old, new, mode=True):
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
                except:
                    print("无法移动" + pj(old, i[:i.rfind("(")]))
                    continue
    for name in range(len(name1)):
        files = os.listdir(pj(new, name1[name]))
        for file in files:
            if os.path.isfile(pj(new, name1[name], file)):
                if os.path.getsize(pj(new, name1[name], file)) == 0:
                    os.remove(pj(new, name1[name], file))
            if os.path.isdir(pj(new, name1[name], file)):
                if not os.listdir(pj(new, name1[name], file)):
                    os.rmdir(pj(new, name1[name], file))
    if mode == False:
        logging.info("成功整理" + old + "至" + new + "，不整理文件夹")
        return
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
    for file in os.listdir(pj(new, "文件夹")):
        if os.path.isdir(pj(new, "文件夹", file)):
            if not os.listdir(pj(new, "文件夹", file)):
                os.rmdir(pj(new, "文件夹", file))
    logging.info("成功整理" + old + "至" + new)


# MC版本爬虫
def get_mc():
    logging.info("开始获取我的世界最新版本")
    useful = ["{{v|java}}", "{{v|java-experimental}}", "{{v|java-snap}}", "{{v|java-combat}}", "{{v|bedrock}}", "{{v|bedrock-beta}}", "{{v|bedrock-preview}}", "{{v|dungeons}}", "{{v|launcher}}", "{{v|launcher-beta}}", "{{v|education}}", "{{v|education-beta}}", "{{v|china-win}}", "{{v|china-android}}"]
    temp = os.getenv("TEMP")
    l1 = []
    v1 = []
    v2 = []
    v3 = []
    v = {}
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
    with open(pj(temp, "mc.txt"), "w", encoding="utf-8") as file:
        for i in range(len(v1)):
            if v1[i][-1] == "版":
                v1[i] = v1[i] + "正式版"
            if v3[i] == "{{v|china-win}}":
                v1[i] = "中国版端游"
            if v3[i] == "{{v|china-android}}":
                v1[i] = "中国版手游"
            if v3[i] in useful and v2[i] != "":
                file.write(v1[i] + "版本：" + v2[i] + "\n")

    os.popen(pj(temp, "mc.txt"))
    logging.info("我的世界最新版本获取成功")


# 重启PPT小助手
def ppt_restart():
    logging.info("重新运行PPT小助手")
    os.popen("taskkill -f -im PPTService.exe")
    time.sleep(0.5)
    os.popen("C:/Program Files (x86)/Seewo/PPTService/Main/PPTService.exe")


# 清理希沃视频展台文件
def clear_seewo():
    logging.info("开始清理希沃视频展台文件")
    try:
        list = os.walk(r"D:/EasiCameraPhoto")
        list2 = []
        for i in list: list2.append(i)
        list = list2[0][1]
        for i in list:
            if i != time.strftime("%Y-%m-%d") and os.path.exists(pj("D:/EasiCameraPhoto", i)): send2trash.send2trash(pj("D:/EasiCameraPhoto", i))
        logging.info("成功清理希沃视频展台文件")
    except:
        pass


# 整理微信文件
def clear_wechat(old, new):
    logging.info("开始整理微信文件")
    list = []
    list2 = []
    for i in os.walk(old): list.append(i)
    for i in list[0][1]:
        if os.path.exists(pj(old, i, "FileStorage/File")): list2.append(pj(old, i, "FileStorage/File"))
    logging.info("获取到的微信用户文件目录为" + str(list2))
    list = []
    list3 = []
    for i in range(len(list2)):
        for j in os.walk(list2[i]): list.append(j)
        for k in list[0][1]: list3.append(pj(list2[i], k))
    list = list3
    for i in list:
        move_files(i, new)
    for i in list2:
        move_files(i, new, False)
    logging.info("成功整理微信文件")


# 整理桌面文件
def clear_desk(to):
    move_files(abs_desktop, to)


# 清理系统缓存
def clear_cache():
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
def clear_rubbish():
    logging.info("开始清理回收站")
    try:
        winshell.recycle_bin().empty(confirm=False, show_progress=False, sound=False)
    except:
        pass
    logging.info("成功清理回收站")


# 重启文件资源管理器
def restart_explorer():
    logging.info("重启文件资源管理器")
    os.popen("taskkill /f /im explorer.exe")
    time.sleep(0.5)
    os.popen("start C:/windows/explorer.exe")


# 整理+清理常用软件文件
def clear_apps(path):
    logging.info("开始整理常用软件文件")
    move_files(r"D:/文件/应用/QQ/93322252/FileRecv", path)
    move_files(r"D:/文件/应用/钉钉", path)
    move_files(r"D:/文件/应用/百度网盘", path)
    logging.info("成功整理常用软件文件")


# 更新模块下载文件
def download(link):
    import requests
    response1 = requests.get(link)
    response1.encoding = "UTF-8"
    main = response1.content
    with open(link[link.rfind("/") + 1:], "wb") as file:
        file.write(main)


# pip安装模块
def pip_install(name):
    logging.info("开始安装" + name + "运行库")
    os.system("pip install " + name + " -i http://mirrors.aliyun.com/pypi/simple/ --trusted-host mirrors.aliyun.com")
    os.system("pip install --upgrade " + name + " -i http://mirrors.aliyun.com/pypi/simple/ --trusted-host mirrors.aliyun.com")


# 获取系统信息
def sys_info():
    logging.info("开始获取系统信息")
    temp = os.getenv("TEMP")

    # CPU
    pythoncom.CoInitialize()
    c = wmi.WMI()
    for cpu in c.Win32_Processor():
        name = cpu.Name
    core = str(psutil.cpu_count(logical=False))
    thread = str(psutil.cpu_count())
    cpuused = str(psutil.cpu_percent(1))
    pythoncom.CoUninitialize()

    # 内存
    total = str(psutil.virtual_memory().total / 1024 / 1024 / 1024)[:4]
    used = str(psutil.virtual_memory().used / 1024 / 1024 / 1024)[:4]
    percent = str(psutil.virtual_memory().percent)

    with open(pj(temp, "sysinfo.txt"), "w", encoding="utf-8") as file:
        file.write("操作系统及版本信息：" + platform.platform())
        file.write("\n系统内核版本号：" + platform.version())
        file.write("\n系统位数：" + platform.architecture()[0].replace("bit", "位"))
        file.write("\n计算机名称：" + platform.node())
        file.write("\nCPU信息：" + name + "，" + core + "核" + thread + "线程" + "，当前占用率" + cpuused + "%")
        file.write("\n内存信息：共" + total + "GB，已使用" + used + "GB，占用率" + percent + "%")
        file.write("\nPython编译信息：" + str(platform.python_build()))
        file.write("\nPython版本信息：" + platform.python_version())

    os.popen(pj(temp, "sysinfo.txt"))
    logging.info("成功获取系统信息")


# 开机自启动
# AutoRun(switch="open", zdynames=os.path.basename(os.path.join(path, "hide.pyw"))
# AutoRun(switch="close", zdynames=os.path.basename(os.path.join(path, "hide.pyw"))
# 判断键是否存在
def Judge_Key(key_name,
              reg_root=win32con.HKEY_CURRENT_USER,  # 根节点  其中的值可以有：HKEY_CLASSES_ROOT、HKEY_CURRENT_USER、HKEY_LOCAL_MACHINE、HKEY_USERS、HKEY_CURRENT_CONFIG
              reg_path=r"SOFTWARE\Microsoft\Windows\CurrentVersion\Run",  # 键的路径
              ):
    # print(key_name)
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
        print("键存在", "location（数据）:", location, "type:", type)
        feedback = 0
    except FileNotFoundError as e:
        print("键不存在", e)
        feedback = 1
    except PermissionError as e:
        print("权限不足", e)
        feedback = 2
    except:
        print("Error")
        feedback = 3
    return feedback

def AutoRun(switch="open",  # 开：open # 关：close
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
    print(zdynames)

    path = abspath + "\\" + zdynames  # 要添加的exe完整路径如：
    judge_key = Judge_Key(reg_root=win32con.HKEY_CURRENT_USER,
                          reg_path=r"Software\Microsoft\Windows\CurrentVersion\Run",  # 键的路径
                          key_name=current_file)
    # 注册表项名
    KeyName = r"Software\Microsoft\Windows\CurrentVersion\Run"
    key = win32api.RegOpenKey(win32con.HKEY_CURRENT_USER, KeyName, 0, win32con.KEY_ALL_ACCESS)
    if switch == "open":
        # 异常处理
        try:
            if judge_key == 0:
                print("已经开启了，无需再开启")
            elif judge_key == 1:
                win32api.RegSetValueEx(key, current_file, 0, win32con.REG_SZ, path)
                win32api.RegCloseKey(key)
                print("开机自启动添加成功！")
        except:
            print("添加失败")
    elif switch == "close":
        try:
            if judge_key == 0:
                win32api.RegDeleteValue(key, current_file)  # 删除值
                win32api.RegCloseKey(key)
                print("成功删除键！")
            elif judge_key == 1:
                print("键不存在")
            elif judge_key == 2:
                print("权限不足")
            else:
                print("出现错误")
        except:
            print("删除失败")
