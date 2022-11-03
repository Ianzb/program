import requests,re,bs4
def b0():
    print("检查更新")
    link = "https://ianzb.github.io/server.github.io/Seewo/"
    res = requests.get(
        link + "seewo.html")
    res.encoding = "UTF-8"
    soup = bs4.BeautifulSoup(res.text, "lxml")
    data = soup.find_all(name="div", text=re.compile("."))
    for i in range(len(data)):
        data[i] = str(data[i]).replace("<div>", "").replace("</div>", "").replace(r"\r", "").replace(r"\n", "").strip()
    for i in range(len(data)):
        response1 = requests.get(link + data[i])
        response1.encoding = "UTF-8"
        main = response1.content
        with open(data[i],"wb")as file:
            file.write(main)
        print(data[i])
b0()