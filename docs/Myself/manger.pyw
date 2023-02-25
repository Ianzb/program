# 程序信息
version = "1.2.2"

# 导入运行库
import os, sys
from tkinter import *
from tkinter import ttk
from zb import *

# 加载信息
path = "E:/编程/server.github.io/docs"
os.chdir(path)

# 窗口初始化
tk = Tk()

tk.title(" zb的小程序管理器 " + version)
x = 200
y = 90
tk.geometry("%dx%d+%d+%d" % (x, y, (tk.winfo_screenwidth() - x) / 2, (tk.winfo_screenheight() - y) / 2))
tk.resizable(False, False)
tk.wm_attributes("-topmost", 1)
check_ico(tk, "logo.ico")
st = ttk.Style()
st.configure("TButton")


# 功能
def b1():
    os.startfile(path)


def open(names):
    os.chdir(pj(path, str(names)))
    os.popen(pj(path, str(names), "main.pyw"))
    sys.exit()


# 控件
ttk.Label(tk, text="管理器").place(x=78, y=0, width=150, height=30)
ttk.Button(tk, text="打开文件夹", style="TButton", command=b1).place(x=0, y=30, width=200, height=30)
ttk.Button(tk, text="打开Myself", style="TButton", command=lambda: open("Myself")).place(x=0, y=60, width=100, height=30)
ttk.Button(tk, text="打开Seewo", style="TButton", command=lambda: open("Seewo")).place(x=100, y=60, width=100, height=30)

tk.mainloop()

'''
2022-11-26：1.0.0：最初版本。
2022-11-27：1.1.0：不再自动读取版本列表。
2022-12-20：1.2.0：修复打开For Seewo后工作目录错误的Bug，添加打开后退出。
2022-12-26：1.2.1：优化代码
2022-12-29：1.2.2：适配新路径
'''
