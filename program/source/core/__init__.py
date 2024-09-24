from data import *
from file import *
from web import *
from system import *


# 旧API部分

def removeIllegalPath(path: str):
    """
    等效于clearCharacters(path,"illegalPath")。
    """
    return clearCharacters(path, "illegalPath")


def sortVersion(self, version: list, reverse: bool = False, clear_repeat: bool = True) -> list:
    """
    等效于sortVersionCode(version,reverse,not clear_repeat)。
    """
    return sortVersionCode(version, reverse, not clear_repeat)


clearString = clearCharacters  # 别名/旧api
compareVersion = compareVersionCode  # 别名/旧api
urlJoin = joinUrl  # 别名/旧api
cmd=easyCmd  # 别名/旧api
requestGet=getUrl  # 别名/旧api
requestPost=postUrl  # 别名/旧api

print(numberAddUnit(3295))