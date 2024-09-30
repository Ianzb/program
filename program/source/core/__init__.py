from info import *
from data import *
from file import *
from web import *
from system import *

# singleDownload("https://vip.123pan.cn/1813801926/code/program/zbProgram_setup.exe",
#                r"C:\Users\93322\Downloads",
#                True,
#                True)

#
d = MultiDownload("https://vip.123pan.cn/1813801926/code/program/zbProgram_setup.exe",
                  r"C:\Users\93322\Downloads",
                  False,
                  True,
                  suffix="downloading"
                  )
import time

while True:
    time.sleep(0.1)
    print(d.finish)
    if d.finish == "finished": break
