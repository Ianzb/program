import requests, lxml, bs4, threading, os, sys
from tkinter import *
from tkinter import ttk
from tkinter.ttk import Separator
from tkinter.messagebox import *

tk = Tk()
st = ttk.Style()
st.configure("TButton")
tk.title(" zb的检查更新模块")
x = 200
y = 60
now_x = (tk.winfo_screenwidth() - x) / 2
now_y = (tk.winfo_screenheight() - y) / 2
tk.geometry("%dx%d+%d+%d" % (x, y, now_x, now_y))
tk.wm_attributes("-topmost", 1)
tk.resizable(False, False)
path = os.getcwd()
try:
    tk.wm_iconbitmap("logo.ico")
except:
    showinfo("提示", "软件图标文件缺失，请使用检查更新功能补全文件！")


def download(link):
    tk.update()
    response1 = requests.get(link)
    response1.encoding = "UTF-8"
    main = response1.content
    tk.update()
    with open(link[link.rfind("/") + 1:], "wb") as file:
        file.write(main)
        tk.update()


a = [0]


def check_update(name):
    if a[0] == 1:
        return False
    a[0] = 1
    import re
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
    os.popen("main.pyw")
    exit()


vari = IntVar()
vari.set(0)
ttk.Progressbar(tk, mode="determinate", variable=vari).place(x=0, y=0, width=200, height=30)
ttk.Button(tk, text="立刻更新Myself", style="TButton", command=lambda: check_update("Myself")).place(x=0, y=30, width=200, height=30)
tk.mainloop()
