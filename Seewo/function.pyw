v = "1.1.0"

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
def draw(a, b, c):
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

    x = numpy.arange(-1000, 1000, 0.1)
    y = a * x ** 2 + b * x + c
    pyplot.xlabel('x')
    pyplot.ylabel('y')
    pyplot.plot(x, y)
    pyplot.xlim(-100, 100)
    pyplot.ylim(-100, 100)
    pyplot.grid(color="0.5", linestyle="--", linewidth=1)
    pyplot.show()


def get(a, b, c):
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
    if a == int(a):
        a = int(a)
    if b == int(b):
        b = int(b)
    if c == int(c):
        c = int(c)
    if a == 0:
        a = 0
    if b == 0:
        b = 0
    if c == 0:
        c = 0
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

    topx = (-1) * (b / (2 * a))
    topy = (4 * a * c - b ** 2) / (4 * a)
    if topx == int(topx):
        topx = int(topx)
    if topy == int(topy):
        topy = int(topy)
    if topx == 0:
        topx = 0
    if topy == 0:
        topy = 0
    topx2 = str(topx)
    topy2 = str(topy)
    if b != "0":
        if b != 0:
            special = "y=" + str(a) + "(x+" + str(-1 * topx) + ")²"
        else:
            special = "y=" + str(a) + "x²"
        if topy != 0:
            special = special + "+" + topy2
        special = special.replace("1(", "(").replace("+-", "-").replace("1x", "x")
    der = b ** 2 - 4 * a * c
    if der == int(der):
        der = int(der)
    if der == 0:
        der = 0
    der1 = ((-1 * b) + (b ** 2 - 4 * a * c) ** (1 / 2)) / (2 * a)
    der2 = ((-1 * b) - (b ** 2 - 4 * a * c) ** (1 / 2)) / (2 * a)
    if "j" not in str(der1) and "j" not in str(der1):
        if der1 == int(der1):
            der1 = int(der1)
        if der2 == int(der2):
            der2 = int(der2)
    if der1 == 0:
        der1 = 0
    if der2 == 0:
        der2 = 0
    if der1 == der2:
        d = "图像与x轴有1个交点，为(" + str(der1) + ",0)"
    if der1 != der2:
        if "j" not in str(der1) and "j" not in str(der1):
            d = "图像与x轴有2个交点，为(" + str(der1) + ",0),(" + str(der2) + ",0)"
        else:
            d = "图像与x轴无交点"
    temp = os.getenv("TEMP")
    with open(pj(temp, "f.txt"), "w", encoding="utf-8") as file:
        file.write("该二次函数一般式为" + normal)
        file.write("\n该二次函数顶点式为" + special)
        file.write("\n顶点坐标为(" + topx2 + "," + topy2 + ")")
        file.write("\n" + d)
        file.write("\n图像与y轴交点为(0," + str(c) + ")")
        file.write("\n当y=0时，Δ为" + str(der))
        if a > 0:
            file.write("\n当x>" + topx2 + "时，y随x的增大而增大，当x<" + topx2 + "时，y随x的增大而减小")
        if a < 0:
            file.write("\n当x>" + topx2 + "时，y随x的增大而减小，当x<" + topx2 + "时，y随x的增大而增大")

    os.popen("taskkill -f -im Notepad.exe")
    time.sleep(0.1)
    os.popen(pj(temp, "f.txt"))


def b1():
    a = entry1.get()
    b = entry2.get()
    c = entry3.get()
    get(a, b, c)


def b2():
    a = entry1.get()
    b = entry2.get()
    c = entry3.get()
    draw(a, b, c)


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
ttk.Button(tk, text="计算", style="TButton", command=b1).place(x=0, y=55, width=100, height=30)
ttk.Button(tk, text="绘制", style="TButton", command=b2).place(x=100, y=55, width=100, height=30)

tk.mainloop()
# 2022-11-18：1.0.0：
# 2022-11-19：1.1.0：添加更多信息，添加图标绘制
