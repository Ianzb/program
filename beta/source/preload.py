import logging

from .function import *


class Init():
    """
    初始化程序
    """

    def __init__(self):
        # 重复运行检测
        program.detectRepeatRun()

        # 日志过大检测
        if f.getSize(program.LOGGING_FILE_PATH) / 1024 >= 32:
            logging.reset()

        # 插件检测
        f.clearFile(program.ADDON_PATH)


Init()


class Thread(threading.Thread):
    """
    threading多线程优化
    """

    def __init__(self, func, *args):
        super().__init__()

        self.func = func
        self.args = args

        self.daemon = True
        self.start()

    def run(self):
        self.func(*self.args)


class NewThread(QThread):
    """
    QThread多线程模块
    """
    signalStr = Signal(str)
    signalInt = Signal(int)
    signalBool = Signal(bool)
    signalList = Signal(list)
    signalDict = Signal(dict)
    signalObject = Signal(object)

    def __init__(self, mode: str, data=None, parent: QWidget = None):
        super().__init__(parent=parent)
        self.mode = mode
        self.data = data
        self.isCancel = False

    def run(self):
        logging.debug(f"{self.mode} 线程开始")
        if self.mode == "更新运行库":
            if not f.checkInternet("https://mirrors.tuna.tsinghua.edu.cn/"):
                self.signalBool.emit(False)
                return
            lib_list = program.REQUIRE_LIB + program.EXTRA_LIB
            for i in range(len(lib_list)):
                self.signalDict.emit({"名称": lib_list[i], "进度": int(i / len(lib_list) * 100)})
                f.pipUpdate(lib_list[i])
            self.signalBool.emit(True)
        elif self.mode == "检查更新":
            if not f.checkInternet(program.UPDATE_URL):
                self.signalBool.emit(False)
                return
            try:
                data = f.getNewestVersion()
            except:
                self.signalBool.emit(False)
                return
            if f.compareVersion(data, program.PROGRAM_VERSION) == program.PROGRAM_VERSION:
                self.signalBool.emit(True)
            else:
                self.signalDict.emit({"版本": data})
        elif self.mode == "立刻更新":
            if not f.checkInternet(program.UPDATE_URL):
                self.signalBool.emit(False)
                return
            try:
                data = f.getNewestVersion()
            except:
                self.signalBool.emit(False)
                return
            if f.compareVersion(data, program.PROGRAM_VERSION) == program.PROGRAM_VERSION:
                self.signalBool.emit(True)
                return
            response = f.requestGet(program.UPDATE_URL, program.REQUEST_HEADER)
            data = json.loads(response)["list"]
            for i in range(len(data)):
                self.signalDict.emit({"数量": len(data), "完成": False, "名称": data[i], "序号": i})
                f.downloadFile(f.urlJoin(program.UPDATE_URL, data[i]), f.pathJoin(program.PROGRAM_PATH, data[i]))
            open(f.pathJoin(program.PROGRAM_PATH, "source/__init__.py"), "w").close()
            self.signalDict.emit({"完成": True})
            logging.debug(f"更新{data}成功")
        elif self.mode == "一键整理+清理":
            try:
                Thread(lambda: f.clearRubbish())
                Thread(lambda: f.clearSystemCache())
                f.sortDir(program.DESKTOP_PATH, setting.read("sortPath"))
                if setting.read("wechatPath"):
                    f.sortWechatFiles()
                for i in setting.read("sortFolder"):
                    if f.isDir(i):
                        if not (f.belongDir(i, setting.read("sortPath")) or f.belongDir(setting.read("sortPath"), i)):
                            f.sortDir(i, setting.read("sortPath"))
                for i in list(setting.read("sortFormat").keys()) + ["文件夹"]:
                    f.clearFile(f.pathJoin(setting.read("sortPath"), i))
                f.clearFile(setting.read("sortPath"))
                self.signalBool.emit(True)
                logging.debug("一键整理成功")
            except Exception as ex:
                self.signalBool.emit(False)
                logging.warning("一键整理失败")
        elif self.mode == "重启文件资源管理器":
            f.cmd("taskkill /f /im explorer.exe", True)
            self.signalStr.emit("完成")
            f.cmd("start C:/windows/explorer.exe", True)
            logging.debug("重启文件资源管理器")
        elif self.mode == "Minecraft最新版本":
            self.signalStr.emit(f.getMC())
        elif self.mode == "下载图片":
            if not f.existPath(self.data[1]):
                f.downloadFile(self.data[0], self.data[1])
            self.signalBool.emit(True)
        elif self.mode == "下载插件":
            try:
                data = f.getAddonDict()
                for k, v in data.items():
                    if k in self.data:
                        data[k] = f.getAddonInfo(v)
                        f.downloadAddon(data[k])
                        self.signalDict.emit(data[k])
                self.signalBool.emit(True)
            except Exception as ex:
                logging.warning(f"插件下载失败{ex}")
        elif self.mode == "云端插件信息":
            try:
                data = f.getAddonDict()
                for k, v in data.items():
                    try:
                        data[k] = f.getAddonInfo(v)
                        self.signalDict.emit(data[k])
                    except Exception as ex:
                        self.signalStr.emit(v)
                self.signalBool.emit(True)
            except Exception as ex:
                self.signalBool.emit(False)
                logging.warning(f"插件信息获取失败{ex}")
        elif self.mode == "清理程序缓存":
            f.clearProgramCache()
            self.signalBool.emit(True)
        elif self.mode == "下载文件":
            try:
                d = DownloadFile(self.data[0], f.pathJoin(setting.read("downloadPath"), self.data[1]), False, ".downloading", program.REQUEST_HEADER)
                while d.result() == None:
                    self.signalInt.emit(d.rate())
                    time.sleep(0.1)
                    if self.isCancel:
                        self.isCancel = False
                        d.stop()
                        d.delete()
                        f.delete(d.path.replace(".downloading", ""))
                        self.signalBool.emit(True)
                        return
                if d.result() == False:
                    self.signalBool.emit(False)
                    logging.debug(f"文件{self.data[1]}下载失败")
                    f.delete(d.path.replace(".downloading", ""))
                if not f.existPath(d.path.replace(".downloading", "")):
                    f.moveFile(d.path, d.path.replace(".downloading", ""))
                else:
                    path = d.path.replace(".downloading", "")
                    if f.existPath(path):
                        i = 1
                        while f.existPath(f.pathJoin(f.splitPath(path, 3), f.splitPath(path, 1) + " (" + str(i) + ")" + f.splitPath(path, 2))) or f.existPath(f.pathJoin(f.splitPath(path, 3), f.splitPath(path, 1) + " (" + str(i) + ")" + f.splitPath(path, 2) + ("." if suffix else "") + suffix)):
                            i = i + 1
                        path = f.pathJoin(f.splitPath(path, 3), f.splitPath(path, 1) + " (" + str(i) + ")" + f.splitPath(path, 2))
                    f.moveFile(d.path, path)
                d.stop()
                self.signalInt.emit(d.rate())
            except:
                self.signalBool.emit(False)
        logging.debug(f"{self.mode} 线程结束")


    def cancel(self):
        logging.debug("取消下载")
        self.isCancel = True


logging.debug("thread.py初始化成功")
