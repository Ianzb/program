from .interface import *
from traceback import format_exception
import importlib

class Window(FluentWindow):
    """
    主窗口
    """

    addAddonEvent = pyqtSignal(dict)
    removeAddonEvent = pyqtSignal(dict)
    addAddonFinishEvent = pyqtSignal(str)
    downloadAddonFailedSignal = pyqtSignal(dict)
    ADDON_OBJECT = {}  # 导入的插件的对象
    ADDON_MAINPAGE = {}

    def __init__(self):
        super().__init__()
        self.__initWindow()
        self.__initWidget()
        self.__initActivity()

    def __initWindow(self):
        """
        窗口初始化
        """
        # 外观调整
        self.navigationInterface.setAcrylicEnabled(True)
        # 窗口属性
        self.resize(900, 700)
        self.setMinimumSize(700, 500)
        self.setWindowIcon(QIcon(program.ICON))
        self.setWindowTitle(program.TITLE)
        self.navigationInterface.setReturnButtonVisible(False)
        # 窗口居中
        desktop = QApplication.screens()[0].size()
        w, h = desktop.width(), desktop.height()
        self.move(w // 2 - self.width() // 2, h // 2 - self.height() // 2)
        # 托盘组件
        self.tray = Tray(self)

    def __initWidget(self):
        """
        组件初始化
        """
        self.mainPage = MainPage(self)
        self.downloadPage = DownloadPage(self)
        self.settingPage = SettingPage(self)
        self.aboutPage = AboutPage(self)

        self.addPage(self.mainPage, "top")
        self.addPage(self.downloadPage, "top")
        self.addSeparator("top")
        self.addSeparator("bottom")
        self.addPage(self.settingPage, "bottom")
        self.addPage(self.aboutPage, "bottom")

    def __initActivity(self):
        # 循环监测事件
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.timerEvent)
        self.timer.start(250)

        # 设置数据异常提醒
        if setting.errorState:
            self.infoBar = InfoBar(InfoBarIcon.ERROR, "错误", "设置文件数据错误，已自动恢复至默认选项，具体错误原因请查看程序日志！", Qt.Orientation.Vertical, True, -1, InfoBarPosition.TOP_RIGHT, self.mainPage)
            self.infoBar.show()

        self.addAddonEvent.connect(self.addAddon)
        self.removeAddonEvent.connect(self.removeAddon)
        self.downloadAddonFailedSignal.connect(self.__downloadAddonFailed)

        # 插件安装
        data = program.getInstalledAddonInfo()
        for i in data.keys():
            self.addAddon(data[i])

    def keyPressEvent(self, QKeyEvent):
        """
        自定义按键事件
        """
        # Esc键
        if QKeyEvent.key() == Qt.Key.Key_Escape:
            if setting.read("hideWhenClose"):
                self.hide()

    def closeEvent(self, QCloseEvent):
        """
        自定义关闭事件
        """
        QCloseEvent.ignore()
        if setting.read("hideWhenClose"):
            self.hide()
        else:
            program.close()

    def addPage(self, page, pos: str):
        """
        添加导航栏页面简易版
        @param page: 页面对象
        @param pos: 位置top/scroll/bottom
        """
        return self.addSubInterface(page, page.icon(), page.objectName(), eval(f"NavigationItemPosition.{pos.upper()}"))

    def addSeparator(self, pos: str):
        """
        添加导航栏分割线简易版
        @param pos: 位置top/scroll/bottom
        """
        self.navigationInterface.addSeparator(eval(f"NavigationItemPosition.{pos.upper()}"))

    def downloadAddon(self, data):
        program.THREAD_POOL.submit(self.__downloadAddon, data)

    def __downloadAddon(self, data):
        result = program.downloadAddonFromInfo(data)
        self.addAddonFinishEvent.emit(data["id"])
        if result:
            self.addAddonEvent.emit(data)
        else:

            self.downloadAddonFailedSignal.emit(data)

    def __downloadAddonFailed(self, data):
        self.infoBar = InfoBar(InfoBarIcon.ERROR, "错误", f"插件{data["name"]}下载失败！", Qt.Orientation.Vertical, True, 10000, InfoBarPosition.TOP_RIGHT, self.mainPage)
        self.infoBar.show()

    def addAddon(self, data: dict):
        """
        添加插件
        @param msg: 数据
        """
        try:
            if data["id"] in self.ADDON_OBJECT.keys():
                self.navigationInterface.removeWidget(data["name"])
                self.stackedWidget.view.removeWidget(self.ADDON_MAINPAGE[data["id"]])
                self.ADDON_MAINPAGE[data["id"]].deleteLater()

                self.infoBar = InfoBar(InfoBarIcon.SUCCESS, "提示", f"插件{data["name"]}更新成功，重启程序生效！", Qt.Orientation.Vertical, True, 5000, InfoBarPosition.TOP_RIGHT, self.mainPage)
                self.button1 = PushButton("重启", self, FIF.SYNC)
                self.button1.clicked.connect(program.restart)
                self.button1.setToolTip("重启程序")
                self.button1.installEventFilter(ToolTipFilter(self.button1, 1000))
                self.infoBar.addWidget(self.button1)
                self.infoBar.show()
            else:
                lib = importlib.import_module(data["id"])
                lib.addonBase.set(program, log, setting, self)
                widget = lib.addonInit()
                widget.setObjectName(data["name"])
                self.addPage(widget, "scroll")

                self.ADDON_OBJECT[data["id"]] = lib
                self.ADDON_MAINPAGE[data["id"]] = widget

                self.infoBar = InfoBar(InfoBarIcon.SUCCESS, "提示", f"插件{data["name"]}安装成功！", Qt.Orientation.Vertical, True, 5000, InfoBarPosition.TOP_RIGHT, self.mainPage)
                self.infoBar.show()
            log.info(f"插件{data["name"]}安装成功")
        except Exception as ex:
            self.infoBar = InfoBar(InfoBarIcon.ERROR, "错误", f"插件{data["name"]}安装失败！", Qt.Orientation.Vertical, True, 10000, InfoBarPosition.TOP_RIGHT, self.mainPage)
            self.infoBar.show()

            log.warning(f"插件{data["name"]}安装失败{ex}")

    def removeAddon(self, data: dict):
        """
        移除插件
        @param msg: 数据
        """
        if data["id"] in self.ADDON_OBJECT.keys():
            self.navigationInterface.removeWidget(data["name"])
            self.stackedWidget.view.removeWidget(self.ADDON_MAINPAGE[data["id"]])
            self.ADDON_MAINPAGE[data["id"]].deleteLater()
            del self.ADDON_OBJECT[data["id"]]
            del self.ADDON_MAINPAGE[data["id"]]
        f.deleteDir(f.joinPath(program.ADDON_PATH, data["id"]), force=True)
        if not f.existPath(f.joinPath(program.ADDON_PATH, data["id"])):
            log.info(f"插件{data["name"]}删除成功")

            self.infoBar = InfoBar(InfoBarIcon.SUCCESS, "提示", f"插件{data["name"]}删除成功！", Qt.Orientation.Vertical, True, 10000, InfoBarPosition.TOP_RIGHT, self.mainPage)
            self.infoBar.show()
        else:
            log.info(f"插件{data["name"]}删除失败")

            self.infoBar = InfoBar(InfoBarIcon.ERROR, "错误", f"插件{data["name"]}删除失败！", Qt.Orientation.Vertical, True, 10000, InfoBarPosition.TOP_RIGHT, self.mainPage)
            self.infoBar.show()

    def timerEvent(self):
        """
        重复运行展示窗口
        """
        if f.existPath(f.joinPath(program.DATA_PATH, "zb.unlock")):
            f.deletePath(f.joinPath(program.DATA_PATH, "zb.unlock"))
            self.show()


log.debug("程序主窗口类初始化成功！")
