from .function import *


class NewThread(QThread):
    """
    多线程模块
    """
    signalStr = pyqtSignal(str)
    signalInt = pyqtSignal(int)
    signalBool = pyqtSignal(bool)
    signalList = pyqtSignal(list)
    signalDict = pyqtSignal(dict)
    signalObject = pyqtSignal(object)

    def __init__(self, mode: str, data=None, parent: QWidget = None):
        super().__init__(parent=parent)
        self.mode = mode
        self.data = data

    def run(self):
        if self.mode == "更新运行库":
            for i in range(len(program.REQUIRE_LIB)):
                self.signalDict.emit({"名称": program.REQUIRE_LIB[i], "序号": i, "完成": False})
                f.pipUpdate(program.REQUIRE_LIB[i])
            self.signalDict.emit({"完成": True})
        if self.mode == "检查更新":
            try:
                data = f.getNewestVersion()
            except:
                self.signalDict.emit({"更新": False})
                return
            if f.compareVersion(data, program.PROGRAM_VERSION) == program.PROGRAM_VERSION:
                self.signalDict.emit({"更新": False})
            else:
                self.signalDict.emit({"更新": True, "版本": data})
        if self.mode == "立刻更新":
            try:
                data = f.getNewestVersion()
            except:
                self.signalDict.emit({"更新": False})
                return
            if f.compareVersion(data, program.PROGRAM_VERSION) == program.PROGRAM_VERSION:
                self.signalDict.emit({"更新": False})
                return
            response = requests.get(program.UPDATE_URL, headers=program.REQUEST_HEADER, stream=True).text
            data = json.loads(response)["list"]
            for i in range(len(data)):
                self.signalDict.emit({"更新": True, "数量": len(data), "完成": False, "名称": data[i], "序号": i})
                f.downloadFile(f.urlJoin(program.UPDATE_URL, data[i]), f.pathJoin(program.PROGRAM_PATH, data[i]))
            open(f.pathJoin(program.PROGRAM_PATH, "source/__init__.py"), "w").close()
            self.signalDict.emit({"更新": True, "完成": True})
            logging.debug(f"更新{data}成功")
        if self.mode == "一键整理+清理":
            try:
                Thread(lambda: f.clearRubbish())
                Thread(lambda: f.clearSystemCache())
                f.sortDir(program.DESKTOP_PATH, setting.read("sortPath"))
                if setting.read("wechatPath") != "":
                    f.sortWechatFiles()
                for i in list(f.SORT_FILE_DIR.keys()) + ["文件夹"]:
                    f.clearFile(f.pathJoin(setting.read("sortPath"), i))
                f.clearFile(setting.read("sortPath"))
                self.signalBool.emit(True)
                logging.debug("一键整理成功")
            except Exception as ex:
                self.signalBool.emit(False)
                logging.warning("一键整理失败")
        if self.mode == "重启文件资源管理器":
            f.cmd("taskkill /f /im explorer.exe", True)
            self.signalStr.emit("完成")
            f.cmd("start C:/windows/explorer.exe", True)
            logging.debug("重启文件资源管理器")
        if self.mode == "Minecraft最新版本":
            self.signalStr.emit(f.getMC())
        if self.mode == "下载图片":
            if not f.existPath(self.data[1]):
                f.downloadFile(self.data[0], self.data[1])
            self.signalBool.emit(True)
        if self.mode == "下载插件":
            try:
                data = f.getAddonDict()
                for k, v in data.items():
                    data[k] = f.getAddonInfo(v)
                    f.downloadAddon(data[k])
                    self.signalDict.emit(data[k])
            except Exception as ex:
                logging.warning(f"插件下载失败{ex}")
        if self.mode == "云端插件信息":
            try:
                data = f.getAddonDict()
                for k, v in data.items():
                    data[k] = f.getAddonInfo(v)
                self.signalDict.emit(data)
            except Exception as ex:
                logging.warning(f"插件信息获取败{ex}")
        if self.mode == "本地插件信息":
            try:
                data = {}
                for i in f.walkDir(program.ADDON_PATH, 1):
                    if f.existPath(f.pathJoin(i, "addon.json")):
                        with open(f.pathJoin(i, "addon.json"), encoding="utf-8") as file:
                            data[f.splitPath(i)] = json.loads(file.read())
                self.signalDict.emit(data)
            except Exception as ex:
                logging.warning(f"插件信息获取败{ex}")
        if self.mode == "清理程序缓存":
            f.clearProgramCache()
            self.signalBool.emit(True)
