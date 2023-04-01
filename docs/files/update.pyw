# 导入运行库
import threading, os, re, pickle
from tkinter import *
from tkinter.ttk import *
from tkinter.messagebox import *


def read_setting():
    if os.path.exists("setting.zb"):
        with open("setting.zb", "rb") as file:
            settings = pickle.load(file)
    else:
        settings = ["Myself", 0, None, "E:/整理文件", "D:/Files/Wechat/WeChat Files"] + [None for i in range(100)]
    return settings


settings = read_setting()
edition = settings[0]
# 加载信息
using = False
path = "C:\zb"
if os.path.exists("main.pyw"):
    path = ""
lib_list = ["lxml", "pypiwin32", "pandas", "numpy", "bs4", "requests", "send2trash", "winshell", "matplotlib", "openpyxl", "PyAudio", "python-xlib", "pymouse", "pyautogui", "PyUserInput", "psutil", "wmi"]
# 窗口初始化
tk = Tk()
tk.title(" zb小程序安装器")
x = 200
y = 90
tk.geometry("%dx%d+%d+%d" % (x, y, (tk.winfo_screenwidth() - x) / 2, (tk.winfo_screenheight() - y) / 2))
tk.resizable(False, False)
tk.wm_attributes("-topmost", 1)
st = Style()
st.configure("TButton")

try:
    tk.wm_iconbitmap("logo.ico")
except:
    pass


# 功能

class MyThread(threading.Thread):
    def __init__(self, func, *args):
        super().__init__()

        self.func = func
        self.args = args

        self.setDaemon(True)
        self.start()

    def run(self):
        self.func(*self.args)


def download(link):
    import requests
    response1 = requests.get(link)
    response1.encoding = "UTF-8"
    main = response1.content
    try:
        os.makedirs(os.path.join(path, link[link.rfind("/") + 1:]).replace("//",r"\ "[:-1]))
    except:
        pass
    try:
        os.mkdir(os.path.join(path, link[link.rfind("/") + 1:]).replace("//",r"\ "[:-1]))
    except:
        pass
    with open(os.path.join(path, link[link.rfind("/") + 1:]), "wb") as file:
        file.write(main)


def check_update(name):
    global using
    if using:
        return None
    using = True
    try:
        import requests, bs4
    except:
        showerror("错误", "请先安装运行库！")
        using = False
        return None
    if "E:\编程\server.github.io\docs" in os.getcwd():
        showerror("错误", "当前目录为开发者目录无法更新！")
        using = False
        return None
    if not askokcancel("提示", "是否安装zb小程序？"):
        using = False
        return None
    link = "https://ianzb.github.io/server.github.io/files/"
    res = requests.get(link + "index.html")
    res.encoding = "UTF-8"
    soup = bs4.BeautifulSoup(res.text, "lxml")
    data = soup.find_all(name="div", class_="download", text=re.compile("."))
    for i in range(len(data)): data[i] = str(data[i]).replace('<div class="download">', "").replace("</div>", "").strip()
    for i in range(len(data)):
        print(data[i])
        MyThread(download(link + data[i]))
        vari.set(int(100 * i / len(data)))
        tk.update()
    showinfo("提示", "zb小程序安装完毕！")
    os.popen(os.path.join(path, "main.pyw"))
    vari.set(100)
    using = False
    exit()


def pip_install(a):
    os.system("pip install " + a + " -i http://mirrors.aliyun.com/pypi/simple/ --trusted-host mirrors.aliyun.com")
    os.system("pip install --upgrade " + a + " -i http://mirrors.aliyun.com/pypi/simple/ --trusted-host mirrors.aliyun.com")


def download_lib():
    global using
    if using:
        return False
    using = True
    for i in range(len(lib_list)):
        pip_install(lib_list[i])
        vari.set(int(100 * (i + 1) / len(lib_list)))
    vari.set(100)
    showinfo("提示", "运行库安装完毕，重启安装器生效！")
    using = False
    exit()


# 控件

vari = IntVar()
vari.set(0)
Progressbar(tk, mode="determinate", variable=vari).place(x=0, y=0, width=200, height=30)
Button(tk, text="立刻安装 zb小程序 " + edition, style="TButton", command=lambda: MyThread(check_update(edition))).place(x=0, y=30, width=200, height=30)
Button(tk, text="安装 zb小程序 运行库", style="TButton", command=lambda: MyThread(download_lib)).place(x=0, y=60, width=200, height=30)

tk.mainloop()
