import sys

from .widget import *


class MainPage(BasicPage):
    """
    主页
    """
    title = "主页"
    subtitle = "常用功能"

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setIcon(FIF.HOME)

        self.button1_1 = PrimaryPushButton("开始整理+清理", self, FIF.ALIGNMENT)
        self.button1_1.clicked.connect(self.button1_1Clicked)
        self.button1_1.setToolTip("开始整理+清理文件，范围包括：\n  整理桌面文件\n  整理微信文件\n  清空回收站\n  清理系统缓存")
        self.button1_1.installEventFilter(ToolTipFilter(self.button1_1, 1000))

        self.button1_2 = ToolButton(FIF.FOLDER, self)
        self.button1_2.clicked.connect(lambda: f.startFile(setting.read("sortPath")))
        self.button1_2.setToolTip("打开整理文件所在目录")
        self.button1_2.installEventFilter(ToolTipFilter(self.button1_2, 1000))

        self.button2_1 = PushButton("重启文件资源管理器", self, FIF.SYNC)
        self.button2_1.clicked.connect(self.button2_1Clicked)
        self.button2_1.setToolTip("重启文件资源管理器")
        self.button2_1.installEventFilter(ToolTipFilter(self.button2_1, 1000))

        self.button3_1 = PushButton("查看Minecraft最新版本", self, FIF.CHECKBOX)
        self.button3_1.clicked.connect(self.button3_1Clicked)
        self.button3_1.setToolTip("查看Minecraft最新版本，数据来源：\n  我的世界中文维基百科（https://zh.minecraft.wiki/）")
        self.button3_1.installEventFilter(ToolTipFilter(self.button3_1, 1000))

        self.card1 = GrayCard("一键整理+清理", self.view)
        self.card1.addWidget(self.button1_1)
        self.card1.addWidget(self.button1_2)

        self.card2 = GrayCard("快捷功能", self.view)
        self.card2.addWidget(self.button2_1)

        self.card3 = GrayCard("游戏功能", self.view)
        self.card3.addWidget(self.button3_1)

        self.vBoxLayout.addWidget(self.card1, 0, Qt.AlignTop)
        self.vBoxLayout.addWidget(self.card2, 0, Qt.AlignTop)
        self.vBoxLayout.addWidget(self.card3, 0, Qt.AlignTop)

    def button1_1Clicked(self):
        if setting.read("sortPath") == "":
            self.infoBar = InfoBar(InfoBarIcon.WARNING, "提示", "当前未设置整理文件目录，无法整理！", Qt.Vertical, True, 5000, InfoBarPosition.TOP_RIGHT, self)
            self.infoBar.show()
            return
        if setting.read("wechatPath") == "":
            self.infoBar = InfoBar(InfoBarIcon.INFORMATION, "提示", "当前未设置微信文件目录，无法整理微信文件！", Qt.Vertical, True, 5000, InfoBarPosition.TOP_RIGHT, self)
            self.infoBar.show()

        self.button1_1.setEnabled(False)

        self.signalBool.emit(False)

        self.stateTooltip = StateToolTip("正在整理文件", "请耐心等待", self)
        self.stateTooltip.move(self.stateTooltip.getSuitablePos())
        self.stateTooltip.show()

        self.thread1_1 = NewThread("一键整理+清理")
        self.thread1_1.signalBool.connect(self.threadEvent1_1)
        self.thread1_1.start()

    def threadEvent1_1(self, msg):
        self.stateTooltip.setState(True)
        self.button1_1.setEnabled(True)
        self.signalBool.emit(True)
        if msg:
            self.stateTooltip.setContent("整理成功")
        else:
            self.stateTooltip.setContent("整理失败")

    def button2_1Clicked(self):
        self.button2_1.setEnabled(False)

        self.thread2_1 = NewThread("重启文件资源管理器")
        self.thread2_1.signalStr.connect(self.threadEvent2_1)
        self.thread2_1.start()

    def threadEvent2_1(self, msg):
        self.button2_1.setEnabled(True)

    def button3_1Clicked(self):
        self.button3_1.setEnabled(False)

        self.thread3_1 = NewThread("Minecraft最新版本")
        self.thread3_1.signalStr.connect(self.threadEvent3_1)
        self.thread3_1.start()
        self.flyout1 = Flyout(FlyoutViewBase())
        self.flyout1.create(
            icon=InfoBarIcon.INFORMATION,
            title="Minecraft最新版本",
            content="正在连接至服务器！",
            target=self.button3_1,
            parent=self,
            isClosable=False,
        )

    def threadEvent3_1(self, msg):
        self.button3_1.setEnabled(True)

        self.flyout2 = Flyout(FlyoutViewBase())
        self.flyout2.create(
            icon=InfoBarIcon.INFORMATION,
            title="Minecraft最新版本",
            content=msg,
            target=self.button3_1,
            parent=self,
            isClosable=True
        )


