from zb import *

logging.info("开机自动更新")
def update():
    link = "https://ianzb.github.io/server.github.io/Windows/"
    res = requests.get(link + "index.html")
    res.encoding = "UTF-8"
    soup = bs4.BeautifulSoup(res.text, "lxml")
    data = soup.find_all(name="div", class_="download", text=re.compile("."))
    for i in range(len(data)): data[i] = data[i].text.strip()
    for i in range(len(data)):
        MyThread(lambda: download(link + data[i]))
        time.sleep(0.5)
if "D:\编程\server.github.io\docs" not in abs_path:
    update()
if ":\WINDOWS\system32" in old_path:
    saveSetting("startfirst","1")
    os.popen("main.pyw")
