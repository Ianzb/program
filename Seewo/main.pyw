v = "3.0.0"
try:
    from zb import *
except:
    import os, sys

    os.system("fix.bat")
    sys.exit()

# 初始化
tk = Tk()
# 设置风格样式
st = ttk.Style()
st.configure("TButton")
# 窗口属性
tk.title(" zb的小程序For Seewo " + v)
x = 400
y = 230
now_x = (tk.winfo_screenwidth() - x) / 2
now_y = (tk.winfo_screenheight() - y) / 2
tk.geometry("%dx%d+%d+%d" % (x, y, now_x, now_y))
tk.wm_attributes("-topmost", 1)
tk.minsize(400, 230)
tk.maxsize(400, 295)
check_ico(tk, "logo.ico")


# 功能


def b0():
    os.popen(pj(os.getcwd(),"update.pyw"))
    time.sleep(0.3)
    exit()


def b6():
    print("打开二次函数工具")
    os.popen("function.pyw")
    time.sleep(0.5)
    exit()


def b100():
    print("打开zb网站")
    webbrowser.open("https://ianzb.github.io/")


def b101():
    pro1 = threading.Thread(target=get_mc)
    pro1.start()


def b1():
    pro2 = threading.Thread(target=ppt_restart)
    pro2.start()


def b2():
    print("关闭PPT小助手")
    os.popen("taskkill -f -im PPTService.exe")
    print("成功关闭PPT小助手")


def b3():
    print("打开CCTV-13")
    webbrowser.open("https://tv.cctv.cn/live/cctv13/?spm=C28340.P4hQlpYBT2vN.ExidtyEJcS5K.25")
    exit()


def b4():
    print("打开校园电视台")
    webbrowser.open("http://10.8.8.35:8443/live/31384275e5e0443fa4364714fcbf85fd")
    exit()


def b5():
    pro3 = threading.Thread(target=clear_seewo)
    pro3.start()


def b9():
    pro9 = threading.Thread(target=clear_rubbish)
    pro9.start()


def b11():
    pro10 = threading.Thread(target=restart_explorer)
    pro10.start()


def b12():
    print("一键整理+清理")
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

    print("成功整理+清理")


def b13():
    print("打开点名器")
    os.popen("choose.pyw")
    time.sleep(0.5)
    exit()


def b14():
    print("打开更新服务器")
    webbrowser.open("https://ianzb.github.io/server.github.io/Seewo/seewo.html")


def b15():
    os.startfile("D:/文件")


def b10():
    t2 = Tk()
    s2 = ttk.Style()
    s2.configure("TButton")
    t2.title(" 设置")
    x = 400
    y = 200
    now_x = (t2.winfo_screenwidth() - x) / 2
    now_y = (t2.winfo_screenheight() - y) / 2
    t2.geometry("%dx%d+%d+%d" % (x, y, now_x, now_y))
    t2.wm_attributes("-topmost", 1)
    t2.resizable(False, False)
    check_ico(t2, "logo.ico")


# txt = ttk.Label(tk, text="文字").place(x=100,y=,width=200,height=30,anchor="center")
# b = ttk.Button(tk, text="按钮", style="TButton", command=b).place(x=,y=,width=100,height=30)
# sep = Separato3r(tk, orient=HORIZONTAL).place(x=0,y=,width=5000,height=30)

ttk.Label(tk, text="实用程序").place(x=75, y=0, width=150, height=30)
ttk.Label(tk, text="功能列表").place(x=275, y=0, width=150, height=30)
ttk.Separator(tk, orient=HORIZONTAL).place(x=0, y=0, width=400, height=2)

# 左侧

ttk.Button(tk, text="点名器", style="TButton", command=b13).place(x=0, y=30, width=200, height=30)
ttk.Button(tk, text="函数工具", style="TButton", command=b6).place(x=0, y=60, width=200, height=30)
# 右侧

ttk.Button(tk, text="一键整理+清理", style="TButton", command=b12).place(x=200, y=30, width=150, height=30)
ttk.Button(tk, text="打开", style="TButton", command=b15).place(x=350, y=30, width=50, height=30)

ttk.Button(tk, text="重启PPT小助手", style="TButton", command=b1).place(x=200, y=60, width=100, height=30)
ttk.Button(tk, text="关闭PPT小助手", style="TButton", command=b2).place(x=300, y=60, width=100, height=30)
ttk.Button(tk, text="清理回收站", style="TButton", command=b9).place(x=200, y=90, width=100, height=30)
ttk.Button(tk, text="重启资源管理器", style="TButton", command=b11).place(x=300, y=90, width=100, height=30)
ttk.Button(tk, text="CCTV-13", style="TButton", command=b3).place(x=200, y=120, width=100, height=30)
ttk.Button(tk, text="校园电视台", style="TButton", command=b4).place(x=300, y=120, width=100, height=30)
ttk.Separator(tk, orient=VERTICAL).place(x=200, y=0, width=1, height=180)
ttk.Separator(tk, orient=HORIZONTAL).place(x=0, y=180, width=400, height=2)
ttk.Label(tk, text="zb的小程序For Seewo 版本  " + v).place(x=20, y=190, width=200, height=30)
ttk.Button(tk, text="检查更新", style="TButton", command=b0).place(x=220, y=190, width=80, height=30)
ttk.Button(tk, text="设置", style="TButton", command=b10).place(x=300, y=190, width=80, height=30)

ttk.Separator(tk, orient=HORIZONTAL).place(x=0, y=230, width=400, height=2)

ttk.Label(tk, text="夹带私货").place(x=175, y=235, width=150, height=30)
ttk.Button(tk, text="zb的网站", style="TButton", command=b100).place(x=0, y=265, width=100, height=30)
ttk.Button(tk, text="更新服务器", style="TButton", command=b14).place(x=100, y=265, width=100, height=30)
ttk.Button(tk, text="MC版本爬虫", style="TButton", command=b101).place(x=200, y=265, width=200, height=30)

tk.mainloop()
