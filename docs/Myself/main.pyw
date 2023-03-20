# 程序信息

version = "2.7.1"
edition = "Myself"

# 导入运行库
import sys, webbrowser, time, os

try:
    from zb import *

    check()
    disable("main.txt")
except:
    os.popen("update.pyw")
    os.remove("main.txt")
    sys.exit()

start()
from tkinter import *
from tkinter import ttk

# 窗口初始化

tk = Tk()
tk.title(" zb的小程序For " + edition + " " + version)
x = 400
y = 200
tk.geometry("%dx%d+%d+%d" % (x, y, (tk.winfo_screenwidth() - x) / 2, (tk.winfo_screenheight() - y) / 2))
tk.resizable(False, False)
tk.wm_attributes("-topmost", 1)
check_ico(tk, "logo.ico")
st = ttk.Style()
st.configure("TButton")


def hide():
    os.popen("hide.pyw")
    enable("main.txt")
    exit()


tk.protocol('WM_DELETE_WINDOW', hide)


# 功能


def b1():
    os.popen("manger.pyw")
    enable("main.txt")
    exit()


def b2():
    clear_rubbish()
    clear_cache()
    clear_desk("E:/整理文件")
    clear_wechat("D:/Files/Wechat/WeChat Files", "E:/整理文件")
    clear_apps()
    clear_repeat("E:/整理文件")


def b3():
    os.popen(pj(os.getcwd(), "update.pyw"))
    enable("main.txt")
    exit()


# 控件
ttk.Label(tk, text="实用程序").place(x=75, y=0, width=150, height=30)
ttk.Label(tk, text="功能列表").place(x=275, y=0, width=150, height=30)
ttk.Separator(tk, orient=HORIZONTAL).place(x=0, y=0, width=400, height=2)
# 左侧
ttk.Button(tk, text="zb的小程序管理器", style="TButton", command=lambda: MyThread(b1)).place(x=0, y=30, width=200, height=30)
# 右侧
ttk.Button(tk, text="一键整理+清理", style="TButton", command=lambda: MyThread(b2)).place(x=200, y=30, width=150, height=30)
ttk.Button(tk, text="打开", style="TButton", command=lambda: MyThread(os.startfile("E:/整理文件"))).place(x=350, y=30, width=50, height=30)
ttk.Button(tk, text="清理回收站", style="TButton", command=lambda: MyThread(clear_rubbish())).place(x=200, y=60, width=100, height=30)
ttk.Button(tk, text="重启资源管理器", style="TButton", command=lambda: MyThread(restart_explorer())).place(x=300, y=60, width=100, height=30)
ttk.Button(tk, text="强制关闭程序", style="TButton", command=lambda: MyThread(kill_py)).place(x=200, y=90, width=100, height=30)
ttk.Button(tk, text="MC版本爬虫", style="TButton", command=lambda: MyThread(get_mc)).place(x=300, y=90, width=100, height=30)
ttk.Button(tk, text="我的网站", style="TButton", command=lambda: MyThread(webbrowser.open("https://ianzb.github.io/"))).place(x=200, y=120, width=100, height=30)
ttk.Button(tk, text="查看系统信息", style="TButton", command=lambda: MyThread(sys_info)).place(x=300, y=120, width=100, height=30)
ttk.Separator(tk, orient=VERTICAL).place(x=200, y=0, width=1, height=150)
ttk.Separator(tk, orient=HORIZONTAL).place(x=0, y=150, width=400, height=2)
ttk.Label(tk, text="zb的小程序For " + edition + " 版本  " + version).place(x=60, y=160, width=200, height=30)
ttk.Button(tk, text="检查更新", style="TButton", command=lambda: MyThread(b3)).place(x=260, y=160, width=80, height=30)
ttk.Separator(tk, orient=HORIZONTAL).place(x=0, y=150, width=400, height=2)
close()
tk.mainloop()
