# 导入运行库
from zb import *

# 读取信息
check()
disable("hide.txt")

# 窗口初始化

tk = Tk()
tk.title("zb小程序-贴边停靠窗口")
x = 10
y = 40
tk.geometry("%dx%d+%d+%d" % (x, y, (tk.winfo_screenwidth() - 10), (tk.winfo_screenheight() - y) * settings[2] * 0.01))
tk.resizable(False, False)
tk.attributes("-alpha", 0.4)
tk.wm_attributes("-topmost", 1)
tk.overrideredirect(True)
st = Style()
st.configure("TButton")
if settings[5] == "Win11浅色模式":
    sv_ttk.use_light_theme()
elif settings[5] == "Win11深色模式":
    sv_ttk.use_dark_theme()


# 功能

def start():
    os.popen("main.pyw")
    tk.destroy()


# 控件
ttk.Button(tk, text="", style="TButton", command=lambda: MyThread(start())).place(x=0, y=0, width=15, height=20)
ttk.Button(tk, text="", style="TButton", command=lambda: MyThread(tk.destroy())).place(x=0, y=20, width=15, height=20)
tk.mainloop()
