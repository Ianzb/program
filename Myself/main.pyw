v = "1.3.1"

import bs4
import os
import requests
import shutil
import sys
import time
import webbrowser
from tkinter import *
from tkinter import ttk
from tkinter.ttk import Separator

date = time.strftime("%Y-%m-%d")
# 初始化
tk = Tk()
st = ttk.Style()
st.configure("TButton")
tk.title("zb的小程序For Myself " + v)
x = 400
y = 170
now_x = (tk.winfo_screenwidth() - x) / 2
now_y = (tk.winfo_screenheight() - y) / 2
tk.geometry("%dx%d+%d+%d" % (x, y, now_x, now_y))
tk.wm_attributes('-topmost', 1)
tk.resizable(False, False)
tk.minsize(400, 170)
tk.maxsize(400, 170)
tk.wm_iconbitmap("ico.ico")


# 定制功能


def pc_remove(d, name):
    for i in [k for (k, v) in d.items() if v == name]: del d[i]


def remove_if_in(d, name):
    a = []
    for i in d.keys():
        if name in i: a.append(i)
    for i in a: del d[i]


def repeat_clear(path):
    import filecmp, glob
    file_lst = []
    for i in glob.glob(path + '/**/*', recursive=True):
        if os.path.isfile(i): file_lst.append(i)
    for x in file_lst:
        for y in file_lst:
            if x != y and os.path.exists(x) and os.path.exists(y):
                if filecmp.cmp(x, y):
                    if len(x) > len(y):
                        os.remove(x)
                    else:
                        os.remove(y)


