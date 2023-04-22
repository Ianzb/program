# 导入运行库
import threading, os, re, pickle, sys
from tkinter import *
from tkinter import ttk
from tkinter.ttk import *
from tkinter.messagebox import *

os.chdir(sys.argv[0][:sys.argv[0].rfind(r"\ "[:-1])])


def read_setting():
    if os.path.exists("setting.zb"):
        with open("setting.zb", "rb") as file:
            settings = pickle.load(file)
    else:
        settings = ["作者个人版", 0, 30, "D:/文件/整理", "D:/文件/应用/微信/WeChat Files"] + [None for i in range(100)]
    return settings


settings = read_setting()
# 加载信息
using = False
lib_list = ["sv-ttk", "lxml", "pypiwin32", "pandas", "numpy", "bs4", "requests", "send2trash", "winshell", "matplotlib", "openpyxl", "PyAudio", "python-xlib", "pymouse", "pyautogui", "PyUserInput", "psutil", "wmi"]
# 窗口初始化
tk = Tk()
tk.title("zb小程序安装器")
x = 200
y = 80
tk.geometry("%dx%d+%d+%d" % (x, y, (tk.winfo_screenwidth() - x) / 2, (tk.winfo_screenheight() - y) / 2))
tk.resizable(False, False)
tk.wm_attributes("-topmost", 1)
st = Style()
st.configure("TButton")
try:
    import sv_ttk

    if settings[5] == "Win11浅色模式":
        sv_ttk.use_light_theme()
    elif settings[5] == "Win11深色模式":
        sv_ttk.use_dark_theme()
except:
    pass
try:
    tk.wm_iconbitmap("logo.ico")
except:
    pass


# 功能
def pj(*a):
    out = ""
    for i in a:
        out = os.path.join(out, i)
    out = out.replace("//", r"\ "[:-1]).replace(r"\\ "[:-1], r"\ "[:-1]).replace("\/", r"\ "[:-1]).replace("/\ "[:-1], r"\ "[:-1]).replace("/", r"\ "[:-1])
    return out


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
    with open(link[link.rfind("/") + 1:], "wb") as file:
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
        showerror("错误", "当前目录为开发者目录无法安装！")
        using = False
        return None
    if not askokcancel("提示", "是否安装zb小程序？"):
        using = False
        return None
    link = "https://ianzb.github.io/server.github.io/pc/"
    res = requests.get(link + "index.html")
    res.encoding = "UTF-8"
    soup = bs4.BeautifulSoup(res.text, "lxml")
    data = soup.find_all(name="div", class_="download", text=re.compile("."))
    for i in range(len(data)): data[i] = str(data[i]).replace('<div class="download">', "").replace("</div>", "").strip()
    for i in range(len(data)):
        download(link + data[i])
        vari.set(int(100 * i / len(data)))
        tk.update()
    showinfo("提示", "zb小程序安装完毕！")
    os.popen("main.pyw")
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
    vari.set(0)
    using = False
    exit()


# 控件

vari = IntVar()
vari.set(0)
ttk.Progressbar(tk, mode="determinate", variable=vari).place(x=0, y=0, width=200, height=10)
ttk.Button(tk, text="安装 zb小程序 " + settings[0], style="TButton", command=lambda: MyThread(check_update(settings[0]))).place(x=0, y=10, width=200, height=35)
ttk.Button(tk, text="安装 zb小程序 运行库", style="TButton", command=lambda: MyThread(download_lib)).place(x=0, y=45, width=200, height=35)

tk.mainloop()
