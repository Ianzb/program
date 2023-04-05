import os

with open(file="pid.txt", mode="w") as file:
    file.write(str(os.getpid()))
from tkinter import *
import sv_ttk

tk = Tk()
x = 100
y = 50
tk.geometry("%dx%d+%d+%d" % (x, y, (tk.winfo_screenwidth() - x) / 2, (tk.winfo_screenheight() - y) / 2))
tk.resizable(False, False)
tk.wm_attributes("-topmost", 1)
tk.overrideredirect(True)
tk.after(5000, tk.destroy)
import sv_ttk, pickle


def read_setting():
    if os.path.exists("setting.zb"):
        with open("setting.zb", "rb") as file:
            settings = pickle.load(file)
    else:
        settings = ["Myself", 0, None, "E:/整理文件", "D:/Files/Wechat/WeChat Files"] + [None for i in range(100)]
    return settings


settings = read_setting()

if settings[5] == "Light":
    sv_ttk.use_light_theme()
elif settings[5] == "Dark":
    sv_ttk.use_dark_theme()
# 控件
Label(tk, text="加载中", font=("等线", 15)).place(x=0, y=0, width=100, height=50)
tk.mainloop()
