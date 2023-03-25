# 导入运行库
from zb import *

check()
disable("setting.txt")

settings = read_setting()
print(settings)
# 窗口初始化

tk = Tk()
tk.title(" 设置")
x = 400
y = 200
tk.geometry("%dx%d+%d+%d" % (x, y, (tk.winfo_screenwidth() - x) / 2, (tk.winfo_screenheight() - y) / 2))
tk.resizable(False, False)
tk.wm_attributes("-topmost", 1)
check_ico(tk, "logo.ico")
st = ttk.Style()
st.configure("TButton")


def hide():
    os.popen("main.pyw")
    exit()


tk.protocol('WM_DELETE_WINDOW', hide)


# 功能
def save():
    # 保存设置
    settings[1] = val1.get()
    path = sys.argv[0][:sys.argv[0].rfind(r"\ "[:-1]) + 1] + "hide.pyw"
    # 应用设置
    if settings[1] == 1:
        AutoRun(switch="open", zdynames=os.path.basename(os.path.join(path, "hide.pyw")))
    else:
        AutoRun(switch="close", zdynames=os.path.basename(os.path.join(path, "hide.pyw")))
    # 结束
    save_setting(settings)
    print(settings)
    tk.destroy()

#控件处理
val1 = IntVar()
if settings[1] == 1:
    val1.set(1)
if settings[1] == 0:
    val1.set(0)
# 控件
ttk.Label(tk, text="设置").place(x=185, y=0, width=150, height=30)
ttk.Checkbutton(tk, variable=val1, text="开机自启动").place(x=0, y=30, width=150, height=30)
ttk.Button(tk, text="保存", style="TButton", command=lambda: save()).place(x=300, y=170, width=100, height=30)
ttk.Button(tk, text="取消", style="TButton", command=lambda: tk.destroy()).place(x=200, y=170, width=100, height=30)
close()

tk.mainloop()
