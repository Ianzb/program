# 程序信息

version = "4.1.0"

# 导入运行库
from zb import *

check()
disable("main.txt")

settings = read_setting()
# 窗口初始化

tk = Tk()
tk.title(" zb的小程序 " + settings[0] + " " + version)
x = 200
y = 210
tk.geometry("%dx%d+%d+%d" % (x, y, (tk.winfo_screenwidth() - x) / 2, (tk.winfo_screenheight() - y) / 2))
tk.resizable(False, False)
tk.wm_attributes("-topmost", 1)
check_ico(tk, "logo.ico")
st = Style()
st.configure("TButton")


def hide():
    os.popen("hide.pyw")
    exit()


tk.protocol("WM_DELETE_WINDOW", hide)


# 功能
def b1():
    os.popen("choose.pyw")
    exit()


def b4():
    os.popen("function.pyw")
    exit()


def b2():
    if settings[0] == "Myself" and "Ian" not in platform.node():
        showerror("错误", "zb小程序 Myself 暂未适配你的电脑，暂时无法使用")
        return
    if settings[0] == "Seewo" and "seewo" not in platform.node().lower():
        showerror("错误", "zb小程序 Seewo 暂未适配你的电脑，暂时无法使用")
        return
    clear_rubbish()
    clear_cache()
    clear_desk(settings[3])
    clear_wechat(settings[4], settings[3])
    if settings[0] == "Myself":
        clear_apps()
    clear_repeat(settings[3])


def b3():
    os.popen(pj(os.getcwd(), "update.pyw"))
    exit()


def b5():
    webbrowser.open("https://tv.cctv.cn/live/cctv13")
    exit()


def b6():
    webbrowser.open("http://10.8.8.35:8443/live/31384275e5e0443fa4364714fcbf85fd")
    exit()


def save():
    showinfo("提示", "即将重启zb小程序！")
    # 保存设置
    settings[1] = val1.get()
    if os.path.exists(entry1.get()):
        settings[3] = entry1.get()
    if os.path.exists(entry2.get()):
        settings[4] = entry2.get()
    if val2.get() != "选择版本":
        settings[0] = val2.get()
        if val2.get() == "Myself":
            settings[3] = "E:/整理文件"
            settings[4] = "D:/Files/Wechat/WeChat Files"
        if val2.get() == "Seewo":
            settings[3] = "D:/文件"
            settings[4] = "D:/WeChat Files/WeChat Files"
    path = sys.argv[0][:sys.argv[0].rfind(r"\ "[:-1]) + 1] + "hide.pyw"
    # 应用设置
    if settings[1] == 1:
        AutoRun(switch="open", zdynames=os.path.basename(os.path.join(path, "hide.pyw")))
    else:
        AutoRun(switch="close", zdynames=os.path.basename(os.path.join(path, "hide.pyw")))
    # 结束
    save_setting(settings)
    print(settings)
    os.popen("main.pyw")
    tk.destroy()


def not_save():
    os.popen("main.pyw")
    tk.destroy()


# 控件处理
val1 = IntVar()
if settings[1] == 1:
    val1.set(1)
if settings[1] == 0:
    val1.set(0)
val2 = StringVar()
listforval2 = ["选择版本", "Myself", "Seewo"]
if settings[0] == "Myself":
    val2.set("Myself")
if settings[0] == "Seewo":
    val2.set("Seewo")
val3 = StringVar()
val3.set(settings[3])
val4 = StringVar()
val4.set(settings[4])
# 控件
# 左侧
tab = ttk.Notebook(tk, width=400, height=200)
tab1 = ttk.Frame()
tab2 = ttk.Frame()
tab3 = ttk.Frame()
tab4 = ttk.Frame()

# Button(tab2, text="zb的小程序管理器", style="TButton", command=lambda: MyThread(b1)).place(x=0, y=0, width=196, height=30)
# 右侧
ttk.Button(tab1, text="一键整理+清理", style="TButton", command=lambda: MyThread(b2)).place(x=0, y=0, width=150, height=30)
ttk.Button(tab1, text="打开", style="TButton", command=lambda: MyThread(os.startfile(settings[3]))).place(x=150, y=0, width=46, height=30)
if settings[0] == "Myself":
    ttk.Button(tab1, text="清理回收站", style="TButton", command=lambda: MyThread(clear_rubbish())).place(x=0, y=30, width=98, height=30)
    ttk.Button(tab1, text="重启资源管理器", style="TButton", command=lambda: MyThread(restart_explorer())).place(x=98, y=30, width=98, height=30)
    ttk.Button(tab1, text="强制关闭程序", style="TButton", command=lambda: MyThread(kill_py)).place(x=98, y=60, width=98, height=30)
    ttk.Button(tab1, text="MC版本爬虫", style="TButton", command=lambda: MyThread(get_mc)).place(x=0, y=60, width=98, height=30)
    ttk.Button(tab1, text="查看系统信息", style="TButton", command=lambda: MyThread(sys_info)).place(x=0, y=90, width=98, height=30)