def move_files(old, new):
    import stat
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
    for i in list3:
        for j in [".ppt", ".PPT"]:
            if j in i and os.path.exists(os.path.join(old + i)): ppt.append(i)
        for j in [".doc", ".DOC", ".txt", ".TXT", ".pdf", ".PDF"]:
            if j in i and os.path.exists(os.path.join(old + i)): doc.append(i)
        for j in [".xls", ".XLS"]:
            if j in i and os.path.exists(os.path.join(old + i)): xls.append(i)
        for j in [".png", ".PNG", ".jpg", ".JPG", ".jpeg", ".JPEG", ".webp", ".WEBP", ".gif", ".GIF"]:
            if j in i and os.path.exists(os.path.join(old + i)): img.append(i)
        for j in [".mp", ".MP"]:
            if j in i and os.path.exists(os.path.join(old + i)): mp3.append(i)
        for j in [".zip", ".ZIP", ".rar", ".RAR", ".7z", ".7Z"]:
            if j in i and os.path.exists(os.path.join(old + i)): zip.append(i)
    for i in range(len(ppt)):
        if os.path.exists(new + "PPT/" + ppt[i]):
            j = 1
            while os.path.exists(
                new + "PPT/" + ppt[i][:ppt[i].rfind(".")] + "(" + str(j) + ")" + ppt[i][ppt[i].rfind("."):]): j = j + 1
            ppt[i] = ppt[i] + "(" + str(j) + ")"
    for i in range(len(doc)):
        if os.path.exists(new + "文档/" + doc[i]):
            j = 1
            while os.path.exists(
                new + "文档/" + doc[i][:doc[i].rfind(".")] + "(" + str(j) + ")" + doc[i][doc[i].rfind("."):]): j = j + 1
            doc[i] = doc[i] + "(" + str(j) + ")"
    for i in range(len(xls)):
        if os.path.exists(new + "表格/" + xls[i]):
            j = 1
            while os.path.exists(
                new + "表格/" + xls[i][:xls[i].rfind(".")] + "(" + str(j) + ")" + xls[i][xls[i].rfind("."):]): j = j + 1
            xls[i] = xls[i] + "(" + str(j) + ")"
    for i in range(len(img)):
        if os.path.exists(new + "图片/" + img[i]):
            j = 1
            while os.path.exists(
                new + "图片/" + img[i][:img[i].rfind(".")] + "(" + str(j) + ")" + img[i][img[i].rfind("."):]): j = j + 1
            img[i] = img[i] + "(" + str(j) + ")"
    for i in range(len(mp3)):
        if os.path.exists(new + "音视频/" + mp3[i]):
            j = 1
            while os.path.exists(new + "音视频/" + mp3[i][:mp3[i].rfind(".")] + "(" + str(j) + ")" + mp3[i][
                                                                                                     mp3[i].rfind(
                                                                                                         "."):]): j = j + 1
            mp3[i] = mp3[i] + "(" + str(j) + ")"
    for i in range(len(zip)):
        if os.path.exists(new + "压缩包/" + zip[i]):
            j = 1
            while os.path.exists(new + "压缩包/" + zip[i][:zip[i].rfind(".")] + "(" + str(j) + ")" + zip[i][
                                                                                                     zip[i].rfind(
                                                                                                         "."):]): j = j + 1
            zip[i] = zip[i] + "(" + str(j) + ")"
    if not os.path.exists(new + "PPT/"): os.makedirs(new + "PPT/")
    if not os.path.exists(new + "表格/"): os.makedirs(new + "表格/")
    if not os.path.exists(new + "文档/"): os.makedirs(new + "文档/")
    if not os.path.exists(new + "图片/"): os.makedirs(new + "图片/")
    if not os.path.exists(new + "音视频/"): os.makedirs(new + "音视频/")
    if not os.path.exists(new + "压缩包/"): os.makedirs(new + "压缩包/")
    if not os.path.exists(new + "文件夹/"): os.makedirs(new + "文件夹/")
    for i in ppt:
        try:
            os.chmod(old + i, stat.S_IWRITE)
            shutil.move(old + i, new + "PPT/" + i)
        except:
            os.chmod(old + i[:i.rfind("(")], stat.S_IWRITE)
            shutil.move(old + i[:i.rfind("(")],
                        new + "PPT/" + i[:i.rfind(".")] + i[i.rfind("("):] + i[i.rfind("."):i.rfind("(")])
    for i in doc:
        try:
            os.chmod(old + i, stat.S_IWRITE)
            shutil.move(old + i, new + "文档/" + i)
        except:
            os.chmod(old + i[:i.rfind("(")], stat.S_IWRITE)
            shutil.move(old + i[:i.rfind("(")],
                        new + "文档/" + i[:i.rfind(".")] + i[i.rfind("("):] + i[i.rfind("."):i.rfind("(")])
    for i in xls:
        try:
            os.chmod(old + i, stat.S_IWRITE)
            shutil.move(old + i, new + "表格/" + i)
        except:
            os.chmod(old + i[:i.rfind("(")], stat.S_IWRITE)
            shutil.move(old + i[:i.rfind("(")],
                        new + "表格/" + i[:i.rfind(".")] + i[i.rfind("("):] + i[i.rfind("."):i.rfind("(")])
    for i in img:
        try:
            os.chmod(old + i, stat.S_IWRITE)
            shutil.move(old + i, new + "图片/" + i)
        except:
            os.chmod(old + i[:i.rfind("(")], stat.S_IWRITE)
            shutil.move(old + i[:i.rfind("(")],
                        new + "图片/" + i[:i.rfind(".")] + i[i.rfind("("):] + i[i.rfind("."):i.rfind("(")])
    for i in mp3:
        try:
            os.chmod(old + i, stat.S_IWRITE)
            shutil.move(old + i, new + "音视频/" + i)
        except:
            os.chmod(old + i[:i.rfind("(")], stat.S_IWRITE)
            shutil.move(old + i[:i.rfind("(")],
                        new + "音视频/" + i[:i.rfind(".")] + i[i.rfind("("):] + i[i.rfind("."):i.rfind("(")])
    for i in zip:
        try:
            os.chmod(old + i, stat.S_IWRITE)
            shutil.move(old + i, new + "压缩包/" + i)
        except:
            os.chmod(old + i[:i.rfind("(")], stat.S_IWRITE)
            shutil.move(old + i[:i.rfind("(")],
                        new + "压缩包/" + i[:i.rfind(".")] + i[i.rfind("("):] + i[i.rfind("."):i.rfind("(")])
    list3 = list2[0][1]
    fold = []
    dont = ["软件", "MobileFile"]
    for i in list3:
        if i not in dont:
            fold.append(i)
    for i in range(len(fold)):
        if os.path.exists(new + "文件夹/" + fold[i]):
            j = 1
            while os.path.exists(new + "文件夹/" + fold[i] + "(" + str(j) + ")"): j = j + 1
            fold[i] = fold[i] + "(" + str(j) + ")"
    for i in fold:
        try:
            shutil.move(old + i, new + "文件夹/" + i)
        except:
            shutil.move(old + i[:i.rfind("(")], new + "文件夹/" + i)


# 功能


def b0():
    print("检查更新")
    import re
    link = "https://ianzb.github.io/server.github.io/Myself/"
    res = requests.get(link + "myself.html")
    res.encoding = "UTF-8"
    soup = bs4.BeautifulSoup(res.text, "lxml")
    data = soup.find_all(name="div", text=re.compile("."))
    for i in range(len(data)): data[i] = str(data[i]).replace("<div>", "").replace("</div>", "").replace(r"\r",
                                                                                                         "").replace(
        r"\n", "").strip()
    for i in range(len(data)):
        response1 = requests.get(link + data[i])
        response1.encoding = "UTF-8"
        main = response1.content
        with open(data[i], "wb") as file: file.write(main)
        print(data[i])
    os.popen("main.pyw")
    sys.exit()


def b100():
    print("打开郑博网站")
    webbrowser.open("https://ianzb.github.io/")


def b101():
    print("MC版本爬虫")
    b = []
    a = []
    v = {}
    response = requests.get("https://minecraft.fandom.com/zh/wiki/Template:Version#table")
    response.encoding = "UTF-8"
    soup = bs4.BeautifulSoup(response.text, "lxml")
    data1 = soup.find_all(name="td")
    for n in data1: a.append(n.text)
    for i in range(len(a)):
        if i % 3 != 2: b.append(a[i])
    for i in range(len(b)):
        if i % 2 == 0: v[b[i]] = b[i + 1]
    pc_remove(v, "")
    list = ["内部", "Windows", "macOS", "Linux", "即将到来", "ChromeOS", "PlayStation", "Nintendo", "Xbox", "Steam",
            "demo", "教育版（iOS）", "Minecraft Dungeons（启动器版）", "战斗测试"]
    for c in list: remove_if_in(v, c)
    with open("mc.txt", "w", encoding="utf-8") as file:
        for (k, v) in v.items(): file.write(k + "版本：" + v + "\n")
    os.popen("mc.txt")
    time.sleep(1)
    os.remove("mc.txt")


