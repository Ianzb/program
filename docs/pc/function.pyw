# 程序信息

version = "3.0.0"

# 导入运行库

from zb import *

check()
disable("function.txt")
from math import *
from decimal import *
from matplotlib import pyplot

# 窗口初始化

tk = Tk()
tk.title("zb的函数工具 " + version)
x = 402
y = 184
if settings[5] == "经典风格":
    x += 2
    y -= 16
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


# 功能

def xy():
    pyplot.xlim(-10, 10)
    pyplot.ylim(-10, 10)
    pyplot.subplots_adjust(left=0.1, right=0.95, top=0.95, bottom=0.1)
    x = numpy.arange(-10000, 10000, 1)
    y = 0 * x
    pyplot.plot(x, y, color="black")
    y = numpy.arange(-10000, 10000, 1)
    x = 0 * y
    pyplot.plot(x, y, color="black")


def de(a):
    return Decimal(str(a))


def dde(a):
    return float(a)


def process(a, num=1, no=None):
    a = str(a)
    if a == str(no):
        logging.info(1 / 0)
    if a == "":
        a = str(num)
    if a == "-":
        a = "-1"
    a = a.replace("^", "**").replace("[", "(").replace("]", ")").replace("{", "(").replace("}", ")").replace("\ "[:-1], "/").replace("（", "(").replace("）", ")").replace("【", "(").replace("】", ")")
    try:
        a = int(a)
    except:
        try:
            if "." in str(a):
                a = str(a).rstrip("0")
            a = Decimal(str(a))
        except:
            a = Decimal(eval(a))
    if a == int(a):
        a = int(a)
    if a == 0:
        a = 0
    return a


def draw(a, b, c):
    a = process(a, 1, 0)
    b = process(b, 1)
    c = process(c, 0)
    xy()
    a = dde(a)
    b = dde(b)
    c = dde(c)
    x = numpy.arange(-10000, 10000, 0.1)
    y = a * x ** 2 + b * x + c
    pyplot.xlim(-10, 10)
    pyplot.ylim(-10, 10)
    pyplot.plot(x, y)
    pyplot.grid(color="0.7", linestyle="--", linewidth=1)
    pyplot.show()


def get1(a, b, c):
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
    normal = normal.replace("+-", "-").replace("-1x", "-x").replace("0x", "01x")
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
    if "." in str(topx):
        topx2 = str(topx).rstrip("0")
    if "." in str(topy):
        topy2 = str(topy).rstrip("0")
    if b != "0":
        if b != 0:
            if a != 1:
                special = "y=" + str(a) + "(x+" + str(-1 * topx) + ")²"
            else:
                special = "y=(x+" + str(-1 * topx) + ")²"
        else:
            if a != 1:
                special = "y=" + str(a) + "x²"
            else:
                special = "y=x²"
        if topy != 0:
            special = special + "+" + topy2
        special = special.replace("+-", "-").replace("1x", "x").replace("0x", "01x")
    der = b ** 2 - 4 * a * c
    if "." in str(der):
        der = float(str(der).rstrip("0"))
    if der == int(der):
        der = int(der)
    if der == 0:
        der = 0
    der = de(der)
    if der > 0:
        der1 = (de(-1 * b) + de(der ** de(0.5))) / de(2 * a)
        der2 = (de(-1 * b) - de(der ** de(0.5))) / de(2 * a)
    elif der == 0:
        der1 = (de(-1 * b) + de(der ** de(0.5))) / de(2 * a)
        der2 = None
    else:
        der1 = None
        der2 = None
    if der1 == 0:
        der1 = 0
    if der2 == 0:
        der2 = 0
    if der >= 0:
        if der1 == int(der1):
            der1 = int(der1)
    if der > 0:
        if der2 == int(der2):
            der2 = int(der2)
    if der > 0:
        d = "图像与x轴有2个交点，为(" + str(der1) + ",0),(" + str(der2) + ",0)"
    elif der == 0:
        d = "图像与x轴有1个交点，为(" + str(der1) + ",0)"
    else:
        d = "图像与x轴无交点"
    temp = os.getenv("TEMP")
    with open(pj(temp, "f.txt"), "w", encoding="utf-8") as file:
        file.write("该二次函数一般式为" + normal)
        file.write("\n该二次函数顶点式为" + special)
        file.write("\n对称轴为直线x=" + topx2)
        file.write("\n顶点坐标为(" + topx2 + "," + topy2 + ")")
        file.write("\n" + d)
        file.write("\n图像与y轴交点为(0," + str(c) + ")")
        file.write("\n当y=0时，Δ为" + str(der))
        if a > 0:
            file.write("\n图像开口向上\n当x>" + topx2 + "时，y随x的增大而增大，当x<" + topx2 + "时，y随x的增大而减小")
        if a < 0:
            file.write("\n图像开口向下\n当x>" + topx2 + "时，y随x的增大而减小，当x<" + topx2 + "时，y随x的增大而增大")
    os.popen(pj(temp, "f.txt"))


