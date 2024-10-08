from .program import *
from .setting import *

# 日志设置
handler2 = log_import.FileHandler(program.LOGGING_FILE_PATH)
handler2.setLevel(log_import.DEBUG)
handler2.setFormatter(log_import.Formatter("[%(levelname)s %(asctime)s %(filename)s %(process)s]:%(message)s"))

logging.addHandler(handler2)


# 检查重复运行
def detectRepeatRun():
    if existPath(joinPath(program.DATA_PATH, "zb.lock")):
        with open(joinPath(program.DATA_PATH, "zb.lock"), "r+", encoding="utf-8") as file:
            pid = file.read().strip()
        if pid and "zbProgram.exe" in easyCmd(f"tasklist |findstr {pid}", True):
            open(joinPath(program.DATA_PATH, "zb.unlock"), "w").close()
            program.close()
        else:
            if existPath(joinPath(program.DATA_PATH, "zb.unlock")):
                os.remove(joinPath(program.DATA_PATH, "zb.unlock"))
            with open(joinPath(program.DATA_PATH, "zb.lock"), "w+", encoding="utf-8") as file:
                file.write(str(program.PROGRAM_PID))


detectRepeatRun()


def addToStartup(mode: bool = True):
    """
    添加开机自启动
    @param mode: True添加/False删除
    """
    import win32api, win32con
    key = win32api.RegOpenKey(win32con.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run", 0, win32con.KEY_ALL_ACCESS)
    try:
        if mode:
            win32api.RegSetValueEx(key, program.NAME, 0, win32con.REG_SZ, f"{program.MAIN_FILE_PATH} startup")
            win32api.RegCloseKey(key)
            logging.debug("启动项添加成功")
        else:
            win32api.RegDeleteValue(key, program.NAME)
            win32api.RegCloseKey(key)
            logging.debug("启动项删除成功")
    except Exception as ex:
        logging.warning(f"启动项编辑失败{ex}")


def checkStartup():
    """
    检查开机自启动
    @return: 是否
    """
    import win32api, win32con
    try:
        key = win32api.RegOpenKeyEx(win32con.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run", 0, win32con.KEY_READ)
        win32api.RegQueryValueEx(key, program.NAME)
        win32api.RegCloseKey(key)
        return True
    except win32api.error:
        return False


def getNewestVersion() -> str:
    """
    获取程序最新版本
    @return: 程序最新版本
    """
    response = getUrl(program.UPDATE_URL, REQUEST_HEADER, (15, 30))
    data = json.loads(response.text)["version"]
    logging.info(f"服务器最新版本：{data}")
    return data


def getAddonDict() -> dict:
    """
    获取插件字典
    @return: 字典
    """
    response = getUrl(program.ADDON_URL, REQUEST_HEADER, (15, 30))
    data = json.loads(response.text)
    logging.debug("插件信息获取成功")
    return data


def getAddonInfo(url: str) -> dict:
    """
    获取指定插件信息
    @param url: 链接
    @return: 信息
    """
    if not url.endswith("/"):
        url += "/"
    response = getUrl(joinUrl(url, "addon.json"), REQUEST_HEADER, (15, 30))
    data = json.loads(response.text)
    data["url"] = url
    logging.debug(f"插件{data["path"]}信息获取成功")
    return data


def downloadAddon(data: dict):
    """
    下载插件
    @param data: 插件信息
    """
    createDir(joinPath(program.ADDON_PATH, data["id"]))
    if "__init__.py" not in data["file"]:
        open(joinPath(program.ADDON_PATH, data["id"], "__init__.py"), "w", encoding="utf-8").close()
    if "addon.json" not in data["file"]:
        data["file"].append("addon.json")
    for i in data["file"]:
        if splitPath(joinPath(program.ADDON_PATH, data["id"], i), 2) == ".zip":
            singleDownload(joinUrl(data["url"], i), joinPath(program.ADDON_PATH, i).replace("init.py", "__init__.py"))
            extractZip(joinPath(program.ADDON_PATH, i), program.ADDON_PATH, True)
        else:
            singleDownload(joinUrl(data["url"], i), joinPath(program.ADDON_PATH, data["id"], i).replace("init.py", "__init__.py"))
    logging.debug(f"插件{data["path"]}下载成功")


def importAddon(path: str):
    """
    导入本体插件
    @param path: 目录
    """
    extractZip(path, program.cache(splitPath(path)))
    if existPath(joinPath(program.cache(splitPath(path)), "addon.json")):
        with open(joinPath(program.cache(splitPath(path)), "addon.json"), "r", encoding="utf-8") as file:
            data = json.loads(file.read())
        extractZip(path, joinPath(program.ADDON_PATH, data[id]))
    else:
        for i in walkDir(program.cache(splitPath(path))):
            if existPath(joinPath(i, "addon.json")):
                with open(joinPath(i, "addon.json"), "r", encoding="utf-8") as file:
                    data = json.loads(file.read())
                break
        extractZip(path, program.ADDON_PATH)
    deletePath(program.cache(splitPath(path)))
    return data


def getInstalledAddonInfo() -> dict:
    """
    获取本地插件信息
    @return: 信息
    """
    data = {}
    for i in walkDir(program.ADDON_PATH, 1):
        if existPath(joinPath(i, "addon.json")):
            with open(joinPath(i, "addon.json"), encoding="utf-8") as file:
                data[splitPath(i)] = json.loads(file.read())
    return data


logging.info("程序动态数据api初始化成功！")
