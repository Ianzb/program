# 程序信息
version = "2.1.1"
edition = "Myself"

# 导入运行库
import os, sys, threading, webbrowser
from tkinter import *
from tkinter import ttk
from tkinter.messagebox import *

try:
    from zb import *
except:
    os.system("fix.bat")
    sys.exit()

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


# 功能

def b1():
    os.popen("manger.pyw")
    exit()


def b2():
    pro5 = threading.Thread(target=clear_rubbish)
    pro5.start()
    pro6 = threading.Thread(target=clear_cache)
    pro6.start()
    pro7 = threading.Thread(target=clear_desk("E:/整理文件"))
    pro7.start()
    pro8 = threading.Thread(target=clear_wechat("D:/Files/Wechat/WeChat Files", "E:/整理文件"))
    pro8.start()
    pro9 = threading.Thread(target=clear_apps)
    pro9.start()
    pro10 = threading.Thread(target=clear_repeat("E:/整理文件"))
    pro10.start()


def b3():
    os.startfile("E:/整理文件")


def b4():
    pro4 = threading.Thread(target=clear_rubbish)
    pro4.start()


def b5():
    pro3 = threading.Thread(target=restart_explorer)
    pro3.start()


def b6():
    webbrowser.open("https://ianzb.github.io/")


def b7():
    pro2 = threading.Thread(target=get_mc)
    pro2.start()


def b8():
    os.popen(pj(os.getcwd(), "update.pyw"))
    exit()


def b9():
    pro11 = threading.Thread(target=sys_info)
    pro11.start()


# 控件
ttk.Label(tk, text="实用程序").place(x=75, y=0, width=150, height=30)
ttk.Label(tk, text="功能列表").place(x=275, y=0, width=150, height=30)
ttk.Separator(tk, orient=HORIZONTAL).place(x=0, y=0, width=400, height=2)
# 左侧
ttk.Button(tk, text="zb的小程序管理器", style="TButton", command=b1).place(x=0, y=30, width=200, height=30)
# 右侧
ttk.Button(tk, text="一键整理+清理", style="TButton", command=b2).place(x=200, y=30, width=150, height=30)
ttk.Button(tk, text="打开", style="TButton", command=b3).place(x=350, y=30, width=50, height=30)
ttk.Button(tk, text="清理回收站", style="TButton", command=b4).place(x=200, y=60, width=100, height=30)
ttk.Button(tk, text="重启资源管理器", style="TButton", command=b5).place(x=300, y=60, width=100, height=30)
ttk.Button(tk, text="我的网站", style="TButton", command=b6).place(x=200, y=90, width=100, height=30)
ttk.Button(tk, text="MC版本爬虫", style="TButton", command=b7).place(x=300, y=90, width=100, height=30)

ttk.Button(tk, text="查看系统信息", style="TButton", command=b9).place(x=200, y=120, width=200, height=30)
ttk.Separator(tk, orient=VERTICAL).place(x=200, y=0, width=1, height=150)
ttk.Separator(tk, orient=HORIZONTAL).place(x=0, y=150, width=400, height=2)
ttk.Label(tk, text="zb的小程序For " + edition + " 版本  " + version).place(x=60, y=160, width=200, height=30)
ttk.Button(tk, text="检查更新", style="TButton", command=b8).place(x=260, y=160, width=80, height=30)
ttk.Separator(tk, orient=HORIZONTAL).place(x=0, y=150, width=400, height=2)

tk.mainloop()
