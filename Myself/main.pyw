v = "1.6.0"
import os, sys

sys.path.append(os.getcwd()[:os.getcwd().rfind("\ "[:-1])] + "\Seewo")
try:
    from zb import *
except:
    import os, sys

    os.system("fix.bat")
    sys.exit()

date = time.strftime("%Y-%m-%d")
# 初始化
tk = Tk()
st = ttk.Style()
st.configure("TButton")
tk.title("zb的小程序For Myself " + v)
x = 400
y = 170
now_x = (tk.winfo_screenwidth() - x) / 2
now_y = (tk.winfo_screenheight() - y) / 2
tk.geometry("%dx%d+%d+%d" % (x, y, now_x, now_y))
tk.wm_attributes("-topmost", 1)
tk.resizable(False, False)
tk.minsize(400, 170)
tk.maxsize(400, 170)
tk.wm_iconbitmap("logo.ico")


# 功能


def b0():
    pro100 = threading.Thread(target=check_update("Myself"))
    pro100.start()


def b100():
    print("打开zb网站")
    webbrowser.open("https://ianzb.github.io/")


def b101():
    pro2 = threading.Thread(target=get_mc)
    pro2.start()


def b11():
    pro3 = threading.Thread(target=restart_explorer)
    pro3.start()


def b1():
    os.startfile("E:/整理文件")


def b2():
    pro4 = threading.Thread(target=clear_rubbish)
    pro4.start()


def b12():
    print("一键整理+清理")
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

    print("成功整理+清理")


# txt = ttk.Label(tk, text="文字").place(x=100,y=,width=200,height=30,anchor="center")
# b = ttk.Button(tk, text="按钮", style="TButton", command=b).place(x=,y=,width=100,height=30)
# sep = Separato3r(tk, orient=HORIZONTAL).place(x=0,y=,width=5000,height=30)

ttk.Label(tk, text="实用程序").place(x=75, y=0, width=150, height=30)
ttk.Label(tk, text="功能列表").place(x=275, y=0, width=150, height=30)
Separator(tk, orient=HORIZONTAL).place(x=0, y=0, width=400, height=2)

# 左侧
ttk.Button(tk, text="我的网站", style="TButton", command=b100).place(x=0, y=30, width=200, height=30)
ttk.Button(tk, text="MC版本爬虫", style="TButton", command=b101).place(x=0, y=60, width=200, height=30)
# 右侧

ttk.Button(tk, text="一键整理+清理", style="TButton", command=b12).place(x=200, y=30, width=150, height=30)
ttk.Button(tk, text="打开", style="TButton", command=b1).place(x=350, y=30, width=50, height=30)
ttk.Button(tk, text="清理回收站", style="TButton", command=b2).place(x=200, y=60, width=100, height=30)
ttk.Button(tk, text="重启资源管理器", style="TButton", command=b11).place(x=300, y=60, width=100, height=30)
Separator(tk, orient=VERTICAL).place(x=200, y=0, width=1, height=120)
Separator(tk, orient=HORIZONTAL).place(x=0, y=120, width=400, height=2)
ttk.Label(tk, text="zb的小程序For Myself 版本  " + v).place(x=45, y=130, width=200, height=30)
ttk.Button(tk, text="检查并更新版本", style="TButton", command=b0).place(x=255, y=130, width=100, height=30)
Separator(tk, orient=HORIZONTAL).place(x=0, y=170, width=400, height=2)

tk.mainloop()
