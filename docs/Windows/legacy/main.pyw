# 程序信息

version = "4.8.6"
# 导入运行库
from zb import *

save_setting(settings)
check()
disable("main.txt")

# 窗口初始化

tk = Tk()
tk.title("zb小程序 Tk版 "+ version+" 已停更")
x = 402
y = 184
if settings[5] == "经典风格":
    x += 2
    y -= 16
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


showinfo("提示","zb小程序Tk版已停止支持，请打开更新模块，安装运行库并升级至Qt版以享受新功能")
AutoRun(switch="close", zdynames=os.path.basename(pj(abs_path, "hide.pyw")))
AutoRun(switch="close", zdynames=os.path.basename(pj(abs_path, "hide.pyw")), current_file="zb小程序")
# 功能
def b1():
    os.popen("choose.pyw")
    exit()


def b4():
    os.popen("function.pyw")
    exit()


def b2():
    if settings[0] == "作者个人版" and "Ian" not in platform.node():
        showerror("错误", "zb小程序 作者个人版 暂未适配你的电脑，暂时无法使用")
        return
    if settings[0] == "Seewo" and "seewo" not in platform.node().lower():
        showerror("错误", "zb小程序 希沃定制版 暂未适配你的电脑，暂时无法使用")
        return
    clear_rubbish()
    clear_cache()
    clear_desk(settings[3])
    clear_wechat(settings[4], settings[3])
    if settings[0] == "作者个人版":
        clear_apps(settings[3])
    if settings[0] == "希沃定制版":
        clear_seewo()
    clear_useless_files(settings[3])
    showinfo("提示", "整理完毕")


def b3():
    os.popen(pj(os.getcwd(), "update.pyw"))
    exit()


def b5():
    webbrowser.open("https://tv.cctv.cn/live/cctv13")
    exit()


def b6():
    webbrowser.open("http://10.8.8.35:8443/live/31384275e5e0443fa4364714fcbf85fd")
    exit()
def use_new():
    os.popen("start ./new/main.pyw")
    tk.destroy()

# 设置功能
def save():
    # settings 0：程序版本 1：是否开机自启0/1 2：贴边位置 3：整理文件目录 4：微信文件目录 5：风格
    showinfo("提示", "即将重启zb小程序！")
    # 保存设置
    settings[1] = val2.get()
    settings[2] = int(float(val3.get()))
    settings[5] = val4.get()
    if settings[0] != val1.get() or settings[3] == "" or settings[4] == "":
        if val1.get() == "作者个人版":
            if settings[3] == "D:/文件":
                settings[3] = "D:/文件/整理"
            if settings[4] == pj(user_path,"Documents/WeChat Files"):
                settings[4] = "D:/文件/应用/微信/WeChat Files"
        if val1.get() == "希沃定制版":
            if settings[3] == "D:/文件/整理":
                settings[3] = "D:/文件"
            if settings[4] == "D:/文件/应用/微信/WeChat Files":
                settings[4] = pj(user_path,"Documents/WeChat Files")
    settings[0] = val1.get()
    save_setting(settings)
    # 应用设置
    if settings[1] == 1:
        AutoRun(switch="open", zdynames=os.path.basename(pj(abs_path, "hide.pyw")), current_file="zb小程序")
    else:
        AutoRun(switch="close", zdynames=os.path.basename(pj(abs_path, "hide.pyw")))
        AutoRun(switch="close", zdynames=os.path.basename(pj(abs_path, "hide.pyw")), current_file="zb小程序")
    # 结束
    logging.info(str(settings))
    os.popen("main.pyw")
    tk.destroy()


def not_save():
    os.popen("main.pyw")
    tk.destroy()


def ask_save():
    path = askdirectory(title="请选择zb小程序整理文件的目标文件夹，当前为：" + str(settings[3]))
    if path != "":
        settings[3] = path


def ask_wechat():
    path = askdirectory(title="请选择zb小程序整理微信文件时需要的微信文件夹，当前为：" + str(settings[4]))
    if path != "":
        settings[4] = path


def change(a=None):
    sval1.set("贴靠位置 " + str(int(float(val3.get()))) + "%")
    tk.update()


# 设置处理

val1 = StringVar()
val2 = IntVar()
val3 = IntVar()
val4 = StringVar()
sval1 = StringVar()
val1.set(settings[0])
val2.set(settings[1])
val3.set(settings[2])
val4.set(settings[5])
sval1.set("贴靠位置 " + str(int(float(val3.get()))) + "%")  # 贴靠位置数值动态显示变量
listforval1 = [settings[0], "作者个人版", "希沃定制版"]  # 版本选择列表
listforval2 = [settings[5], "Win11浅色模式", "Win11深色模式", "经典风格"]  # 风格选择列表

# 控件
tab = ttk.Notebook(tk, width=402, height=184)
tab1 = ttk.Frame()
tab2 = ttk.Frame()
tab3 = ttk.Frame()
tab4 = ttk.Frame()