def b1():
    a = entry1.get()
    b = entry2.get()
    c = entry3.get()
    a = process(a, 1, 0)
    b = process(b, 1)
    c = process(c, 0)
    get1(a, b, c)


def b2():
    a = entry1.get()
    b = entry2.get()
    c = entry3.get()
    a = process(a, 1, 0)
    b = process(b, 1)
    c = process(c, 0)
    draw(a, b, c)


def b3():
    a = entry4.get()
    b = entry5.get()
    c = entry6.get()
    a = process(a, 1, 0)
    b = process(b, 0)
    c = process(c, 0)
    a1 = de(a)
    c1 = de(a * b ** 2 + c)
    b1 = de(a * 2 * b)
    get1(a1, b1, c1)


def b4():
    a = entry4.get()
    b = entry5.get()
    c = entry6.get()
    a = process(a, 1, 0)
    b = process(b, 0)
    c = process(c, 0)
    a1 = str(a)
    c1 = str(a * b ** 2 + c)
    b1 = str(a * 2 * b)
    draw(a1, b1, c1)


def b5():
    k = entry7.get()
    b = entry8.get()
    k = process(k, 1, 0)
    b = process(b, 0)
    normal = "y="
    if k == 1:
        normal = normal + "x"
    elif k == -1:
        normal = normal + "-x"
    else:
        normal = normal + str(k) + "x"
    if b != 0:
        normal = normal + "+" + str(b)
    temp = os.getenv("TEMP")
    with open(pj(temp, "f.txt"), "w", encoding="utf-8") as file:
        file.write("该一次函数一般式为" + normal)
        file.write("\n图像与x轴交点为(" + str(process((-1 * b) / k)) + ",0)")
        file.write("\n图像与y轴交点为(0," + str(b) + ")")
        if k > 0:
            file.write("\ny随x的增大而增大")
        if k < 0:
            file.write("\ny随x的增大而减小")
    os.popen(pj(temp, "f.txt"))


def b6():
    k = entry7.get()
    b = entry8.get()
    k = process(k, 1, 0)
    b = process(b, 0)
    xy()
    k = dde(k)
    b = dde(b)
    x = numpy.arange(-10000, 10000, 0.1)
    y = k * x + b
    pyplot.xlim(-10, 10)
    pyplot.ylim(-10, 10)
    pyplot.plot(x, y)
    pyplot.grid(color="0.7", linestyle="--", linewidth=1)
    pyplot.show()


def b7():
    k = entry9.get()
    k = process(k, 1, 0)
    if k == 0:
        return False
    k = dde(k)
    xy()
    pyplot.xlim(-10, 10)
    pyplot.ylim(-10, 10)
    col = (random.randint(0, 10) / 10, random.randint(0, 10) / 10, random.randint(0, 10) / 10)
    x = numpy.arange(-10000, 0, 0.1)
    y = k / x
    pyplot.plot(x, y, color=col)
    x = numpy.arange(0, 10000, 0.1)
    y = k / x
    pyplot.plot(x, y, color=col)
    y = numpy.arange(0, 10000, 0.1)
    x = k / y
    pyplot.plot(x, y, color=col)
    y = numpy.arange(-10000, 0, 0.1)
    x = k / y
    pyplot.plot(x, y, color=col)
    pyplot.grid(color="0.7", linestyle="--", linewidth=1)
    pyplot.show()


def b8():
    e1 = process(entry11.get(), 0)
    e2 = process(entry12.get(), 0)
    e3 = process(entry13.get(), 0)
    e4 = process(entry14.get(), 0)
    e5 = process(entry15.get(), 0)
    e6 = process(entry16.get(), 0)
    xy()
    e1 = dde(e1)
    e2 = dde(e2)
    e3 = dde(e3)
    e4 = dde(e4)
    e5 = dde(e5)
    e6 = dde(e6)
    x = numpy.arange(-10000, 10000, 0.1)
    y = e1 * x ** 5 + e2 * x ** 4 + e3 * x ** 3 + e4 * x ** 2 + e5 * x + e6
    pyplot.xlim(-10, 10)
    pyplot.ylim(-10, 10)
    pyplot.plot(x, y)
    pyplot.grid(color="0.7", linestyle="--", linewidth=1)
    pyplot.show()


