import importlib
import traceback

from .interface import *


class Window(zbw.Window):
    """
    主窗口
    """
    initFinished = pyqtSignal()

    addAddonEvent = pyqtSignal(dict)
    removeAddonEvent = pyqtSignal(dict)
    addAddonFinishEvent = pyqtSignal(str)
    downloadAddonFailedSignal = pyqtSignal(dict)
    ADDON_OBJECT = {}  # 导入的插件的对象
    ADDON_MAINPAGE = {}

    def __init__(self):
        super().__init__()

        # 托盘组件
        self.tray = Tray(self)

        self.mainPage = MainPage(self)
        self.downloadPage = DownloadPage(self)
        self.settingPage = SettingPage(self)
        self.aboutPage = AboutPage(self)
        self.addPage(self.mainPage, self.mainPage.title(), self.mainPage.icon(), "top")
        self.addPage(self.downloadPage, self.downloadPage.title(), self.downloadPage.icon(), "top")
        self.addSeparator("top")
        self.addSeparator("bottom")
        self.addPage(self.settingPage, self.settingPage.title(), self.settingPage.icon(), "bottom")
        self.addPage(self.aboutPage, self.aboutPage.title(), self.aboutPage.icon(), "bottom")

        # 循环监测事件
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.timerEvent)
        self.timer.start(250)

        self.addAddonEvent.connect(self.addAddon)
        self.removeAddonEvent.connect(self.removeAddon)
        self.downloadAddonFailedSignal.connect(self.__downloadAddonFailed)

        # 外观调整
        self.navigationInterface.setAcrylicEnabled(True)
        # 窗口属性
        self.setMinimumSize(700, 500)
        self.setWindowIcon(QIcon(program.ICON))
        self.setWindowTitle(program.TITLE)
        self.navigationInterface.setReturnButtonVisible(False)

        if program.isStartup and setting.read("autoHide"):
            self.setWindowOpacity(0)
        self.show()
        self.resize(900, 700)
        # 窗口居中
        desktop = QApplication.screens()[0].size()
        w, h = desktop.width(), desktop.height()
        self.move(w // 2 - self.width() // 2, h // 2 - self.height() // 2)

        # 设置数据异常提醒
        if setting.errorState:
            self.infoBar = InfoBar(InfoBarIcon.ERROR, "错误", "设置文件数据错误，已自动恢复至默认选项，具体错误原因请查看程序日志！", Qt.Orientation.Vertical, True, -1, InfoBarPosition.TOP_RIGHT, self.mainPage)
            self.infoBar.show()
        self.initFinished.emit()

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

    def downloadAddon(self, data):
        program.THREAD_POOL.submit(self.__downloadAddon, data)

    def __downloadAddon(self, data):
        result = program.downloadAddonFromInfo(data)
        self.addAddonFinishEvent.emit(data.get("id"))
        if result:
            self.addAddonEvent.emit(data)
        else:
            self.downloadAddonFailedSignal.emit(data)

    def __downloadAddonFailed(self, data):
        self.infoBar = InfoBar(InfoBarIcon.ERROR, "错误", f"插件{data.get("name", "")}下载失败！", Qt.Orientation.Vertical, True, 10000, InfoBarPosition.TOP_RIGHT, self.mainPage)
        self.infoBar.show()

    def addAddon(self, data: dict):
        """
        添加插件
        @param msg: 数据
        """
        try:
            if data.get("id") in self.ADDON_OBJECT:
                try:
                    self.navigationInterface.removeWidget(data.get("name", ""))
                    self.stackedWidget.view.removeWidget(self.ADDON_MAINPAGE.get(data.get("id")))
                    if self.ADDON_MAINPAGE.get(data.get("id")):
                        self.ADDON_MAINPAGE.get(data.get("id")).deleteLater()
                except:
                    pass

                self.infoBar = InfoBar(InfoBarIcon.SUCCESS, "提示", f"插件{data.get("name", "")}更新成功，重启程序生效！", Qt.Orientation.Vertical, True, 5000, InfoBarPosition.TOP_RIGHT, self.mainPage)
                self.button1 = PushButton("重启", self, FIF.SYNC)
                self.button1.clicked.connect(program.restart)
                self.button1.setToolTip("重启程序")
                self.button1.installEventFilter(ToolTipFilter(self.button1, 1000))
                self.infoBar.addWidget(self.button1)
                self.infoBar.show()
            else:
                lib = importlib.import_module(data.get("id", ""))
                lib.addonBase.set(program, setting, self)
                lib.addonInit()
                widget = lib.addonWidget()
                widget.setObjectName(data.get("name", ""))
                self.addPage(widget, widget.title(), widget.icon(), "scroll")

                self.ADDON_OBJECT[data.get("id")] = lib
                self.ADDON_MAINPAGE[data.get("id")] = widget

                self.infoBar = InfoBar(InfoBarIcon.SUCCESS, "提示", f"插件{data.get("name", "")}安装成功！", Qt.Orientation.Vertical, True, 5000, InfoBarPosition.TOP_RIGHT, self.mainPage)
                self.infoBar.show()
            logging.info(f"插件{data.get("name", "")}安装成功")
        except Exception as ex:
            self.infoBar = InfoBar(InfoBarIcon.ERROR, "错误", f"插件{data.get("name", "")}安装失败！", Qt.Orientation.Vertical, True, 10000, InfoBarPosition.TOP_RIGHT, self.mainPage)
            self.infoBar.show()

            logging.warning(f"插件{data.get("name", "")}安装失败{traceback.format_exc()}")

    def removeAddon(self, data: dict):
        """
        移除插件
        @param msg: 数据
        """
        if data.get("id") in self.ADDON_OBJECT:
            self.navigationInterface.removeWidget(data.get("name", ""))
            mainpage = self.ADDON_MAINPAGE.get(data.get("id"))
            if mainpage:
                self.stackedWidget.view.removeWidget(mainpage)
                mainpage.deleteLater()
            self.ADDON_OBJECT.pop(data.get("id"), None)
            self.ADDON_MAINPAGE.pop(data.get("id"), None)
        zb.deleteDir(zb.joinPath(program.ADDON_PATH, data.get("id", "")), force=True)
        if not zb.existPath(zb.joinPath(program.ADDON_PATH, data.get("id", ""))):
            logging.info(f"插件{data.get("name", "")}删除成功")

            self.infoBar = InfoBar(InfoBarIcon.SUCCESS, "提示", f"插件{data.get("name", "")}删除成功！", Qt.Orientation.Vertical, True, 10000, InfoBarPosition.TOP_RIGHT, self.mainPage)
            self.infoBar.show()
        else:
            logging.info(f"插件{data.get("name", "")}删除失败")

            self.infoBar = InfoBar(InfoBarIcon.ERROR, "错误", f"插件{data.get("name", "")}删除失败！", Qt.Orientation.Vertical, True, 10000, InfoBarPosition.TOP_RIGHT, self.mainPage)
            self.infoBar.show()

    def timerEvent(self):
        """
        重复运行展示窗口
        """
        if zb.existPath(zb.joinPath(program.DATA_PATH, "zb.unlock")):
            zb.deletePath(zb.joinPath(program.DATA_PATH, "zb.unlock"))
            self.show()


logging.debug("程序主窗口类初始化成功！")