ttk.Button(tab1, text="一键整理+清理", style="TButton", command=lambda: MyThread(b2)).place(x=0, y=0, width=140, height=35)
ttk.Button(tab1, text="打开", style="TButton", command=lambda: MyThread(lambda: os.startfile(settings[3]))).place(x=140, y=0, width=60, height=35)
if settings[0] == "作者个人版":
    ttk.Button(tab1, text="清理回收站", style="TButton", command=lambda: MyThread(clear_rubbish)).place(x=0, y=35, width=100, height=35)
    ttk.Button(tab1, text="重启资源管理器", style="TButton", command=lambda: MyThread(restart_explorer)).place(x=100, y=35, width=100, height=35)
    ttk.Button(tab1, text="强制关闭程序", style="TButton", command=lambda: MyThread(kill_py)).place(x=100, y=70, width=100, height=35)
    ttk.Button(tab1, text="MC版本爬虫", style="TButton", command=lambda: MyThread(get_mc)).place(x=0, y=70, width=100, height=35)
    ttk.Button(tab1, text="查看系统信息", style="TButton", command=lambda: MyThread(sys_info)).place(x=0, y=105, width=100, height=35)
if settings[0] == "希沃定制版":
    ttk.Button(tab1, text="清理回收站", style="TButton", command=lambda: MyThread(clear_rubbish())).place(x=0, y=35, width=100, height=35)
    ttk.Button(tab1, text="重启资源管理器", style="TButton", command=lambda: MyThread(restart_explorer())).place(x=100, y=35, width=100, height=35)
    ttk.Button(tab1, text="重启PPT小助手", style="TButton", command=lambda: MyThread(ppt_restart)).place(x=0, y=70, width=100, height=35)
    ttk.Button(tab1, text="关闭PPT小助手", style="TButton", command=lambda: MyThread(lambda: os.popen("taskkill -f -im PPTService.exe"))).place(x=100, y=70, width=100, height=35)
    ttk.Button(tab1, text="CCTV-13", style="TButton", command=lambda: MyThread(b5)).place(x=0, y=105, width=100, height=35)
    ttk.Button(tab1, text="校园电视台", style="TButton", command=lambda: MyThread(b6)).place(x=100, y=105, width=100, height=35)
    ttk.Button(tab1, text="强制关闭程序", style="TButton", command=lambda: MyThread(kill_py)).place(x=200, y=0, width=100, height=35)
    ttk.Button(tab1, text="查看系统信息", style="TButton", command=lambda: MyThread(sys_info)).place(x=300, y=0, width=100, height=35)

ttk.Button(tab2, text="点名器", style="TButton", command=lambda: MyThread(b1)).place(x=0, y=0, width=200, height=35)
ttk.Button(tab2, text="函数工具", style="TButton", command=lambda: MyThread(b4)).place(x=200, y=0, width=200, height=35)

ttk.Label(tab3, text="修改版本").place(x=0, y=0, width=100, height=35)
ttk.OptionMenu(tab3, val1, *listforval1).place(x=60, y=0, width=140, height=35)
ttk.Label(tab3, text="修改风格").place(x=0, y=35, width=100, height=35)
ttk.OptionMenu(tab3, val4, *listforval2).place(x=60, y=35, width=140, height=35)
ttk.Button(tab3, text="整理文件目录", style="TButton", command=lambda: MyThread(ask_save)).place(x=0, y=70, width=100, height=35)
ttk.Button(tab3, text="微信文件目录", style="TButton", command=lambda: MyThread(ask_wechat)).place(x=100, y=70, width=100, height=35)

ttk.Label(tab3, textvariable=sval1).place(x=200, y=0, width=100, height=35)
scale1 = ttk.Scale(tab3, from_=0, to=100, orient=HORIZONTAL, variable=val3, command=change)
scale1.place(x=290, y=0, width=100, height=35)
ttk.Checkbutton(tab3, variable=val2, text="开机自启动").place(x=200, y=35, width=200, height=35)
ttk.Button(tab3, text="取消", style="TButton", command=not_save).place(x=200, y=105, width=100, height=35)
ttk.Button(tab3, text="保存", style="TButton", command=save).place(x=300, y=105, width=100, height=35)

ttk.Label(tab4, text="zb小程序 Tk版").place(x=0, y=0, width=200, height=35)
ttk.Label(tab4, text="作者 Ianzb 版本 " + version).place(x=0, y=25, width=200, height=35)
ttk.Label(tab4, text="Tk版已停更").place(x=0, y=50, width=200, height=35)

#ttk.Button(tab4, text="体验Qt版", style="TButton", command=use_new).place(x=0, y=105, width=200, height=35)


ttk.Button(tab4, text="程序官网", style="TButton", command=lambda: MyThread(lambda: webbrowser.open("https://ianzb.github.io/server.github.io/"))).place(x=200, y=0, width=100, height=35)
ttk.Button(tab4, text="检查更新", style="TButton", command=lambda: MyThread(b3)).place(x=300, y=0, width=100, height=35)
ttk.Button(tab4, text="安装目录", style="TButton", command=lambda: MyThread(lambda: os.startfile(sys.argv[0][:sys.argv[0].rfind(r"\ "[:-1])]))).place(x=200, y=35, width=100, height=35)
ttk.Button(tab4, text="查看日志", style="TButton", command=lambda: os.popen("start NotePad.exe zb.log")).place(x=300, y=35, width=100, height=35)
#ttk.Button(tab4, text="添加桌面快捷方式", style="TButton", command=lambda: create_link(name="zb小程序", path=pj(abs_path, "main.pyw"), to=abs_desktop, icon=pj(abs_path, "logo.ico"))).place(x=200, y=70, width=200, height=35)
#ttk.Button(tab4, text="添加至开始菜单", style="TButton", command=add_to_start_menu).place(x=200, y=105, width=200, height=35)

#tab.add(tab1, text="便携功能")
#tab.add(tab2, text="实用程序")
#tab.add(tab3, text="设置")
tab.add(tab4, text="关于")
tab.pack()
close()
tk.mainloop()
