v = "2.0.0"
import filecmp
import glob
import os
import re
import shutil
import stat
import sys
import time
import webbrowser
import winreg
from tkinter import *
from tkinter import ttk
from tkinter.ttk import Separator

import bs4
import requests
import send2trash
import winshell

date = time.strftime("%Y-%m-%d")
# 初始化
tk = Tk()
# 设置风格样式
st = ttk.Style()
st.configure("TButton")
# 窗口属性
tk.title(" zb的小程序For Seewo " + v)
x = 400
y = 230
now_x = (tk.winfo_screenwidth() - x) / 2
now_y = (tk.winfo_screenheight() - y) / 2
tk.geometry("%dx%d+%d+%d" % (x, y, now_x, now_y))
tk.wm_attributes('-topmost', 1)
tk.minsize(400, 230)
tk.maxsize(400, 295)
tk.wm_iconbitmap("ico.ico")


# 定制


def pc_remove(d, name):
    a = [k for (k, v) in d.items() if v == name]
    for i in a:
        del d[i]


def remove_if_in(d, name):
    a = []
    for i in d.keys():
        if name in i:
            a.append(i)
    for i in a:
        del d[i]


def repeat_clear(path):
    file_lst = []
    for i in glob.glob(path + '/**/*', recursive=True):
        if os.path.isfile(i):
            file_lst.append(i)
    for x in file_lst:
        for y in file_lst:
            if x != y and os.path.exists(x) and os.path.exists(y):
                if filecmp.cmp(x, y):
                    if len(x) > len(y):
                        os.remove(x)
                    else:
                        os.remove(y)


def move_files(old, new):
    list2 = []
    list3 = os.walk(old)
    for i in list3:
        list2.append(i)
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
        if ".ppt" in i and os.path.exists(os.path.join(old + i)):
            ppt.append(i)
        if (".doc" in i or ".txt" in i or ".pdf" in i) and os.path.exists(os.path.join(old + i)):
            doc.append(i)
        if ".xls" in i and os.path.exists(os.path.join(old + i)):
            xls.append(i)
        if (
                ".png" in i or ".jpg" in i or ".jpeg" in i or ".webp" in i or ".JPG" in i or ".PNG" in i or ".gif" in i) and os.path.exists(
            os.path.join(old + i)):
            img.append(i)
        if ".mp" in i and os.path.exists(os.path.join(old + i)):
            mp3.append(i)
        if (".zip" in i or ".rar" in i or ".7z" in i) and os.path.exists(os.path.join(old + i)):
            zip.append(i)
    for i in range(len(ppt)):
        if os.path.exists(new + "PPT/" + ppt[i]):
            j = 1
            while os.path.exists(
                    new + "PPT/" + ppt[i][:ppt[i].rfind(".")] + "(" + str(j) + ")" + ppt[i][ppt[i].rfind("."):]):
                j = j + 1
            ppt[i] = ppt[i] + "(" + str(j) + ")"
    for i in range(len(doc)):
        if os.path.exists(new + "文档/" + doc[i]):
            j = 1
            while os.path.exists(
                    new + "文档/" + doc[i][:doc[i].rfind(".")] + "(" + str(j) + ")" + doc[i][doc[i].rfind("."):]):
                j = j + 1
            doc[i] = doc[i] + "(" + str(j) + ")"
    for i in range(len(xls)):
        if os.path.exists(new + "表格/" + xls[i]):
            j = 1
            while os.path.exists(
                    new + "表格/" + xls[i][:xls[i].rfind(".")] + "(" + str(j) + ")" + xls[i][xls[i].rfind("."):]):
                j = j + 1
            xls[i] = xls[i] + "(" + str(j) + ")"
    for i in range(len(img)):
        if os.path.exists(new + "图片/" + img[i]):
            j = 1
            while os.path.exists(
                    new + "图片/" + img[i][:img[i].rfind(".")] + "(" + str(j) + ")" + img[i][img[i].rfind("."):]):
                j = j + 1
            img[i] = img[i] + "(" + str(j) + ")"
    for i in range(len(mp3)):
        if os.path.exists(new + "音视频/" + mp3[i]):
            j = 1
            while os.path.exists(
                    new + "音视频/" + mp3[i][:mp3[i].rfind(".")] + "(" + str(j) + ")" + mp3[i][mp3[i].rfind("."):]):
                j = j + 1
            mp3[i] = mp3[i] + "(" + str(j) + ")"
    for i in range(len(zip)):
        if os.path.exists(new + "压缩包/" + zip[i]):
            j = 1
            while os.path.exists(
                    new + "压缩包/" + zip[i][:zip[i].rfind(".")] + "(" + str(j) + ")" + zip[i][zip[i].rfind("."):]):
                j = j + 1
            zip[i] = zip[i] + "(" + str(j) + ")"
    if not os.path.exists(new + "PPT/"):
        os.makedirs(new + "PPT/")
    if not os.path.exists(new + "表格/"):
        os.makedirs(new + "表格/")
    if not os.path.exists(new + "文档/"):
        os.makedirs(new + "文档/")
    if not os.path.exists(new + "图片/"):
        os.makedirs(new + "图片/")
    if not os.path.exists(new + "音视频/"):
        os.makedirs(new + "音视频/")
    if not os.path.exists(new + "压缩包/"):
        os.makedirs(new + "压缩包/")
    if not os.path.exists(new + "文件夹/"):
        os.makedirs(new + "文件夹/")
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
    for i in list3:
        if i != "软件":
            fold.append(i)
    for i in range(len(fold)):
        if os.path.exists(new + "文件夹/" + fold[i]):
            j = 1
            while os.path.exists(new + "文件夹/" + fold[i] + "(" + str(j) + ")"):
                j = j + 1
            fold[i] = fold[i] + "(" + str(j) + ")"
    for i in fold:
        try:
            shutil.move(old + i, new + "文件夹/" + i)
        except:
            shutil.move(old + i[:i.rfind("(")], new + "文件夹/" + i)