def b11():
    print("重启文件资源管理器")
    os.popen("taskkill /f /im explorer.exe")
    time.sleep(0.2)
    os.popen("start c:\windows\explorer.exe")


def b1():
    os.startfile("E:\整理文件")


def b2():
    print("清理回收站")
    import winshell
    try:
        winshell.recycle_bin().empty(confirm=False, show_progress=False, sound=False)
    except:
        pass


def b12():
    print("一键整理+清理")
    print("清理回收站")
    import winshell
    try:
        winshell.recycle_bin().empty(confirm=False, show_progress=False, sound=False)
    except:
        pass
    print("清理系统缓存")
    list = []
    list1 = os.walk(os.getenv("TEMP"))
    for i in list1:
        list.append(i)
    if list != []:
        list1 = list[0][1]
    list2 = list[0][2]
    for i in list1:
        try:
            shutil.rmtree(os.path.join(os.getenv("TEMP"), i))
        except:
            pass
    for i in list2:
        try:
            os.remove(os.path.join(os.getenv("TEMP"), i))
        except:
            pass
    print("整理桌面文件")
    import winreg
    key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r'Software\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders')
    path = winreg.QueryValueEx(key, "Desktop")[0] + r"\ "[0:-1]
    move_files(path, "E:/整理文件/")
    print("整理微信文件")
    try:
        list = []
        list2 = []
        for i in os.walk("E:/Files/Wechat/WeChat Files/"): list.append(i)
        for i in list[0][1]:
            if os.path.exists(os.path.join("E:/Files/Wechat/WeChat Files/", i, "FileStorage\File")): list2.append(
                os.path.join("E:/Files/Wechat/WeChat Files/", i, "FileStorage\File"))
        list = []
        list3 = []
        for i in range(len(list2)):
            for j in os.walk(list2[i]): list.append(j)
            for k in list[0][1]: list3.append(os.path.join(list2[i], k))
        list = list3
        for i in list: move_files(i + "/", "E:/整理文件/")
    except:
        pass
    print("整理QQ文件")
    move_files(r"E:\Files\QQ\93322252\FileRecv/", "E:/整理文件/")
    print("整理钉钉文件")
    move_files(r"E:\Files\Ding Talk/", "E:/整理文件/")
    print("整理百度网盘下载文件")
    move_files(r"E:\Files\百度网盘/", "E:/整理文件/")
    repeat_clear("E:/整理文件/PPT/")
    repeat_clear("E:/整理文件/表格/")
    repeat_clear("E:/整理文件/图片/")
    repeat_clear("E:/整理文件/文档/")
    repeat_clear("E:/整理文件/文件夹/")
    repeat_clear("E:/整理文件/压缩包/")
    repeat_clear("E:/整理文件/音视频/")


# txt = ttk.Label(tk, text="文字").place(x=100,y=,width=200,height=30,anchor="center")
# b = ttk.Button(tk, text="按钮", style="TButton", command=b).place(x=,y=,width=100,height=30)
# sep = Separato3r(tk, orient=HORIZONTAL).place(x=0,y=,width=5000,height=30)

ttk.Label(tk, text="实用程序").place(x=75, y=0, width=150, height=30)
ttk.Label(tk, text="功能列表").place(x=275, y=0, width=150, height=30)
Separator(tk, orient=HORIZONTAL).place(x=0, y=0, width=400, height=2)

# 左侧
ttk.Button(tk, text="我的网站", style="TButton", command=b100).place(x=0, y=30, width=200, height=30)
ttk.Button(tk, text="MC版本爬虫", style="TButton", command=b101).place(x=0, y=60, width=200, height=30)
# 右侧

ttk.Button(tk, text="一键整理+清理", style="TButton", command=b12).place(x=200, y=30, width=150, height=30)
ttk.Button(tk, text="打开", style="TButton", command=b1).place(x=350, y=30, width=50, height=30)
ttk.Button(tk, text="清理回收站", style="TButton", command=b2).place(x=200, y=60, width=100, height=30)
ttk.Button(tk, text="重启资源管理器", style="TButton", command=b11).place(x=300, y=60, width=100, height=30)
Separator(tk, orient=VERTICAL).place(x=200, y=0, width=1, height=120)
Separator(tk, orient=HORIZONTAL).place(x=0, y=120, width=400, height=2)
ttk.Label(tk, text="郑博的小程序For Myself 版本  " + v).place(x=40, y=130, width=200, height=30)
ttk.Button(tk, text="检查并更新版本", style="TButton", command=b0).place(x=260, y=130, width=100, height=30)
Separator(tk, orient=HORIZONTAL).place(x=0, y=170, width=400, height=2)

tk.mainloop()
