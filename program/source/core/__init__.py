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
for i in range(10):
    MultiDownload(r"https://vip.123pan.cn/1813801926/code/program/zbProgram_setup.exe",
                      r"C:\Users\93322\Downloads",
                      False,
                      False,
                      suffix="downloading"
                      )
