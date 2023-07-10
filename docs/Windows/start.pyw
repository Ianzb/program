from zb import *

logging.info("开机自动更新")

def update():
    link = "https://ianzb.github.io/program/Windows/"
    res = requests.get(link + "index.html")
    res.encoding = "UTF-8"
    soup = bs4.BeautifulSoup(res.text, "lxml")
    data = soup.find_all(name="div", class_="download", text=re.compile("."))
    for i in range(len(data)): data[i] = data[i].text.strip()
    for i in range(len(data)):
        download(link + data[i])


if "D:\编程\program\docs" not in abs_path:
    update()
logging.info("自启动默认工作目录" + old_path + "，当前工作目录" + abs_path)
if ":\WINDOWS\system32".lower() in old_path.lower():
    saveSetting("startfirst", "1")
    cmd("main.pyw")