# 功能


def b0():
    print("检查更新")
    link = "https://ianzb.github.io/server.github.io/Seewo/"
    res = requests.get(
        link + "seewo.html")
    res.encoding = "UTF-8"
    soup = bs4.BeautifulSoup(res.text, "lxml")
    data = soup.find_all(name="div", text=re.compile("."))
    for i in range(len(data)):
        data[i] = str(data[i]).replace("<div>", "").replace("</div>", "").replace(r"\r", "").replace(r"\n", "").strip()
    for i in range(len(data)):
        response1 = requests.get(link + data[i])
        response1.encoding = "UTF-8"
        main = response1.content
        with open(data[i], "wb") as file:
            file.write(main)
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
    for n in data1:
        a.append(n.text)
    for i in range(len(a)):
        if i % 3 != 2:
            b.append(a[i])
    for i in range(len(b)):
        if i % 2 == 0:
            v[b[i]] = b[i + 1]
    pc_remove(v, "")
    for c in ["内部", "Windows", "macOS", "Linux", "即将到来", "ChromeOS", "PlayStation", "Nintendo", "Xbox", "Steam", "demo", "教育版（iOS）", "Minecraft Dungeons（启动器版）", "战斗测试"]:
        remove_if_in(v, c)
    with open("mc.txt", "w", encoding="utf-8") as file:
        for (k, v) in v.items():
            file.write(k + "版本：" + v + "\n")
    os.popen("mc.txt")
    time.sleep(1)
    os.remove("mc.txt")


def b1():
    print("重启PPT小助手")
    os.popen("taskkill -f -im PPTService.exe")
    time.sleep(0.2)
    os.popen("C:\Program Files (x86)\Seewo\PPTService\Main\PPTService.exe")


def b2():
    print("关闭PPT小助手")
    os.popen("taskkill -f -im PPTService.exe")


