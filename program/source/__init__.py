
from .function import *
from .widget import *
from .program import *
from .interface import *
from traceback import format_exception
import importlib

class Window(FluentWindow, SignalBase):
    """
    主窗口
    """
    ADDON_IMPORT = {}  # 导入的插件的对象
    ADDON_MAINPAGE = {}  # 导入的插件的主页

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
        setTheme(eval(setting.read("theme")), lazy=True)
        setThemeColor("#0078D4", lazy=True)
        self.navigationInterface.setAcrylicEnabled(True)
        self.setMicaEffectEnabled(setting.read("micaEffect"))
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

    def __initWidget(self):
        """
        组件初始化
        """
        self.mainPage = MainPage(self)
        self.settingPage = SettingPage(self)
        self.aboutPage = AboutPage(self)

        self.addPage(self.mainPage, "top")
        self.addSeparator("top")
        self.addSeparator("bottom")
        self.addPage(self.settingPage, "bottom")
        self.addPage(self.aboutPage, "bottom")

    def __initActivity(self):
        # 报错检测
        if program.isExe:
            sys.excepthook = self.getException
        # 循环监测事件
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.timerEvent)
        self.timer.start(250)

        # 托盘组件
        self.tray = Tray(self)
        self.tray.setVisible(setting.read("showTray"))

        # 插件安装
        # self.addAddon(getInstalledAddonInfo())

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

    def getException(self, type, value, traceback):
        """
        报错拦截
        @param type: 报错类型
        @param value: 报错对象
        @param traceback: 报错返回信息
        """
        info = "".join(format_exception(type, value, traceback))
        logging.fatal(f"程序发生异常\n{info}")
        self.messageBox = MessageBox("程序发生异常", info, self.window())
        self.messageBox.contentLabel.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        self.messageBox.yesButton.setText("重启")
        self.messageBox.yesButton.setIcon(FIF.SYNC)
        self.messageBox.yesButton.clicked.connect(program.restart)
        self.messageBox.cancelButton.setText("关闭")
        self.messageBox.exec()

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

    def addAddon(self, msg):
        """
        添加插件
        @param msg: 数据
        """
        if "id" in msg.keys():
            self.__addAddon(msg)
        else:
            for v in msg.values():
                self.__addAddon(v)

    def removeAddon(self, msg):
        """
        移除插件
        @param msg: 数据
        """
        if "id" in msg.keys():
            self.__removeAddon(msg)
        else:
            for v in msg.values():
                self.__removeAddon(v)

    def __addAddon(self, data):
        """
        添加插件
        @param data: 数据
        """

        try:
            if data["id"] in self.ADDON_IMPORT.keys():
                self.navigationInterface.removeWidget(data["path"])
                self.stackedWidget.view.removeWidget(self.ADDON_MAINPAGE[data["id"]])
                self.ADDON_MAINPAGE[data["id"]].deleteLater()
                del self.ADDON_IMPORT[data["id"]]
                del self.ADDON_MAINPAGE[data["id"]]

                self.infoBar = InfoBar(InfoBarIcon.SUCCESS, "提示", f"插件{data["path"]}更新成功，重启程序生效！", Qt.Orientation.Vertical, True, 5000, InfoBarPosition.TOP_RIGHT, self.mainPage)
                self.button1 = PushButton("重启", self, FIF.SYNC)
                self.button1.clicked.connect(program.restart)
                self.button1.setToolTip("重启程序")
                self.button1.installEventFilter(ToolTipFilter(self.button1, 1000))
                self.infoBar.addWidget(self.button1)
                self.infoBar.show()
            else:
                self.ADDON_IMPORT[data["id"]] = importlib.import_module(data["id"])
                self.ADDON_MAINPAGE[data["id"]] = self.ADDON_IMPORT[data["id"]].AddonPage(self)
                self.ADDON_MAINPAGE[data["id"]].setObjectName(data["path"])
                self.addPage(self.ADDON_MAINPAGE[data["id"]], "scroll")

                self.infoBar = InfoBar(InfoBarIcon.SUCCESS, "提示", f"插件{data["path"]}安装成功！", Qt.Orientation.Vertical, True, 5000, InfoBarPosition.TOP_RIGHT, self.mainPage)
                self.infoBar.show()
            logging.info(f"插件{data["path"]}安装成功")
        except Exception as ex:
            self.infoBar = InfoBar(InfoBarIcon.ERROR, "错误", f"插件{data["path"]}安装失败{ex}！", Qt.Orientation.Vertical, True, 10000, InfoBarPosition.TOP_RIGHT, self.mainPage)
            self.infoBar.show()

            logging.warning(f"插件{data["path"]}安装失败{ex}")

    def __removeAddon(self, data):
        """
        移除插件
        @param data: 数据
        """
        if data["id"] in self.ADDON_IMPORT.keys():
            self.navigationInterface.removeWidget(data["path"])
            self.stackedWidget.view.removeWidget(self.ADDON_MAINPAGE[data["id"]])
            self.ADDON_MAINPAGE[data["id"]].deleteLater()
            del self.ADDON_IMPORT[data["id"]]
            del self.ADDON_MAINPAGE[data["id"]]
        easyCmd(f"del /F /Q /S {joinPath(program.ADDON_PATH, data["id"])}", True)
        deletePath(joinPath(program.ADDON_PATH, data["id"]))
        logging.info(f"插件{data["path"]}删除成功")

        self.infoBar = InfoBar(InfoBarIcon.SUCCESS, "提示", f"插件{data["path"]}删除成功！", Qt.Orientation.Vertical, True, 10000, InfoBarPosition.TOP_RIGHT, self.settingPage)
        self.infoBar.show()

    def timerEvent(self):
        """
        重复运行展示窗口
        """
        if existPath(joinPath(program.DATA_PATH, "zb.unlock")):
            deletePath(joinPath(program.DATA_PATH, "zb.unlock"))
            self.show()


logging.debug("主窗口类初始化成功")
