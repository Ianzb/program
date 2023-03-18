# 导入运行库

import os
from zb import *
from tkinter import *
from tkinter import ttk

# 读取信息
if os.path.exists("hide.txt"):
    exit()
disable("hide.txt")

# 窗口初始化

tk = Tk()
tk.title(" zb的小程序-贴边停靠窗口")
x = 10
y = 40
tk.geometry("%dx%d+%d+%d" % (x, y, (tk.winfo_screenwidth() - 10), (tk.winfo_screenheight() - y) * 0.25))
tk.resizable(False, False)
tk.attributes("-alpha", 0.4)
tk.wm_attributes("-topmost", 1)
tk.overrideredirect(True)
st = ttk.Style()
st.configure("TButton")
tk.protocol('WM_DELETE_WINDOW', lambda: hide("hide.txt"))


# 功能

def start():
    os.popen("main.pyw")
    enable("hide.txt")
    tk.destroy()


def close():
    enable("hide.txt")
    tk.destroy()


# 控件
ttk.Button(tk, text="", style="TButton", command=lambda: MyThread(start())).place(x=0, y=0, width=15, height=20)
ttk.Button(tk, text="", style="TButton", command=lambda: MyThread(close())).place(x=0, y=20, width=15, height=20)
tk.mainloop()
