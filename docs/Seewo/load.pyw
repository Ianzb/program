import os
with open(file="pid.txt", mode="w") as file:
    file.write(str(os.getpid()))
from tkinter import *
tk = Tk()
x = 100
y = 50
tk.geometry("%dx%d+%d+%d" % (x, y, (tk.winfo_screenwidth() - x) / 2, (tk.winfo_screenheight() - y) / 2))
tk.resizable(False, False)
tk.wm_attributes("-topmost", 1)
tk.overrideredirect(True)
tk.after(5000, tk.destroy)
# 控件
Label(tk, text="加载中", font=("等线", 15)).place(x=0, y=0, width=100, height=50)
tk.mainloop()
