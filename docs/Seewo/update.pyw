# 程序信息
edition = "Seewo"

# 导入运行库
import threading, os, re, time
from tkinter import *
from tkinter import ttk
from tkinter.messagebox import *

if os.path.exists("update.txt"):
    exit()
with open(file="update.txt", mode="w") as file:
    file.write("zb小程序安装器运行时请勿删除此文件，如关闭后无法再次打开安装器请删除此文件")

# 加载信息
path = os.getcwd()
using = False
lib_list = ["lxml", "pypiwin32", "pandas", "numpy", "bs4", "requests", "send2trash", "winshell", "matplotlib", "openpyxl", "PyAudio", "python-xlib", "pymouse", "pyautogui", "PyUserInput", "psutil", "wmi"]

# 窗口初始化
tk = Tk()
tk.title(" zb小程序安装模块")
x = 200
y = 120
tk.geometry("%dx%d+%d+%d" % (x, y, (tk.winfo_screenwidth() - x) / 2, (tk.winfo_screenheight() - y) / 2))
tk.resizable(False, False)
tk.wm_attributes("-topmost", 1)
st = ttk.Style()
st.configure("TButton")

try:
    tk.wm_iconbitmap("logo.ico")
except:
    pass


def hide():
    try:
        os.remove("update.txt")
    except:
        pass
    tk.destroy()


tk.protocol('WM_DELETE_WINDOW', hide)


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


def reflash():
    while True:
        tk.update()


def download(link):
    MyThread(reflash)
    import requests
    response1 = requests.get(link)
    response1.encoding = "UTF-8"
    main = response1.content
    with open(link[link.rfind("/") + 1:], "wb") as file:
        file.write(main)


def check_update(name):
    global using
    if using == True:
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
    if askokcancel("提示", "是否更新？") == False:
        using = False
        return None
    link = "https://ianzb.github.io/server.github.io/" + name + "/"
    res = requests.get(link + "index.html")
    res.encoding = "UTF-8"
    soup = bs4.BeautifulSoup(res.text, "lxml")
    data = soup.find_all(name="div", class_="download", text=re.compile("."))
    for i in range(len(data)): data[i] = str(data[i]).replace(r'<div class="download">', "").replace("</div>", "").strip()
    print(data)
    for i in range(len(data)):
        MyThread(download(link + data[i]))
        vari.set(int(100 * i / len(data)))
        tk.update()
    os.popen("main.pyw")
    vari.set(100)
    using = False
    try:
        os.remove("update.txt")
    except:
        pass
    exit()


def pip_install(a):
    os.system("pip install " + a + " -i http://mirrors.aliyun.com/pypi/simple/ --trusted-host mirrors.aliyun.com")
    os.system("pip install --upgrade " + a + " -i http://mirrors.aliyun.com/pypi/simple/ --trusted-host mirrors.aliyun.com")


def download_lib():
    global using
    if using == True:
        return False
    using = True
    for i in range(len(lib_list)):
        pip_install(lib_list[i])
        vari.set(int(100 * i / len(lib_list)))
    vari.set(100)
    showinfo("提示", "运行库安装完毕！")
    vari.set(0)
    using = False


# 此处代码来自https://blog.csdn.net/weixin_43945855/article/details/103567811
try:
    import win32api, win32con, winreg, os


    """判断键是否存在"""


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


    """开机自启动"""


    def AutoRun(switch="open",  # 开：open # 关：close
                zdynames=None,
                current_file=None,
                abspath=os.path.abspath(os.path.dirname(__file__))):
        """
        :param switch: 注册表开启、关闭自启动
        :param zdynames: 当前文件名
        :param current_file: 获得文件名的前部分
        :param abspath: 当前文件路径
        :return:
        """
        print(zdynames)

        path = abspath + '\\' + zdynames  # 要添加的exe完整路径如：
        judge_key = Judge_Key(reg_root=win32con.HKEY_CURRENT_USER,
                              reg_path=r"Software\Microsoft\Windows\CurrentVersion\Run",  # 键的路径
                              key_name=current_file)
        # 注册表项名
        KeyName = r'Software\Microsoft\Windows\CurrentVersion\Run'
        key = win32api.RegOpenKey(win32con.HKEY_CURRENT_USER, KeyName, 0, win32con.KEY_ALL_ACCESS)
        if switch == "open":
            # 异常处理
            try:
                if judge_key == 0:
                    print("已经开启了，无需再开启")
                elif judge_key == 1:
                    win32api.RegSetValueEx(key, current_file, 0, win32con.REG_SZ, path)
                    win32api.RegCloseKey(key)
                    print('开机自启动添加成功！')
            except:
                print('添加失败')
        elif switch == "close":
            try:
                if judge_key == 0:
                    win32api.RegDeleteValue(key, current_file)  # 删除值
                    win32api.RegCloseKey(key)
                    print('成功删除键！')
                elif judge_key == 1:
                    print("键不存在")
                elif judge_key == 2:
                    print("权限不足")
                else:
                    print("出现错误")
            except:
                print('删除失败')
except:
    pass

# 控件

vari = IntVar()
vari.set(0)
ttk.Progressbar(tk, mode="determinate", variable=vari).place(x=0, y=0, width=200, height=30)
ttk.Button(tk, text="立刻安装 zb小程序 for " + edition, style="TButton", command=lambda: MyThread(check_update(edition))).place(x=0, y=30, width=200, height=30)
ttk.Button(tk, text="安装 zb小程序 运行库", style="TButton", command=lambda: MyThread(download_lib)).place(x=0, y=60, width=200, height=30)
ttk.Button(tk, text="添加开机自启动", style="TButton", command=lambda: AutoRun(switch="open", zdynames=os.path.basename("hide.pyw"), current_file=os.path.splitext(os.path.basename("hide.pyw"))[0], abspath=os.path.abspath(os.path.dirname("hide.pyw")))).place(x=0, y=90, width=100, height=30)
ttk.Button(tk, text="取消开机自启动", style="TButton", command=lambda: AutoRun(switch="close", zdynames=os.path.basename("hide.pyw"), current_file=os.path.splitext(os.path.basename("hide.pyw"))[0], abspath=os.path.abspath(os.path.dirname("hide.pyw")))).place(x=100, y=90, width=100, height=30)

tk.mainloop()
