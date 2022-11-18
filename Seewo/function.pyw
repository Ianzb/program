v = "1.0.0"

from zb import *

# 初始化
tk = Tk()
# 设置风格样式
st = ttk.Style()
st.configure("TButton")
# 窗口属性
tk.title(" zb的二次函数工具 " + v)
x = 200
y = 200
now_x = (tk.winfo_screenwidth() - x) / 2
now_y = (tk.winfo_screenheight() - y) / 2
tk.geometry("%dx%d+%d+%d" % (x, y, now_x, now_y))
tk.wm_attributes("-topmost", 1)
tk.resizable(False, False)
check_ico(tk, "logo.ico")


# 功能
def b1():
    a = entry1.get()
    b = entry2.get()
    c = entry3.get()
    if a == "":
        a = "1"

    if a == "-":
        a = "-1"
    if b == "-":
        b = "-1"
    if b == "":
        b = "1"
    if c == "":
        c = "0"
    if c == "-":
        showinfo("提示", "填写的数字无效")
        return False
    try:
        a = int(a)
    except:
        a = float(a)
    try:
        b = int(b)
    except:
        b = float(b)
    try:
        c = int(c)
    except:
        c = float(c)
    if a == 0:
        showinfo("提示", "二次项次数不能为零")
        return False
    if a == 1:
        normal = "y=x²"
    else:
        normal = "y=" + str(a) + "x²"
    if b == 0:
        pass
    elif b == 1:
        normal = normal + "+x"
    else:
        normal = normal + "+" + str(b) + "x"
    if c != 0:
        normal = normal + "+" + str(c)
    normal = normal.replace("+-", "-").replace("-1x", "-x")
    print("该二次函数一般式为" + normal)
    topx = (-1) * (b / (2 * a))
    topy = (4 * a * c - b ** 2) / (4 * a)
    if topx == int(topx):
        topx == int(topx)
    if topy == int(topy):
        topy == int(topy)
    topx2 = str(topx)
    topy2 = str(topy)
    topx2 = topx2.replace("-0.0", "0")
    topy2 = topy2.replace("-0.0", "0")
    if b != "0":
        special = "y="+str(a) + "(x+" + str(-1 * topx) + ")²"
        if topy != 0:
            special = special + "+" + topy2
        special = special.replace("1(", "(").replace("+-", "-")
        print("该二次函数顶点式为" + special)
    print("顶点坐标为(" + topx2 + "," + topy2 + ")")

    temp = os.getenv("TEMP")
    with open(pj(temp, "f.txt"), "w", encoding="utf-8") as file:
        file.write("\n该二次函数一般式为" + normal)
        file.write("\n该二次函数顶点式为" + special)
        file.write("\n顶点坐标为(" + topx2 + "," + topy2 + ")")
    os.popen("taskkill -f -im Notepad.exe")
    os.popen(pj(temp, "f.txt"))


# txt = ttk.Label(tk, text="文字").place(x=100,y=,width=200,height=30,anchor="center")
# b = ttk.Button(tk, text="按钮", style="TButton", command=b).place(x=,y=,width=100,height=30)
# sep = Separato3r(tk, orient=HORIZONTAL).place(x=0,y=,width=5000,height=30)
ttk.Label(tk, text="一般式").place(x=75, y=0, width=150, height=30)
ttk.Label(tk, text="y=").place(x=0, y=30, width=40, height=20)
entry1 = Entry(tk)
entry1.place(x=20, y=30, width=30, height=20)
ttk.Label(tk, text="x²+").place(x=50, y=30, width=40, height=20)
entry2 = Entry(tk)
entry2.place(x=75, y=30, width=30, height=20)
ttk.Label(tk, text="x+").place(x=105, y=30, width=40, height=20)
entry3 = Entry(tk)
entry3.place(x=125, y=30, width=30, height=20)
ttk.Button(tk, text="计算", style="TButton", command=b1).place(x=50, y=55, width=100, height=30)
tk.mainloop()
# 2022-11-18：1.0.0：