class ToolPage(BasicTabPage):
    """
    工具页面
    """
    title = "工具"
    subtitle = "实用工具"

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setIcon(FIF.DEVELOPER_TOOLS)


class GamePage(BasicTabPage):
    """
    游戏页面
    """
    title = "游戏"
    subtitle = "游戏功能"

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setIcon(FIF.GAME)


class SettingPage(BasicPage):
    """
    设置页面
    """
    title = "设置"
    subtitle = "设置程序"

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setIcon(FIF.SETTING)

        self.cardGroup1 = CardGroup("外观", self)
        self.cardGroup2 = CardGroup("行为", self)
        self.cardGroup3 = CardGroup("功能", self)

        self.themeSettingCard = ThemeSettingCard(self)
        self.colorSettingCard = ColorSettingCard(self)
        self.micaEffectSettingCard = MicaEffectSettingCard(self)

        self.startupSettingCard = StartupSettingCard(self)
        self.traySettingCard = TraySettingCard(self)
        self.hideSettingCard = HideSettingCard(self)

        self.sortSettingCard = SortPathSettingCard(self)
        self.sortFolderSettingCard = SortSettingCard(self)
        self.downloadSettingCard = DownloadSettingCard(self)

        self.cardGroup1.addWidget(self.themeSettingCard)
        self.cardGroup1.addWidget(self.colorSettingCard)
        self.cardGroup1.addWidget(self.micaEffectSettingCard)

        self.cardGroup2.addWidget(self.startupSettingCard)
        self.cardGroup2.addWidget(self.traySettingCard)
        self.cardGroup2.addWidget(self.hideSettingCard)

        self.cardGroup3.addWidget(self.sortSettingCard)
        self.cardGroup3.addWidget(self.sortFolderSettingCard)
        self.cardGroup3.addWidget(self.downloadSettingCard)

        self.vBoxLayout.addWidget(self.cardGroup1, 0, Qt.AlignTop)
        self.vBoxLayout.addWidget(self.cardGroup2, 0, Qt.AlignTop)
        self.vBoxLayout.addWidget(self.cardGroup3, 0, Qt.AlignTop)


class AboutPage(BasicPage):
    """
    关于页面
    """
    title = "关于"
    subtitle = "关于程序"

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setIcon(FIF.INFO)

        self.cardGroup1 = CardGroup("插件", self)
        self.cardGroup2 = CardGroup("关于", self)

        self.addonSettingCard = AddonSettingCard(self)

        self.updateSettingCard = UpdateSettingCard(self)
        self.helpSettingCard = HelpSettingCard(self)
        self.controlSettingCard = ControlSettingCard(self)
        self.shortcutSettingCard = ShortcutSettingCard(self)
        self.aboutSettingCard = AboutSettingCard(self)

        self.cardGroup1.addWidget(self.addonSettingCard)

        self.cardGroup2.addWidget(self.updateSettingCard)
        self.cardGroup2.addWidget(self.helpSettingCard)
        self.cardGroup2.addWidget(self.controlSettingCard)
        self.cardGroup2.addWidget(self.shortcutSettingCard)
        self.cardGroup2.addWidget(self.aboutSettingCard)

        self.vBoxLayout.addWidget(self.cardGroup1, 0, Qt.AlignTop)
        self.vBoxLayout.addWidget(self.cardGroup2, 0, Qt.AlignTop)