def b3():
    print("打开CCTV-13")
    webbrowser.open("https://tv.cctv.cn/live/cctv13/?spm=C28340.P4hQlpYBT2vN.ExidtyEJcS5K.25")
    sys.exit()


def b4():
    print("打开校园电视台")
    webbrowser.open("http://10.8.8.35:8443/live/31384275e5e0443fa4364714fcbf85fd")
    sys.exit()


def b5():
    print("清理希沃视频展台文件")
    try:
        list = os.walk(r"D:/EasiCameraPhoto")
        list2 = []
        for i in list:
            list2.append(i)
        list = list2[0][1]
        for i in list:
            if i != date and os.path.exists(r"D:/EasiCameraPhoto/" + i):
                send2trash.send2trash(os.path.join(r"D:\EasiCameraPhoto\ "[:-1] + i))
    except:
        pass


def b6():
    print("清理回收站")
    try:
        winshell.recycle_bin().empty(confirm=False, show_progress=False, sound=False)
    except:
        pass


def b7():
    print("整理桌面文件")
    key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r'Software\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders')
    path = winreg.QueryValueEx(key, "Desktop")[0] + r"\ "[0:-1]
    move_files(path, "D:/文件/")
    repeat_clear("D:/文件/PPT/")
    repeat_clear("D:/文件/表格/")
    repeat_clear("D:/文件/图片/")
    repeat_clear("D:/文件/文档/")
    repeat_clear("D:/文件/文件夹/")
    repeat_clear("D:/文件/压缩包/")
    repeat_clear("D:/文件/音视频/")


def b8():
    print("整理微信文件")
    try:
        list = []
        list2 = []
        for i in os.walk("D:/WeChat Files/WeChat Files/"):
            list.append(i)
        for i in list[0][1]:
            if os.path.exists(os.path.join("D:/WeChat Files/WeChat Files/", i, "FileStorage\File")):
                list2.append(os.path.join("D:/WeChat Files/WeChat Files/", i, "FileStorage\File"))
        list = []
        list3 = []
        for i in range(len(list2)):
            for j in os.walk(list2[i]):
                list.append(j)
            for k in list[0][1]:
                list3.append(os.path.join(list2[i], k))
        list = list3
        for i in list:
            move_files(i + "/", "D:/文件/")
        repeat_clear("D:/文件/PPT/")
        repeat_clear("D:/文件/表格/")
        repeat_clear("D:/文件/图片/")
        repeat_clear("D:/文件/文档/")
        repeat_clear("D:/文件/文件夹/")
        repeat_clear("D:/文件/压缩包/")
        repeat_clear("D:/文件/音视频/")
    except:
        pass


def b9():
    print("清理整理文件")
    try:
        send2trash.send2trash(r"D:\文件")
    except:
        pass


def b10():
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


def b11():
    print("重启文件资源管理器")
    os.popen("taskkill /f /im explorer.exe")
    time.sleep(0.2)
    os.popen("start c:\windows\explorer.exe")


