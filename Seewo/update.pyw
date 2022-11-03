print("正在连接到服务器")
from sys import*
import requests
try:
    response1 = requests.get("https://ianzb.github.io/For%20SEEWO/main.pyw")
except:
    print("无法连接到服务器")
    exit()
print("成功连接到服务器")
response1.encoding = "UTF-8"
main = response1.text
with open("main.pyw","w",encoding="utf-8") as file:
    file.write(main)
with open("main.pyw", "r", encoding="utf-8") as file:
    main=file.readlines()
for i in range(len(main)):
    main[i]=main[i].replace("\n","")
while "" in main:
    main.remove("")
with open("main.pyw","w",encoding="utf-8") as file:
    file.close()
with open("main.pyw","a",encoding="utf-8") as file:
    for i in main:
        file.write(i+"\n")
print("更新成功")
from os import*
popen("main.pyw")
# https://ianzb.github.io/For%20SEEWO/main.pyw
