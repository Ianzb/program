import sys
import os
import pandas
import time
import random
from tkinter.ttk import Separator
from tkinter.constants import *
from tkinter.messagebox import *
from tkinter import ttk
from tkinter import *
v = "1.2.0"

# 读取表格
df = pandas.read_excel("list.xlsx")
names = []
for i in df["姓名"]:
    names.append(i)
numbers = list(range(1, 42))
del df


def get(list):
    return random.choice(list)


# 初始化
tk = Tk()
tk.title("zb的随机点名器 " + v)
x = 700
y = 300
max_x = tk.winfo_screenwidth()
max_y = tk.winfo_screenheight()
now_x = (max_x - x) / 2
now_y = (max_y - y) / 2
tk.resizable(False, False)
tk.geometry("%dx%d+%d+%d" % (x, y, now_x, now_y))
# 设置样式
st = ttk.Style()
st.configure("TButton")
t2 = StringVar()
t3 = StringVar()
w=[0]

def btn1():
    if w[0]==0:
        w[0] = 1
        t3.set("")
        wait = 0
        repeat = random.randint(35, 40)
        for i in range(repeat):
            if len(names) < 1:
                showinfo("提示", "所有人已经被点名，点击确定重置")
                os.popen("choose.pyw")
                time.sleep(1)
                sys.exit()
            name = get(names)
            num = numbers[names.index(name)]
            t2.set("                    "+str(num) + "号 " + name)
            tk.update()
            if i == repeat-1:
                print(name)
                names.remove(name)
                numbers.remove(num)
            time.sleep(wait)
            wait += 0.002
        t3.set("恭喜这位同学(ง •_•)ง")
        tk.update()
        w[0] =0


def btn2():
    if w[0] == 0:
        w[0] = 1
        if len(names) < 2:
            showinfo("提示", "所有人已经被点名，点击确定重置")
            os.popen("choose.pyw")
            time.sleep(1)
            sys.exit()
        t3.set("")
        wait = 0
        repeat = random.randint(35, 40)
        for i in range(repeat):
            n = ""
            for i in range(5):
                name = get(names)
                num = numbers[names.index(name)]
                n=n+" "+name
            t2.set(n)
            tk.update()
            time.sleep(wait)
            wait += 0.002
        tk.update()
        t3.set("")
        n = ""
        tk.update()
        for i in range(5):
            t2.set("")
            repeat = random.randint(25, 30)
            for i in range(repeat):
                if len(names) < 2:
                    showinfo("提示", "所有人已经被点名，点击确定重新开始")
                    os.popen("choose.pyw")
                    time.sleep(1)
                    sys.exit()
                name = get(names)
                num = numbers[names.index(name)]
                if i == repeat - 1:
                    n = n+" "+name
                    names.remove(name)
                    numbers.remove(num)
                tk.update()
        tk.update()
        print(n)
        t2.set(n)
        t3.set("恭喜这5位同学(ง •_•)ง")
        w[0] = 0


# txt = ttk.Label(tk, text="文字").place(x=100,y=,width=200,height=30,anchor="center")
# b = ttk.Button(tk, text="按钮", style="TButton", command=b).place(x=,y=,width=100,height=30)
# 横 sep = Separato3r(tk, orient=HORIZONTAL).place(x=0,y=,width=5000,height=30)
# 竖 sep = Separato3r(tk, orient=VERTICAL).place(x=0,y=,width=5000,height=30)
txt = ttk.Label(tk, font=("微软雅黑", 15), text="   点名器").place(
    x=300, y=0, width=200, height=30)
txt2 = ttk.Label(tk, font=("微软雅黑", 30), textvariable=t2).place(
    x=-5, y=50, width=800, height=100)
txt3 = ttk.Label(tk, font=("微软雅黑", 20), textvariable=t3).place(
    x=230, y=150, width=400, height=100)
b1 = ttk.Button(tk, text="点名1人", style="TButton", command=btn1).place(
    x=250, y=270, width=100, height=30)
b2 = ttk.Button(tk, text="点名5人", style="TButton", command=btn2).place(
    x=350, y=270, width=100, height=30)
tk.mainloop()
# 2022-11-01：1.0.0：
# 2022-11-02：1.1.0：添加5连抽，无法抽中同一个人，添加提示语，增大字体
# 2022-11-03：1.2.0：优化动画，修复连点错乱bug
