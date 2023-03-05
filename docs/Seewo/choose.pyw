# 程序信息

version = "1.5.1"

# 导入运行库

import random, pandas, os, time
from secrets import choice
from zb import *
from tkinter import *
from tkinter import ttk
from tkinter.messagebox import *

# 读取信息

df = pandas.read_excel("list.xlsx")
names = []
numbers = []
for i in df["姓名"]:
    names.append(i)
for i in df["学号"]:
    numbers.append(i)
del df
using = False

# 窗口初始化

tk = Tk()
tk.title("zb的点名器 " + version)
x = 700
y = 300
tk.geometry("%dx%d+%d+%d" % (x, y, (tk.winfo_screenwidth() - x) / 2, (tk.winfo_screenheight() - y) / 2))
tk.resizable(False, False)
tk.wm_attributes("-topmost", 1)
check_ico(tk, "logo.ico")
st = ttk.Style()
st.configure("TButton")
t2 = StringVar()
t3 = StringVar()


# 功能

def btn1():
    global using, names, numbers
    if using:
        return False
    using = True
    t3.set("")
    wait = 0
    repeat = random.randint(35, 40)
    for i in range(repeat):
        if len(names) < 1:
            showinfo("提示", "所有人已经被点名，点击确定重置！")
            os.popen("choose.pyw")
            exit()
        name = choice(names)
        num = numbers[names.index(name)]
        t2.set("                          " + name)
        tk.update()
        if i == repeat - 1:
            names.remove(name)
            numbers.remove(num)
        time.sleep(wait)
        wait += 0.002
    t3.set("恭喜这位同学(ง •_•)ง")
    tk.update()
    using = False


def btn2():
    global using, names, numbers
    if using:
        return False
    using = True
    if len(names) < 5:
        showinfo("提示", "所有人已经被点名，点击确定重置！")
        os.popen("choose.pyw")
        exit()
    t3.set("")
    wait = 0
    repeat = random.randint(35, 40)
    for i in range(repeat):
        n = ""
        for j in range(5):
            name = choice(names)
            num = numbers[names.index(name)]
            n = n + " " + name
        t2.set(n)
        tk.update()
        time.sleep(wait)
        wait += 0.002
    tk.update()
    t3.set("")
    n = ""
    tk.update()
    for i in range(5):
        repeat = random.randint(25, 30)
        for j in range(repeat):
            if len(names) < 2:
                showinfo("提示", "所有人已经被点名，点击确定重新开始")
                os.popen("choose.pyw")
                exit()
            name = choice(names)
            num = numbers[names.index(name)]
            if j == repeat - 1:
                n = n + " " + name
                names.remove(name)
                numbers.remove(num)
            tk.update()
    tk.update()
    t2.set(n)
    t3.set("恭喜这5位同学(ง •_•)ง")
    using = False


# 控件

ttk.Label(tk, font=("等线", 15), text="   点名器").place(x=300, y=0, width=200, height=30)
ttk.Label(tk, font=("等线", 30), textvariable=t2).place(x=-5, y=50, width=800, height=100)
ttk.Label(tk, font=("等线", 20), textvariable=t3).place(x=230, y=150, width=400, height=100)
ttk.Button(tk, text="点名1人", style="TButton", command=btn1).place(x=250, y=270, width=100, height=30)
ttk.Button(tk, text="点名5人", style="TButton", command=btn2).place(x=350, y=270, width=100, height=30)

tk.mainloop()

'''
2022-11-01：1.0.0：
2022-11-02：1.1.0：添加5连抽，无法抽中同一个人，添加提示语，增大字体
2022-11-03：1.2.0：优化动画，修复连点错乱Bug
2022-11-05：1.3.0：优化字体，添加窗口图标，置顶
2022-11-06：1.3.1：优化代码，提高速度
2022-11-07：1.3.2：添加阻止恶搞版本提示，添加图标缺失提示
2022-11-12：1.3.3：优化阻止恶搞版本提示
2022-11-15：1.4.0：修复学号错位Bug，添加新同学，优化图标，优化退出方式
2022-11-16：1.4.1：将部分功能移动至zb库中，修复退出异常Bug
2022-11-26：1.4.2：删除阻止恶搞版本提示，优化代码，删除重启后的延迟关闭，删除图标缺失提示
2022-12-05：1.4.3：将随机方式从伪随机（random）更改为真随机（secrets），将新同学的学号移动到正确的位置
2022-12-25：1.4.4：优化代码
2022-03-04：1.5.0：删除学号显示，优化点满提示
2022-03-05：1.5.1：优化代码
'''
