# 程序信息

version = "1.0.0"
# 导入运行库
from zb import *

check()
disable("chat.txt")

# 窗口初始化

tk = Tk()
tk.title("zb的留言板 " + version)
x = 400
y = 200
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

cookie = "cookie: _ga=GA1.1.1344297400.1683002112; cf_clearance=l2aNsjVVgdkrTMjV5EQ1VUhtmICHNTqhsUWW..o2AiY-1683002132-0-150; _identity-frontend=3b058c44e405e75ea04006b8cbb2fe0c239254f0963f5423c920b133d3b1abd5a%3A2%3A%7Bi%3A0%3Bs%3A18%3A%22_identity-frontend%22%3Bi%3A1%3Bs%3A53%3A%22%5B9799192%2C%22WDC4rSrm7yI8yCyyuoMxpvd9osOGsymI%22%2C15552000%5D%22%3B%7D; pastebin-frontend=8e9d547ab83f8ec36d217df6b1506975; _csrf-frontend=691654cce2862922aeb802e5f9d5f0eac0b102889a366fad3a62175ec163e1cba%3A2%3A%7Bi%3A0%3Bs%3A14%3A%22_csrf-frontend%22%3Bi%3A1%3Bs%3A32%3A%22cveDygC-fpuhDO395lDrdbSe6bUOLrqG%22%3B%7D; _ga_S72LBY47R8=GS1.1.1683097339.2.1.1683097429.0.0.0; l2c_1=true"

headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36 Edg/112.0.1722.68"}


def get_information():
    response = requests.get("https://pastebin.com/G3tHyqtr")
    response.encoding = "UTF-8"
    soup = bs4.BeautifulSoup(response.text, "lxml")
    words = soup.find_all(class_="de1")[0].text
    return words


get_information()


def add_information():
    response = requests.get("https://pastebin.com/edit/G3tHyqtr")
    response.encoding = "UTF-8"
    soup = bs4.BeautifulSoup(response.text, "lxml")
    words = soup.find_all(class_="de1")[0].text
    return words


close()
tk.mainloop()