def b12():
    print("一键整理+清理")
    print("重启PPT小助手")
    os.popen("taskkill -f -im PPTService.exe")
    time.sleep(0.1)
    os.popen("C:\Program Files (x86)\Seewo\PPTService\Main\PPTService.exe")
    print("清理希沃视频展台文件")
    try:
        list = os.walk(r"D:/EasiCameraPhoto")
        list2 = []
        for i in list:
            list2.append(i)
        list = list2[0][1]
        for i in list:
            if i != date and os.path.exists(r"D:/EasiCameraPhoto/" + i):
                send2trash.send2trash(
                    os.path.join(r"D:\EasiCameraPhoto\ "[:-1] + i))
    except:
        pass
    print("清理回收站")
    try:
        winshell.recycle_bin().empty(confirm=False, show_progress=False, sound=False)
    except:
        pass
    print("整理桌面文件")
    key = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                         r'Software\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders')
    path = winreg.QueryValueEx(key, "Desktop")[0] + r"\ "[0:-1]
    move_files(path, "D:/文件/")
    print("整理微信文件")
    try:
        list = []
        list2 = []
        for i in os.walk("D:/WeChat Files/WeChat Files/"):
            list.append(i)
        for i in list[0][1]:
            if os.path.exists(os.path.join("D:/WeChat Files/WeChat Files/", i, "FileStorage\File")):
                list2.append(
                    os.path.join("D:/WeChat Files/WeChat Files/", i, "FileStorage\File"))
        list = []
        list3 = []
        for i in range(len(list2)):
            for j in os.walk(list2[i]):
                list.append(j)
            for k in list[0][1]:
                list3.append(os.path.join(list2[i], k))
        list = list3
        for i in list:
            move_files(i + "/", "D:/文件/")
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
    repeat_clear("D:/文件/PPT/")
    repeat_clear("D:/文件/表格/")
    repeat_clear("D:/文件/图片/")
    repeat_clear("D:/文件/文档/")
    repeat_clear("D:/文件/文件夹/")
    repeat_clear("D:/文件/压缩包/")
    repeat_clear("D:/文件/音视频/")


def b13():
    print("打开点名器")
    os.popen("choose.pyw")
    time.sleep(0.5)
    sys.exit()


# txt = ttk.Label(tk, text="文字").place(x=100,y=,width=200,height=30,anchor="center")
# b = ttk.Button(tk, text="按钮", style="TButton", command=b).place(x=,y=,width=100,height=30)
# sep = Separato3r(tk, orient=HORIZONTAL).place(x=0,y=,width=5000,height=30)

txt = ttk.Label(tk, text="实用程序").place(x=75, y=0, width=150, height=30)
txt = ttk.Label(tk, text="功能列表").place(x=275, y=0, width=150, height=30)
sep = Separator(tk, orient=HORIZONTAL).place(x=0, y=0, width=400, height=2)

# 左侧

b13 = ttk.Button(tk, text="点名器", style="TButton", command=b13).place(x=0, y=30, width=200, height=30)
# 右侧

b12 = ttk.Button(tk, text="一键整理+清理", style="TButton", command=b12).place(x=200, y=30, width=200, height=30)
b1 = ttk.Button(tk, text="重启PPT小助手", style="TButton", command=b1).place(x=200, y=60, width=100, height=30)
b2 = ttk.Button(tk, text="关闭PPT小助手", style="TButton", command=b2).place(x=300, y=60, width=100, height=30)
b9 = ttk.Button(tk, text="清理整理文件", style="TButton", command=b9).place(x=200, y=90, width=100, height=30)
b11 = ttk.Button(tk, text="重启资源管理器", style="TButton", command=b11).place(x=300, y=90, width=100, height=30)
b3 = ttk.Button(tk, text="CCTV-13", style="TButton", command=b3).place(x=200, y=120, width=100, height=30)
b4 = ttk.Button(tk, text="校园电视台", style="TButton", command=b4).place(x=300, y=120, width=100, height=30)
sep = Separator(tk, orient=VERTICAL).place(x=200, y=0, width=1, height=180)
sep = Separator(tk, orient=HORIZONTAL).place(x=0, y=180, width=400, height=2)
txt = ttk.Label(tk, text="郑博的小程序For Seewo 版本  " + v).place(x=40, y=190, width=200, height=30)
b0 = ttk.Button(tk, text="检查并更新版本", style="TButton", command=b0).place(x=260, y=190, width=100, height=30)
sep = Separator(tk, orient=HORIZONTAL).place(x=0, y=230, width=400, height=2)

txt = ttk.Label(tk, text="夹带私货").place(x=175, y=235, width=150, height=30)
b100 = ttk.Button(tk, text="我的网站", style="TButton", command=b100).place(x=0, y=265, width=200, height=30)
b101 = ttk.Button(tk, text="MC版本爬虫", style="TButton", command=b101).place(x=200, y=265, width=200, height=30)

tk.mainloop()
