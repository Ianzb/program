from program.source.program.setting import *


class ProgramFunctions():
    """
    应用函数
    """

    def __init__(self):
        super().__init__()

    def clearProgramCache(self):
        """
        清理本软件缓存
        """
        try:
            logging.reset()
            self.clearDir(f.pathJoin(program.DATA_PATH, "cache"))
        except:
            pass

    def addToStartup(self, mode: bool = True):
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

    def checkStartup(self):
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

    def getNewestVersion(self) -> str:
        """
        获取程序最新版本
        @return: 程序最新版本
        """
        response = self.requestGet(program.UPDATE_URL, program.REQUEST_HEADER, (15, 30))
        data = json.loads(response)["version"]
        logging.info(f"程序最新版本：{data}")
        return data

    def getAddonDict(self) -> dict:
        """
        获取插件字典
        @return: 字典
        """
        response = self.requestGet(program.ADDON_URL, program.REQUEST_HEADER, (15, 30))
        data = json.loads(response)
        logging.debug("插件信息获取成功")
        return data

    def getAddonInfo(self, url: str) -> dict:
        """
        获取指定插件信息
        @param url: 链接
        @return: 信息
        """
        if not url.endswith("/"):
            url += "/"
        response = self.requestGet(self.urlJoin(url, "addon.json"), program.REQUEST_HEADER, (15, 30))
        data = json.loads(response)
        data["url"] = url
        logging.debug(f"插件{data["path"]}信息获取成功")
        return data

    def downloadAddon(self, data: dict):
        """
        下载插件
        @param data: 插件信息
        """
        self.makeDir(self.pathJoin(program.ADDON_PATH, data["id"]))
        if "__init__.py" not in data["file"]:
            open(self.pathJoin(program.ADDON_PATH, data["id"], "__init__.py"), "w", encoding="utf-8").close()
        if "addon.json" not in data["file"]:
            data["file"].append("addon.json")
        for i in data["file"]:
            if self.splitPath(self.pathJoin(program.ADDON_PATH, data["id"], i), 2) == ".zip":
                self.downloadFile(self.urlJoin(data["url"], i), self.pathJoin(program.ADDON_PATH, i).replace("init.py", "__init__.py"))
                f.extractZip(self.pathJoin(program.ADDON_PATH, i), program.ADDON_PATH, True)
            else:
                self.downloadFile(self.urlJoin(data["url"], i), self.pathJoin(program.ADDON_PATH, data["id"], i).replace("init.py", "__init__.py"))
        logging.debug(f"插件{data["path"]}下载成功")

    def importAddon(self, path: str):
        """
        导入本体插件
        @param path: 目录
        """
        self.extractZip(path, program.cache(self.splitPath(path)))
        if self.existPath(self.pathJoin(program.cache(self.splitPath(path)), "addon.json")):
            with open(self.pathJoin(program.cache(self.splitPath(path)), "addon.json"), "r", encoding="utf-8") as file:
                data = json.loads(file.read())
            self.extractZip(path, self.pathJoin(program.ADDON_PATH, data[id]))
        else:
            for i in self.walkDir(program.cache(self.splitPath(path))):
                if self.existPath(self.pathJoin(i, "addon.json")):
                    with open(self.pathJoin(i, "addon.json"), "r", encoding="utf-8") as file:
                        data = json.loads(file.read())
                    break
            self.extractZip(path, program.ADDON_PATH)
        self.delete(program.cache(self.splitPath(path)))
        return data

    def getInstalledAddonInfo(self) -> dict:
        """
        获取本地插件信息
        @return: 信息
        """
        data = {}
        for i in f.walkDir(program.ADDON_PATH, 1):
            if f.existPath(f.pathJoin(i, "addon.json")):
                with open(f.pathJoin(i, "addon.json"), encoding="utf-8") as file:
                    data[f.splitPath(i)] = json.loads(file.read())
        return data





f = ProgramFunctions()
