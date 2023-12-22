import threading, os, sys, json
from tkinter import *
from tkinter import ttk
from tkinter.ttk import *
from tkinter.messagebox import *
from tkinter.filedialog import *


class MyThread(threading.Thread):
    """
    多线程优化
    """

    def __init__(self, func, *args):
        super().__init__()

        self.func = func
        self.args = args

        self.daemon = True
        self.start()

    def run(self):
        self.func(*self.args)


class ProgramInit():
    """
    zb小程序信息类-处理信息
    """
    PROGRAM_NAME = "zb小程序"  # 程序名称
    PROGRAM_VERSION = "安装器"  # 程序版本
    PROGRAM_TITLE = f"{PROGRAM_NAME} {PROGRAM_VERSION}"  # 程序窗口标题
    PROGRAM_MAIN_FILE_PATH = sys.argv[0].replace("download.pyw", "main.pyw")  # 程序主文件路径
    USER_PATH = os.path.expanduser("~")  # 系统用户路径
    PROGRAM_PATH = os.path.join(USER_PATH, "zb")  # 程序安装路径
    STARTUP_ARGUMENT = sys.argv[1:]  # 程序启动参数
    CHANNEL = "正式版"  # 程序更新通道
    REQUEST_HEADER = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0"}  # 程序默认网络请求头
    REQUIRE_LIB = ["PyQt-Fluent-Widgets",
                   "qt5_tools",
                   "requests",
                   "bs4",
                   "lxml",
                   "pypiwin32",
                   "pandas",
                   "winshell",
                   "xmltodict",
                   ]

    @property
    def DESKTOP_PATH(self) -> str:
        """
        获得桌面路径
        @return: 桌面路径
        """
        import winreg
        return winreg.QueryValueEx(winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders"), "Desktop")[0]

    @property
    def isStartup(self) -> bool:
        """
        判断程序是否为开机自启动
        @return: bool
        """
        return "startup" in self.STARTUP_ARGUMENT

    @property
    def UPDATE_URL(self) -> str:
        """
        获得更新网址
        @return: 网址
        """
        if self.CHANNEL == "正式版":
            return "https://vip.123pan.cn/1813801926/program/index.json"
        elif self.CHANNEL == "抢先版":
            return "https://ianzb.github.io/program/release/index.json"
        elif self.CHANNEL == "测试版":
            return "https://ianzb.github.io/program/beta/index.json"



program = ProgramInit()


class Functions():
    """
    程序相关函数
    """

    def formatPath(self, path: str) -> str:
        """
        格式化路径
        @param path: 路径
        @return: 格式化结果
        """
        path = os.path.normpath(path).replace("//", r"\ "[:-1]).replace("\\ "[:-1], r"\ "[:-1])
        return path

    def pathJoin(self, *data) -> str:
        """
        拼接路径
        @param data: 多个字符串参数
        @return: 拼接后的字符串
        """
        path = ""
        for i in data:
            path = os.path.join(path, i)
        return self.formatPath(path)

    def existPath(self, path: str) -> bool:
        """
        文件是否存在
        @param path: 文件路径
        @return: bool
        """
        return os.path.exists(path)

    def splitPath(self, path: str, mode: int = 0) -> str:
        """
        分割路径信息
        @param path: 文件路径
        @param mode: 模式：0 文件完整名称 1 文件名称 2 文件扩展名 3 文件所在目录
        @return: 文件名信息
        """
        if mode == 0:
            return os.path.basename(path)
        if mode == 1:
            return os.path.splitext(os.path.basename(path))[0]
        if mode == 2:
            return os.path.splitext(os.path.basename(path))[1]
        if mode == 3:
            return os.path.dirname(path)

    def makeDir(self, path: str):
        """
        创建文件夹
        @param path: 文件路径
        """
        if not self.existPath(path):
            os.makedirs(path)

    def downloadFile(self, link: str, path: str):
        """
        下载文件
        @param link: 文件链接
        @param path: 下载路径
        """
        try:
            import requests
            path = os.path.abspath(path)
            data = requests.get(link, headers=program.REQUEST_HEADER)
            self.makeDir(self.splitPath(path, 3))
            with open(path, "wb") as file:
                file.write(data.content)
        except:
            showerror("提示", f"{program.PROGRAM_NAME}无法正常安装，可能是由于运行库缺失，请您在安装前先安装运行库！")

    def urlJoin(self, *args):
        """
        拼接网址
        @param args: 网址
        @return: 拼接结果
        """
        import urllib.parse
        data = ""
        for i in range(len(args)):
            data = urllib.parse.urljoin(data, args[i])
        return data

    def cmd(self, command: str, pause: bool = False) -> str:
        """
        简单的使用cmd
        @param command: 命令
        @param pause: 是否返回输出结果
        @return: 输出结果
        """
        value = os.popen(command)
        if pause:
            return value.read()

    def pipTest(self):
        """
        测试pip是否生效
        @return: 是否生效
        """
        return "pip <command> [options]" in self.cmd("pip", True)

    def pipInstall(self, lib_name: str | list):
        """
        pip安装运行库
        @param lib_name: 运行库名称
        """
        button1.config(state=DISABLED)
        button2.config(state=DISABLED)
        button3.config(state=DISABLED)
        combobox.config(state=DISABLED)
        if f.pipTest():
            if type(lib_name) is str:
                self.cmd(f"pip install {lib_name} -i https://pypi.tuna.tsinghua.edu.cn/simple some-package", True)
            elif type(lib_name) is list:
                for i in range(len(lib_name)):
                    self.cmd(f"pip install {lib_name[i]} -i https://pypi.tuna.tsinghua.edu.cn/simple some-package", True)
                    progress.set(int(100 * (i + 1) / len(lib_name)))
                progress.set(100)
                showinfo("提示", "运行库安装成功！")
                progress.set(0)
        else:
            showwarning("警告", "Python未添加环境变量，pip无法使用，无法安装运行库！请依次尝试重启安装器、等待一段时间后重试或重启电脑！")
        button1.config(state=NORMAL)
        button2.config(state=NORMAL)
        button3.config(state=NORMAL)
        combobox.config(state=NORMAL)

    def installProgram(self):
        """
        安装应用
        """

        if not askyesno(f"是否要安装{program.PROGRAM_NAME}", f"当前设置的安装目录为：\n{program.PROGRAM_PATH}\n更新通道：{program.CHANNEL}"):
            return
        button1.config(state=DISABLED)
        button2.config(state=DISABLED)
        button3.config(state=DISABLED)
        combobox.config(state=DISABLED)

        try:
            import requests
            response = requests.get(program.UPDATE_URL, headers=program.REQUEST_HEADER, stream=True).text
            data = json.loads(response)["list"]
            for i in range(len(data)):
                self.downloadFile(f.urlJoin(program.UPDATE_URL, data[i]), f.pathJoin(program.PROGRAM_PATH, data[i]))
                progress.set(int(100 * (i + 1) / len(data)))
            open(f.pathJoin(program.PROGRAM_PATH, "source/__init__.py"), "w").close()
            progress.set(100)
            try:
                self.createShortcut(f.pathJoin(program.PROGRAM_PATH, "main.pyw"), self.pathJoin(program.DESKTOP_PATH, "zb小程序.lnk"), program.source("program.ico"))
                self.createShortcut(f.pathJoin(program.PROGRAM_PATH, "main.pyw"), self.pathJoin(program.USER_PATH, r"AppData\Roaming\Microsoft\Windows\Start Menu\Programs", "zb小程序.lnk"), program.source("program.ico"))
                showinfo("提示", f"{program.PROGRAM_NAME}安装成功，将会自动运行程序！")
            except Exception as ex:
                showinfo("提示", f"{program.PROGRAM_NAME}安装成功，但添加快捷方式时出现问题，将会自动运行程序，请您在程序的关于页面中手动添加快捷方式！\n报错信息：{ex}")
            self.cmd(f.pathJoin(program.PROGRAM_PATH, "main.pyw"))
            sys.exit()
        except Exception as ex:
            showerror("提示", f"{program.PROGRAM_NAME}无法正常安装，可能是由于运行库缺失，请您在安装前先安装运行库！\n报错信息：{ex}")
        button1.config(state=NORMAL)
        button2.config(state=NORMAL)
        button3.config(state=NORMAL)
        combobox.config(state=NORMAL)

    def switchInstallPath(self):
        button1.config(state=DISABLED)
        button2.config(state=DISABLED)
        button3.config(state=DISABLED)
        combobox.config(state=DISABLED)
        data = askdirectory(title="选择安装目录", initialdir=program.PROGRAM_PATH)
        if data:
            program.PROGRAM_PATH = data
        text.set(f"当前安装路径：{program.PROGRAM_PATH}")
        button1.config(state=NORMAL)
        button2.config(state=NORMAL)
        button3.config(state=NORMAL)
        combobox.config(state=NORMAL)

    def switchChannal(self, event):
        program.CHANNEL = combobox.get()

    def createShortcut(self, old: str, new: str, icon: str, arguments: str = ""):
        """
        创建快捷方式
        @param old: 源文件路径
        @param new: 新文件路径
        @param icon: 图标
        @param arguments: 参数
        """
        import win32com.client
        if not new.endswith(".lnk"):
            new += ".lnk"
        shell = win32com.client.Dispatch("WScript.Shell")
        shortcut = shell.CreateShortCut(new)
        shortcut.Targetpath = old
        shortcut.IconLocation = icon
        shortcut.Arguments = arguments
        shortcut.save()

    def addToStartup(self, name: str, path: str, mode: bool = True):
        """
        添加开机自启动
        @param name: 启动项名字
        @param path: 文件路径
        @param mode: True添加/False删除
        """
        import win32api, win32con
        key = win32api.RegOpenKey(win32con.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run", 0, win32con.KEY_ALL_ACCESS)
        if mode:
            win32api.RegSetValueEx(key, name, 0, win32con.REG_SZ, f"{path} startup")
            win32api.RegCloseKey(key)
        else:
            win32api.RegDeleteValue(key, name)
            win32api.RegCloseKey(key)


f = Functions()
if "error" in program.STARTUP_ARGUMENT:
    showerror("提示", f"{program.PROGRAM_NAME}无法正常运行，可能是由于运行库缺失，现已自动启动安装器，请您自行点击安装运行库！")

tk = Tk()
tk.title(f"{program.PROGRAM_NAME}安装器")
x = 500
y = 400
tk.geometry("%dx%d+%d+%d" % (x, y, (tk.winfo_screenwidth() - x) / 2, (tk.winfo_screenheight() - y) / 2))
tk.resizable(False, False)
tk.wm_attributes("-topmost", 1)
st = Style()
st.configure("TButton")

progress = IntVar()
progress.set(0)
progressbar = ttk.Progressbar(tk, variable=progress)
progressbar.place(x=50, y=150, width=400, height=25)

button1 = ttk.Button(tk, text=f"安装 {program.PROGRAM_NAME} 最新版", style="TButton", command=lambda: MyThread(f.installProgram))
button1.place(x=330, y=350, width=150, height=30)
button2 = ttk.Button(tk, text=f"安装 {program.PROGRAM_NAME} 运行库", style="TButton", command=lambda: MyThread(lambda: f.pipInstall(program.REQUIRE_LIB)))
button2.place(x=160, y=350, width=150, height=30)

label1 = ttk.Label(tk, text=f"欢迎安装 {program.PROGRAM_NAME}", font=("等线", 20))
label1.config(anchor=CENTER, justify=CENTER)
label1.place(x=0, y=10, width=500, height=50)

text = StringVar()
label2 = ttk.Label(tk, textvariable=text)
label2.config(anchor=CENTER, justify=CENTER)
label2.place(x=0, y=250, width=500, height=30)
text.set(f"当前安装路径：{program.PROGRAM_PATH}")

button3 = ttk.Button(tk, text="选择安装路径", style="TButton", command=f.switchInstallPath)
button3.place(x=260, y=300, width=100, height=30)

channel = StringVar()
combobox = ttk.Combobox(tk, textvariable=channel)
combobox.place(x=380, y=300, width=100, height=30)
combobox["value"] = ["正式版", "抢先版", "测试版"]
combobox["state"] = "readonly"
combobox.current(0)

combobox.bind("<<ComboboxSelected>>", f.switchChannal)

tk.mainloop()
