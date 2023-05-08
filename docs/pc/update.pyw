# 导入运行库
from zb import *

check()
disable("update.txt")
# 读取信息

using = False
lib_list = ["PyQt5-sip","pyqt5-tools","PyQt5","PyQt5Designer","PyQt-Fluent-Widgets[full]","sv-ttk", "lxml", "pypiwin32", "pandas", "numpy", "bs4", "requests", "send2trash", "winshell", "matplotlib", "openpyxl", "PyAudio", "python-xlib", "pymouse", "pyautogui", "PyUserInput", "psutil", "wmi"]

# 窗口初始化

tk = Tk()
tk.title("更新程序")
x = 200
y = 80
tk.geometry("%dx%d+%d+%d" % (x, y, (tk.winfo_screenwidth() - x) / 2, (tk.winfo_screenheight() - y) / 2))
tk.resizable(False, False)
tk.wm_attributes("-topmost", 1)
check_ico(tk, "logo.ico")
st = Style()
st.configure("TButton")
if settings[5] == "Win11浅色模式":
    sv_ttk.use_light_theme()
elif settings[5] == "Win11深色模式":
    sv_ttk.use_dark_theme()


# 功能


def check_update(name):
    showerror("错误", "tkinter版已停更，4.8.3版本为最终版本！")


def download_lib(list=lib_list):
    logging.info("开始安装运行库")
    global using
    if using:
        return False
    using = True
    for i in range(len(list)):
        pip_install(list[i])
        vari.set(int(100 * (i + 1) / len(list)))
        tk.update()
    vari.set(100)
    showinfo("提示", "运行库安装完毕，重启检查更新模块生效！")
    vari.set(0)
    using = False
    logging.info("成功安装运行库")


# 控件
vari = IntVar()
vari.set(0)
ttk.Progressbar(tk, mode="determinate", variable=vari).place(x=0, y=0, width=200, height=10)
ttk.Button(tk, text="更新 zb小程序 至最新版本", style="TButton", command=lambda: MyThread(lambda: check_update(settings[0]))).place(x=0, y=10, width=200, height=35)
ttk.Button(tk, text="安装 zb小程序 运行库", style="TButton", command=lambda: MyThread(lambda: download_lib(lib_list))).place(x=0, y=45, width=200, height=35)
close()
tk.mainloop()