tab = ttk.Notebook(tk, width=400, height=200)
tab1 = ttk.Frame()
tab2 = ttk.Frame()
tab3 = ttk.Frame()
tab4 = ttk.Frame()
# 控件


ttk.Label(tab1, text="y=").place(x=70, y=35, width=100, height=35)
entry7 = ttk.Entry(tab1)
entry7.place(x=90, y=35, width=100, height=35)
ttk.Label(tab1, text="x+").place(x=195, y=35, width=100, height=35)
entry8 = ttk.Entry(tab1)
entry8.place(x=215, y=35, width=100, height=35)
ttk.Button(tab1, text="计算", style="TButton", command=b5).place(x=0, y=105, width=200, height=35)
ttk.Button(tab1, text="绘制", style="TButton", command=b6).place(x=200, y=105, width=200, height=35)

ttk.Label(tab2, text="y=").place(x=130, y=35, width=100, height=35)
entry9 = ttk.Entry(tab2)
entry9.place(x=150, y=35, width=100, height=35)
ttk.Label(tab2, text="/x").place(x=255, y=35, width=100, height=35)
ttk.Button(tab2, text="绘制", style="TButton", command=b7).place(x=100, y=105, width=200, height=35)

ttk.Label(tab3, text="y=").place(x=10, y=0, width=100, height=35)
entry1 = ttk.Entry(tab3)
entry1.place(x=30, y=0, width=100, height=35)
ttk.Label(tab3, text="x²+").place(x=135, y=0, width=100, height=35)
entry2 = ttk.Entry(tab3)
entry2.place(x=160, y=0, width=100, height=35)
ttk.Label(tab3, text="x+").place(x=265, y=0, width=100, height=35)
entry3 = ttk.Entry(tab3)
entry3.place(x=285, y=0, width=100, height=35)
ttk.Button(tab3, text="计算", style="TButton", command=b1).place(x=0, y=35, width=200, height=35)
ttk.Button(tab3, text="绘制", style="TButton", command=b2).place(x=200, y=35, width=200, height=35)

ttk.Label(tab3, text="y=").place(x=10, y=70, width=100, height=35)
entry4 = ttk.Entry(tab3)
entry4.place(x=30, y=70, width=100, height=35)
ttk.Label(tab3, text="(x+").place(x=135, y=70, width=100, height=35)
entry5 = ttk.Entry(tab3)
entry5.place(x=160, y=70, width=100, height=35)
ttk.Label(tab3, text=")²+").place(x=265, y=70, width=100, height=35)
entry6 = ttk.Entry(tab3)
entry6.place(x=285, y=70, width=100, height=35)
ttk.Button(tab3, text="计算", style="TButton", command=b3).place(x=0, y=105, width=200, height=35)
ttk.Button(tab3, text="绘制", style="TButton", command=b4).place(x=200, y=105, width=200, height=35)

x1 = 0
y1 = 185
ttk.Label(tab4, text="y=").place(x=10, y=0, width=100, height=35)
entry11 = ttk.Entry(tab4)
entry11.place(x=30, y=0, width=100, height=35)
ttk.Label(tab4, text="x⁵+").place(x=135, y=0, width=100, height=35)
entry12 = ttk.Entry(tab4)
entry12.place(x=160, y=0, width=100, height=35)
ttk.Label(tab4, text="x⁴+").place(x=265, y=0, width=100, height=35)
entry13 = ttk.Entry(tab4)
entry13.place(x=290, y=0, width=100, height=35)
ttk.Label(tab4, text="x³+").place(x=10, y=35, width=100, height=35)
entry14 = ttk.Entry(tab4)
entry14.place(x=35, y=35, width=100, height=35)
ttk.Label(tab4, text="x²+").place(x=140, y=35, width=100, height=35)
entry15 = ttk.Entry(tab4)
entry15.place(x=165, y=35, width=100, height=35)
ttk.Label(tab4, text="x+").place(x=270, y=35, width=100, height=35)
entry16 = ttk.Entry(tab4)
entry16.place(x=290, y=35, width=100, height=35)
ttk.Button(tab4, text="绘制", style="TButton", command=b8).place(x=100, y=105, width=200, height=35)

tab.add(tab1, text="一次函数")
tab.add(tab2, text="反比例函数")
tab.add(tab3, text="二次函数")
tab.add(tab4, text="自由绘制")
tab.pack()
close()
tk.mainloop()
