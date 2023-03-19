# 多线程优化
import threading


class MyThread(threading.Thread):
    def __init__(self, func, *args):
        super().__init__()

        self.func = func
        self.args = args

        self.setDaemon(True)
        self.start()

    def run(self):
        self.func(*self.args)


# 开始加载
def start():
    import os, time
    os.popen("load.pyw")
    time.sleep(0.5)


# 取消加载
def close():
    import os
    if not os.path.exists("pid.txt"):
        return
    with open(file="pid.txt", mode="r") as file:
        pid = file.read()
    os.remove("pid.txt")
    os.popen("taskkill.exe /F /pid:" + pid)


# 关闭程序
def exit():
    import sys, os
    os.popen("taskkill.exe /pid:" + str(os.getpid()))
    sys.exit()


# 不可以打开就关闭程序
def check():
    import os,sys
    if os.path.exists(sys.argv[0].replace(".pyw",".txt")):
        with open(file=sys.argv[0].replace(".pyw",".txt"), mode="r") as file:
            pid=file.read()
        try:
            os.kill(int(pid), 0)
        except:
            os.remove(sys.argv[0].replace(".pyw", ".txt"))
            return None
        exit()


# 不可以打开程序
def disable(name):
    import os
    with open(file=name, mode="w") as file:
        file.write(str(os.getpid()))


# 可以打开程序
def enable(name):
    import os
    try:
        os.remove(name)
    except:
        pass

#关闭程序后
def hide(name):
    enable(name)
    exit()

# 关闭所有python程序
def kill_py():
    import os
    enable("../Myself/main.txt")
    enable("../Myself/hide.txt")
    enable("../Myself/manger.txt")
    enable("../Myself/update.txt")
    enable("../Seewo/hide.txt")
    enable("../Seewo/main.txt")
    enable("../Seewo/function.txt")
    enable("../Seewo/choose.txt")
    enable("../Seewo/update.txt")
    enable("main.txt")
    enable("hide.txt")
    enable("manger.txt")
    enable("function.txt")
    enable("choose.txt")
    enable("update.txt")
    os.popen("taskkill.exe /F /IM py.exe")
    os.popen("taskkill.exe /F /IM pyw.exe")
    os.popen("taskkill.exe /F /IM python.exe")
    os.popen("taskkill.exe /F /IM pythonw.exe")


# 更好的路径拼接
def pj(*a):
    import os
    out = ""
    for i in a:
        out = os.path.join(out, i)
    out = out.replace("//", r"\ "[:-1]).replace(r"\\ "[:-1], r"\ "[:-1]).replace("\/", r"\ "[:-1]).replace("/\ "[:-1], r"\ "[:-1]).replace("/", r"\ "[:-1])
    return out


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
    import filecmp, glob, os
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
def move_files(old, new):
    import stat, shutil, os
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


# MC版本爬虫
def get_mc():
    useful = ["{{v|java}}", "{{v|java-experimental}}", "{{v|java-snap}}", "{{v|java-combat}}", "{{v|bedrock}}", "{{v|bedrock-beta}}", "{{v|bedrock-preview}}", "{{v|dungeons}}", "{{v|launcher}}", "{{v|launcher-beta}}", "{{v|education}}", "{{v|education-beta}}", "{{v|china-win}}", "{{v|china-android}}"]
    import bs4, lxml, requests, os
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


# 重启PPT小助手
def ppt_restart():
    import time, os
    os.popen("taskkill -f -im PPTService.exe")
    time.sleep(0.2)
    os.popen("C:/Program Files (x86)/Seewo/PPTService/Main/PPTService.exe")


# 清理希沃视频展台文件
def clear_seewo():
    import send2trash, time, os
    try:
        list = os.walk(r"D:/EasiCameraPhoto")
        list2 = []
        for i in list: list2.append(i)
        list = list2[0][1]
        for i in list:
            if i != time.strftime("%Y-%m-%d") and os.path.exists(pj("D:/EasiCameraPhoto", i)): send2trash.send2trash(pj("D:/EasiCameraPhoto", i))
    except:
        pass


# 整理微信文件
def clear_wechat(path, to):
    import os
    try:
        list = []
        list2 = []
        for i in os.walk(path): list.append(i)
        for i in list[0][1]:
            if os.path.exists(pj(path, i, "FileStorage/File")): list2.append(pj(path, i, "FileStorage/File"))
        list = []
        list3 = []
        for i in range(len(list2)):
            for j in os.walk(list2[i]): list.append(j)
            for k in list[0][1]: list3.append(pj(list2[i], k))
        list = list3
        for i in list: move_files(i, to)
    except:
        pass


# 整理桌面文件
def clear_desk(to):
    import winreg
    key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Software\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders")
    path = winreg.QueryValueEx(key, "Desktop")[0]
    move_files(path, to)


# 清理系统缓存
def clear_cache():
    import shutil, os
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


# 清理回收站
def clear_rubbish():
    import winshell
    try:
        winshell.recycle_bin().empty(confirm=False, show_progress=False, sound=False)
    except:
        pass


# 重启文件资源管理器
def restart_explorer():
    import time, os
    os.popen("taskkill /f /im explorer.exe")
    time.sleep(0.2)
    os.popen("start C:/windows/explorer.exe")


# 整理+清理常用软件文件
def clear_apps():
    import shutil
    move_files(r"D:/Files/QQ/93322252/FileRecv", "E:/整理文件")
    move_files(r"D:/Files/Ding Talk", "E:/整理文件")
    move_files(r"D:/Files/百度网盘", "E:/整理文件")
    try:
        shutil.rmtree("C:/Users/93322/AppData/Roaming/Tencent/WeMeet/Global/IM")
    except:
        pass


# 获取系统信息
def sys_info():
    import platform, os, psutil, wmi, pythoncom
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
