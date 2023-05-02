# 程序信息

version = "1.9.2"

# 导入运行库

from zb import *

check()
disable("choose.txt")
from secrets import choice

# 读取信息

with open("names.zb", "r", encoding="utf-8") as file:
    names = file.readlines()
for i in range(len(names)):
    names[i] = names[i].strip()
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
st = Style()
st.configure("TButton")
if settings[5] == "Win11浅色模式":
    sv_ttk.use_light_theme()
elif settings[5] == "Win11深色模式":
    sv_ttk.use_dark_theme()
t2 = StringVar()
t3 = StringVar()


# 功能

def btn1():
    global using, names
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
        t2.set("                          " + name)
        tk.update()
        if i == repeat - 1:
            names.remove(name)
        time.sleep(wait)
        wait += 0.002
    t3.set("恭喜这位同学(ง •_•)ง")
    t12["text"] = "不可点"
    tk.update()
    using = False


def btn2():
    global using, names
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
            name = choice(names)
            if j == repeat - 1:
                n = n + " " + name
                names.remove(name)
            tk.update()
    tk.update()
    t2.set(n)
    t3.set("恭喜这5位同学(ง •_•)ง")
    using = False


# 控件

ttk.Label(tk, font=("等线", 15), text="   点名器").place(x=300, y=0, width=200, height=30)
ttk.Label(tk, font=("等线", 30), textvariable=t2).place(x=-5, y=50, width=800, height=100)
ttk.Label(tk, font=("等线", 20), textvariable=t3).place(x=230, y=150, width=400, height=100)
ttk.Button(tk, text="点名1人", style="TButton", command=btn1).place(x=250, y=265, width=100, height=35)
ttk.Button(tk, text="点名5人", style="TButton", command=btn2).place(x=350, y=265, width=100, height=35)
close()
tk.mainloop()