# 导入运行库
import threading, os, re, pickle, sys, winreg, shutil, urllib.parse
from tkinter import *
from tkinter import ttk
from tkinter.ttk import *
from tkinter.messagebox import *
from tkinter.filedialog import *

old_path = os.getcwd()
abs_path = sys.argv[0][:sys.argv[0].rfind(r"\ "[:-1])]
abs_name = sys.argv[0][sys.argv[0].rfind(r"\ "[:-1]) + 1:]
abs_cache = abs_name[:abs_name.rfind(".")]
abs_pid = os.getpid()
user_path = os.path.expanduser("~")
abs_desktop = winreg.QueryValueEx(winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders"), "Desktop")[0]
install_path = os.path.join(user_path, "zb")
if not os.path.exists(install_path):
    os.makedirs(install_path)
# 加载信息
using = False
lib_list = ["PyQt-Fluent-Widgets[full]", "requests", "bs4", "lxml", "pypiwin32", "pandas", "send2trash", "winshell"]
# 窗口初始化
tk = Tk()
tk.title("zb小程序安装器")
x = 200
y = 150
tk.geometry("%dx%d+%d+%d" % (x, y, (tk.winfo_screenwidth() - x) / 2, (tk.winfo_screenheight() - y) / 2))
tk.resizable(False, False)
tk.wm_attributes("-topmost", 1)
st = Style()
st.configure("TButton")


# 功能
# 路径拼接
def join(*data):
    path = ""
    for i in data:
        path = os.path.join(path, i)
    path = path.replace("//", r"\ "[:-1]).replace(r"\\ "[:-1], r"\ "[:-1]).replace("\/", r"\ "[:-1]).replace("/\ "[:-1], r"\ "[:-1]).replace("/", r"\ "[:-1])
    return path


# 网址拼接
def urlJoin(url1, url2):
    return urllib.parse.urljoin(url1, url2)


try:
    os.makedirs(join(user_path, "zb"))
except:
    pass


class MyThread(threading.Thread):
    def __init__(self, func, *args):
        super().__init__()

        self.func = func
        self.args = args

        self.daemon = True
        self.start()

    def run(self):
        self.func(*self.args)


def download(link):
    import requests
    response1 = requests.get(link)
    response1.encoding = "UTF-8"
    main = response1.content
    if not os.path.exists(join(install_path, link.replace("https://ianzb.github.io/program/Windows/", ""))[:join(install_path, link.replace("https://ianzb.github.io/program/Windows/", "")).rfind("\ "[:-1])]):
        os.makedirs(join(install_path, link.replace("https://ianzb.github.io/program/Windows/", ""))[:join(install_path, link.replace("https://ianzb.github.io/program/Windows/", "")).rfind("\ "[:-1])])
    with open(join(install_path, link.replace("https://ianzb.github.io/program/Windows/", "")), "wb") as file:
        file.write(main)


def check_update(link):
    if not os.path.exists(install_path):
        os.makedirs(install_path)
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
    if "program" in os.getcwd() and "编程" in install_path:
        showerror("错误", "当前目录为开发者目录无法安装！")
        using = False
        return None
    if not askokcancel("提示", "是否安装zb小程序？"):
        using = False
        return None
    res = requests.get(urlJoin(link, "index.html"))
    res.encoding = "UTF-8"
    soup = bs4.BeautifulSoup(res.text, "lxml")
    data = soup.find_all(name="div", class_="download", string=re.compile("."))
    for i in range(len(data)): data[i] = data[i].text.strip()
    for i in range(len(data)):
        download(urlJoin(link, data[i]))
        vari.set(int(100 * i / len(data)))
        tk.update()
    showinfo("提示", "zb小程序安装完毕！")
    os.popen(join(install_path, "main.pyw"))
    vari.set(100)
    using = False
    exit()


def pip_install(name):
    p = os.popen("pip install " + name + " -i https://pypi.tuna.tsinghua.edu.cn/simple some-package")
    print(p.read())
    p = os.popen("pip install --upgrade " + name + " -i https://pypi.tuna.tsinghua.edu.cn/simple some-package")
    print(p.read())


def download_lib(list):
    global using
    if using:
        return False
    using = True
    for i in range(len(list)):
        pip_install(list[i])
        vari.set(int(100 * (i + 1) / len(list)))
    vari.set(100)
    showinfo("提示", "运行库安装完毕，重启安装器生效！")
    vari.set(0)
    using = False


def show():
    global install_path
    install_path = askdirectory(title="选择安装目录", initialdir=install_path)
    text.set(install_path)


text = StringVar()
label = ttk.Label(tk, textvariable=text)
label.place(x=0, y=115, width=200, height=35)
text.set(install_path)
ttk.Button(tk, text="选择安装目录", style="TButton", command=show).place(x=0, y=80, width=200, height=35)

# 控件

vari = IntVar()
vari.set(0)
ttk.Progressbar(tk, mode="determinate", variable=vari).place(x=0, y=0, width=200, height=10)
ttk.Button(tk, text="安装 zb小程序 最新版", style="TButton", command=lambda: MyThread(lambda: check_update("https://ianzb.github.io/program/Windows/"))).place(x=0, y=10, width=200, height=35)
ttk.Button(tk, text="安装 zb小程序 运行库", style="TButton", command=lambda: MyThread(lambda: download_lib(lib_list))).place(x=0, y=45, width=200, height=35)
tk.mainloop()