if settings[0] == "Seewo":
    ttk.Button(tab1, text="清理回收站", style="TButton", command=lambda: MyThread(clear_rubbish())).place(x=0, y=30, width=98, height=30)
    ttk.Button(tab1, text="重启资源管理器", style="TButton", command=lambda: MyThread(restart_explorer())).place(x=98, y=30, width=98, height=30)
    ttk.Button(tab1, text="重启PPT小助手", style="TButton", command=lambda: MyThread(ppt_restart)).place(x=0, y=60, width=98, height=30)
    ttk.Button(tab1, text="关闭PPT小助手", style="TButton", command=lambda: MyThread(os.popen("taskkill -f -im PPTService.exe"))).place(x=98, y=60, width=98, height=30)
    ttk.Button(tab1, text="CCTV-13", style="TButton", command=lambda: MyThread(b5)).place(x=0, y=90, width=98, height=30)
    ttk.Button(tab1, text="校园电视台", style="TButton", command=lambda: MyThread(b6)).place(x=98, y=90, width=98, height=30)
    ttk.Button(tab1, text="强制关闭程序", style="TButton", command=lambda: MyThread(kill_py)).place(x=0, y=120, width=98, height=30)
    ttk.Button(tab1, text="查看系统信息", style="TButton", command=lambda: MyThread(sys_info)).place(x=98, y=120, width=98, height=30)

ttk.Button(tab2, text="点名器", style="TButton", command=lambda: MyThread(b1)).place(x=0, y=0, width=196, height=30)
ttk.Button(tab2, text="函数工具", style="TButton", command=lambda: MyThread(b4)).place(x=0, y=30, width=196, height=30)

ttk.OptionMenu(tab3, val2, *listforval2).place(x=0, y=0, width=90, height=30)
ttk.Label(tab3, text="当前为 " + settings[0]).place(x=98, y=0, width=98, height=30)
ttk.Checkbutton(tab3, variable=val1, text="开机自启动").place(x=0, y=30, width=196, height=30)
ttk.Label(tab3, text="整理文件目录").place(x=0, y=60, width=98, height=30)
entry1 = ttk.Entry(tab3, textvariable=val3)
entry1.place(x=88, y=60, width=108, height=30)
ttk.Label(tab3, text="微信文件目录").place(x=0, y=90, width=98, height=30)
entry2 = Entry(tab3, textvariable=val4)
entry2.place(x=88, y=90, width=108, height=30)
ttk.Button(tab3, text="取消", style="TButton", command=lambda: not_save()).place(x=0, y=150, width=98, height=30)
ttk.Button(tab3, text="保存", style="TButton", command=lambda: save()).place(x=98, y=150, width=98, height=30)

ttk.Label(tab4, text="zb的小程序 " + settings[0]).place(x=0, y=0, width=196, height=30)
ttk.Label(tab4, text="版本  " + version).place(x=0, y=25, width=196, height=30)
ttk.Label(tab4, text="作者：Ianzb").place(x=0, y=50, width=200, height=30)
ttk.Button(tab4, text="程序官网", style="TButton", command=lambda: MyThread(webbrowser.open("https://ianzb.github.io/server.github.io/"))).place(x=0, y=120, width=98, height=30)
ttk.Button(tab4, text="检查更新", style="TButton", command=lambda: MyThread(b3)).place(x=98, y=120, width=98, height=30)
ttk.Button(tab4, text="安装目录", style="TButton", command=lambda: MyThread(os.startfile(sys.argv[0][:sys.argv[0].rfind(r"\ "[:-1])]))).place(x=0, y=150, width=196, height=30)

tab.add(tab1, text="便携功能")
tab.add(tab2, text="实用程序")
tab.add(tab3, text="设置")
tab.add(tab4, text="关于")
tab.pack(padx=0, pady=0)
close()
tk.mainloop()
