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


def getMD5(path: str):
    """
    等效于getHash(path,"md5")。
    """
    return getFileHash(path, "md5")


def getSha1(path: str):
    """
    等效于getHash(path,"sha1")。
    """
    return getFileHash(path, "sha1")


clearString = clearCharacters
compareVersion = compareVersionCode
urlJoin = joinUrl
cmd = easyCmd
requestGet = getUrl
requestPost = postUrl
formatPath = formatPathString
pathJoin = joinPath
makeDir = createDir

a = isSameFile(r"C:\Users\93322\p", r"C:\Users\\93322\Dop")
a = requestGet("https://ianzb.gi3thub.io")
print(a)
