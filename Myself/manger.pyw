# 程序信息
version = "1.0.0"

# 导入运行库
import os, sys
from tkinter import *
from tkinter import ttk
from tkinter.messagebox import *
from zb import *

# 读取信息
path = "E:/编程/server.github.io"
list2 = []
list = os.walk(path)
for i in list:
    list2.append(i)
try:
    list = list2[0][1]
except:
    exit()
no = [".idea", "venv"]
for i in no:
    list.remove(i)
del no, list2

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
    os.popen(pj(path, str(names), "main.pyw"))


# 控件
ttk.Label(tk, text="管理器").place(x=78, y=0, width=150, height=30)
ttk.Button(tk, text="打开文件夹", style="TButton", command=b1).place(x=0, y=30, width=200, height=30)
for i in range(len(list)):
    ttk.Button(tk, text="打开" + list[i], style="TButton", command=lambda f=list[i]: open(f)).place(x=i % 2 * 100, y=i // 2 * 30 + 60, width=100, height=30)

tk.mainloop()

'''
2022-11-26：1.0.0：
'''
