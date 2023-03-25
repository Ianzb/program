# 程序信息

version = "4.0.0"
edition = "Seewo"

# 导入运行库
from zb import *

check()
disable("main.txt")

settings = read_setting()
settings[0]=edition
save_setting(settings)
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


def hide():
    os.popen("hide.pyw")
    exit()


tk.protocol('WM_DELETE_WINDOW', hide)


# 功能


def b1():
    os.popen("choose.pyw")
    exit()


def b2():
    os.popen("function.pyw")
    exit()


def b3():
    ppt_restart()
    clear_seewo()
    clear_rubbish()
    clear_desk("D:/文件")
    clear_wechat("D:/WeChat Files/WeChat Files/", "D:/文件")
    clear_cache()
    clear_repeat("D:/文件")


def b4():
    webbrowser.open("https://tv.cctv.cn/live/cctv13")
    exit()


def b5():
    webbrowser.open("http://10.8.8.35:8443/live/31384275e5e0443fa4364714fcbf85fd")
    exit()


def b6():
    os.popen(pj(os.getcwd(), "update.pyw"))
    exit()
def b7():
    os.popen(pj(os.getcwd(), "setting.pyw"))
    exit()

# 控件

ttk.Label(tk, text="实用程序").place(x=75, y=0, width=150, height=30)
ttk.Label(tk, text="功能列表").place(x=275, y=0, width=150, height=30)
ttk.Separator(tk, orient=HORIZONTAL).place(x=0, y=0, width=400, height=2)
# 左侧
ttk.Button(tk, text="点名器", style="TButton", command=lambda: MyThread(b1)).place(x=0, y=30, width=200, height=30)
ttk.Button(tk, text="函数工具", style="TButton", command=lambda: MyThread(b2)).place(x=0, y=60, width=200, height=30)
# 右侧
ttk.Button(tk, text="一键整理+清理", style="TButton", command=lambda: MyThread(b3)).place(x=200, y=30, width=150, height=30)
ttk.Button(tk, text="打开", style="TButton", command=lambda: MyThread(os.startfile("D:/文件"))).place(x=350, y=30, width=50, height=30)
ttk.Button(tk, text="重启PPT小助手", style="TButton", command=lambda: MyThread(ppt_restart)).place(x=200, y=60, width=100, height=30)
ttk.Button(tk, text="关闭PPT小助手", style="TButton", command=lambda: MyThread(os.popen("taskkill -f -im PPTService.exe"))).place(x=300, y=60, width=100, height=30)
ttk.Button(tk, text="清理回收站", style="TButton", command=lambda: MyThread(clear_rubbish)).place(x=200, y=90, width=100, height=30)
ttk.Button(tk, text="重启资源管理器", style="TButton", command=lambda: MyThread(restart_explorer)).place(x=300, y=90, width=100, height=30)
ttk.Button(tk, text="CCTV-13", style="TButton", command=lambda: MyThread(b4)).place(x=200, y=120, width=100, height=30)
ttk.Button(tk, text="校园电视台", style="TButton", command=lambda: MyThread(b5)).place(x=300, y=120, width=100, height=30)
ttk.Button(tk, text="查看系统信息", style="TButton", command=lambda: MyThread(sys_info)).place(x=300, y=150, width=100, height=30)
ttk.Button(tk, text="强制关闭程序", style="TButton", command=lambda: MyThread(kill_py)).place(x=200, y=150, width=100, height=30)
ttk.Separator(tk, orient=VERTICAL).place(x=200, y=0, width=1, height=180)
ttk.Separator(tk, orient=HORIZONTAL).place(x=0, y=180, width=400, height=2)
ttk.Label(tk, text="zb的小程序For " + edition + " 版本  " + version).place(x=30, y=190, width=200, height=30)
ttk.Button(tk, text="设置", style="TButton", command=lambda: MyThread(b7)).place(x=230, y=190, width=80, height=30)
ttk.Button(tk, text="检查更新", style="TButton", command=lambda: MyThread(b6)).place(x=310, y=190, width=80, height=30)
ttk.Separator(tk, orient=HORIZONTAL).place(x=0, y=230, width=400, height=2)
ttk.Label(tk, text="夹带私货").place(x=175, y=235, width=150, height=30)
ttk.Button(tk, text="zb的网站", style="TButton", command=lambda: MyThread(webbrowser.open("https://ianzb.github.io/"))).place(x=0, y=265, width=100, height=30)
ttk.Button(tk, text="更新服务器", style="TButton", command=lambda: MyThread(webbrowser.open("https://ianzb.github.io/server.github.io"))).place(x=100, y=265, width=100, height=30)
ttk.Button(tk, text="MC版本爬虫", style="TButton", command=lambda: MyThread(get_mc)).place(x=200, y=265, width=200, height=30)
close()
tk.mainloop()
