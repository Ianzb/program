v = "1.0.0"
import os, sys

sys.path.append(os.getcwd()[:os.getcwd().rfind("\ "[:-1])] + "\Seewo")
from zb import *

date = time.strftime("%Y-%m-%d")
# 初始化
tk = Tk()
st = ttk.Style()
st.configure("TButton")
tk.title("zb的小程序管理器 " + v)
x = 200
y = 90
now_x = (tk.winfo_screenwidth() - x) / 2
now_y = (tk.winfo_screenheight() - y) / 2
tk.geometry("%dx%d+%d+%d" % (x, y, now_x, now_y))
tk.wm_attributes("-topmost", 1)
tk.resizable(False, False)
check_ico(tk, "logo.ico")
path1 = "E:/编程/server.github.io"


# 功能
def b1():
    os.startfile(path1)


list2 = []
list = os.walk(path1)
for i in list: list2.append(i)
try:
    list = list2[0][1]
except:
    exit()
no = [".idea", "venv"]
for i in no:
    list.remove(i)
print(list)


def open(names):
    os.popen(pj(path1, str(names), "main.pyw"))


for i in range(len(list)):
    ttk.Button(tk, text="打开" + list[i], style="TButton", command=lambda f=list[i]: open(f)).place(x=i % 2 * 100, y=i // 2 * 30 + 60, width=100, height=30)
# txt = ttk.Label(tk, text="文字").place(x=100,y=,width=200,height=30,anchor="center")
# b = ttk.Button(tk, text="按钮", style="TButton", command=b).place(x=,y=,width=100,height=30)
# sep = Separato3r(tk, orient=HORIZONTAL).place(x=0,y=,width=5000,height=30)

ttk.Label(tk, text="管理器").place(x=78, y=0, width=150, height=30)
ttk.Button(tk, text="打开文件夹", style="TButton", command=b1).place(x=0, y=30, width=200, height=30)
tk.mainloop()
# 2022-11-26：1.0.0：
