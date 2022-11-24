v = "2.0.0"

from zb import *
from fractions import Fraction
from math import *
from decimal import Decimal, getcontext

# 初始化
tk = Tk()
# 设置风格样式
st = ttk.Style()
st.configure("TButton")
# 窗口属性
tk.title(" zb的函数工具 " + v)
x = 400
y = 270
now_x = (tk.winfo_screenwidth() - x) / 2
now_y = (tk.winfo_screenheight() - y) / 2
tk.geometry("%dx%d+%d+%d" % (x, y, now_x, now_y))
tk.wm_attributes("-topmost", 1)
tk.resizable(False, False)
check_ico(tk, "logo.ico")


def xy():
    x = numpy.arange(-10000, 10000, 1)
    y = 0 * x
    pyplot.plot(x, y, color="black")
    y = numpy.arange(-10000, 10000, 1)
    x = 0 * y
    pyplot.plot(x, y, color="black")


def process(a, num=1, no=None):
    a = str(a)
    if a == str(no):
        print(1 / 0)
    if a == "":
        a = str(num)
    if a == "-":
        a = "-1"
    a = a.replace("^", "**").replace("[", "(").replace("]", ")").replace("{", "(").replace("}", ")").replace("\ "[:-1], "/").replace("（", "(").replace("）", ")").replace("【", "(").replace("】", ")")
    try:
        a = int(a)
    except:
        try:
            a = float(a)
            # a = Fraction(a)
        except:
            a = eval(a)
    if a == int(a):
        a = int(a)
    if a == 0:
        a = 0
    return a


# 功能
def draw(a, b, c):
    a = process(a, 1, 0)
    b = process(b, 1)
    c = process(c, 0)
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
    xy()
    x = numpy.arange(-10000, 10000, 0.1)
    y = a * x ** 2 + b * x + c
    pyplot.xlabel('x')
    pyplot.ylabel('y')
    pyplot.plot(x, y)
    pyplot.xlim(-20, 20)
    pyplot.ylim(-20, 20)
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
        special = special.replace("+-", "-").replace("1x", "x")
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
    a1 = a
    c1 = a * b ** 2 + c
    b1 = a * 2 * b
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
    x = numpy.arange(-10000, 10000, 0.1)
    y = k * x + b
    pyplot.xlabel('x')
    pyplot.ylabel('y')
    pyplot.plot(x, y)
    pyplot.xlim(-20, 20)
    pyplot.ylim(-20, 20)
    pyplot.grid(color="0.7", linestyle="--", linewidth=1)
    pyplot.show()


def b7():
    k = entry9.get()
    k = process(k, 1, 0)
    if k == 0:
        return False
    xy()
    pyplot.xlabel('x')
    pyplot.ylabel('y')
    col = (random.randint(0, 10) / 10, random.randint(0, 10) / 10, random.randint(0, 10) / 10)
    x = numpy.arange(-10000, 0, 0.1)
    y = k / x
    pyplot.plot(x, y, color=col)

    pyplot.xlim(-20, 20)
    pyplot.ylim(-20, 20)
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
    x = numpy.arange(-10000, 10000, 0.1)
    y = e1 * x ** 5 + e2 * x ** 4 + e3 * x ** 3 + e4 * x ** 2 + e5 * x + e6
    pyplot.xlabel('x')
    pyplot.ylabel('y')
    pyplot.plot(x, y)
    pyplot.xlim(-20, 20)
    pyplot.ylim(-20, 20)
    pyplot.grid(color="0.7", linestyle="--", linewidth=1)
    pyplot.show()


