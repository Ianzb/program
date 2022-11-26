# 程序信息
edition = "Seewo"

# 导入运行库
import requests, bs4, threading, os, re
from tkinter import *
from tkinter import ttk

# 读取信息
path = os.getcwd()
using = False

# 窗口初始化
tk = Tk()
tk.title(" zb的检查更新模块")
x = 200
y = 60
tk.geometry("%dx%d+%d+%d" % (x, y, (tk.winfo_screenwidth() - x) / 2, (tk.winfo_screenheight() - y) / 2))
tk.resizable(False, False)
tk.wm_attributes("-topmost", 1)
st = ttk.Style()
st.configure("TButton")

try:
    tk.wm_iconbitmap("logo.ico")
except:
    pass


# 功能
def download(link):
    response1 = requests.get(link)
    response1.encoding = "UTF-8"
    main = response1.content
    with open(link[link.rfind("/") + 1:], "wb") as file:
        file.write(main)
    tk.update()


def check_update(name):
    global using
    if using == True:
        return False
    using = True
    link = "https://ianzb.github.io/server.github.io/" + name + "/"
    res = requests.get(link + name.lower() + ".html")
    res.encoding = "UTF-8"
    soup = bs4.BeautifulSoup(res.text, "lxml")
    data = soup.find_all(name="div", text=re.compile("."))
    for i in range(len(data)): data[i] = str(data[i]).replace("<div>", "").replace("</div>", "").replace(r"\r", "").replace(r"\n", "").strip()
    for i in range(len(data)):
        vari.set(int(100 * i / len(data)))
        tk.update()
        pr = threading.Thread(target=download(link + data[i]))
        pr.start()
        tk.update()
    tk.update()
    os.popen("main.pyw")
    using = False
    exit()


# 控件
vari = IntVar()
vari.set(0)
ttk.Progressbar(tk, mode="determinate", variable=vari).place(x=0, y=0, width=200, height=30)
ttk.Button(tk, text="立刻更新For "+edition, style="TButton", command=lambda: check_update(edition)).place(x=0, y=30, width=200, height=30)

tk.mainloop()