class Window(FluentWindow):
    """
    主窗口
    """
    signalStr = pyqtSignal(str)
    signalInt = pyqtSignal(int)
    signalBool = pyqtSignal(bool)
    signalList = pyqtSignal(list)
    signalDict = pyqtSignal(dict)
    signalObject = pyqtSignal(object)

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
        setTheme(eval(setting.read("theme")))
        setThemeColor("#0078D4")
        # 窗口属性
        self.resize(900, 700)
        self.setMinimumSize(700, 500)
        self.setWindowIcon(QIcon(program.PROGRAM_ICON))
        self.setWindowTitle(f"{program.PROGRAM_TITLE} {setting.read("updateChannel")}")
        self.navigationInterface.setReturnButtonVisible(False)
        # 窗口居中
        desktop = QApplication.desktop().availableGeometry()
        w, h = desktop.width(), desktop.height()
        self.move(w // 2 - self.width() // 2, h // 2 - self.height() // 2)

    def __initWidget(self):
        """
        组件初始化
        """
        self.mainPage = MainPage(self)
        self.toolPage = ToolPage(self)
        self.gamePage = GamePage(self)
        self.settingPage = SettingPage(self)
        self.aboutPage = AboutPage(self)

        self.addPage(self.mainPage, "top")
        self.addSeparator("top")
        self.addPage(self.toolPage, "scroll")
        self.addPage(self.gamePage, "scroll")
        self.addSeparator("bottom")
        self.addPage(self.settingPage, "bottom")
        self.addPage(self.aboutPage, "bottom")

    def __initActivity(self):
        # 循环监测事件
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.repeatOpen)
        self.timer.start(100)

        # 托盘组件
        self.tray = Tray(self)
        self.tray.setVisible(setting.read("showTray"))

        self.setMicaEffectEnabled(setting.read("micaEffect"))
        if setting.read("autoUpdate") and program.isStartup:
            self.aboutPage.updateSettingCard.button3Clicked()
        if program.PYTHON_VERSION.split(".")[1] != "12":
            QMessageBox(QMessageBox.Warning, "警告", f"当前Python版本为{program.PYTHON_VERSION}，{program.PROGRAM_NAME}推荐使用Python3.12版本！").exec()

        # 插件安装
        self.addAddon(f.getInstalledAddonInfo())

    def repeatOpen(self):
        """
        重复运行展示窗口
        """
        if setting.read("showWindow") == "1":
            setting.save("showWindow", "0")
            self.show()

    def keyPressEvent(self, QKeyEvent):
        """
        自定义按键事件
        """
        # Esc键
        if QKeyEvent.key() == Qt.Key_Escape:
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
            sys.exit()

    def addPage(self, page: QWidget, pos: str):
        """
        添加导航栏页面简易版
        @param page: 页面对象
        @param pos: 位置top/scroll/bottom
        """
        self.addSubInterface(page, page.icon, page.title, eval(f"NavigationItemPosition.{pos.upper()}"))

    def addSeparator(self, pos: str):
        """
        添加导航栏分割线简易版
        @param pos: 位置top/scroll/bottom
        """
        self.navigationInterface.addSeparator(eval(f"NavigationItemPosition.{pos.upper()}"))

    def addAddon(self, msg):
        """
        添加插件
        @param data: 数据
        """
        if "id" in msg.keys():
            self.__addAddon(msg)
        else:
            for v in msg.values():
                self.__addAddon(v)

    def removeAddon(self, msg):
        """
        移除插件
        @param data: 数据
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
        sys.path = [program.ADDON_PATH] + sys.path
        import importlib
        try:
            lib = importlib.import_module(data["id"])
            if data["pos"] == "tool":
                self.page = lib.AddonTab()
                self.toolPage.addPage(self.page, data["name"])
            elif data["pos"] == "game":
                self.page = lib.AddonTab()
                self.gamePage.addPage(self.page, data["name"])
            elif data["pos"] == "page":
                self.page = lib.AddonPage()
                if not self.page.title:
                    self.page.title = data["name"]
                self.addPage(self.page, "scroll")
        except Exception as ex:
            self.signalStr.emit(data["id"])
            logging.warning(f"插件{data["name"]}安装失败{ex}")

    def __removeAddon(self, data):
        """
        移除插件
        @param data: 数据
        """
        f.cmd(f"del /F /Q {f.pathJoin(program.ADDON_PATH, data["id"])}", True)
        f.delete(f.pathJoin(program.ADDON_PATH, data["id"]))
        logging.info(f"插件{data["name"]}删除成功")

        self.infoBar = InfoBar(InfoBarIcon.SUCCESS, "提示", f"插件{data["name"]}删除成功！", Qt.Vertical, True, 10000, InfoBarPosition.TOP_RIGHT, self.aboutPage)

        self.button1 = PushButton("重新启动", self, FIF.SYNC)
        self.button1.clicked.connect(self.aboutPage.controlSettingCard.button2Clicked)

        self.infoBar.addWidget(self.button1)
        self.infoBar.show()


logging.debug("window.py初始化成功")