# txt = ttk.Label(tk, text="文字").place(x=100,y=,width=200,height=30,anchor="center")
# b = ttk.Button(tk, text="按钮", style="TButton", command=b).place(x=,y=,width=100,height=30)
# sep = Separato3r(tk, orient=HORIZONTAL).place(x=0,y=,width=5000,height=30)
x1 = 0
y1 = 0
ttk.Label(tk, text="一次函数").place(x=x1 + 75, y=y1, width=150, height=30)
ttk.Label(tk, text="y=").place(x=x1 + 50, y=y1 + 30, width=40, height=20)
entry7 = ttk.Entry(tk)
entry7.place(x=x1 + 70, y=y1 + 30, width=30, height=20)
ttk.Label(tk, text="x+").place(x=x1 + 100, y=y1 + 30, width=40, height=20)
entry8 = ttk.Entry(tk)
entry8.place(x=x1 + 120, y=y1 + 30, width=30, height=20)
ttk.Button(tk, text="计算", style="TButton", command=b5).place(x=x1, y=y1 + 55, width=100, height=30)
ttk.Button(tk, text="绘制", style="TButton", command=b6).place(x=x1 + 100, y=y1 + 55, width=100, height=30)
x1 = 200
y1 = 0
ttk.Label(tk, text="反比例函数").place(x=x1 + 70, y=y1, width=150, height=30)
ttk.Label(tk, text="y=").place(x=x1 + 70, y=y1 + 30, width=40, height=20)
entry9 = ttk.Entry(tk)
entry9.place(x=x1 + 90, y=y1 + 30, width=30, height=20)
ttk.Label(tk, text="/x").place(x=x1 + 120, y=y1 + 30, width=40, height=20)
ttk.Button(tk, text="绘制", style="TButton", command=b7).place(x=x1 + 50, y=y1 + 55, width=100, height=30)
x1 = 0
y1 = 95
ttk.Label(tk, text="一般式").place(x=x1 + 75, y=y1, width=150, height=30)
ttk.Label(tk, text="y=").place(x=x1, y=y1 + 30, width=40, height=20)
entry1 = ttk.Entry(tk)
entry1.place(x=x1 + 20, y=y1 + 30, width=30, height=20)
ttk.Label(tk, text="x²+").place(x=x1 + 50, y=y1 + 30, width=40, height=20)
entry2 = ttk.Entry(tk)
entry2.place(x=x1 + 75, y=y1 + 30, width=30, height=20)
ttk.Label(tk, text="x+").place(x=x1 + 105, y=y1 + 30, width=40, height=20)
entry3 = ttk.Entry(tk)
entry3.place(x=x1 + 125, y=y1 + 30, width=30, height=20)
ttk.Button(tk, text="计算", style="TButton", command=b1).place(x=x1, y=y1 + 55, width=100, height=30)
ttk.Button(tk, text="绘制", style="TButton", command=b2).place(x=x1 + 100, y=y1 + 55, width=100, height=30)
x1 = 200
y1 = 95
ttk.Label(tk, text="顶点式").place(x=x1 + 75, y=y1, width=150, height=30)
ttk.Label(tk, text="y=").place(x=x1, y=y1 + 30, width=40, height=20)
entry4 = ttk.Entry(tk)
entry4.place(x=x1 + 20, y=y1 + 30, width=30, height=20)
ttk.Label(tk, text="(x+").place(x=x1 + 50, y=y1 + 30, width=40, height=20)
entry5 = ttk.Entry(tk)
entry5.place(x=x1 + 75, y=y1 + 30, width=30, height=20)
ttk.Label(tk, text=")²+").place(x=x1 + 105, y=y1 + 30, width=40, height=20)
entry6 = ttk.Entry(tk)
entry6.place(x=x1 + 125, y=y1 + 30, width=30, height=20)
ttk.Button(tk, text="计算", style="TButton", command=b3).place(x=x1, y=y1 + 55, width=100, height=30)
ttk.Button(tk, text="绘制", style="TButton", command=b4).place(x=x1 + 100, y=y1 + 55, width=100, height=30)
ttk.Label(tk, text="二次函数").place(x=170, y=85, width=100, height=30)

ttk.Label(tk, text="自由绘制").place(x=170, y=185, width=150, height=30)

ttk.Label(tk, text="y=").place(x=0, y=215, width=20, height=20)
entry11 = ttk.Entry(tk)
entry11.place(x=20, y=215, width=30, height=20)
ttk.Label(tk, text="x⁵+").place(x=50, y=215, width=25, height=20)
entry12 = ttk.Entry(tk)
entry12.place(x=75, y=215, width=30, height=20)
ttk.Label(tk, text="x⁴+").place(x=105, y=215, width=25, height=20)
entry13 = ttk.Entry(tk)
entry13.place(x=130, y=215, width=30, height=20)
ttk.Label(tk, text="x³+").place(x=160, y=215, width=25, height=20)
entry14 = ttk.Entry(tk)
entry14.place(x=185, y=215, width=30, height=20)
ttk.Label(tk, text="x²+").place(x=215, y=215, width=25, height=20)
entry15 = ttk.Entry(tk)
entry15.place(x=240, y=215, width=30, height=20)
ttk.Label(tk, text="x+").place(x=270, y=215, width=20, height=20)
entry16 = ttk.Entry(tk)
entry16.place(x=290, y=215, width=30, height=20)

ttk.Button(tk, text="绘制", style="TButton", command=b8).place(x=150, y=240, width=100, height=30)
ttk.Separator(tk, orient=VERTICAL).place(x=200, y=0, width=1, height=85)
ttk.Separator(tk, orient=HORIZONTAL).place(x=0, y=0, width=400, height=2)
ttk.Separator(tk, orient=HORIZONTAL).place(x=0, y=85, width=400, height=2)
ttk.Separator(tk, orient=HORIZONTAL).place(x=0, y=180, width=400, height=2)
ttk.Separator(tk, orient=HORIZONTAL).place(x=0, y=270, width=400, height=2)

tk.mainloop()
# 2022-11-18：1.0.0：
# 2022-11-20：1.1.0：添加更多信息，添加图标绘制，添加顶点式，优化代码，优化外观
# 2022-11-22：1.2.0：添加分数和运算式处理功能
# 2022-11-23：2.0.0：更名为zb的函数工具，添加中文括号支持，修复顶点式标注错误的bug，添加一次函数绘制、反比例函数绘制和自由绘制功能
# 2022-11-24：2.1.0：界面完全适配系统自带风格，添加x、y轴的绘制，修复反比例函数图像绘制异常的bug
