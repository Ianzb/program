from .program import *
from .setting import *

# 关闭SSL证书验证
import ssl

ssl._create_default_https_context = ssl._create_unverified_context()

# 日志设置
open(program.LOGGING_FILE_PATH, "w").close() if not f.existPath(program.LOGGING_FILE_PATH) or f.fileSize(program.LOGGING_FILE_PATH) >= 1024 * 128 else None

handler2 = logging.FileHandler(program.LOGGING_FILE_PATH)
handler2.setLevel(logging.DEBUG)
handler2.setFormatter(logging.Formatter("[%(levelname)s %(asctime)s %(filename)s %(process)s]:%(message)s"))

Log.addHandler(handler2)

Log.info(f"程序启动参数{program.STARTUP_ARGUMENT}!")


# 检查重复运行
def detectRepeatRun():
    if f.existPath(f.joinPath(program.DATA_PATH, "zb.lock")):
        with open(f.joinPath(program.DATA_PATH, "zb.lock"), "r+", encoding="utf-8") as file:
            pid = file.read().strip()
        if pid and "zbProgram.exe" in f.easyCmd(f"tasklist |findstr {pid}", True):
            open(f.joinPath(program.DATA_PATH, "zb.unlock"), "w").close()
            program.close()
        else:
            if f.existPath(f.joinPath(program.DATA_PATH, "zb.unlock")):
                os.remove(f.joinPath(program.DATA_PATH, "zb.unlock"))
            with open(f.joinPath(program.DATA_PATH, "zb.lock"), "w+", encoding="utf-8") as file:
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
            Log.info("启动项添加成功")
        else:
            win32api.RegDeleteValue(key, program.NAME)
            win32api.RegCloseKey(key)
            Log.info("启动项删除成功")
    except Exception as ex:
        Log.warning(f"启动项编辑失败{ex}")


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
    response = f.getUrl(program.UPDATE_URL, f.REQUEST_HEADER, (15, 30))
    data = json.loads(response.text)["version"]
    Log.info(f"服务器最新版本：{data}")
    return data


def getOnlineAddonDict():
    """
    获取插件字典
    @return: 字典
    """
    try:
        response = f.getUrl(program.ADDON_URL, f.REQUEST_HEADER, (15, 30))
        data = json.loads(response.text)
        Log.info("插件信息获取成功！")
        return data
    except Exception as ex:
        Log.warning(f"插件信息获取失败，报错信息：{ex}！")


def getAddonInfoFromUrl(url: str):
    """
    通过自述文件链接获取指定插件信息
    @param url: 自述文件链接
    @return: 信息
    """
    try:
        response = f.getUrl(url, f.REQUEST_HEADER, (15, 30))
        data = json.loads(response.text)
        data["url"] = url
        Log.info(f"插件{data["name"]}信息获取成功")
        return data
    except Exception as ex:
        Log.error(f"插件{url}信息获取失败，报错信息：{ex}！")
        return False


def downloadAddonFromInfo(data: dict, base_url: str = ""):
    """
    通过插件自述文件数据链接获取指定插件信息
    @param data: 插件链接
    @param base_url: 基础链接（addon.json链接，仅文件为相对路径的时候需要）
    """
    try:
        dir_path = f.joinPath(program.ADDON_PATH, data["id"])
        f.createDir(dir_path)
        with open(f.joinPath(dir_path, "addon.json"), "w+") as file:
            file.write(json.dumps(data, indent=4, ensure_ascii=False))
        if not f.isUrl(data["file"]):
            data["file"] = f.joinUrl(base_url, data["file"])
        result = f.singleDownload(data["file"], dir_path)
        if result:
            f.extractZip(result, dir_path, True)
            Log.info(f"插件{data["name"]}下载成功！")
            return True
        else:
            Log.error(f"插件{data["name"]}下载失败！")
            return False
    except Exception as ex:
        Log.error(f"插件{data["name"]}在下载与解压过程中发生错误，报错信息：{ex}！")
        return False


def importAddon(path: str):
    """
    导入本体插件
    @param path: 目录
    """
    f.extractZip(path, program.cache(f.splitPath(path)))
    if f.existPath(f.joinPath(program.cache(f.splitPath(path)), "addon.json")):
        with open(f.joinPath(program.cache(f.splitPath(path)), "addon.json"), "r", encoding="utf-8") as file:
            data = json.loads(file.read())
        f.extractZip(path, f.joinPath(program.ADDON_PATH, data[id]))
    else:
        for i in f.walkDir(program.cache(f.splitPath(path))):
            if f.existPath(f.joinPath(i, "addon.json")):
                with open(f.joinPath(i, "addon.json"), "r", encoding="utf-8") as file:
                    data = json.loads(file.read())
                break
        f.extractZip(path, program.ADDON_PATH)
    f.deletePath(program.cache(f.splitPath(path)))
    return data


def getInstalledAddonInfo():
    """
    获取本地插件信息，格式为 {“插件id”:{自述文件字典数据}...}
    @return: 信息
    """
    data = {}
    for i in f.walkDir(program.ADDON_PATH, 1):
        if f.isFile(f.joinPath(i, "addon.json")):
            with open(f.joinPath(i, "addon.json"), encoding="utf-8") as file:
                addon_data = json.load(file)
                data[addon_data["id"]] = addon_data
    return data


Log.info("程序动态数据api初始化成功！")
