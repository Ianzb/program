# 程序信息
version = "3.1.2"
edition = "Seewo"

# 导入运行库
import threading, webbrowser, os, sys, time
from tkinter import *
from tkinter import ttk

try:
    from zb import *
except:
    os.system("fix.bat")
    sys.exit()

# 窗口初始化
tk = Tk()
tk.title(" zb的小程序For " + edition + " " + version)
x = 400
y = 230
tk.geometry("%dx%d+%d+%d" % (x, y, (tk.winfo_screenwidth() - x) / 2, (tk.winfo_screenheight() - y) / 2))
tk.minsize(400, 230)
tk.maxsize(400, 295)
tk.wm_attributes("-topmost", 1)
check_ico(tk, "logo.ico")
st = ttk.Style()
st.configure("TButton")


# 功能


def b1():
    os.popen("choose.pyw")
    exit()


def b2():
    os.popen("function.pyw")
    exit()


def b3():
    pro4 = threading.Thread(target=ppt_restart)
    pro4.start()
    pro3 = threading.Thread(target=clear_seewo)
    pro3.start()
    pro8 = threading.Thread(target=clear_rubbish)
    pro8.start()
    pro6 = threading.Thread(target=clear_desk("D:/文件"))
    pro6.start()
    pro5 = threading.Thread(target=clear_wechat("D:/WeChat Files/WeChat Files/", "D:/文件"))
    pro5.start()
    pro7 = threading.Thread(target=clear_cache)
    pro7.start()
    pro11 = threading.Thread(target=clear_repeat("D:/文件"))
    pro11.start()


def b4():
    os.startfile("D:/文件")


def b5():
    pro2 = threading.Thread(target=ppt_restart)
    pro2.start()


def b6():
    os.popen("taskkill -f -im PPTService.exe")


def b7():
    pro9 = threading.Thread(target=clear_rubbish)
    pro9.start()


def b8():
    pro10 = threading.Thread(target=restart_explorer)
    pro10.start()


def b9():
    webbrowser.open("https://tv.cctv.cn/live/cctv13")
    exit()


def b10():
    webbrowser.open("http://10.8.8.35:8443/live/31384275e5e0443fa4364714fcbf85fd")
    exit()


def b11():
    os.popen(pj(os.getcwd(), "update.pyw"))
    exit()


def b13():
    print("打开zb网站")
    webbrowser.open("https://ianzb.github.io/")


def b14():
    print("打开更新服务器")
    webbrowser.open("https://ianzb.github.io/server.github.io/Seewo/seewo.html")


def b15():
    pro1 = threading.Thread(target=get_mc)
    pro1.start()


def b16():
    pro12 = threading.Thread(target=sys_info)
    pro12.start()


# 控件
ttk.Label(tk, text="实用程序").place(x=75, y=0, width=150, height=30)
ttk.Label(tk, text="功能列表").place(x=275, y=0, width=150, height=30)
ttk.Separator(tk, orient=HORIZONTAL).place(x=0, y=0, width=400, height=2)
# 左侧
ttk.Button(tk, text="点名器", style="TButton", command=b1).place(x=0, y=30, width=200, height=30)
ttk.Button(tk, text="函数工具", style="TButton", command=b2).place(x=0, y=60, width=200, height=30)
# 右侧
ttk.Button(tk, text="一键整理+清理", style="TButton", command=b3).place(x=200, y=30, width=150, height=30)
ttk.Button(tk, text="打开", style="TButton", command=b4).place(x=350, y=30, width=50, height=30)
ttk.Button(tk, text="重启PPT小助手", style="TButton", command=b5).place(x=200, y=60, width=100, height=30)
ttk.Button(tk, text="关闭PPT小助手", style="TButton", command=b6).place(x=300, y=60, width=100, height=30)
ttk.Button(tk, text="清理回收站", style="TButton", command=b7).place(x=200, y=90, width=100, height=30)
ttk.Button(tk, text="重启资源管理器", style="TButton", command=b8).place(x=300, y=90, width=100, height=30)
ttk.Button(tk, text="CCTV-13", style="TButton", command=b9).place(x=200, y=120, width=100, height=30)
ttk.Button(tk, text="校园电视台", style="TButton", command=b10).place(x=300, y=120, width=100, height=30)
ttk.Button(tk, text="查看系统信息", style="TButton", command=b16).place(x=200, y=150, width=200, height=30)
ttk.Separator(tk, orient=VERTICAL).place(x=200, y=0, width=1, height=180)
ttk.Separator(tk, orient=HORIZONTAL).place(x=0, y=180, width=400, height=2)
ttk.Label(tk, text="zb的小程序For " + edition + " 版本  " + version).place(x=60, y=190, width=200, height=30)
ttk.Button(tk, text="检查更新", style="TButton", command=b11).place(x=260, y=190, width=80, height=30)
ttk.Separator(tk, orient=HORIZONTAL).place(x=0, y=230, width=400, height=2)
ttk.Label(tk, text="夹带私货").place(x=175, y=235, width=150, height=30)
ttk.Button(tk, text="zb的网站", style="TButton", command=b13).place(x=0, y=265, width=100, height=30)
ttk.Button(tk, text="更新服务器", style="TButton", command=b14).place(x=100, y=265, width=100, height=30)
ttk.Button(tk, text="MC版本爬虫", style="TButton", command=b15).place(x=200, y=265, width=200, height=30)

tk.mainloop()
